"""
practice/session-logger/session_logger.py

Log meditation sessions and analyze patterns over time.
Tracks: duration, technique, hindrances, quality, notes.
Uses LLM for pattern analysis — but core logging works without it.

Usage:
    python session_logger.py log 45 --technique vipassana --note "restless first 20min"
    python session_logger.py log 30 --hindrances restlessness,doubt
    python session_logger.py status
    python session_logger.py patterns          # LLM pattern analysis
    python session_logger.py export            # CSV export
"""

import json
import csv
import argparse
from datetime import date, datetime, timedelta
from pathlib import Path
from collections import Counter

DATA_FILE = Path.home() / ".dharma_tech" / "sessions.json"

TECHNIQUES = [
    "vipassana", "samatha", "metta", "anapanasati",
    "dzogchen", "mahamudra", "tonglen", "shamatha",
    "shikantaza", "zazen", "nembutsu", "mantra",
    "body_scan", "noting", "open_awareness", "other"
]

HINDRANCES = [
    "sensual_desire", "ill_will", "sloth_torpor",
    "restlessness", "doubt", "none"
]

HINDRANCE_ALIASES = {
    "desire": "sensual_desire", "lust": "sensual_desire",
    "anger": "ill_will", "aversion": "ill_will",
    "sloth": "sloth_torpor", "torpor": "sloth_torpor", "sleepy": "sloth_torpor",
    "rest": "restlessness", "worry": "restlessness", "agitation": "restlessness",
    "skeptical": "doubt", "skepticism": "doubt",
}

QUALITY_MAP = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
               "poor": 1, "fair": 2, "ok": 3, "good": 4, "excellent": 5}

PATTERN_PROMPT = """You are a meditation teacher reviewing a practitioner's session log.
Identify genuine patterns — not superficial ones. Look for:
- Hindrance patterns (time of day, duration, technique)
- Quality trends over time
- Technique correlations with quality
- Duration sweet spots
- Concerning patterns (avoidance, stagnation)

Be specific and grounded in the actual data. Do not be vague or generic.
Do not be preachy. One concrete suggestion is worth more than five general ones.

Session data (last 30 sessions):
{sessions}

Summary statistics:
{stats}

Write a brief pattern analysis (5-8 sentences) and one concrete suggestion:"""


def load_data():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"sessions": []}


def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def parse_hindrances(h_str):
    if not h_str:
        return []
    parts = [p.strip().lower() for p in h_str.split(",")]
    resolved = []
    for p in parts:
        resolved.append(HINDRANCE_ALIASES.get(p, p))
    return [h for h in resolved if h in HINDRANCES or h == "none"]


def log_session(duration, technique=None, hindrances=None,
                quality=None, note=""):
    data = load_data()
    now = datetime.now()

    h_list = parse_hindrances(hindrances) if hindrances else []
    q = QUALITY_MAP.get(str(quality).lower(), quality) if quality else None

    session = {
        "id":         len(data["sessions"]) + 1,
        "date":       str(date.today()),
        "time":       now.strftime("%H:%M"),
        "weekday":    now.strftime("%A"),
        "hour":       now.hour,
        "duration":   duration,
        "technique":  technique or "unspecified",
        "hindrances": h_list,
        "quality":    q,
        "note":       note,
    }
    data["sessions"].append(session)
    save_data(data)

    h_str = ", ".join(h_list) if h_list else "none noted"
    q_str = f", quality {q}/5" if q else ""
    print(f"\n  Logged: {duration}min {technique or ''}{q_str}")
    print(f"  Hindrances: {h_str}")
    if note:
        print(f"  Note: {note}")

    # streak
    sessions = data["sessions"]
    dates = sorted(set(s["date"] for s in sessions), reverse=True)
    streak = 1
    for i in range(1, len(dates)):
        expected = str(
            date.fromisoformat(dates[i-1]) - timedelta(days=1)
        )
        if dates[i] == expected:
            streak += 1
        else:
            break
    print(f"  Streak: {streak} day{'s' if streak != 1 else ''}")
    print()


