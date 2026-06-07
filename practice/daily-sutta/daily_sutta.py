"""
practice/daily-sutta/daily_sutta.py

Sends or prints a daily sutta passage with context and reflection.
Picks from the passage corpus, rotates through texts.
Optionally emails via SMTP or prints to terminal.

Usage:
    python daily_sutta.py                    # print today's sutta
    python daily_sutta.py --tradition theravada
    python daily_sutta.py --concept sunyata
    python daily_sutta.py --schedule         # run daily at 7am
    python daily_sutta.py --email you@email.com

Setup for email:
    export SMTP_HOST=smtp.gmail.com
    export SMTP_PORT=587
    export SMTP_USER=you@gmail.com
    export SMTP_PASS=your_app_password
"""

import sys
import os
import json
import random
import hashlib
import argparse
import smtplib
from datetime import date
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.llm import DharmaLLM
from core.rag import GraphRAG

TRADITION_CONCEPTS = {
    "theravada":  ["anatta", "pratityasamutpada", "five_aggregates", "twelve_nidanas"],
    "madhyamaka": ["sunyata", "svabhava", "prasanga", "two_truths"],
    "mahayana":   ["sunyata", "bodhichitta", "nonduality", "skillful_means"],
    "yogacara":   ["alayavijnana", "three_natures", "cittamatra"],
    "general":    ["sunyata", "anatta", "pratityasamutpada", "nonduality",
                   "bodhichitta", "two_truths"],
}

REFLECT_PROMPT = """Given this Buddhist passage, write a brief daily reflection.
Keep it to 3 sentences. Make it practical — how might a practitioner relate
this to ordinary experience today. Do not be preachy. End with one open question.

Passage ({text_id}):
{passage}

Write a reflection and one question:"""


def pick_passage(tradition="general", concept=None, seed=None):
    """Pick a passage deterministically by date, or randomly."""
    rag = GraphRAG()

    if concept:
        passages = rag.retrieve_constrained(concept, hops=1, top_n=20)
    elif tradition in TRADITION_CONCEPTS:
        concept = random.choice(TRADITION_CONCEPTS[tradition])
        passages = rag.retrieve(concept, top_n=20)
    else:
        passages = rag.passages

    if not passages:
        return None

    # deterministic by date so same passage appears all day
    day_seed = seed or int(hashlib.md5(str(date.today()).encode()).hexdigest(), 16)
    return passages[day_seed % len(passages)]


def generate_reflection(passage, model="qwen2.5:7b"):
    try:
        import ollama
        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": REFLECT_PROMPT.format(
                    text_id=passage["text_id"],
                    passage=passage["text"][:600]
                )
            }],
            options={"temperature": 0.5}
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"(Reflection unavailable: {e})"


def format_output(passage, reflection):
    text_id = passage.get("text_id", "unknown")
    today = date.today().strftime("%A, %B %-d, %Y")

    lines = [
        f"Daily Sutta — {today}",
        f"Source: {text_id.replace('_', ' ').title()}",
        "",
        "─" * 50,
        "",
        passage["text"],
        "",
        "─" * 50,
        "",
        "Reflection:",
        reflection,
        "",
    ]
    return "\n".join(lines)


def send_email(content, recipient, subject=None):
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", 587))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASS", "")

    if not user or not password:
        print("Set SMTP_USER and SMTP_PASS environment variables to send email")
        return False

    subject = subject or f"Daily Sutta — {date.today().strftime('%B %-d')}"
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, recipient, msg.as_string())
        print(f"Sent to {recipient}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def run_daily(tradition="general", concept=None, email=None,
              model="qwen2.5:7b"):
    passage = pick_passage(tradition=tradition, concept=concept)
    if not passage:
        print("No passages found. Check that data/passages.jsonl exists.")
        return

    reflection = generate_reflection(passage, model)
    output = format_output(passage, reflection)

    print(output)

    if email:
        send_email(output, email)


def schedule_daily(tradition="general", model="qwen2.5:7b",
                   email=None, hour=7):
    try:
        import schedule
        import time
    except ImportError:
        print("Install schedule: pip install schedule")
        return

    print(f"Scheduling daily sutta at {hour:02d}:00")

    def job():
        run_daily(tradition=tradition, model=model, email=email)

    schedule.every().day.at(f"{hour:02d}:00").do(job)
    job()  # run immediately

    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    parser = argparse.ArgumentParser(
        description="Daily Buddhist sutta with reflection"
    )
    parser.add_argument("--tradition",
                        choices=["theravada", "madhyamaka", "mahayana",
                                 "yogacara", "general"],
                        default="general")
    parser.add_argument("--concept",
                        help="Specific concept to draw passages from")
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--email",
                        help="Email address to send to")
    parser.add_argument("--schedule", action="store_true",
                        help="Run on a daily schedule at 7am")
    parser.add_argument("--hour", type=int, default=7,
                        help="Hour for scheduled delivery (24h)")
    args = parser.parse_args()

    if args.schedule:
        schedule_daily(tradition=args.tradition, model=args.model,
                       email=args.email, hour=args.hour)
    else:
        run_daily(tradition=args.tradition, concept=args.concept,
                  model=args.model, email=args.email)


if __name__ == "__main__":
    main()
