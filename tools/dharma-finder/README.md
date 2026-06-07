# dharma-finder-local

Find free legal sources for any Buddhist text using a local LLM.
No API keys. No cost. Runs entirely on your machine.

## How it works — 4 agents, no hallucinated URLs

```
[1] Text Identifier (Ollama/Qwen)
     — understands your query, identifies the text,
       returns canonical reference (DN 2, Toh 107 etc.)

[2] URL Generator (deterministic, no LLM)
     — builds candidate URLs from templates and canonical refs
     — SuttaCentral pattern: suttacentral.net/{ref}/en/{translator}
     — 84000 pattern: 84000.co/translation/{toh-number}
     — tradition routing: Pali → SuttaCentral first,
       Tibetan → 84000 + Lotsawa House first

[3] URL Validator (requests.head, no LLM)
     — actually checks each direct URL returns HTTP 200
     — only confirmed live links are shown as "verified"
     — search pages shown separately without validation

[4] Response Synthesizer (Ollama/Qwen)
     — writes natural language summary from verified data only
     — cannot invent URLs — ground truth is locked by step 3
```

The LLM is used only for language understanding (step 1) and natural language
generation (step 4). All URLs come from deterministic templates validated
against live servers. The LLM never invents a URL.

## Setup

```bash
# 1. Install Ollama
# https://ollama.com/download

# 2. Pull a model
ollama pull qwen2.5:7b        # recommended — good balance
ollama pull qwen2.5:3b        # faster, lighter
ollama pull llama3.2:3b       # alternative

# 3. Install Python dependencies
pip install ollama requests rich

# 4. Run
python agent.py "Samaññaphala Sutta"
python agent.py "Longchenpa treasury dharmadhatu"
python agent.py "Words of My Perfect Teacher"
python agent.py --interactive
```

## Example outputs

```
Search: Samaññaphala Sutta

[1/4] Identifying text...
  Identified: Samaññaphala Sutta [DN 2]
[2/4] Generating candidates...
  Generated 6 candidates
[3/4] Validating...
  Checking: https://suttacentral.net/dn2/en/sujato... ✓
  Checking: https://suttacentral.net/dn2/en/bodhi... ✓
  Checking: https://suttacentral.net/dn2/en/thanissaro... ✓
  2 confirmed, 3 search links

Direct links (verified):
  ✓ [SuttaCentral] https://suttacentral.net/dn2/en/sujato
  ✓ [SuttaCentral] https://suttacentral.net/dn2/en/thanissaro

  The Samaññaphala Sutta (DN 2) is freely available in multiple
  translations on SuttaCentral. Sujato's modern English translation
  is recommended for readability; Thanissaro's version includes
  extensive notes from the Thai Forest tradition.
```

```
Search: Words of My Perfect Teacher

[1/4] Identifying text...
  Identified: Words of My Perfect Teacher (Kunzang Lamai Shelung)
[2/4] Generating candidates...
  Generated 3 candidates
[3/4] Validating...
  0 confirmed direct links

  No complete free English translation exists for this text.
  The standard Padmakara/Shambhala translation is commercial.
  The Tibetan original is available on BDRC (W1KG11138).
  FPMT has free ngondro practice texts that cover similar ground.

Search on these sources:
  → [Lotsawa House] https://www.lotsawahouse.org/search?keys=Words+of+My+Perfect+Teacher
  → [Internet Archive] https://archive.org/search?query=...
```

## Sources covered

| Source | Tradition | Method |
|--------|-----------|--------|
| SuttaCentral | Pali/early | Canonical ref templates + validation |
| Access to Insight | Theravada | Search URL |
| Dhammatalks.org | Thai Forest | Index page |
| BuddhaNet | All | Search URL |
| 84000 | Tibetan canonical | Tohoku number + validation |
| Lotsawa House | Tibetan | Search URL |
| BDRC/BUDA | Tibetan originals | Search URL |
| Internet Archive | All PD | Search API |
| GRETIL | Sanskrit | Direct |
| Wisdomlib | All | Search URL |
| Sacred Texts | PD translations | Search URL |

## Without Ollama

The tool works without Ollama using keyword-based tradition detection,
but text identification will be weaker. Run:

```bash
python agent.py "DN 2" --no-validate
```

Using a canonical reference directly bypasses the LLM identification step.

## Adding texts to the known registry

Edit `sources.py` and add entries to `KNOWN_TEXTS` for texts with
complex free-source situations (partial translations, multiple versions,
or definitively no free translation). This overrides the LLM lookup
for those specific texts and guarantees accurate results.

## Why local LLM over API

- No cost per query
- Works offline after setup
- No data sent to third parties
- Practitioners in restricted or expensive-internet regions can use it
- Can be integrated into local dharma study setups alongside
  falkor-rag, indic-concept-graph etc.

## License

MIT
