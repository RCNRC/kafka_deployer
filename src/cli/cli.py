import click
from pathlib import Path
from ..core import ConfigManager, AnsibleRunner
from ..core.monitoring import MetricsCollector, AutoOptimizer
from ..ssl_manager import SSLCertManager

@click.group()
def cli():
    pass

@cli.command()
@click.argument('config_path')
def deploy(config_path):
    """Deploy Kafka cluster using configuration file"""
    cm = ConfigManager()
    config = cm.load_config(config_path)
    ansible = AnsibleRunner()
    ansible.run_playbook('deploy_kafka.yml', cm.generate_inventory(config['nodes']))

@cli.command()
def status():
    """Show cluster health status"""
    collector = MetricsCollector()
    click.echo("Cluster health metrics:")
    click.echo(f"Memory Used: {collector.metrics['kafka_jvm_memory_used'].collect()[0].samples[0].value} MB")
    click.echo(f"Consumer Lag: {collector.metrics['consumer_lag'].collect()[0].samples[0].value} messages")

@cli.command()
@click.option('--threshold', default=80, help='CPU usage threshold for optimization')
def optimize(threshold):
    """Automatically optimize cluster configuration"""
    collector = MetricsCollector()
    optimizer = AutoOptimizer()
    optimizations = optimizer.optimize_configuration(collector.get_current_metrics())
    
    if optimizations:
        click.echo("Applying optimizations:")
        for key, value in optimizations.items():
            click.echo(f"{key} = {value}")
    else:
        click.echo("No optimizations required at this time")

@cli.command()
@click.option('--dns', help='Comma-separated list of domains for certificate')
@click.option('--force', is_flag=True, help='Force renewal even if not expired')
def rotate-certs(dns, force):
    """Rotate SSL certificates for the cluster"""
    ssl_mgr = SSLCertManager()
    hostnames = dns.split(',') if dns else None
    
    try:
        if not force:
            ssl_mgr.validate_certificates(hostnames)
            click.echo("Certificates are valid, use --force to renew anyway")
            return
    except Exception as e:
        click.echo(f"Certificate validation failed: {str(e)}, proceeding with renewal")
    
    ssl_mgr.renew_certificates(hostnames)
    click.echo("Successfully rotated certificates")

