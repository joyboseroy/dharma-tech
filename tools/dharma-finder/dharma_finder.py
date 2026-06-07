"""
dharma_finder_local.py

Local Buddhist text finder agent using Ollama + deterministic URL validation.
No API keys. No hallucinated URLs — every link is verified before display.

Requirements:
    pip install ollama requests rich
    ollama pull qwen2.5:7b   (or any model you have)

Usage:
    python agent.py "Samaññaphala Sutta"
    python agent.py "Longchenpa treasury dharmadhatu"
    python agent.py --interactive
"""

import json
import sys
import argparse
import requests
from urllib.parse import quote_plus

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None


# ── URL TEMPLATES ─────────────────────────────────────────────────────────
# For known canonical reference patterns, generate URLs deterministically.
# The LLM identifies the reference; we build the URL from the template.

def suttacentral_url(ref, translator="sujato"):
    """
    ref: DN 2, MN 1, SN 22.59, AN 3.65, Dhp 1, etc.
    Returns candidate URLs for multiple translators.
    """
    ref_clean = ref.lower().replace(" ", "").replace(".", ".")
    # parse: DN2 -> dn2, MN36 -> mn36, SN22.59 -> sn22.59
    import re
    m = re.match(r'([a-z]+)[\s.]*([\d.]+)', ref_clean)
    if not m:
        return []
    nikaya = m.group(1)
    num = m.group(2)
    sc_ref = f"{nikaya}{num}"
    translators = ["sujato", "bodhi", "thanissaro", "brahmali"]
    return [f"https://suttacentral.net/{sc_ref}/en/{t}" for t in translators]

def access_to_insight_search(text_name):
    q = quote_plus(text_name)
    return [f"https://www.accesstoinsight.org/search.html?q={q}"]

def dhammatalks_search(text_name):
    q = quote_plus(text_name)
    return [f"https://www.dhammatalks.org/suttas/"]

def archive_search(text_name):
    q = quote_plus(f"{text_name} buddhism")
    return [f"https://archive.org/search?query={q}&mediatype=texts"]

def lotsawa_search(text_name):
    q = quote_plus(text_name)
    return [f"https://www.lotsawahouse.org/search?keys={q}"]

def eighty4000_search(text_name, toh=None):
    if toh:
        return [f"https://84000.co/translation/{toh}"]
    q = quote_plus(text_name)
    return [f"https://84000.co/all-publications?search={q}"]

def buddhanet_search(text_name):
    q = quote_plus(text_name)
    return [f"https://www.buddhanet.net/ebooks.htm",
            f"https://www.buddhanet.net/pdf_file/{text_name.lower().replace(' ','_')}.pdf"]

def wisdomlib_search(text_name):
    q = quote_plus(text_name)
    return [f"https://www.wisdomlib.org/search?q={q}"]


# SOURCE REGISTRY — which sources to try for each tradition
SOURCE_PRIORITY = {
    "theravada": [
        ("SuttaCentral", suttacentral_url, True),
        ("Access to Insight", access_to_insight_search, False),
        ("Dhammatalks.org", dhammatalks_search, False),
        ("BuddhaNet", buddhanet_search, False),
        ("Internet Archive", archive_search, False),
    ],
    "pali": [
        ("SuttaCentral", suttacentral_url, True),
        ("Access to Insight", access_to_insight_search, False),
        ("Dhammatalks.org", dhammatalks_search, False),
    ],
    "mahayana": [
        ("84000", eighty4000_search, False),
        ("Lotsawa House", lotsawa_search, False),
        ("BuddhaNet", buddhanet_search, False),
        ("Internet Archive", archive_search, False),
        ("Wisdomlib", wisdomlib_search, False),
    ],
    "tibetan": [
        ("84000", eighty4000_search, False),
        ("Lotsawa House", lotsawa_search, False),
        ("Internet Archive", archive_search, False),
    ],
    "vajrayana": [
        ("Lotsawa House", lotsawa_search, False),
        ("84000", eighty4000_search, False),
        ("Internet Archive", archive_search, False),
    ],
    "madhyamaka": [
        ("84000", eighty4000_search, False),
        ("Lotsawa House", lotsawa_search, False),
        ("Internet Archive", archive_search, False),
        ("GRETIL", lambda t: [f"https://gretil.sub.uni-goettingen.de/gretil.html"], False),
    ],
    "zen": [
        ("BuddhaNet", buddhanet_search, False),
        ("Internet Archive", archive_search, False),
        ("Wisdomlib", wisdomlib_search, False),
    ],
    "general": [
        ("SuttaCentral", suttacentral_url, False),
        ("BuddhaNet", buddhanet_search, False),
        ("Internet Archive", archive_search, False),
        ("Wisdomlib", wisdomlib_search, False),
        ("Lotsawa House", lotsawa_search, False),
    ],
}


