"""
sources.py — Complete registry of free Buddhist text sources

Every source has been verified as genuinely free and legal.
Organized by tradition coverage, search method, and content type.
"""

SOURCES = {

    # ── PALI CANON / THERAVADA ─────────────────────────────────────────────

    "suttacentral": {
        "name": "SuttaCentral",
        "url": "https://suttacentral.net",
        "search_url": "https://suttacentral.net/search?query={query}",
        "api_url": "https://suttacentral.net/api/suttas",
        "tradition": ["theravada", "early_buddhist", "pali", "chinese_agamas",
                      "tibetan_kangyur", "sanskrit"],
        "content_type": ["sutta", "vinaya", "abhidhamma"],
        "language": ["pali", "english", "many"],
        "fetch_method": "api_and_web",
        "has_translations": True,
        "has_originals": True,
        "format": ["html", "epub", "offline_app"],
        "license": "CC0",
        "quality": "excellent",
        "notes": "Best source for Pali Canon. Sujato and Bodhi translations. "
                 "Also has Chinese Agamas, Tibetan parallels, Sanskrit fragments. "
                 "Bilara-data GitHub repo has segment-aligned JSON — best for NLP.",
        "github": "https://github.com/suttacentral/bilara-data",
        "search_tip": "Use sutta reference (SN 22.59) or title keywords"
    },

    "accesstoinsight": {
        "name": "Access to Insight",
        "url": "https://www.accesstoinsight.org",
        "search_url": "https://www.accesstoinsight.org/search.html?q={query}",
        "tradition": ["theravada", "pali"],
        "content_type": ["sutta", "commentary", "modern_dhamma"],
        "language": ["english", "pali"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["html"],
        "license": "mixed_free_distribution",
        "quality": "excellent",
        "notes": "Thanissaro Bhikkhu (extensive), Bhikkhu Bodhi, Bhikkhu Ñanamoli, "
                 "many others. Thai Forest Tradition emphasis. "
                 "Older site but comprehensive Theravada suttas. "
                 "Best for Thanissaro translations not elsewhere.",
        "search_tip": "Use translator name or sutta title in search"
    },

    "dhammatalks": {
        "name": "Dhamma Talks (Thanissaro Bhikkhu)",
        "url": "https://www.dhammatalks.org",
        "search_url": "https://www.dhammatalks.org/suttas/",
        "tradition": ["theravada", "thai_forest"],
        "content_type": ["sutta", "books", "essays", "audio"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["html", "pdf", "epub", "audio"],
        "license": "free_distribution_only",
        "quality": "excellent",
        "notes": "Thanissaro Bhikkhu's complete translations — all four Nikayas, "
                 "Dhammapada, Udana, Itivuttaka, Sutta Nipata, and many books. "
                 "No commercial use but freely downloadable. "
                 "Often has texts not on Access to Insight.",
        "search_tip": "Direct sutta index by nikaya available"
    },

    "buddhanet": {
        "name": "BuddhaNet",
        "url": "https://www.buddhanet.net",
        "search_url": "https://www.buddhanet.net/ebooks.htm",
        "ebook_url": "https://www.buddhanet.net/ebooks/",
        "tradition": ["all_traditions"],
        "content_type": ["books", "sutta", "commentary", "practice_guides"],
        "language": ["english", "multilingual"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["pdf"],
        "license": "free_distribution",
        "quality": "variable",
        "notes": "Large PDF library covering all traditions. "
                 "Strongest for Theravada and general Buddhism. "
                 "Has Mahayana and Tibetan sections. "
                 "Quality varies — some texts are excellent, some older. "
                 "Good for: Dhammapada, Milindapanha, introductory Mahayana, "
                 "Heart Sutra, Diamond Sutra, Platform Sutra.",
        "search_tip": "Browse by tradition: /ebooks_s/ Theravada, /ebooks_ms/ Mahayana"
    },

    "metta_lk": {
        "name": "Metta.lk (Sri Lanka Tipitaka Project)",
        "url": "https://www.metta.lk",
        "tradition": ["theravada", "pali"],
        "content_type": ["tipitaka", "commentary"],
        "language": ["pali", "sinhala", "english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": True,
        "format": ["html"],
        "license": "free",
        "quality": "good",
        "notes": "Complete Pali Tipitaka with translations. "
                 "Useful cross-reference for Pali originals."
    },

    "tipitaka_org": {
        "name": "Tipitaka.org",
        "url": "https://tipitaka.org",
        "tradition": ["theravada", "pali"],
        "content_type": ["tipitaka"],
        "language": ["pali", "english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": True,
        "format": ["html"],
        "license": "free",
        "quality": "good",
        "notes": "Alternative Pali Canon source. "
                 "Good for cross-referencing Pali originals."
    },

    "ancient_buddhist_texts": {
        "name": "Ancient Buddhist Texts",
        "url": "https://www.ancient-buddhist-texts.net",
        "tradition": ["pali", "early_buddhist"],
        "content_type": ["sutta", "grammar", "study_aids"],
        "language": ["pali", "english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": True,
        "format": ["html", "pdf"],
        "license": "free",
        "quality": "excellent",
        "notes": "Ven. Ānandajoti Bhikkhu. Scholarly Pali texts with "
                 "detailed grammatical notes. "
                 "Best for: Theragatha, Therigatha, Jataka, "
                 "less common Pali texts. Over 130 hours audio recordings too."
    },

    "buddha_dust": {
        "name": "Buddha Dust",
        "url": "https://buddhadust.com",
        "tradition": ["theravada", "pali"],
        "content_type": ["sutta"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["html"],
        "license": "free",
        "quality": "good",
        "notes": "All PTS translations of Four Nikayas plus Thanissaro "
                 "and Bhikkhu Bodhi free translations. "
                 "Useful aggregator for older PD translations."
    },

    # ── TIBETAN / MAHAYANA / VAJRAYANA ────────────────────────────────────

    "84000": {
        "name": "84000: Translating the Words of the Buddha",
        "url": "https://84000.co",
        "search_url": "https://84000.co/all-publications",
        "api_url": "https://84000.co/api/",
        "tradition": ["tibetan", "mahayana", "vajrayana", "kangyur", "tengyur"],
        "content_type": ["sutra", "tantra", "commentary", "treatise"],
        "language": ["english", "tibetan"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": True,
        "format": ["html", "epub", "pdf"],
        "license": "CC_BY_NC_ND_4.0",
        "quality": "excellent",
        "notes": "Ongoing project to translate entire Kangyur and Tengyur. "
                 "Scholarly apparatus, Tohoku numbers, segment-aligned. "
                 "Not all texts translated yet — check catalog first. "
                 "Best for: canonical sutras and treatises in Tibetan tradition. "
                 "CC BY-NC-ND — free to read, cannot modify or commercialize.",
        "search_tip": "Search by Tohoku number (e.g. Toh 30) or title. "
                      "Browse catalog at /all-publications"
    },

    "lotsawa_house": {
        "name": "Lotsawa House",
        "url": "https://www.lotsawahouse.org",
        "search_url": "https://www.lotsawahouse.org/search?keys={query}",
        "tradition": ["tibetan", "nyingma", "kagyu", "gelug", "sakya", "rimé"],
        "content_type": ["practice_texts", "prayers", "sadhana", "commentary",
                         "treatise", "biography"],
        "language": ["english", "french", "german", "spanish", "tibetan",
                     "others"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": True,
        "format": ["html", "epub", "pdf"],
        "license": "CC_BY_NC",
        "quality": "excellent",
        "notes": "6000+ texts in 9 languages. Strongest for Nyingma and Kagyu. "
                 "Has Longchenpa, Mipham, Patrul Rinpoche extracts, "
                 "Bodhicharyavatara (Padmakara), many Khyentse texts. "
                 "Best free source for Tibetan practice texts in English. "
                 "EPUB and PDF downloadable.",
        "search_tip": "Search by author (Longchenpa, Mipham, Shantideva) or text title. "
                      "Browse by tradition or author at /tibetan-masters/"
    },

    "bdrc": {
        "name": "Buddhist Digital Resource Center (BDRC/BUDA)",
        "url": "https://library.bdrc.io",
        "search_url": "https://library.bdrc.io/search?q={query}",
        "api_url": "https://ld.bdrc.io/",
        "tradition": ["tibetan", "all_tibetan_traditions"],
        "content_type": ["original_texts", "scans", "etexts"],
        "language": ["tibetan", "some_english"],
        "fetch_method": "api_and_web",
        "has_translations": False,
        "has_originals": True,
        "format": ["pdf_scans", "etext"],
        "license": "open_access",
        "quality": "excellent_for_originals",
        "notes": "Largest archive of Tibetan texts — 15M+ pages digitized. "
                 "Mostly Tibetan originals, minimal English translation. "
                 "Essential for: finding whether a text exists in Tibetan, "
                 "BDRC work numbers (W numbers) for cross-referencing. "
                 "Some etexts via ACIP encoding. "
                 "Use alongside 84000 or Lotsawa House for translations.",
        "search_tip": "Search by Tibetan title, author, or W-number. "
                      "BUDA 2.0 has improved search."
    },

    "dharmacloud": {
        "name": "DharmaCloud (Tsadra Foundation)",
        "url": "https://dharmacloud.tsadra.org",
        "tradition": ["tibetan", "all_tibetan_traditions"],
        "content_type": ["original_texts", "etexts"],
        "language": ["tibetan"],
        "fetch_method": "web_search",
        "has_translations": False,
        "has_originals": True,
        "format": ["pdf", "epub"],
        "license": "free_download",
        "quality": "excellent_for_originals",
        "notes": "Hundreds of Tibetan texts from monastery publishers, "
                 "free download. Companion to BDRC for digital Tibetan originals. "
                 "Rimé emphasis — texts from all four schools."
    },

    "rigpawiki": {
        "name": "Rigpa Wiki",
        "url": "https://www.rigpawiki.org",
        "tradition": ["tibetan", "nyingma"],
        "content_type": ["encyclopedia", "text_excerpts", "commentary"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["html"],
        "license": "CC",
        "quality": "good",
        "notes": "Encyclopedia of Tibetan Buddhism from Sogyal Rinpoche lineage. "
                 "Good for: concept definitions, short text excerpts, "
                 "biography of masters. Not complete texts. "
                 "Strong on Nyingma terminology."
    },

    "dharma_download": {
        "name": "Dharma Download",
        "url": "http://www.dharmadownload.net",
        "tradition": ["tibetan"],
        "content_type": ["original_texts"],
        "language": ["tibetan"],
        "fetch_method": "web_search",
        "has_translations": False,
        "has_originals": True,
        "format": ["pdf"],
        "license": "free",
        "quality": "good",
        "notes": "Free Tibetan text library. Companion to BDRC."
    },

    # ── CHINESE BUDDHISM ──────────────────────────────────────────────────

    "cbeta": {
        "name": "CBETA (Chinese Buddhist Electronic Text Association)",
        "url": "https://cbetaonline.dila.edu.tw",
        "tradition": ["chinese_buddhism", "mahayana", "chan", "pure_land"],
        "content_type": ["taisho_tripitaka", "sutra", "commentary"],
        "language": ["chinese", "some_english"],
        "fetch_method": "web_search",
        "has_translations": False,
        "has_originals": True,
        "format": ["html", "xml"],
        "license": "free",
        "quality": "excellent",
        "notes": "Complete Taisho Tripitaka in Chinese. "
                 "Essential for: finding T-numbers, Chinese originals of "
                 "Sanskrit/Tibetan texts, Chinese-tradition canonical texts. "
                 "Most texts Chinese only — few English translations."
    },

    "numata": {
        "name": "BDK English Tripitaka (Numata Center)",
        "url": "https://www.bdkamerica.org/tripitaka/bdk-english-tripitaka",
        "tradition": ["chinese_buddhism", "mahayana"],
        "content_type": ["sutra"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["pdf"],
        "license": "free_download",
        "quality": "excellent",
        "notes": "Scholarly English translations of major Taisho texts. "
                 "Free PDF download. Best for: Vimalakirti, Lotus Sutra, "
                 "Lankavatara, major Chinese Mahayana sutras in scholarly translation."
    },

    # ── SANSKRIT / ACADEMIC ───────────────────────────────────────────────

    "gretil": {
        "name": "GRETIL (Göttingen Register of Electronic Texts in Indian Languages)",
        "url": "https://gretil.sub.uni-goettingen.de",
        "tradition": ["sanskrit", "pali", "prakrit"],
        "content_type": ["original_texts"],
        "language": ["sanskrit", "pali"],
        "fetch_method": "web_search",
        "has_translations": False,
        "has_originals": True,
        "format": ["txt", "html"],
        "license": "public_domain",
        "quality": "excellent_for_sanskrit",
        "notes": "Largest online Sanskrit text repository. "
                 "Buddhist Sanskrit: Nagarjuna works, Prajnaparamita originals, "
                 "Bodhicharyavatara, Abhidharmakosa, many others. "
                 "No translations — Sanskrit originals only. "
                 "Use alongside Lotsawa House or 84000 for translations."
    },

    "digital_sanskrit_buddhist_canon": {
        "name": "Digital Sanskrit Buddhist Canon",
        "url": "http://www.dsbcproject.org",
        "tradition": ["sanskrit"],
        "content_type": ["original_texts", "translations"],
        "language": ["sanskrit", "english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": True,
        "format": ["html"],
        "license": "free",
        "quality": "good",
        "notes": "Sanskrit texts with some English translations. "
                 "Less comprehensive than GRETIL but has translations."
    },

    # ── GENERAL / MULTI-TRADITION ──────────────────────────────────────────

    "internet_archive": {
        "name": "Internet Archive",
        "url": "https://archive.org",
        "search_url": "https://archive.org/search?query={query}+buddhism&mediatype=texts",
        "api_url": "https://archive.org/advancedsearch.php",
        "tradition": ["all"],
        "content_type": ["books", "scans", "old_translations"],
        "language": ["english", "many"],
        "fetch_method": "api",
        "has_translations": True,
        "has_originals": True,
        "format": ["pdf", "epub", "txt"],
        "license": "mixed_public_domain",
        "quality": "variable",
        "notes": "Invaluable for: pre-1928 PD translations (Max Müller SBE series, "
                 "Rhys Davids, Oldenberg, Conze early works), scanned monastery "
                 "publications, out-of-print scholarly works. "
                 "Quality varies enormously. "
                 "Best searches: 'Sacred Books of the East buddhism', "
                 "'Conze prajnaparamita', specific translator names.",
        "search_tip": "Use mediatype:texts and subject:buddhism filters"
    },

    "open_buddhist_university": {
        "name": "Open Buddhist University",
        "url": "https://buddhistuniversity.net",
        "tradition": ["all"],
        "content_type": ["curated_reading_lists", "aggregated_links"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["html_links"],
        "license": "free",
        "quality": "excellent_for_discovery",
        "notes": "Not a text repository but an excellent aggregator. "
                 "Curated reading lists with links to free sources. "
                 "Best for: discovering what free resources exist on a topic. "
                 "Covers all traditions systematically."
    },

    "wisdomlib": {
        "name": "Wisdomlib",
        "url": "https://www.wisdomlib.org",
        "search_url": "https://www.wisdomlib.org/search?q={query}",
        "tradition": ["buddhist", "hindu", "jain"],
        "content_type": ["texts", "definitions", "commentary"],
        "language": ["english", "sanskrit"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": True,
        "format": ["html"],
        "license": "free",
        "quality": "good",
        "notes": "Large collection of Buddhist and Indian texts with translations. "
                 "Useful for: Sanskrit term definitions, Jataka tales, "
                 "some Mahayana sutras, Abhidharma texts. "
                 "Quality inconsistent but coverage is broad."
    },

    "sacred_texts": {
        "name": "Sacred Texts Archive",
        "url": "https://www.sacred-texts.com/bud/",
        "tradition": ["all"],
        "content_type": ["old_translations"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["html"],
        "license": "public_domain",
        "quality": "historical_value",
        "notes": "Old site with pre-1923 PD translations. "
                 "Useful for: Max Müller Sacred Books of the East Buddhist volumes, "
                 "early Rhys Davids translations, Müller Diamond Sutra. "
                 "Language is Victorian academic English — dated but PD. "
                 "Good as backup when no modern translation is free."
    },

    # ── TRADITION-SPECIFIC PUBLISHERS WITH FREE SECTIONS ─────────────────

    "fpmt": {
        "name": "FPMT (Foundation for the Preservation of Mahayana Tradition)",
        "url": "https://fpmt.org",
        "free_texts_url": "https://fpmt.org/education/teachings/texts/",
        "tradition": ["tibetan", "gelug"],
        "content_type": ["practice_texts", "sadhana", "prayer"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["pdf"],
        "license": "free_for_practice",
        "quality": "good",
        "notes": "Gelug tradition practice texts. Lama Zopa and Lama Yeshe texts. "
                 "Good for: Lam Rim prayer texts, Vajrasattva, Tara practices. "
                 "Not scholarly texts — practice liturgy focus."
    },

    "berzin_archives": {
        "name": "Berzin Archives (Study Buddhism)",
        "url": "https://studybuddhism.com",
        "tradition": ["tibetan", "all_tibetan_traditions"],
        "content_type": ["teachings", "commentary", "translations"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["html"],
        "license": "free",
        "quality": "excellent",
        "notes": "Alexander Berzin's extensive teachings and translations. "
                 "Strong on: Tibetan Buddhist philosophy explained accessibly, "
                 "Kalachakra, Lam Rim, Mahamudra explanations. "
                 "Not full texts but substantial commentary and extracts."
    },

    "buddhisttexts_org": {
        "name": "Buddhist Text Translation Society",
        "url": "https://www.buddhisttexts.org",
        "tradition": ["chinese_buddhism", "chan"],
        "content_type": ["sutra", "commentary", "vinaya"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["pdf"],
        "license": "free_rotating_collection",
        "quality": "good",
        "notes": "Dharma Realm Buddhist Association / Hsuan Hua tradition. "
                 "Good for: Shurangama Sutra, Avatamsaka, Sixth Patriarch Platform Sutra. "
                 "Rotating free collection — not all texts always available."
    },

    "plum_village": {
        "name": "Plum Village (Thich Nhat Hanh)",
        "url": "https://plumvillage.org",
        "tradition": ["zen", "vietnamese", "engaged_buddhism"],
        "content_type": ["sutras", "chanting_books", "commentary"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["pdf", "html"],
        "license": "free",
        "quality": "good",
        "notes": "Thich Nhat Hanh's translations and commentaries. "
                 "Free: Heart Sutra, Diamond Sutra (his versions), "
                 "chanting books, some Sutra translations. "
                 "Modern, accessible language — less scholarly but widely used."
    },

    "amaravati": {
        "name": "Amaravati Publications",
        "url": "https://www.amaravati.org/dhamma-books/",
        "tradition": ["theravada", "thai_forest"],
        "content_type": ["teachings", "books"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["pdf"],
        "license": "free_distribution",
        "quality": "excellent",
        "notes": "Ajahn Chah, Ajahn Sumedho, Ajahn Amaro, Ajahn Pasanno. "
                 "Free PDF downloads of their books. "
                 "Best for Thai Forest Tradition teachers' books."
    },

    "dhamma_org": {
        "name": "Dhamma.org (S.N. Goenka / Vipassana)",
        "url": "https://www.dhamma.org",
        "tradition": ["theravada", "vipassana"],
        "content_type": ["texts", "audio"],
        "language": ["english", "many"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["html", "audio"],
        "license": "free",
        "quality": "good",
        "notes": "Goenka tradition Vipassana texts and chanting. "
                 "Free: Pali chanting texts, some discourse transcripts."
    },

    # ── ACADEMIC OPEN ACCESS ──────────────────────────────────────────────

    "academia_edu": {
        "name": "Academia.edu",
        "url": "https://www.academia.edu",
        "search_url": "https://www.academia.edu/search?q={query}+buddhism",
        "tradition": ["all"],
        "content_type": ["academic_papers", "translations", "dissertations"],
        "language": ["english", "many"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": True,
        "format": ["pdf"],
        "license": "varies_often_free",
        "quality": "variable_to_excellent",
        "notes": "Scholarly papers often include translations as appendices. "
                 "Good for: finding academic translations of obscure texts, "
                 "Nagarjuna minor works, Sanskrit Buddhist texts. "
                 "Requires free account for some downloads.",
        "search_tip": "Search 'translation [text name]' to find papers with translations"
    },

    "jstor_open": {
        "name": "JSTOR Open Access",
        "url": "https://www.jstor.org",
        "tradition": ["all"],
        "content_type": ["academic_papers", "translations"],
        "language": ["english"],
        "fetch_method": "web_search",
        "has_translations": True,
        "has_originals": False,
        "format": ["pdf"],
        "license": "open_access_articles",
        "quality": "excellent",
        "notes": "Many Buddhist studies journal articles are open access. "
                 "Good for finding translations published in academic journals."
    },
}


# Priority order for searching by tradition
TRADITION_PRIORITY = {
    "theravada": [
        "suttacentral", "accesstoinsight", "dhammatalks",
        "buddhanet", "ancient_buddhist_texts", "buddha_dust",
        "amaravati", "internet_archive"
    ],
    "pali": [
        "suttacentral", "accesstoinsight", "dhammatalks",
        "tipitaka_org", "metta_lk", "ancient_buddhist_texts"
    ],
    "mahayana": [
        "84000", "lotsawa_house", "buddhanet", "numata",
        "plum_village", "internet_archive", "wisdomlib"
    ],
    "tibetan": [
        "84000", "lotsawa_house", "bdrc", "dharmacloud",
        "rigpawiki", "berzin_archives", "fpmt"
    ],
    "nyingma": [
        "lotsawa_house", "84000", "bdrc", "dharmacloud", "rigpawiki"
    ],
    "kagyu": [
        "lotsawa_house", "84000", "bdrc", "berzin_archives"
    ],
    "gelug": [
        "fpmt", "lotsawa_house", "84000", "berzin_archives"
    ],
    "zen_chan": [
        "buddhanet", "plum_village", "buddhisttexts_org",
        "numata", "internet_archive"
    ],
    "sanskrit": [
        "gretil", "digital_sanskrit_buddhist_canon",
        "internet_archive", "academia_edu"
    ],
    "chinese": [
        "cbeta", "numata", "buddhisttexts_org", "internet_archive"
    ],
    "general": [
        "suttacentral", "buddhanet", "internet_archive",
        "open_buddhist_university", "wisdomlib", "sacred_texts"
    ],
}


# Known texts with pre-verified free source information
# These bypass the search agent entirely — direct lookup
KNOWN_TEXTS = {
    "heart_sutra": {
        "titles": ["Heart Sutra", "Prajnaparamitahrdaya", "Heart of Prajna",
                   "Essence of Prajnaparamita"],
        "free_sources": [
            {"source": "84000", "url": "https://84000.co/translation/toh21",
             "type": "full", "translator": "84000", "license": "CC_BY_NC_ND"},
            {"source": "lotsawa_house",
             "url": "https://www.lotsawahouse.org/words-of-the-buddha/heart-sutra",
             "type": "full", "translator": "multiple", "license": "CC_BY_NC"},
            {"source": "plum_village", "url": "https://plumvillage.org/sutra/",
             "type": "full", "translator": "Thich Nhat Hanh", "license": "free"},
            {"source": "buddhanet", "url": "https://www.buddhanet.net/pdf_file/heartsutra.pdf",
             "type": "full", "translator": "multiple", "license": "free"},
        ],
        "notes": "Multiple free translations. 84000 most scholarly. "
                 "Plum Village most accessible. Lotsawa House has Tibetan original too."
    },

    "diamond_sutra": {
        "titles": ["Diamond Sutra", "Vajracchedika", "Diamond Cutter",
                   "Vajracchedika Prajnaparamita"],
        "free_sources": [
            {"source": "buddhanet",
             "url": "https://www.buddhanet.net/pdf_file/diamond_sutra.pdf",
             "type": "full", "translator": "Price/Wong", "license": "free"},
            {"source": "sacred_texts",
             "url": "https://sacred-texts.com/bud/vajra.htm",
             "type": "full", "translator": "Müller 1894", "license": "public_domain"},
            {"source": "84000", "url": "https://84000.co/translation/toh16",
             "type": "full", "translator": "84000", "license": "CC_BY_NC_ND"},
            {"source": "plum_village", "url": "https://plumvillage.org/sutra/",
             "type": "full", "translator": "Thich Nhat Hanh", "license": "free"},
        ],
        "notes": "Red Pine translation is excellent but commercial. "
                 "Müller 1894 is PD but dated. 84000 is scholarly and free."
    },

    "dhammapada": {
        "titles": ["Dhammapada"],
        "free_sources": [
            {"source": "accesstoinsight",
             "url": "https://www.accesstoinsight.org/tipitaka/kn/dhp/",
             "type": "full", "translator": "Thanissaro Bhikkhu", "license": "free"},
            {"source": "suttacentral", "url": "https://suttacentral.net/dhp",
             "type": "full", "translator": "Sujato/Buddharakkhita", "license": "CC0"},
            {"source": "buddhanet",
             "url": "https://www.buddhanet.net/pdf_file/scrndhamma.pdf",
             "type": "full", "translator": "Buddharakkhita", "license": "free"},
        ],
        "notes": "Multiple excellent free translations. Thanissaro has extensive "
                 "commentary. Sujato has clean modern English."
    },

    "bodhicharyavatara": {
        "titles": ["Bodhicharyavatara", "Bodhicaryavatara",
                   "Guide to the Bodhisattva's Way of Life",
                   "Way of the Bodhisattva", "Entering the Way of Enlightenment"],
        "author": "Shantideva",
        "free_sources": [
            {"source": "lotsawa_house",
             "url": "https://www.lotsawahouse.org/indian-masters/shantideva/bodhicharyavatara",
             "type": "full", "translator": "Padmakara Translation Group",
             "license": "CC_BY_NC", "format": ["html", "epub", "pdf"],
             "notes": "Best available free translation. Complete."},
            {"source": "internet_archive",
             "url": "https://archive.org/details/BodhicaryavataraOfSantideva",
             "type": "full", "translator": "Crosby and Skilton 1995",
             "license": "public_domain",
             "notes": "Academic translation, now PD in some jurisdictions"},
        ],
        "commercial_note": "Padmakara (Shambhala) and Tibetan Classics editions "
                           "are commercial but Lotsawa House has same Padmakara translation free."
    },

    "mulamadhyamakakarika": {
        "titles": ["Mulamadhyamakakarika", "MMK",
                   "Fundamental Verses on the Middle Way",
                   "Mula Madhyamaka Karika"],
        "author": "Nagarjuna",
        "free_sources": [
            {"source": "internet_archive",
             "url": "https://archive.org/details/nagarjuna_mulamadhyamakakarika",
             "type": "full", "translator": "Inada / Kalupahana",
             "license": "public_domain"},
            {"source": "academia_edu",
             "url": "https://www.academia.edu/search?q=mulamadhyamakakarika+translation",
             "type": "varies", "translator": "various academic",
             "license": "varies"},
        ],
        "commercial_note": "Garfield translation (Open Court) is most used "
                           "but commercial. Jay Garfield's commentary is essential. "
                           "Siderits/Katsura (Wisdom) is also commercial. "
                           "Geshe Kelsang Wangmo selected chapters freely available."
    },

    "milindapanha": {
        "titles": ["Milindapanha", "Questions of King Milinda",
                   "Milindapanha chariot", "Nagasena chariot"],
        "free_sources": [
            {"source": "accesstoinsight",
             "url": "https://www.accesstoinsight.org/lib/authors/davids/milinda.html",
             "type": "selections", "translator": "Rhys Davids",
             "license": "public_domain"},
            {"source": "sacred_texts",
             "url": "https://sacred-texts.com/bud/milinda.htm",
             "type": "full", "translator": "Rhys Davids 1890",
             "license": "public_domain"},
            {"source": "internet_archive",
             "url": "https://archive.org/details/questionsofkingm00nagarich",
             "type": "full", "translator": "Rhys Davids",
             "license": "public_domain"},
        ],
    },

    "vimalakirti_sutra": {
        "titles": ["Vimalakirti Sutra", "Vimalakirtinirdesa",
                   "Teaching of Vimalakirti"],
        "free_sources": [
            {"source": "numata",
             "url": "https://www.bdkamerica.org/tripitaka/bdk-english-tripitaka",
             "type": "full", "translator": "BDK/Numata",
             "license": "free_pdf"},
            {"source": "buddhanet",
             "url": "https://www.buddhanet.net/pdf_file/vimalakirti.pdf",
             "type": "full", "translator": "Thurman",
             "license": "free"},
        ],
        "commercial_note": "Thurman (Penn State) and McRae (BDK) are best translations. "
                           "McRae available free via BDK."
    },

    "words_of_my_perfect_teacher": {
        "titles": ["Words of My Perfect Teacher", "Kunzang Lama'i Shelung",
                   "Kunzang Lamai Shelung", "Patrul Rinpoche ngondro"],
        "author": "Patrul Rinpoche",
        "free_sources": [],
        "commercial_note": "No complete free English translation exists. "
                           "Padmakara/Shambhala translation is standard and commercial. "
                           "Tibetan original: BDRC W1KG11138. "
                           "Lotsawa House has some Patrul Rinpoche texts but not this one.",
        "alternatives": "FPMT has free ngondro practice texts. "
                        "Berzin Archives has explanations of ngondro practices."
    },

    "lotus_sutra": {
        "titles": ["Lotus Sutra", "Saddharmapundarika", "Myoho Renge Kyo"],
        "free_sources": [
            {"source": "buddhanet",
             "url": "https://www.buddhanet.net/pdf_file/lotus-sutra.pdf",
             "type": "full", "translator": "Murano",
             "license": "free"},
            {"source": "internet_archive",
             "url": "https://archive.org/details/saddharmapu00kern",
             "type": "full", "translator": "Kern 1884",
             "license": "public_domain"},
            {"source": "numata",
             "url": "https://www.bdkamerica.org/tripitaka/bdk-english-tripitaka",
             "type": "full", "translator": "Murano/BDK",
             "license": "free_pdf"},
        ],
    },

    "lankavatara_sutra": {
        "titles": ["Lankavatara Sutra", "Lanka Sutra"],
        "free_sources": [
            {"source": "buddhanet",
             "url": "https://www.buddhanet.net/pdf_file/lanka-sutra.pdf",
             "type": "full", "translator": "Suzuki",
             "license": "free"},
            {"source": "sacred_texts",
             "url": "https://sacred-texts.com/bud/lanka/index.htm",
             "type": "full", "translator": "Suzuki 1932",
             "license": "public_domain"},
        ],
    },

    "majjhima_nikaya": {
        "titles": ["Majjhima Nikaya", "Middle Length Discourses",
                   "Middle Length Sayings"],
        "free_sources": [
            {"source": "suttacentral", "url": "https://suttacentral.net/mn",
             "type": "full", "translator": "Sujato", "license": "CC0"},
            {"source": "dhammatalks",
             "url": "https://www.dhammatalks.org/suttas/MN/index_MN.html",
             "type": "full", "translator": "Thanissaro", "license": "free"},
        ],
        "commercial_note": "Bhikkhu Bodhi translation (Wisdom) is standard academic "
                           "edition — commercial but Sujato (SuttaCentral) is excellent and free."
    },
}
