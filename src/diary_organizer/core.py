#!/usr/bin/env python3
"""Diary Journal Organizer - Core functions for diary management and AI insights."""

import sys
import os
import json
import logging
import re
from datetime import datetime, timedelta
from collections import Counter

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import generate, check_ollama_running

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')


def load_config() -> dict:
    """Load configuration from config.yaml."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return yaml.safe_load(f)
        except (yaml.YAMLError, IOError) as exc:
            logger.warning("Failed to load config.yaml: %s – using defaults", exc)
    return {
        "app": {"name": "Diary Journal Organizer", "version": "1.0.0", "log_level": "INFO", "data_dir": "./data"},
        "diary": {"default_period": "week", "entries_per_page": 10},
        "llm": {"model": "llama3", "temperature": 0.6, "system_prompt": "You are a compassionate journal therapist."},
    }


config = load_config()

logging.basicConfig(
    level=getattr(logging, config.get("app", {}).get("log_level", "INFO"), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', config.get("app", {}).get("data_dir", "./data")))
os.makedirs(DATA_DIR, exist_ok=True)
DIARY_FILE = os.path.join(DATA_DIR, "diary.json")

MOOD_EMOJIS = {
    "happy": "😊",
    "sad": "😢",
    "anxious": "😰",
    "calm": "😌",
    "excited": "🎉",
    "angry": "😤",
    "grateful": "🙏",
    "tired": "😴",
    "nostalgic": "🥹",
    "inspired": "✨",
    "peaceful": "🕊️",
    "loved": "❤️",
    "proud": "🏆",
    "confused": "😕",
    "hopeful": "🌅",
    "creative": "🎨",
}

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "this", "that",
    "these", "those", "i", "me", "my", "we", "our", "you", "your",
    "he", "she", "they", "them", "his", "her", "its", "not", "no",
    "so", "if", "just", "about", "up", "out", "then", "than", "very",
    "really", "also", "some", "any", "all", "more", "most", "much",
    "many", "such", "what", "which", "who", "when", "where", "how",
    "each", "every", "both", "few", "as", "into", "over", "after",
    "before", "between", "through", "during", "because", "while",
}

# ---------------------------------------------------------------------------
# Core diary functions (original)
# ---------------------------------------------------------------------------


def load_diary() -> dict:
    """Load diary entries from JSON file."""
    if os.path.exists(DIARY_FILE):
        try:
            with open(DIARY_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            logger.error("Failed to load diary file, returning empty diary")
            return {"entries": []}
    return {"entries": []}


def save_diary(diary: dict) -> None:
    """Save diary entries to JSON file."""
    with open(DIARY_FILE, 'w') as f:
        json.dump(diary, f, indent=2)
    logger.info("Diary saved with %d entries", len(diary.get("entries", [])))


def write_entry(content: str, mood: str = "", tags: list = None) -> dict:
    """Write a new diary entry."""
    diary = load_diary()
    entry = {
        "id": len(diary["entries"]) + 1,
        "date": datetime.now().isoformat(),
        "content": content,
        "mood": mood,
        "tags": tags or [],
    }
    diary["entries"].append(entry)
    save_diary(diary)
    logger.info("New entry #%d written", entry["id"])
    return entry


def get_entries_for_period(period: str) -> list:
    """Get entries for a specific time period."""
    diary = load_diary()
    now = datetime.now()

    if period == "week":
        cutoff = now - timedelta(days=7)
    elif period == "month":
        cutoff = now - timedelta(days=30)
    elif period == "year":
        cutoff = now - timedelta(days=365)
    else:
        cutoff = now - timedelta(days=7)

    filtered = []
    for entry in diary["entries"]:
        try:
            entry_date = datetime.fromisoformat(entry["date"])
            if entry_date >= cutoff:
                filtered.append(entry)
        except (ValueError, KeyError):
            continue

    logger.debug("Found %d entries for period '%s'", len(filtered), period)
    return filtered


# ---------------------------------------------------------------------------
# AI-powered analysis functions (original)
# ---------------------------------------------------------------------------


def analyze_mood(entries: list) -> str:
    """Analyze mood patterns using AI."""
    entries_text = "\n\n".join(
        f"Date: {e['date'][:10]}\nMood: {e.get('mood', 'not specified')}\nEntry: {e['content']}"
        for e in entries
    )

    prompt = f"""Analyze the mood patterns in these diary entries:

