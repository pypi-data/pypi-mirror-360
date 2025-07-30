"""
Review functions for asimov events.
"""

import os

import click

from asimov import config, current_ledger
from asimov.pipelines import known_pipelines
from asimov.review import ReviewMessage


@click.group()
def review():
    """Add and view review information and sign-offs"""
    pass


@click.option("--message", "-m", "message", default=None)
@click.argument("status", required=False, default=None)
@click.argument("production", required=True)
@click.argument("event", required=True)
@review.command()
def add(event, production, status, message):
    """
    Add a review signoff or rejection to an event.
    """
    valid = {"REJECTED", "APPROVED", "PREFERRED", "DEPRECATED"}
    events = current_ledger.get_event(event)
    if events is None:
        click.echo(
            click.style("●", fg="red") + f" Could not find an event called {event}"
        )
    else:
        for event in events:
            production = [
                production_o
                for production_o in event.productions
                if production_o.name == production
            ][0]
            click.secho(event.name, bold=True)

            if status is not None and status.upper() in valid:
                message = ReviewMessage(
                    message=message, status=status, production=production
                )
                production.review.add(message)
            elif status is None:
                message = ReviewMessage(
                    message=message, status=None, production=production
                )
                production.review.add(message)
            else:
                click.echo(
                    click.style("●", fg="red")
                    + f" Did not understand the review status {status.lower()}."
                    + " The review status must be one of "
                    + "{APPROVED, REJECTED, PREFERRED, DEPRECATED}"
                )

            if hasattr(event, "issue_object"):
                production.event.update_data()
            current_ledger.update_event(event)
            if status is not None:
                click.echo(
                    click.style("●", fg="green")
                    + f" {event.name}/{production.name} {status.lower()}"
                )
            else:
                click.echo(
                    click.style("●", fg="green")
                    + f" {event.name}/{production.name} Note added"
                )


@click.argument("production", default=None, required=False)
@click.argument("event", default=None, required=False)
@review.command()
def status(event, production):
    """
    Show the review status of an event.
    """
    for event in current_ledger.get_event(event):
        click.secho(event.name, bold=True)
        if production:
            productions = [
                prod for prod in event.productions if prod.name == production
            ]
        else:
            productions = event.productions

        for production in productions:
            click.secho(f"\t{production.name}", bold=True)
            if production.review:
                click.echo(f"\t\t {production.review.status.lower()}")
            else:
                click.secho("\t\tNo review information exists for this production.")


@click.argument("event", default=None, required=False)
@review.command()
def audit(event):
    """
    Conduct an audit of the contents of production ini files
    against the production ledger.

    Parameters
    ----------
    event : str, optional
       The event to be checked.
       Optional; if the event isn't provided all events will be audited.
    """
    if isinstance(event, str):
        event = [event]

    for production in current_ledger.get_event(event)[0].productions:
        category = config.get("general", "calibration_directory")
        config_file = os.path.join(
            production.event.repository.directory, category, f"{production.name}.ini"
        )
        pipe = known_pipelines[production.pipeline.lower()](production, category)
        click.echo(pipe.read_ini(config_file))