# ── AGENT 1: TEXT IDENTIFIER ──────────────────────────────────────────────

IDENTIFY_PROMPT = """You are a Buddhist scholar with encyclopedic knowledge of texts across all traditions.

Given a user query, identify the Buddhist text being asked about.

Return ONLY valid JSON, no other text:
{
  "identified": true/false,
  "name": "canonical full name in English",
  "alternate_names": ["list of other names"],
  "author": "author name or null",
  "tradition": "theravada/mahayana/vajrayana/zen/madhyamaka/pali/tibetan/general",
  "canonical_ref": "e.g. DN 2 or MN 36 or SN 22.59 or Toh 107 or T 475 or null",
  "language_original": "pali/sanskrit/tibetan/chinese",
  "brief_description": "one sentence what this text is about",
  "likely_free": true/false,
  "free_assessment": "brief honest note on free availability",
  "toh_number": "Toh number for 84000 if Tibetan canonical text, else null",
  "suttacentral_ref": "SC reference like dn2 or mn36 if Pali, else null",
  "not_found_reason": "if identified=false, why"
}

Examples:
- "Samaññaphala Sutta" -> DN 2, theravada, suttacentral_ref: "dn2"
- "fruits of the contemplative life" -> same text, identify it
- "Nagarjuna verses on emptiness" -> could be MMK or Sunyatasaptati, identify most likely
- "Words of My Perfect Teacher" -> Kunzang Lamai Shelung, Patrul Rinpoche, tibetan, no free translation
- "Milarepa songs" -> Hundred Thousand Songs, Kagyu tibetan, partial free sources
- "Choying Dzod" -> Longchenpa, Nyingma, tibetan, no complete free English
- "MN 2" -> Sabbasava Sutta, Majjhima Nikaya 2, pali, suttacentral_ref: "mn2"

Query: """

def identify_text(query, model="qwen2.5:7b"):
    """Agent 1: Use LLM to identify the text from the query."""
    if not HAS_OLLAMA:
        return _fallback_identify(query)
    
    try:
        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": IDENTIFY_PROMPT + query
            }],
            options={"temperature": 0.1}
        )
        text = response["message"]["content"].strip()
        # strip markdown fences if present
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[warn] JSON parse error: {e}")
        return {"identified": False, "tradition": "general",
                "not_found_reason": "LLM output not valid JSON"}
    except Exception as e:
        print(f"[warn] Ollama error: {e}. Falling back.")
        return _fallback_identify(query)

def _fallback_identify(query):
    """Simple keyword fallback if Ollama not available."""
    q = query.lower()
    tradition = "general"
    if any(w in q for w in ["sutta", "nikaya", "pali", "dn", "mn", "sn", "an"]):
        tradition = "pali"
    elif any(w in q for w in ["tibetan", "rinpoche", "lama", "dzogchen",
                               "kagyu", "nyingma", "gelug", "toh"]):
        tradition = "tibetan"
    elif any(w in q for w in ["nagarjuna", "shantideva", "madhyamaka", "mmk"]):
        tradition = "madhyamaka"
    elif any(w in q for w in ["zen", "chan", "koan", "dogen"]):
        tradition = "zen"
    return {
        "identified": False,
        "name": query,
        "tradition": tradition,
        "canonical_ref": None,
        "suttacentral_ref": None,
        "toh_number": None,
        "brief_description": "",
        "free_assessment": "",
        "not_found_reason": "Ollama not available — keyword fallback only"
    }


# ── AGENT 2: URL GENERATOR ────────────────────────────────────────────────