def show_status():
    data = load_data()
    sessions = data["sessions"]
    if not sessions:
        print("No sessions logged yet.")
        return

    total    = len(sessions)
    total_min = sum(s["duration"] for s in sessions)
    avg_dur  = total_min / total

    # last 7 days
    week_ago = str(date.today() - timedelta(days=7))
    recent   = [s for s in sessions if s["date"] >= week_ago]

    # hindrance frequency
    all_hindrances = []
    for s in sessions:
        all_hindrances.extend(s.get("hindrances", []))
    h_counts = Counter(h for h in all_hindrances if h != "none")

    # quality average
    qualities = [s["quality"] for s in sessions if s.get("quality")]
    avg_q = sum(qualities) / len(qualities) if qualities else None

    print(f"\n  Meditation Log — {total} sessions")
    print(f"  Total time: {total_min:,} minutes ({total_min//60}h {total_min%60}m)")
    print(f"  Average duration: {avg_dur:.0f} minutes")
    if avg_q:
        print(f"  Average quality: {avg_q:.1f}/5")
    print(f"  Sessions last 7 days: {len(recent)}")
    print()

    # technique breakdown
    techniques = Counter(s["technique"] for s in sessions)
    print(f"  Techniques:")
    for tech, count in techniques.most_common(5):
        pct = count / total * 100
        print(f"    {tech:<20} {count:>4} sessions ({pct:.0f}%)")
    print()

    if h_counts:
        print(f"  Most frequent hindrances:")
        for h, count in h_counts.most_common(3):
            print(f"    {h.replace('_',' '):<25} {count} times")
    print()

    # recent sessions
    print(f"  Last 5 sessions:")
    for s in sessions[-5:][::-1]:
        h = ", ".join(s.get("hindrances", [])) or "none"
        q = f" [{s['quality']}/5]" if s.get("quality") else ""
        print(f"    {s['date']} {s.get('time','')}  "
              f"{s['duration']}min {s['technique']}{q}  [{h}]")
    print()


def analyze_patterns(model="qwen2.5:7b"):
    try:
        import ollama
    except ImportError:
        print("Ollama not installed. Pattern analysis requires: pip install ollama")
        return

    data = load_data()
    sessions = data["sessions"]
    if len(sessions) < 5:
        print("Log at least 5 sessions before requesting pattern analysis.")
        return

    recent = sessions[-30:]

    all_hindrances = []
    for s in recent:
        all_hindrances.extend(s.get("hindrances", []))
    h_counts = Counter(h for h in all_hindrances if h != "none")
    qualities = [s["quality"] for s in recent if s.get("quality")]

    stats = {
        "total_sessions": len(sessions),
        "sessions_analyzed": len(recent),
        "avg_duration": round(sum(s["duration"] for s in recent) / len(recent), 1),
        "avg_quality": round(sum(qualities) / len(qualities), 1) if qualities else None,
        "most_common_hindrance": h_counts.most_common(1)[0] if h_counts else None,
        "techniques_used": dict(Counter(s["technique"] for s in recent).most_common(5)),
        "by_weekday": dict(Counter(s["weekday"] for s in recent)),
        "by_hour": dict(Counter(s["hour"] for s in recent)),
    }

    session_summary = [
        {k: v for k, v in s.items() if k != "id"}
        for s in recent
    ]

    try:
        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": PATTERN_PROMPT.format(
                    sessions=json.dumps(session_summary, indent=2),
                    stats=json.dumps(stats, indent=2)
                )
            }],
            options={"temperature": 0.3}
        )
        print(f"\n  Pattern Analysis:\n")
        print(f"  {response['message']['content'].strip()}")
        print()
    except Exception as e:
        print(f"  Error: {e}")


def export_csv(output="sessions.csv"):
    data = load_data()
    sessions = data["sessions"]
    if not sessions:
        print("No sessions to export.")
        return

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "date", "time", "weekday", "hour",
            "duration", "technique", "hindrances", "quality", "note"
        ])
        writer.writeheader()
        for s in sessions:
            row = dict(s)
            row["hindrances"] = ",".join(s.get("hindrances", []))
            writer.writerow(row)

    print(f"Exported {len(sessions)} sessions to {output}")


def main():
    parser = argparse.ArgumentParser(
        description="Log and analyze meditation sessions"
    )
    sub = parser.add_subparsers(dest="command")

    log_p = sub.add_parser("log", help="Log a session")
    log_p.add_argument("duration", type=int, help="Duration in minutes")
    log_p.add_argument("--technique", choices=TECHNIQUES)
    log_p.add_argument("--hindrances",
                       help="Comma-separated: sensual_desire,ill_will,etc.")
    log_p.add_argument("--quality", help="1-5 or poor/fair/ok/good/excellent")
    log_p.add_argument("--note", default="")

    sub.add_parser("status", help="Show summary")

    pat_p = sub.add_parser("patterns", help="LLM pattern analysis")
    pat_p.add_argument("--model", default="qwen2.5:7b")

    exp_p = sub.add_parser("export", help="Export to CSV")
    exp_p.add_argument("--output", default="sessions.csv")

    args = parser.parse_args()

    if args.command == "log":
        log_session(args.duration, args.technique, args.hindrances,
                    args.quality, args.note)
    elif args.command == "status":
        show_status()
    elif args.command == "patterns":
        analyze_patterns(args.model)
    elif args.command == "export":
        export_csv(args.output)
    else:
        show_status()


if __name__ == "__main__":
    main()
