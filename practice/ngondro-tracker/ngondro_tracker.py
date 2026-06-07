"""
practice/ngondro-tracker/ngondro_tracker.py

Track ngondro accumulations across all four foundations.
Supports multiple traditions with different target counts.
Persists to JSON. No LLM required for core functionality.

Usage:
    python ngondro_tracker.py log prostrations 108
    python ngondro_tracker.py log mantra 1000
    python ngondro_tracker.py log mandala 21
    python ngondro_tracker.py log guruyoga 108
    python ngondro_tracker.py status
    python ngondro_tracker.py history
    python ngondro_tracker.py --tradition karma_kagyu status
"""

import json
import argparse
from datetime import date, datetime
from pathlib import Path

DATA_FILE = Path.home() / ".dharma_tech" / "ngondro.json"

# Target counts by tradition
TRADITIONS = {
    "nyingma_standard": {
        "name": "Nyingma (standard)",
        "prostrations": 111111,
        "mantra": 111111,
        "mandala": 111111,
        "guruyoga": 111111,
    },
    "nyingma_100k": {
        "name": "Nyingma (100,000)",
        "prostrations": 100000,
        "mantra": 100000,
        "mandala": 100000,
        "guruyoga": 100000,
    },
    "karma_kagyu": {
        "name": "Karma Kagyu",
        "prostrations": 100000,
        "mantra": 100000,      # Vajrasattva 100-syllable
        "mandala": 100000,
        "guruyoga": 100000,
    },
    "gelug": {
        "name": "Gelug (Lam Rim Ngondro)",
        "prostrations": 100000,
        "mantra": 100000,
        "mandala": 100000,
        "guruyoga": 100000,
    },
    "custom": {
        "name": "Custom",
        "prostrations": 100000,
        "mantra": 100000,
        "mandala": 100000,
        "guruyoga": 100000,
    }
}

PRACTICE_LABELS = {
    "prostrations": "Prostrations with Refuge",
    "mantra":       "Vajrasattva Mantra",
    "mandala":      "Mandala Offerings",
    "guruyoga":     "Guru Yoga",
}

PRACTICE_ALIASES = {
    "pros": "prostrations", "prostration": "prostrations",
    "bow": "prostrations", "bows": "prostrations",
    "vajrasattva": "mantra", "100syl": "mantra",
    "man": "mandala", "mandalas": "mandala",
    "guru": "guruyoga", "gy": "guruyoga",
    "guru_yoga": "guruyoga",
}


def load_data():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {
        "tradition": "nyingma_standard",
        "started": str(date.today()),
        "totals": {
            "prostrations": 0,
            "mantra": 0,
            "mandala": 0,
            "guruyoga": 0,
        },
        "sessions": []
    }


def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def resolve_practice(name):
    name = name.lower().strip()
    return PRACTICE_ALIASES.get(name, name)


def log_session(practice, count, note="", tradition=None):
    practice = resolve_practice(practice)
    if practice not in PRACTICE_LABELS:
        print(f"Unknown practice: {practice}")
        print(f"Valid: {', '.join(PRACTICE_LABELS.keys())}")
        return

    data = load_data()
    if tradition:
        data["tradition"] = tradition

    data["totals"][practice] = data["totals"].get(practice, 0) + count
    data["sessions"].append({
        "date": str(date.today()),
        "time": datetime.now().strftime("%H:%M"),
        "practice": practice,
        "count": count,
        "note": note,
        "running_total": data["totals"][practice]
    })
    save_data(data)

    targets = TRADITIONS.get(data["tradition"], TRADITIONS["nyingma_standard"])
    target = targets.get(practice, 100000)
    total = data["totals"][practice]
    pct = min(100, total / target * 100)
    remaining = max(0, target - total)

    label = PRACTICE_LABELS[practice]
    print(f"\n  Logged {count:,} {label}")
    print(f"  Total: {total:,} / {target:,} ({pct:.1f}%)")
    if remaining > 0:
        print(f"  Remaining: {remaining:,}")
    else:
        print(f"  COMPLETE")
    print()


