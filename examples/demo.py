"""
Demo script for Diary Journal Organizer
Shows how to use the core module programmatically.

Usage:
    python examples/demo.py
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.diary_organizer.core import load_config, load_diary, save_diary, write_entry, get_entries_for_period, analyze_mood, find_themes, generate_insights, display_entries, analyze_themes


def main():
    """Run a quick demo of Diary Journal Organizer."""
    print("=" * 60)
    print("🚀 Diary Journal Organizer - Demo")
    print("=" * 60)
    print()
    # Load configuration from config.yaml.
    print("📝 Example: load_config()")
    result = load_config()
    print(f"   Result: {result}")
    print()
    # Load diary entries from JSON file.
    print("📝 Example: load_diary()")
    result = load_diary()
    print(f"   Result: {result}")
    print()
    # Save diary entries to JSON file.
    print("📝 Example: save_diary()")
    result = save_diary(
        diary={}
    )
    print(f"   Result: {result}")
    print()
    # Write a new diary entry.
    print("📝 Example: write_entry()")
    result = write_entry(
        content="The quick brown fox jumps over the lazy dog. This is sample content for demonstration."
    )
    print(f"   Result: {result}")
    print()
    print("✅ Demo complete! See README.md for more examples.")


if __name__ == "__main__":
    main()
