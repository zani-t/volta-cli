# Entry point script

from volta_cli import __app_name__, cli

def main():
    cli.app(prog_name=__app_name__)