def show_status(tradition=None):
    data = load_data()
    if tradition:
        data["tradition"] = tradition

    trad_key = data.get("tradition", "nyingma_standard")
    targets = TRADITIONS.get(trad_key, TRADITIONS["nyingma_standard"])
    trad_name = targets.get("name", trad_key)

    started = data.get("started", "unknown")
    print(f"\n  Ngondro Progress — {trad_name}")
    print(f"  Started: {started}")
    print()
    print(f"  {'Practice':<30} {'Done':>10} {'Target':>10} {'%':>7} {'Remaining':>12}")
    print(f"  {'-'*72}")

    for practice, label in PRACTICE_LABELS.items():
        total  = data["totals"].get(practice, 0)
        target = targets.get(practice, 100000)
        pct    = min(100, total / target * 100)
        remaining = max(0, target - total)
        bar_len = int(pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        done_str = "DONE" if remaining == 0 else f"{remaining:,} left"
        print(f"  {label:<30} {total:>10,} {target:>10,} {pct:>6.1f}% {done_str:>12}")
        print(f"  [{bar}]")
        print()

    # recent sessions
    sessions = data.get("sessions", [])
    if sessions:
        print(f"  Recent sessions:")
        for s in sessions[-5:][::-1]:
            note = f" — {s['note']}" if s.get("note") else ""
            print(f"    {s['date']} {s.get('time','')}  "
                  f"{PRACTICE_LABELS.get(s['practice'], s['practice'])}: "
                  f"{s['count']:,}{note}")
    print()


def show_history(practice=None):
    data = load_data()
    sessions = data.get("sessions", [])

    if practice:
        practice = resolve_practice(practice)
        sessions = [s for s in sessions if s["practice"] == practice]

    if not sessions:
        print("No sessions logged yet.")
        return

    print(f"\n  Session history{f' — {PRACTICE_LABELS[practice]}' if practice else ''}:")
    print()
    for s in sessions:
        label = PRACTICE_LABELS.get(s["practice"], s["practice"])
        note  = f" — {s['note']}" if s.get("note") else ""
        print(f"  {s['date']}  {label:<30} {s['count']:>8,}  "
              f"(total: {s.get('running_total', 0):,}){note}")
    print()


def set_tradition(tradition):
    if tradition not in TRADITIONS:
        print(f"Unknown tradition: {tradition}")
        print(f"Valid: {', '.join(TRADITIONS.keys())}")
        return
    data = load_data()
    data["tradition"] = tradition
    save_data(data)
    print(f"  Tradition set to: {TRADITIONS[tradition]['name']}")


def main():
    parser = argparse.ArgumentParser(
        description="Track ngondro accumulations"
    )
    sub = parser.add_subparsers(dest="command")

    # log
    log_p = sub.add_parser("log", help="Log a session")
    log_p.add_argument("practice",
        help="prostrations/mantra/mandala/guruyoga (aliases work too)")
    log_p.add_argument("count", type=int)
    log_p.add_argument("--note", default="", help="Optional note")

    # status
    sub.add_parser("status", help="Show current progress")

    # history
    hist_p = sub.add_parser("history", help="Show session history")
    hist_p.add_argument("practice", nargs="?",
                         help="Filter by practice")

    # tradition
    trad_p = sub.add_parser("tradition", help="Set tradition")
    trad_p.add_argument("name", choices=list(TRADITIONS.keys()))

    parser.add_argument("--tradition",
                        choices=list(TRADITIONS.keys()),
                        help="Specify tradition")

    args = parser.parse_args()

    if args.command == "log":
        log_session(args.practice, args.count, args.note,
                    getattr(args, "tradition", None))
    elif args.command == "status":
        show_status(getattr(args, "tradition", None))
    elif args.command == "history":
        show_history(getattr(args, "practice", None))
    elif args.command == "tradition":
        set_tradition(args.name)
    else:
        show_status()


if __name__ == "__main__":
    main()