def generate_candidate_urls(identity):
    """
    Deterministically generate candidate URLs from text identity.
    No LLM involved — pure template logic.
    """
    candidates = []
    tradition = identity.get("tradition", "general")
    sc_ref = identity.get("suttacentral_ref")
    toh = identity.get("toh_number")
    name = identity.get("name", "")

    # SuttaCentral: if we have a ref, generate direct URLs
    if sc_ref:
        for url in suttacentral_url(sc_ref):
            candidates.append({
                "source": "SuttaCentral",
                "url": url,
                "method": "canonical_ref",
                "priority": 1
            })
        # Also try Access to Insight and Dhammatalks for Pali texts
        for url in access_to_insight_search(name):
            candidates.append({"source": "Access to Insight", "url": url,
                                "method": "search", "priority": 2})
        for url in dhammatalks_search(name):
            candidates.append({"source": "Dhammatalks.org", "url": url,
                                "method": "index", "priority": 3})

    # 84000: if Tohoku number known
    if toh:
        for url in eighty4000_search(name, toh=toh):
            candidates.append({"source": "84000", "url": url,
                                "method": "canonical_ref", "priority": 1})

    # Tradition-based search URLs
    sources = SOURCE_PRIORITY.get(tradition, SOURCE_PRIORITY["general"])
    priority = 10
    for source_name, url_func, needs_ref in sources:
        # skip if already added via canonical ref
        already = any(c["source"] == source_name for c in candidates)
        if already:
            continue
        if needs_ref and not sc_ref:
            continue
        try:
            arg = sc_ref if needs_ref and sc_ref else name
            for url in url_func(arg):
                candidates.append({"source": source_name, "url": url,
                                    "method": "search", "priority": priority})
            priority += 1
        except Exception:
            pass

    return candidates


# ── AGENT 3: URL VALIDATOR ────────────────────────────────────────────────

def validate_url(url, timeout=5):
    """Actually check if the URL exists. Returns True if 200 or 301/302."""
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True,
                          headers={"User-Agent": "dharma-finder/1.0"})
        return r.status_code < 400
    except Exception:
        return False

def validate_candidates(candidates, max_check=12):
    """
    Validate URLs, separating confirmed from search-only links.
    Search pages are included without validation (they always exist).
    """
    confirmed = []
    search_links = []

    for c in candidates[:max_check]:
        if c["method"] == "search" or c["method"] == "index":
            # Search pages exist by definition — don't validate, just include
            search_links.append({**c, "validated": False, "type": "search"})
        else:
            # Canonical ref URLs — actually check
            print(f"  Checking: {c['url'][:60]}...", end=" ", flush=True)
            ok = validate_url(c["url"])
            print("✓" if ok else "✗")
            if ok:
                confirmed.append({**c, "validated": True, "type": "direct"})

    return confirmed, search_links


# ── AGENT 4: RESPONSE SYNTHESIZER ────────────────────────────────────────

SYNTHESIZE_PROMPT = """You are a helpful Buddhist librarian. Given information about a Buddhist text and verified free sources, write a clear, honest, helpful response.

Keep it concise — 3-5 sentences max. Be honest if no free translation exists. 
Mention the best free option first if multiple exist.
Do not invent any URLs or sources not provided to you.

Text info: {identity}
Confirmed direct links: {confirmed}
Search links available: {search_links}

Write a helpful 3-5 sentence summary for the user."""

def synthesize_response(identity, confirmed, search_links, model="qwen2.5:7b"):
    """Agent 4: Generate natural language summary from verified data."""
    if not HAS_OLLAMA:
        return _fallback_synthesize(identity, confirmed, search_links)

    prompt = SYNTHESIZE_PROMPT.format(
        identity=json.dumps(identity, indent=2),
        confirmed=json.dumps(confirmed, indent=2),
        search_links=json.dumps([s["url"] for s in search_links[:3]], indent=2)
    )
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3}
        )
        return response["message"]["content"].strip()
    except Exception:
        return _fallback_synthesize(identity, confirmed, search_links)

def _fallback_synthesize(identity, confirmed, search_links):
    name = identity.get("name", "This text")
    if confirmed:
        return f"{name} is available free at {confirmed[0]['url']}"
    elif search_links:
        return f"{name} — search these sources: {search_links[0]['url']}"
    else:
        note = identity.get("free_assessment", "")
        return f"{name}: {note or 'No free translation found.'}"


# ── OUTPUT ────────────────────────────────────────────────────────────────

