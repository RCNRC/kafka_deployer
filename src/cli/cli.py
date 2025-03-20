import click
from pathlib import Path
from ..core import ConfigManager, AnsibleRunner

@click.group()
def cli():
    """Kafka cluster deployment tool"""
    pass

@cli.command()
@click.option("--config", required=True, help="Path to cluster config file")
def deploy(config):
    """Deploy Kafka cluster using configuration file"""
    click.echo(f"Starting deployment with config: {config}")
    
    # Load configuration
    cm = ConfigManager()
    config_data = cm.load_config(config)
    
    # Generate inventory
    inventory = cm.generate_inventory(config_data["nodes"])
    with open("inventory.ini", "w") as f:
        f.write(inventory)
    
    # Run Ansible playbooks
    ansible = AnsibleRunner()
    success = ansible.run_playbook("kafka_deploy.yml")
    
    if success:
        click.secho("Deployment completed successfully!", fg="green")
    else:
        click.secho("Deployment failed!", fg="red")
