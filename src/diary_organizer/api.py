from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from .core import (
    write_entry,
    get_entries_for_period,
    analyze_mood,
    find_themes,
    generate_insights,
    analyze_themes,
    generate_word_cloud_data,
    generate_monthly_reflection,
    get_mood_stats,
    get_writing_streak,
)

app = FastAPI(title="Diary / Journal Organizer", version="1.0.0")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class WriteEntryRequest(BaseModel):
    content: str
    mood: str = ""
    tags: Optional[List[str]] = None


class PeriodRequest(BaseModel):
    period: str = Field(..., description="Period such as 'week', 'month', or 'year'")


class MonthlyReflectionRequest(BaseModel):
    year: int
    month: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/entries")
def api_write_entry(req: WriteEntryRequest):
    try:
        entry = write_entry(content=req.content, mood=req.mood, tags=req.tags)
        return entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entries/{period}")
def api_get_entries(period: str):
    try:
        entries = get_entries_for_period(period)
        return {"entries": entries}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entries/analyze-mood")
def api_analyze_mood(req: PeriodRequest):
    try:
        entries = get_entries_for_period(req.period)
        result = analyze_mood(entries)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entries/find-themes")
def api_find_themes(req: PeriodRequest):
    try:
        entries = get_entries_for_period(req.period)
        result = find_themes(entries)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entries/insights")
def api_generate_insights(req: PeriodRequest):
    try:
        entries = get_entries_for_period(req.period)
        result = generate_insights(entries)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entries/analyze-themes")
def api_analyze_themes(req: PeriodRequest):
    try:
        entries = get_entries_for_period(req.period)
        themes = analyze_themes(entries)
        return {"themes": themes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entries/word-cloud")
def api_word_cloud(req: PeriodRequest):
    try:
        entries = get_entries_for_period(req.period)
        data = generate_word_cloud_data(entries)
        return {"word_cloud": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entries/monthly-reflection")
def api_monthly_reflection(req: MonthlyReflectionRequest):
    try:
        result = generate_monthly_reflection(req.year, req.month)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entries/mood-stats")
def api_mood_stats(req: PeriodRequest):
    try:
        entries = get_entries_for_period(req.period)
        stats = get_mood_stats(entries)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entries/writing-streak")
def api_writing_streak():
    try:
        streak = get_writing_streak()
        return {"streak": streak}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
