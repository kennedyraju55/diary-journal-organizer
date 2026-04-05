# Examples for Diary Journal Organizer

This directory contains example scripts demonstrating how to use this project.

## Quick Demo

```bash
python examples/demo.py
```

## What the Demo Shows

- **`load_config()`** — Load configuration from config.yaml.
- **`load_diary()`** — Load diary entries from JSON file.
- **`save_diary()`** — Save diary entries to JSON file.
- **`write_entry()`** — Write a new diary entry.
- **`get_entries_for_period()`** — Get entries for a specific time period.

## Prerequisites

- Python 3.10+
- Ollama running with Gemma 4 model
- Project dependencies installed (`pip install -e .`)

## Running

From the project root directory:

```bash
# Install the project in development mode
pip install -e .

# Run the demo
python examples/demo.py
```