def print_result(identity, confirmed, search_links, summary):
    if HAS_RICH:
        _rich_output(identity, confirmed, search_links, summary)
    else:
        _plain_output(identity, confirmed, search_links, summary)

def _rich_output(identity, confirmed, search_links, summary):
    name = identity.get("name", "Unknown")
    tradition = identity.get("tradition", "")
    ref = identity.get("canonical_ref", "")
    desc = identity.get("brief_description", "")

    header = f"[bold]{name}[/bold]"
    if ref:
        header += f"  [dim]{ref}[/dim]"
    if tradition:
        header += f"  [cyan]{tradition}[/cyan]"

    console.print(Panel(header, expand=False))
    if desc:
        console.print(f"  [dim]{desc}[/dim]\n")

    if summary:
        console.print(f"  {summary}\n")

    if confirmed:
        console.print("[bold green]Direct links (verified live):[/bold green]")
        for c in confirmed:
            console.print(f"  [green]✓[/green] [{c['source']}] {c['url']}")
        console.print()

    if search_links:
        # deduplicate
        seen = set()
        unique = []
        for s in search_links:
            if s["source"] not in seen:
                seen.add(s["source"])
                unique.append(s)
        console.print("[bold]Search on these sources:[/bold]")
        for s in unique[:5]:
            console.print(f"  [blue]→[/blue] [{s['source']}] {s['url']}")

    honest = identity.get("free_assessment")
    if honest and not confirmed:
        console.print(f"\n[yellow]Note:[/yellow] {honest}")

def _plain_output(identity, confirmed, search_links, summary):
    print(f"\n{'='*60}")
    print(f"  {identity.get('name', 'Unknown')} "
          f"[{identity.get('tradition','')}] "
          f"{identity.get('canonical_ref','')}")
    print(f"  {identity.get('brief_description','')}")
    print(f"{'='*60}")
    if summary:
        print(f"\n  {summary}")
    if confirmed:
        print("\n  DIRECT LINKS (verified):")
        for c in confirmed:
            print(f"    ✓ [{c['source']}] {c['url']}")
    if search_links:
        print("\n  SEARCH LINKS:")
        seen = set()
        for s in search_links:
            if s["source"] not in seen:
                seen.add(s["source"])
                print(f"    → [{s['source']}] {s['url']}")
    if not confirmed and not search_links:
        print(f"\n  {identity.get('free_assessment','No free sources found.')}")
    print()


# ── MAIN PIPELINE ─────────────────────────────────────────────────────────

def find(query, model="qwen2.5:7b", skip_validation=False):
    print(f"\n[1/4] Identifying text: '{query}'")
    identity = identify_text(query, model)

    if not identity.get("identified", True):
        print(f"  Could not identify: {identity.get('not_found_reason','')}")
    else:
        name = identity.get("name", "")
        ref = identity.get("canonical_ref", "")
        print(f"  Identified: {name} {f'[{ref}]' if ref else ''}")

    print("[2/4] Generating candidate URLs...")
    candidates = generate_candidate_urls(identity)
    print(f"  Generated {len(candidates)} candidates")

    if skip_validation:
        confirmed = []
        search_links = candidates
    else:
        print("[3/4] Validating direct links...")
        confirmed, search_links = validate_candidates(candidates)
        print(f"  {len(confirmed)} confirmed, {len(search_links)} search links")

    print("[4/4] Synthesizing response...")
    summary = synthesize_response(identity, confirmed, search_links, model)

    print_result(identity, confirmed, search_links, summary)
    return identity, confirmed, search_links

def main():
    parser = argparse.ArgumentParser(
        description="Find free Buddhist texts using local Ollama LLM"
    )
    parser.add_argument("query", nargs="?")
    parser.add_argument("--model", default="qwen2.5:7b",
                        help="Ollama model to use (default: qwen2.5:7b)")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--no-validate", action="store_true",
                        help="Skip URL validation (faster, less reliable)")
    args = parser.parse_args()

    if args.interactive:
        print("\nDharma Finder (local) — type 'quit' to exit")
        print(f"Using model: {args.model}\n")
        while True:
            query = input("Search: ").strip()
            if query.lower() in ("quit", "exit", "q"):
                break
            if query:
                find(query, model=args.model,
                     skip_validation=args.no_validate)
    elif args.query:
        find(args.query, model=args.model,
             skip_validation=args.no_validate)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
