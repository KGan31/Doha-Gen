"""
Devanagari Matra Counter (Doha Version)
=======================================
Breaks down Hindi words and entire Dohas into their phonetic units and counts matras.

Matra counting rules (used in Hindi poetry / Chhanda shastra):
  - Laghu (लघु) = 1 matra  → short vowel sound (अ, इ, उ + their matras)
  - Guru  (गुरु) = 2 matras → long vowel sound (आ, ई, ऊ, ए, ऐ, ओ, औ + their matras)
                              Also: anusvara (ं), visarga (ः) add 1 to make it Guru
  - Zero  (0)   = 0 matras → halant (्) suppresses the vowel, consonant cluster
"""

import unicodedata

# ── Unicode codepoints ────────────────────────────────────────────────────────

HALANT      = '\u094D'   # ्   virama / halant
ANUSVARA    = '\u0902'   # ं
CHANDRABINDU= '\u0901'   # ँ
VISARGA     = '\u0903'   # ः
NUKTA       = '\u093C'   # ़

SWAR_WEIGHT = {
    '\u0905': 1, '\u0906': 2, '\u0907': 1, '\u0908': 2, '\u0909': 1, '\u090A': 2,
    '\u090B': 1, '\u090C': 1, '\u090F': 2, '\u0910': 2, '\u0913': 2, '\u0914': 2,
    '\u0904': 1, '\u0911': 2, '\u0912': 2,
}

MATRA_WEIGHT = {
    '\u093E': 2, '\u093F': 1, '\u0940': 2, '\u0941': 1, '\u0942': 2, '\u0943': 1,
    '\u0944': 2, '\u0945': 1, '\u0946': 1, '\u0947': 2, '\u0948': 2, '\u0949': 2,
    '\u094A': 1, '\u094B': 2, '\u094C': 2, '\u094E': 1, '\u094F': 2,
}

def is_consonant(ch):
    cp = ord(ch)
    return (0x0915 <= cp <= 0x0939) or (0x0958 <= cp <= 0x095F) or cp in (
        0x0900, 0x0978, 0x097B, 0x097C, 0x097E, 0x097F
    )

def is_devanagari(ch):
    cp = ord(ch)
    return 0x0900 <= cp <= 0x097F


# ── Tokeniser ────────────────────────────────────────────────────────────────

def tokenize(word):
    word = unicodedata.normalize('NFC', word)
    tokens = []
    i = 0
    chars = list(word)
    n = len(chars)

    while i < n:
        ch = chars[i]

        # ── Standalone vowel ──────────────────────────────────────────────
        if ch in SWAR_WEIGHT:
            weight = SWAR_WEIGHT[ch]
            unit   = ch
            note   = f"स्वर (swar): {'गुरु/2' if weight == 2 else 'लघु/1'}"
            i += 1
            while i < n and chars[i] in (ANUSVARA, CHANDRABINDU, VISARGA, NUKTA):
                mark = chars[i]
                unit += mark
                if mark == VISARGA:
                    weight = 2
                    note += " + विसर्ग → गुरु"
                elif mark == ANUSVARA:
                    weight = 2
                    note += " + अनुस्वार → गुरु"
                i += 1
            tokens.append({'unit': unit, 'type': 'vowel', 'weight': weight, 'note': note})

        # ── Consonant (start of a consonant cluster) ──────────────────────
        elif is_consonant(ch):
            unit = ch
            i += 1

            if i < n and chars[i] == NUKTA:
                unit += chars[i]
                i += 1

            # Is there a halant? → consonant cluster continues
            if i < n and chars[i] == HALANT:
                unit += chars[i]
                i += 1
                
                # Conjunct Consonant Rule
                if len(tokens) > 0 and tokens[-1]['weight'] == 1:
                    tokens[-1]['weight'] = 2
                    tokens[-1]['note'] = tokens[-1]['note'].replace('लघु/1', 'गुरु/2') + " (संयुक्ताक्षर के कारण)"
                
                tokens.append({'unit': unit, 'type': 'consonant_cluster', 'weight': 0,
                                'note': 'हलन्त (halant) → 0 matras'})
                continue

            # Check for dependent vowel matra
            matra = ''
            matra_weight = 0
            matra_note = ''
            if i < n and chars[i] in MATRA_WEIGHT:
                matra = chars[i]
                matra_weight = MATRA_WEIGHT[matra]
                matra_note = f"मात्रा {'गुरु/2' if matra_weight == 2 else 'लघु/1'}"
                unit += matra
                i += 1

            if not matra:
                weight = 1
                note = f"व्यंजन + अन्तर्निहित अ → लघु/1"
            else:
                weight = matra_weight
                note = f"व्यंजन + {matra_note}"

            while i < n and chars[i] in (ANUSVARA, CHANDRABINDU, VISARGA, NUKTA):
                mark = chars[i]
                unit += mark
                if mark == VISARGA:
                    weight = 2
                    note += " + विसर्ग → गुरु/2"
                elif mark == ANUSVARA:
                    weight = 2
                    note += " + अनुस्वार → गुरु/2"
                elif mark == CHANDRABINDU:
                    note += " + चन्द्रबिन्दु → (weight unchanged)"
                i += 1

            tokens.append({'unit': unit, 'type': 'consonant_unit', 'weight': weight, 'note': note})

        # ── Non-Devanagari / punctuation ─────────────────────────────────
        else:
            tokens.append({'unit': ch, 'type': 'other', 'weight': 0,
                           'note': 'non-Devanagari / punctuation'})
            i += 1

    return tokens


