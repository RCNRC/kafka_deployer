@cli.command()
@click.option('--daemon', is_flag=True, help='Run in auto-renewal daemon mode')
def cert-manager(daemon):
    """Manage SSL certificates"""
    ssl_mgr = SSLCertManager()
    
    if daemon:
        ssl_mgr.start_auto_renewal()
        while True:
            time.sleep(3600)  # Keep process alive
    else:
        ssl_mgr.check_and_renew()
