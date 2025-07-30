import asyncio
import signal
import threading
import subprocess
import click
from uvicorn import Config, Server
from linkiq.view.api import app

from linkiq.controller.scheduler import Scheduler
from linkiq.controller.search_handler import LISearchHandler
from linkiq.controller.li_handler import LIHandler
from linkiq.controller.profile_handler import LIProfileHandler
from linkiq.controller.message_handler import LIMessageHandler
from linkiq.controller.view_handler import LIViewHandler
from linkiq.controller.post_handler import LIPostHandler
from linkiq.controller.reaction_handler import LIReactionHandler
from linkiq.controller.campaign_handler import CampaignHandler

from linkiq.model.db_client import DBClient


# Shared state
stop_event = threading.Event()

def run_scheduler():
    scheduler = Scheduler()
    scheduler.run(stop_event=stop_event)

async def run_uvicorn():
    config = Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = Server(config)
    await server.serve()

def signal_handler(*args):
    print("Signal received, stopping...")
    stop_event.set()

async def async_main():
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    await asyncio.gather(
        asyncio.to_thread(run_scheduler),
        run_uvicorn(),
    )

def main_background():
    """Run background scheduler and UI together."""
    try:
        asyncio.run(async_main())
    except Exception as e:
        print(f"Application stopped! Reason: {e}")

def run_search(max_profiles):
    try:
        db_client = DBClient()
        li_handler = LIHandler()
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        raise
    page = li_handler.get_page(headless=False)
    li_search_handler = LISearchHandler(db_client, page)
    while True:
        li_search_handler.gather_profiles(max_profiles=max_profiles)
        choice = input("Do you want to continue search? (Y/N): ").strip().lower()
        if choice != 'y':
            print("[green]Exiting search.[/green]")
            break
    li_profile_handler = LIProfileHandler(db_client, page)
    li_profile_handler.get_profiles()

def run_leadgen(max_profiles):
    try:
        db_client = DBClient()
        li_handler = LIHandler()
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        raise
    page = li_handler.get_page(headless=False)
    li_profile_handler = LIProfileHandler(db_client, page)
    li_profile_handler.get_profiles(max_profiles)

def run_outreach(max_connect_request, max_first_message):
    try:
        db_client = DBClient()
        li_handler = LIHandler()
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        raise
    page = li_handler.get_page(headless=False)
    li_message_handler = LIMessageHandler(db_client, page)
    li_message_handler.process_leads(max_connect_request, max_first_message)

def run_gatherer(profile_views: bool, post_reaction: bool):
    try:
        db_client = DBClient()
        li_handler = LIHandler()
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        raise
    page = li_handler.get_page(headless=False)
    if profile_views:
        print("[green]Gathering profile views...[/green]")
        li_view_handler = LIViewHandler(db_client, page)
        li_view_handler.gather_profile_views()

    if post_reaction:
        print("[green]Gathering post reactions...[/green]")
        li_post_handler = LIPostHandler(db_client, page)
        li_post_handler.get_post_urls()
        li_reaction_handler = LIReactionHandler(db_client, page)
        li_reaction_handler.gather_reactions()

# === CLI section ===

@click.group()
def cli():
    """LinkIQ CLI - Your LinkedIn Growth Assistant"""
    pass

@cli.command()
def view():
    """Launch just the FastAPI UI server."""
    subprocess.run(["uvicorn", "linkiq.view.api:app", "--host", "0.0.0.0", "--port", "8000"])

@cli.command()
def scheduler():
    """Run only the scheduler."""
    run_scheduler()

@cli.command()
def run():
    """Run both background scheduler and UI."""
    main_background()

@cli.command()
@click.option(
    '--max-profiles', '-m',
    default=100,
    show_default=True,
    type=int,
    help='Maximum number of profiles to gather per search round.'
)
def search(max_profiles):
    """Search and gather LinkedIn profiles."""
    run_search(max_profiles)

@cli.command()
@click.option(
    '--max-profiles', '-m',
    default=20,
    show_default=True,
    type=int,
    help='Maximum number of profiles to evaluate.'
)
def leadgen(max_profiles):
    """Search and gather LinkedIn profiles."""
    run_leadgen(max_profiles)