{entries_text}

Provide:
1. **Overall Mood Trend**: How has the mood changed over time?
2. **Common Emotions**: Most frequently expressed emotions
3. **Mood Triggers**: What events or topics affect mood positively/negatively
4. **Emotional Patterns**: Any recurring patterns (day of week, time patterns)
5. **Wellness Suggestions**: Kind, supportive suggestions for emotional well-being

Be empathetic, supportive, and non-judgmental in your analysis."""

    llm_config = config.get("llm", {})
    return generate(
        prompt=prompt,
        system_prompt=llm_config.get("system_prompt", "You are a compassionate journal therapist who provides supportive mood analysis. Be warm, empathetic, and constructive."),
        temperature=llm_config.get("temperature", 0.6),
    )


def find_themes(entries: list) -> str:
    """Find recurring themes in diary entries."""
    entries_text = "\n\n".join(
        f"- {e['date'][:10]}: {e['content'][:200]}" for e in entries
    )

    prompt = f"""Identify recurring themes in these diary entries:

{entries_text}

Provide:
1. **Major Themes**: Top 5 recurring topics or concerns
2. **Growth Areas**: Topics showing personal development
3. **Patterns**: Recurring situations or feelings
4. **Reflection Prompts**: Questions for deeper self-reflection based on themes

Format in clear markdown."""

    llm_config = config.get("llm", {})
    return generate(
        prompt=prompt,
        system_prompt="You are a thoughtful journal analysis assistant.",
        temperature=llm_config.get("temperature", 0.5),
    )


def generate_insights(entries: list) -> str:
    """Generate comprehensive insights from diary entries."""
    entries_text = "\n\n".join(
        f"Date: {e['date'][:10]}\nMood: {e.get('mood', 'N/A')}\nTags: {', '.join(e.get('tags', []))}\nEntry: {e['content']}"
        for e in entries
    )

    prompt = f"""Provide comprehensive insights from these diary entries:

{entries_text}

Generate:
1. **Summary**: Brief overview of the period
2. **Mood Analysis**: Emotional trends and patterns
3. **Key Events**: Most significant happenings
4. **Recurring Themes**: Topics that come up repeatedly
5. **Personal Growth**: Areas of development or change
6. **Recommendations**: Supportive suggestions for well-being

