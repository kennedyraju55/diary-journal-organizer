#!/usr/bin/env python3
"""Diary Journal Organizer - Streamlit Web Interface."""

import sys
import os
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import streamlit as st
import pandas as pd

from diary_organizer.core import (
    write_entry,
    load_diary,
    get_entries_for_period,
    analyze_mood,
    find_themes,
    generate_insights,
    analyze_themes,
    generate_word_cloud_data,
    generate_monthly_reflection,
    get_mood_stats,
    get_writing_streak,
    MOOD_EMOJIS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Diary Journal Organizer", page_icon="📔", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

st.sidebar.title("📔 Diary Journal")
page = st.sidebar.radio(
    "Navigate",
    ["Write Entry", "Calendar View", "Mood Chart", "Insights Dashboard"],
)

# ---------------------------------------------------------------------------
# Write Entry page
# ---------------------------------------------------------------------------

if page == "Write Entry":
    st.header("✍️ Write a New Entry")

    content = st.text_area("What's on your mind today?", height=200, placeholder="Write your thoughts here...")

    col1, col2 = st.columns(2)
    with col1:
        mood_options = [f"{emoji} {name}" for name, emoji in MOOD_EMOJIS.items()]
        selected_mood = st.selectbox("How are you feeling?", [""] + mood_options)
    with col2:
        tags_input = st.text_input("Tags (comma-separated)", placeholder="work, family, health")

    if st.button("💾 Save Entry", type="primary"):
        if not content.strip():
            st.warning("Please write something before saving.")
        else:
            mood = selected_mood.split(" ", 1)[-1] if selected_mood else ""
            tag_list = [t.strip() for t in tags_input.split(",") if t.strip()]
            entry = write_entry(content, mood, tag_list)
            st.success(f"✅ Entry #{entry['id']} saved for {entry['date'][:10]}")
            st.balloons()

# ---------------------------------------------------------------------------
# Calendar View page
# ---------------------------------------------------------------------------

elif page == "Calendar View":
    st.header("📅 Calendar View")

    period = st.selectbox("Time period", ["week", "month", "year"])
    entries = get_entries_for_period(period)

    if not entries:
        st.info(f"No entries found for the past {period}.")
    else:
        st.write(f"Found **{len(entries)}** entries for the past {period}.")

        # Group entries by date
        entries_by_date: dict = {}
        for entry in entries:
            date_key = entry["date"][:10]
            entries_by_date.setdefault(date_key, []).append(entry)

        for date_key in sorted(entries_by_date.keys(), reverse=True):
            day_entries = entries_by_date[date_key]
            with st.expander(f"📅 {date_key} ({len(day_entries)} entries)", expanded=False):
                for entry in day_entries:
                    mood = entry.get("mood", "")
                    emoji = MOOD_EMOJIS.get(mood.lower(), "📝")
                    tags = ", ".join(entry.get("tags", []))
                    st.markdown(f"**{emoji} {mood.capitalize() if mood else 'No mood'}** {f'| Tags: {tags}' if tags else ''}")
                    st.write(entry["content"])
                    st.divider()

# ---------------------------------------------------------------------------
# Mood Chart page
# ---------------------------------------------------------------------------

elif page == "Mood Chart":
    st.header("🎭 Mood Chart")

    period = st.selectbox("Time period", ["week", "month", "year"], index=1)
    entries = get_entries_for_period(period)

    if not entries:
        st.info(f"No entries found for the past {period}.")
    else:
        stats = get_mood_stats(entries)

        # Metrics row
        col1, col2, col3 = st.columns(3)
        streak_info = get_writing_streak(entries)
        with col1:
            st.metric("Total Entries", stats["total"])
        with col2:
            st.metric("🔥 Current Streak", f"{streak_info['current_streak']} days")
        with col3:
            st.metric("🏆 Longest Streak", f"{streak_info['longest_streak']} days")

        if stats["counts"]:
            # Bar chart
            st.subheader("Mood Distribution")
            mood_df = pd.DataFrame([
                {"Mood": f"{MOOD_EMOJIS.get(m, '📝')} {m.capitalize()}", "Count": c}
                for m, c in stats["counts"].items()
            ])
            mood_df = mood_df.set_index("Mood")
            st.bar_chart(mood_df)

            # Percentage table
            st.subheader("Mood Breakdown")
            for mood, pct in sorted(stats["percentages"].items(), key=lambda x: x[1], reverse=True):
                emoji = MOOD_EMOJIS.get(mood, "📝")
                st.write(f"{emoji} **{mood.capitalize()}**: {pct}% ({stats['counts'][mood]} entries)")
        else:
            st.info("No mood data available. Add moods to your entries!")

# ---------------------------------------------------------------------------
# Insights Dashboard page
# ---------------------------------------------------------------------------

elif page == "Insights Dashboard":
    st.header("✨ Insights Dashboard")

    period = st.selectbox("Time period", ["week", "month", "year"], index=1)
    entries = get_entries_for_period(period)

    if not entries:
        st.info(f"No entries found for the past {period}.")
    else:
        # Metrics
        streak_info = get_writing_streak(entries)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Entries", len(entries))
        with col2:
            st.metric("🔥 Current Streak", f"{streak_info['current_streak']} days")
        with col3:
            st.metric("🏆 Longest Streak", f"{streak_info['longest_streak']} days")
        with col4:
            st.metric("📅 Days Written", streak_info["total_days"])

        # Themes
        st.subheader("🏷️ Top Themes")
        themes = analyze_themes(entries)
        if themes:
            theme_df = pd.DataFrame(themes[:15], columns=["Theme", "Count"])
            theme_df = theme_df.set_index("Theme")
            st.bar_chart(theme_df)

        # Word cloud data
        st.subheader("☁️ Word Cloud Data")
        word_data = generate_word_cloud_data(entries)
        if word_data:
            top_words = sorted(word_data.items(), key=lambda x: x[1], reverse=True)[:20]
            word_df = pd.DataFrame(top_words, columns=["Word", "Frequency"])
            word_df = word_df.set_index("Word")
            st.bar_chart(word_df)

        # Monthly reflection
        st.subheader("📅 Monthly Reflection")
        now = datetime.now()
        col_y, col_m = st.columns(2)
        with col_y:
            year = st.number_input("Year", min_value=2020, max_value=2030, value=now.year)
        with col_m:
            month = st.number_input("Month", min_value=1, max_value=12, value=now.month)

        if st.button("🔮 Generate Reflection"):
            with st.spinner("Generating monthly reflection..."):
                reflection = generate_monthly_reflection(int(year), int(month))
            st.markdown(reflection)