# ── Doha Analyzer ─────────────────────────────────────────────────────────────

def count_matra(word):
    """Returns integer matra count for a single word."""
    tokens = tokenize(word)
    return sum(t['weight'] for t in tokens)

def analyse_doha(doha_text):
    """Analyzes a full doha, breaking it down by lines and charans (half-lines)."""
    # Split the input text into lines, ignoring empty ones
    lines = [line.strip() for line in doha_text.strip().split('\n') if line.strip()]
    total_doha_matras = 0
    
    print(f"\n{'═'*70}")
    print(f"  दोहा विश्लेषण (Full Doha Analysis)")
    print(f"{'═'*70}")
    
    for line_num, line in enumerate(lines, 1):
        # Split by comma to separate the 13-matra and 11-matra phases
        parts = line.split(',')
        line_total = 0
        
        print(f"\n  पंक्ति {line_num} (Line {line_num}): {line}")
        
        for part_num, part in enumerate(parts, 1):
            words = part.split()
            part_matras = 0
            word_breakdown = []
            
            for w in words:
                w_count = count_matra(w)
                part_matras += w_count
                
                # Clean punctuation just for a neater visual display
                clean_w = w.replace('।', '').replace('॥', '').replace('.', '')
                if clean_w: # Avoid printing empty brackets for punctuation marks
                    word_breakdown.append(f"{clean_w}({w_count})")
            
            line_total += part_matras
            total_doha_matras += part_matras
            
            # In a valid doha, Phase 1 should be 13, Phase 2 should be 11
            target = 13 if part_num == 1 else 11
            status = "✓" if part_matras == target else f"✗ (Expected {target})"
            
            print(f"    चरण {part_num} (Phase {part_num}) [{part_matras} मात्राएँ {status}] → {' + '.join(word_breakdown)}")
            
        print(f"    >> पंक्ति {line_num} कुल मात्रा (Line Total) = {line_total}")
        
    print(f"\n{'─'*70}")
    print(f"  दोहे की कुल मात्राएँ (Total Doha Matras) = {total_doha_matras} / 48")
    print(f"{'═'*70}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Test with a structurally perfect classic Doha by Kabir
    sample_doha = """
    मेरा मुझ में कुछ नहीं, जो कुछ है सो तेरा
    तेरा तुझकौं सौंपता, क्या लागै है मेरा
    """
    
    analyse_doha(sample_doha)