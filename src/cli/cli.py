@cli.command()
@click.option('--daemon', is_flag=True, help='Run in auto-renewal daemon mode')
@click.option('--force', is_flag=True, help='Force immediate renewal')
@click.option('--provider', type=click.Choice(['aws', 'gcp', 'letsencrypt', 'selfsigned']), help='Specify certificate provider')
def cert_manager(daemon, force, provider):
    """Manage SSL certificates"""
    ssl_mgr = SSLCertManager()
    
    if provider:
        ssl_mgr.config.update({'use_custom_ca': False, 'cloud_provider': provider})
    
    if force:
        ssl_mgr.renew_certificates()
        
    if daemon:
        ssl_mgr.start_auto_renewal()
        while True:
            time.sleep(3600)
    else:
        ssl_mgr.check_and_renew()

@cli.command()
def cert_audit_log():
    """Show certificate audit log"""
    ssl_mgr = SSLCertManager()
    click.echo(json.dumps(ssl_mgr.audit_log, indent=2))

