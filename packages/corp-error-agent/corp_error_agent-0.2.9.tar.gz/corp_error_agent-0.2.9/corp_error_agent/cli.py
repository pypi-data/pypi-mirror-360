"""corp_error_agent CLI – just a one-time helper for config management."""
import click, json, pathlib, os
from platformdirs import user_config_dir

CONF_PATH = pathlib.Path(user_config_dir("corp_error_agent")) / "config.json"

@click.group()
def main(): ...

@main.command(help="Configure backend URL once per machine.")
@click.option("--url", required=True)
def configure(url):
    CONF_PATH.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"backend_url": url}, CONF_PATH.open("w"))
    click.echo(f"Saved backend URL → {CONF_PATH}")

if __name__ == "__main__":
    main()
