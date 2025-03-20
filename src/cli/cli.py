import click
from pathlib import Path
from ..core import ConfigManager, AnsibleRunner
from ..core.monitoring import MetricsCollector, AutoOptimizer

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
        # Apply config changes through Ansible
    else:
        click.echo("No optimizations required at this time")

