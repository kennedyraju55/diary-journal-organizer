"""Tests for Diary Journal Organizer core functions."""

import sys
import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from diary_organizer.core import (
    load_diary,
    save_diary,
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
    DIARY_FILE,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_diary_file(tmp_path, monkeypatch):
    """Use a temporary diary file for tests."""
    diary_path = str(tmp_path / "diary.json")
    monkeypatch.setattr('diary_organizer.core.DIARY_FILE', diary_path)
    return diary_path


def _make_entry(content, mood="happy", tags=None, days_ago=0):
    """Helper to create an entry dict with a specific date."""
    date = (datetime.now() - timedelta(days=days_ago)).isoformat()
    return {
        "id": 1,
        "date": date,
        "content": content,
        "mood": mood,
        "tags": tags or [],
    }


# ---------------------------------------------------------------------------
# Original function tests
# ---------------------------------------------------------------------------


class TestLoadSaveDiary:
    def test_load_empty(self):
        diary = load_diary()
        assert diary == {"entries": []}

    def test_save_and_load(self, mock_diary_file):
        diary = {"entries": [{"id": 1, "date": "2024-01-01", "content": "test", "mood": "happy", "tags": []}]}
        save_diary(diary)
        loaded = load_diary()
        assert loaded == diary

    def test_load_corrupt_file(self, mock_diary_file):
        with open(mock_diary_file, 'w') as f:
            f.write("not valid json{{{")
        diary = load_diary()
        assert diary == {"entries": []}


class TestWriteEntry:
    def test_write_basic_entry(self):
        entry = write_entry("Had a great day", "happy", ["outdoors"])
        assert entry["content"] == "Had a great day"
        assert entry["mood"] == "happy"
        assert "outdoors" in entry["tags"]
        assert entry["id"] == 1

    def test_write_multiple_entries(self):
        write_entry("Morning jog", "energetic")
        write_entry("Work was stressful", "anxious")
        entry3 = write_entry("Nice dinner", "happy")
        assert entry3["id"] == 3
        diary = load_diary()
        assert len(diary["entries"]) == 3

    def test_write_entry_default_tags(self):
        entry = write_entry("Simple entry")
        assert entry["tags"] == []
        assert entry["mood"] == ""


class TestGetEntriesForPeriod:
    def test_week(self):
        write_entry("Recent", "happy")
        entries = get_entries_for_period("week")
        assert len(entries) == 1

    def test_month(self):
        write_entry("Recent", "happy")
        entries = get_entries_for_period("month")
        assert len(entries) == 1

    def test_year(self):
        write_entry("Recent", "happy")
        entries = get_entries_for_period("year")
        assert len(entries) == 1

    def test_default_period(self):
        write_entry("Recent", "happy")
        entries = get_entries_for_period("unknown")
        assert len(entries) == 1

    def test_no_entries(self):
        entries = get_entries_for_period("week")
        assert entries == []


class TestDisplayEntries:
    def test_display(self, capsys):
        entries = [_make_entry("Test content", "happy", ["work"])]
        display_entries(entries)
        # display_entries prints via rich; no assertion needed beyond no-crash


# ---------------------------------------------------------------------------
# AI function tests (LLM mocked)
# ---------------------------------------------------------------------------


class TestAnalyzeMood:
    @patch('diary_organizer.core.generate')
    def test_analyze_mood(self, mock_generate):
        entries = [
            {"date": "2024-03-25T10:00:00", "mood": "happy", "content": "Great day!"},
            {"date": "2024-03-26T10:00:00", "mood": "sad", "content": "Feeling down."},
        ]
        mock_generate.return_value = "## Mood Trend\n- Fluctuating between happy and sad"
        result = analyze_mood(entries)
        assert "Fluctuating" in result
        mock_generate.assert_called_once()


class TestFindThemes:
    @patch('diary_organizer.core.generate')
    def test_find_themes(self, mock_generate):
        entries = [
            {"date": "2024-03-25T10:00:00", "content": "Work was busy today"},
        ]
        mock_generate.return_value = "## Major Themes\n- Work"
        result = find_themes(entries)
        assert "Work" in result
        mock_generate.assert_called_once()


class TestGenerateInsights:
    @patch('diary_organizer.core.generate')
    def test_generate_insights(self, mock_generate):
        entries = [
            {"date": "2024-03-25T10:00:00", "mood": "happy", "content": "Productive day", "tags": ["work"]},
        ]
        mock_generate.return_value = "## Summary\nA productive week with positive mood."
        result = generate_insights(entries)
        assert "Summary" in result
        mock_generate.assert_called_once()


# ---------------------------------------------------------------------------
# New enhanced function tests
# ---------------------------------------------------------------------------


class TestAnalyzeThemes:
    def test_basic_themes(self):
        entries = [
            _make_entry("I love working on my garden and planting flowers in the garden"),
            _make_entry("The garden is growing well with beautiful flowers"),
        ]
        themes = analyze_themes(entries)
        assert len(themes) > 0
        theme_words = [t[0] for t in themes]
        assert "garden" in theme_words

    def test_tags_weighted(self):
        entries = [
            _make_entry("Something random", tags=["programming"]),
            _make_entry("Another random entry", tags=["programming"]),
        ]
        themes = analyze_themes(entries)
        theme_dict = dict(themes)
        assert "programming" in theme_dict
        assert theme_dict["programming"] >= 6  # 2 entries * 3 weight

    def test_empty_entries(self):
        themes = analyze_themes([])
        assert themes == []


class TestGenerateWordCloudData:
    def test_word_cloud_data(self):
        entries = [
            _make_entry("The quick brown fox jumps over the lazy dog fox fox"),
        ]
        data = generate_word_cloud_data(entries)
        assert isinstance(data, dict)
        assert "fox" in data
        assert data["fox"] == 3

    def test_stop_words_excluded(self):
        entries = [_make_entry("the and but or is are was")]
        data = generate_word_cloud_data(entries)
        assert "the" not in data
        assert "and" not in data

    def test_empty(self):
        data = generate_word_cloud_data([])
        assert data == {}


class TestGetMoodStats:
    def test_basic_stats(self):
        entries = [
            _make_entry("Good day", "happy"),
            _make_entry("Great day", "happy"),
            _make_entry("Sad day", "sad"),
        ]
        stats = get_mood_stats(entries)
        assert stats["counts"]["happy"] == 2
        assert stats["counts"]["sad"] == 1
        assert stats["total"] == 3
        assert abs(stats["percentages"]["happy"] - 66.7) < 0.1
        assert abs(stats["percentages"]["sad"] - 33.3) < 0.1

    def test_no_moods(self):
        entries = [_make_entry("No mood entry", "")]
        stats = get_mood_stats(entries)
        assert stats["total"] == 0
        assert stats["counts"] == {}

    def test_empty_entries(self):
        stats = get_mood_stats([])
        assert stats["total"] == 0


class TestGetWritingStreak:
    def test_consecutive_days(self):
        entries = [
            _make_entry("Day 1", days_ago=0),
            _make_entry("Day 2", days_ago=1),
            _make_entry("Day 3", days_ago=2),
        ]
        streak = get_writing_streak(entries)
        assert streak["current_streak"] == 3
        assert streak["longest_streak"] == 3
        assert streak["total_days"] == 3

    def test_broken_streak(self):
        entries = [
            _make_entry("Today", days_ago=0),
            _make_entry("3 days ago", days_ago=3),
            _make_entry("4 days ago", days_ago=4),
        ]
        streak = get_writing_streak(entries)
        assert streak["current_streak"] == 1
        assert streak["longest_streak"] == 2
        assert streak["total_days"] == 3

    def test_no_entries(self):
        streak = get_writing_streak([])
        assert streak["current_streak"] == 0
        assert streak["longest_streak"] == 0
        assert streak["total_days"] == 0

    def test_no_current_streak(self):
        entries = [
            _make_entry("Old entry", days_ago=5),
            _make_entry("Older entry", days_ago=6),
        ]
        streak = get_writing_streak(entries)
        assert streak["current_streak"] == 0
        assert streak["longest_streak"] == 2


class TestGenerateMonthlyReflection:
    @patch('diary_organizer.core.generate')
    def test_monthly_reflection(self, mock_generate):
        now = datetime.now()
        write_entry("Great month", "happy")

        mock_generate.return_value = "## Month Overview\nA wonderful month."
        result = generate_monthly_reflection(now.year, now.month)
        assert "Overview" in result
        mock_generate.assert_called_once()

    @patch('diary_organizer.core.generate')
    def test_monthly_reflection_no_entries(self, mock_generate):
        result = generate_monthly_reflection(2020, 1)
        assert "No entries" in result
        mock_generate.assert_not_called()


class TestMoodEmojis:
    def test_all_moods_have_emojis(self):
        expected_moods = [
            "happy", "sad", "anxious", "calm", "excited", "angry", "grateful", "tired",
            "nostalgic", "inspired", "peaceful", "loved", "proud", "confused", "hopeful", "creative",
        ]
        for mood in expected_moods:
            assert mood in MOOD_EMOJIS, f"Missing emoji for mood: {mood}"

    def test_emoji_values(self):
        assert MOOD_EMOJIS["happy"] == "😊"
        assert MOOD_EMOJIS["nostalgic"] == "🥹"
        assert MOOD_EMOJIS["creative"] == "🎨"
