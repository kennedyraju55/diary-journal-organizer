#!/usr/bin/env python3
"""Diary Journal Organizer - Click CLI interface."""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from diary_organizer.core import (
    write_entry,
    get_entries_for_period,
    analyze_mood,
    find_themes,
    generate_insights,
    display_entries,
    analyze_themes,
    generate_word_cloud_data,
    generate_monthly_reflection,
    get_mood_stats,
    get_writing_streak,
    MOOD_EMOJIS,
    load_diary,
)

console = Console()


@click.group()
def cli():
    """📔 Diary Journal Organizer - Private diary with AI-powered insights."""
    pass


@cli.command()
@click.option('--content', '-c', default=None, help='Entry content (or enter interactively)')
@click.option('--mood', '-m', default='', help='Your current mood')
@click.option('--tags', '-t', default='', help='Comma-separated tags')
def write(content, mood, tags):
    """Write a new diary entry."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]\n"
        "[dim]Write a new entry...[/dim]",
        border_style="blue",
    ))

    if not content:
        content = Prompt.ask("[cyan]What's on your mind today?[/cyan]")

    if not mood:
        mood_options = ", ".join(f"{emoji} {name}" for name, emoji in MOOD_EMOJIS.items())
        console.print(f"[dim]Available moods: {mood_options}[/dim]")
        mood = Prompt.ask(
            "[cyan]How are you feeling?[/cyan]",
            default="neutral",
        )

    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    entry = write_entry(content, mood, tag_list)
    mood_emoji = MOOD_EMOJIS.get(mood.lower(), "📝")
    console.print(f"\n[green]✅ Entry #{entry['id']} saved for {entry['date'][:10]} {mood_emoji}[/green]")


@cli.command()
@click.option('--period', '-p', default='week', type=click.Choice(['week', 'month', 'year']),
              help='Time period for insights')
@click.option('--mood-only', is_flag=True, help='Show only mood analysis')
@click.option('--themes-only', is_flag=True, help='Show only theme analysis')
def insights(period, mood_only, themes_only):
    """Get AI-powered insights from your diary."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]\n"
        f"[dim]Generating {period}ly insights...[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    entries = get_entries_for_period(period)
    if not entries:
        console.print(f"[yellow]No entries found for the past {period}.[/yellow]")
        return

    console.print(f"[dim]Found {len(entries)} entries for the past {period}[/dim]\n")

    if mood_only:
        with console.status("[bold green]Analyzing mood patterns..."):
            result = analyze_mood(entries)
        console.print(Panel(Markdown(result), title="🎭 Mood Analysis", border_style="magenta"))
    elif themes_only:
        with console.status("[bold green]Finding themes..."):
            result = find_themes(entries)
        console.print(Panel(Markdown(result), title="🔍 Recurring Themes", border_style="cyan"))
    else:
        with console.status("[bold green]Generating comprehensive insights..."):
            result = generate_insights(entries)
        console.print(Panel(Markdown(result), title="✨ Journal Insights", border_style="green"))


@cli.command()
@click.option('--period', '-p', default='week', type=click.Choice(['week', 'month', 'year']),
              help='Time period to view')
@click.option('--last', '-n', default=10, help='Number of recent entries to show')
def view(period, last):
    """View recent diary entries."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]",
        border_style="blue",
    ))

    entries = get_entries_for_period(period)
    if not entries:
        console.print(f"[yellow]No entries found for the past {period}.[/yellow]")
        return

    display_entries(entries[-last:])
    console.print(f"\n[dim]Showing {min(last, len(entries))} of {len(entries)} entries[/dim]")


@cli.command("mood-stats")
@click.option('--period', '-p', default='month', type=click.Choice(['week', 'month', 'year']),
              help='Time period for mood stats')
def mood_stats(period):
    """Show mood statistics for a time period."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]\n"
        f"[dim]Mood statistics for the past {period}...[/dim]",
        border_style="blue",
    ))

    entries = get_entries_for_period(period)
    if not entries:
        console.print(f"[yellow]No entries found for the past {period}.[/yellow]")
        return

    stats = get_mood_stats(entries)

    table = Table(title=f"🎭 Mood Statistics ({period})")
    table.add_column("Mood", style="cyan")
    table.add_column("Emoji", justify="center")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Percentage", justify="right", style="magenta")

    for mood, count in sorted(stats["counts"].items(), key=lambda x: x[1], reverse=True):
        emoji = MOOD_EMOJIS.get(mood, "📝")
        pct = stats["percentages"].get(mood, 0)
        bar = "█" * int(pct / 5)
        table.add_row(mood.capitalize(), emoji, str(count), f"{pct}% {bar}")

    console.print(table)
    console.print(f"\n[dim]Total entries with mood: {stats['total']}[/dim]")


@cli.command("word-cloud")
@click.option('--period', '-p', default='month', type=click.Choice(['week', 'month', 'year']),
              help='Time period')
@click.option('--top', '-n', default=20, help='Number of top words to show')
def word_cloud(period, top):
    """Show top words from your diary entries."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]\n"
        "[dim]Generating word cloud data...[/dim]",
        border_style="blue",
    ))

    entries = get_entries_for_period(period)
    if not entries:
        console.print(f"[yellow]No entries found for the past {period}.[/yellow]")
        return

    word_data = generate_word_cloud_data(entries)
    top_words = sorted(word_data.items(), key=lambda x: x[1], reverse=True)[:top]

    table = Table(title=f"☁️ Word Cloud ({period})")
    table.add_column("Word", style="cyan")
    table.add_column("Frequency", justify="right", style="green")
    table.add_column("", style="magenta")

    max_count = top_words[0][1] if top_words else 1
    for word, count in top_words:
        bar_len = int((count / max_count) * 20)
        table.add_row(word, str(count), "█" * bar_len)

    console.print(table)


@cli.command()
@click.option('--year', '-y', default=None, type=int, help='Year (default: current)')
@click.option('--month', '-m', default=None, type=int, help='Month (default: current)')
def reflection(year, month):
    """Generate a monthly reflection using AI."""
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]\n"
        f"[dim]Generating reflection for {year}-{month:02d}...[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    with console.status("[bold green]Creating monthly reflection..."):
        result = generate_monthly_reflection(year, month)

    console.print(Panel(Markdown(result), title=f"📅 Monthly Reflection – {year}-{month:02d}", border_style="green"))


@cli.command()
def streak():
    """Show your writing streak."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]\n"
        "[dim]Checking your writing streak...[/dim]",
        border_style="blue",
    ))

    streak_info = get_writing_streak()

    console.print()
    if streak_info["current_streak"] > 0:
        console.print(f"  🔥 [bold green]Current Streak:[/bold green] {streak_info['current_streak']} day(s)")
    else:
        console.print("  ❄️  [yellow]Current Streak:[/yellow] 0 days – write today to start one!")

    console.print(f"  🏆 [bold cyan]Longest Streak:[/bold cyan]  {streak_info['longest_streak']} day(s)")
    console.print(f"  📝 [bold]Total Days Written:[/bold] {streak_info['total_days']}")
    console.print()


if __name__ == '__main__':
    cli()
