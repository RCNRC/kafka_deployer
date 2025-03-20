@cli.command()
@click.argument('version', type=int)
def rollback-config(version):
    """Rollback to specific configuration version"""
    versioning = ConfigurationVersioning()
    try:
        config = versioning.rollback(version)
        click.echo(f"Successfully rolled back to version {version}")
    except IndexError:
        click.echo("Invalid version number")

@cli.command()
def config-history():
    """Show configuration change history"""
    versioning = ConfigurationVersioning()
    for idx, ver in enumerate(versioning.history):
        click.echo(f"Version {idx}: {ver['timestamp']} - {ver['comment']}")

@cli.command()
def train-model():
    """Retrain ML tuning model"""
    tuner = TuningEngine()
    training_data = pd.read_csv('training_data.csv')
    tuner.train_model(training_data)
    click.echo("Model retraining completed")