Be compassionate and constructive."""

    llm_config = config.get("llm", {})
    return generate(
        prompt=prompt,
        system_prompt="You are a caring journal insights assistant providing thoughtful, supportive analysis.",
        temperature=llm_config.get("temperature", 0.6),
    )


def display_entries(entries: list) -> None:
    """Display diary entries in formatted panels."""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    for entry in entries:
        mood_emoji = MOOD_EMOJIS.get(entry.get("mood", "").lower(), "📝")
        date_str = entry["date"][:10]
        tags = ", ".join(entry.get("tags", []))
        header = f"{mood_emoji} {date_str}"
        if entry.get("mood"):
            header += f" | Mood: {entry['mood']}"
        if tags:
            header += f" | Tags: {tags}"

        console.print(Panel(entry["content"], title=header, border_style="blue"))


# ---------------------------------------------------------------------------
# New enhanced functions
# ---------------------------------------------------------------------------


def analyze_themes(entries: list) -> list:
    """Extract top themes from entries using keyword frequency.

    Returns a list of (theme, count) tuples sorted by frequency.
    """
    word_counts: Counter = Counter()

    for entry in entries:
        words = re.findall(r"[a-zA-Z']+", entry.get("content", "").lower())
        meaningful = [w for w in words if w not in STOP_WORDS and len(w) > 2]
        word_counts.update(meaningful)

    # Also count tags
    for entry in entries:
        for tag in entry.get("tags", []):
            word_counts[tag.lower()] += 3  # tags are weighted higher

    themes = word_counts.most_common(20)
    logger.debug("Analyzed themes: top 5 = %s", themes[:5])
    return themes


def generate_word_cloud_data(entries: list) -> dict:
    """Return word frequency dict suitable for word cloud rendering."""
    word_counts: Counter = Counter()

    for entry in entries:
        words = re.findall(r"[a-zA-Z']+", entry.get("content", "").lower())
        meaningful = [w for w in words if w not in STOP_WORDS and len(w) > 2]
        word_counts.update(meaningful)

    return dict(word_counts.most_common(100))


def generate_monthly_reflection(year: int, month: int) -> str:
    """Summarize a month's entries using AI."""
    diary = load_diary()
    month_entries = []
    for entry in diary["entries"]:
        try:
            entry_date = datetime.fromisoformat(entry["date"])
            if entry_date.year == year and entry_date.month == month:
                month_entries.append(entry)
        except (ValueError, KeyError):
            continue

    if not month_entries:
        return f"No entries found for {year}-{month:02d}."

    entries_text = "\n\n".join(
        f"Date: {e['date'][:10]}\nMood: {e.get('mood', 'N/A')}\nEntry: {e['content']}"
        for e in month_entries
    )

    prompt = f"""Create a thoughtful monthly reflection for {year}-{month:02d} based on these diary entries:

{entries_text}

Include:
1. **Month Overview**: What was this month about?
2. **Emotional Journey**: How did feelings evolve through the month?
3. **Highlights**: Best moments and achievements
4. **Challenges**: Difficulties faced and how they were handled
5. **Lessons Learned**: Key takeaways
6. **Intentions for Next Month**: Gentle suggestions for growth

Be warm, supportive, and reflective."""

    llm_config = config.get("llm", {})
    return generate(
        prompt=prompt,
        system_prompt=llm_config.get("system_prompt", "You are a compassionate journal therapist."),
        temperature=llm_config.get("temperature", 0.6),
    )


def get_mood_stats(entries: list) -> dict:
    """Count moods and calculate percentages.

    Returns dict with 'counts', 'percentages', and 'total' keys.
    """
    mood_counts: Counter = Counter()
    for entry in entries:
        mood = entry.get("mood", "").lower().strip()
        if mood:
            mood_counts[mood] += 1

    total = sum(mood_counts.values())
    percentages = {}
    if total > 0:
        percentages = {mood: round((count / total) * 100, 1) for mood, count in mood_counts.items()}

    return {
        "counts": dict(mood_counts),
        "percentages": percentages,
        "total": total,
    }


def get_writing_streak(entries: list = None) -> dict:
    """Calculate consecutive days with entries.

    Returns dict with 'current_streak', 'longest_streak', and 'total_days'.
    """
    if entries is None:
        diary = load_diary()
        entries = diary.get("entries", [])

    if not entries:
        return {"current_streak": 0, "longest_streak": 0, "total_days": 0}

    # Collect unique dates
    dates_set = set()
    for entry in entries:
        try:
            entry_date = datetime.fromisoformat(entry["date"]).date()
            dates_set.add(entry_date)
        except (ValueError, KeyError):
            continue

    if not dates_set:
        return {"current_streak": 0, "longest_streak": 0, "total_days": 0}

    sorted_dates = sorted(dates_set)
    total_days = len(sorted_dates)

    # Calculate longest streak
    longest_streak = 1
    current_run = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            current_run += 1
            longest_streak = max(longest_streak, current_run)
        else:
            current_run = 1

    # Calculate current streak (from today backwards)
    today = datetime.now().date()
    current_streak = 0
    check_date = today
    while check_date in dates_set:
        current_streak += 1
        check_date -= timedelta(days=1)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_days": total_days,
    }