@cli.command()
@click.option('--max-connect-request', '-c', default=10, show_default=True, type=int,help='Maximum connect requests to send. Max is 10')
@click.option('--max-first-message', '-m', default=10, show_default=True, type=int,help='Maximum connect requests to send. Max is 10')
def outreach(max_connect_request, max_first_message):
    """Send messages to qualified leads"""
    max_connect_request = min(max_connect_request, 10)
    max_first_message = min(max_first_message, 10)
    run_outreach(max_connect_request, max_first_message)

@cli.command()
@click.option('-v', '--profile-views', is_flag=True, help='Gather profile views only.')
@click.option('-p', '--post-reaction', is_flag=True, help='Gather post reactions only.')
def gather(profile_views, post_reaction):
    """Gather LinkedIn data like profile views and post reactions."""
    # If neither flag is set, assume both
    if not profile_views and not post_reaction:
        profile_views = True
        post_reaction = True

    run_gatherer(profile_views=profile_views, post_reaction=post_reaction)

# === Campaign Subcommands ===

@cli.group()
def camp():
    """Manage campaigns."""
    pass

@camp.command("create")
@click.option("-A", "--all", is_flag=True, help="Prompt for all campaign fields")
def create(all):
    """Create a new campaign interactively."""
    click.echo("Creating a new campaign...")

    name = click.prompt("Campaign name", type=str).strip()
    if not name:
        click.secho("Campaign name is required.", fg="red")
        return

    include_keywords = click.prompt(
        "Include keywords (comma separated) (empty means everyone is qualified)", default="", show_default=False
    ).strip().split(",")

    exclude_keywords = click.prompt(
        "Exclude keywords (comma separated) (empty means everyone is qualified)", default="", show_default=False
    ).strip().split(",")

    connect_message = click.prompt(
        "Connection request message", default="", show_default=False
    ).strip()

    first_message = click.prompt(
        "First message after connection", default="", show_default=False
    ).strip()

    campaign_data = {
        "name": name,
        "include_keywords": [kw.strip() for kw in include_keywords if kw.strip()],
        "exclude_keywords": [kw.strip() for kw in exclude_keywords if kw.strip()],
        "connect_message": connect_message,
        "first_message": first_message
    }

    if all:
        ideal_persona = click.prompt("Ideal persona", default="", show_default=False).strip()
        lead_score_threshold = click.prompt("Lead score threshold (0-100)", type=int, default=0)
        model_provider = click.prompt("Model provider (openai, anthropic, grok)", default="", show_default=False).strip()
        model = click.prompt("Model name", default="", show_default=False).strip()
        subject_line = click.prompt("Subject line", default="", show_default=False).strip()
        follow_up = click.prompt("Follow-up message", default="", show_default=False).strip()

        campaign_data.update({
            "ideal_persona": ideal_persona,
            "lead_score_threshold": lead_score_threshold,
            "model_provider": model_provider,
            "model": model,
            "subject_line": subject_line,
            "follow_up": follow_up
        })

    CampaignHandler.create(campaign_data)
    click.secho(f"Campaign '{name}' created successfully.", fg="green")

@camp.command("list")
def list():
    """List all campaign names."""
    ch = CampaignHandler()
    names = ch.get_names()
    if not names:
        click.echo("No campaigns found.")
        return
    click.echo("Available campaigns:")
    for name in names:
        click.echo(f" - {name}")

@camp.command("get")
@click.argument("name")
@click.option("-j", "as_json", is_flag=True, help="Output in JSON format")
def get(name, as_json):
    """Get campaign details by name."""
    ch = CampaignHandler()
    campaign = ch.get_by_name(name)

    if campaign is None:
        click.secho(f"❌ Campaign '{name}' not found.", fg="red")
        return

    data = campaign.model_dump() if hasattr(campaign, "model_dump") else campaign.dict()

    if as_json:
        import json
        click.echo(json.dumps(data, indent=2))
        return

    click.secho(f"📄 Campaign: {name}\n", fg="cyan", bold=True)

    for k, v in data.items():
        key_str = click.style(f"{k}:", fg="yellow")
        val_str = "(none)" if v is None else v
        click.echo(f"{key_str} {val_str}")
