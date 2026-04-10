import unicodedata

# Unicode Constants
HALANT       = '\u094D'
ANUSVARA     = '\u0902'
CHANDRABINDU = '\u0901'
VISARGA      = '\u0903'
NUKTA        = '\u093C'

SWAR_WEIGHT = {
    '\u0905': 1, '\u0906': 2, '\u0907': 1, '\u0908': 2, '\u0909': 1, '\u090A': 2,
    '\u090B': 1, '\u090C': 1, '\u090F': 2, '\u0910': 2, '\u0913': 2, '\u0914': 2,
}
MATRA_WEIGHT = {
    '\u093E': 2, '\u093F': 1, '\u0940': 2, '\u0941': 1, '\u0942': 2, '\u0943': 1,
    '\u0947': 2, '\u0948': 2, '\u094B': 2, '\u094C': 2,
}

def is_consonant(ch):
    cp = ord(ch)
    return (0x0915 <= cp <= 0x0939) or (0x0958 <= cp <= 0x095F)

def tokenize(word):
    word = unicodedata.normalize('NFC', word)
    tokens = []
    chars = list(word)
    i = 0
    n = len(chars)

    while i < n:
        ch = chars[i]

        # 1. Handle Vowels
        if ch in SWAR_WEIGHT:
            weight = SWAR_WEIGHT[ch]
            unit = ch
            i += 1
            while i < n and chars[i] in (ANUSVARA, VISARGA):
                weight = 2 # Anusvara/Visarga makes it Guru
                unit += chars[i]
                i += 1
            tokens.append({'unit': unit, 'weight': weight})

        # 2. Handle Consonants
        elif is_consonant(ch):
            unit = ch
            i += 1
            if i < n and chars[i] == NUKTA:
                unit += chars[i]; i += 1

            # CONJUNCT RULE: Halant makes the PREVIOUS syllable Guru
            if i < n and chars[i] == HALANT:
                unit += chars[i]; i += 1
                if tokens:
                    tokens[-1]['weight'] = 2
                tokens.append({'unit': unit, 'weight': 0})
            else:
                # Check for Matras
                matra_w = 1 # Default inherent 'a'
                if i < n and chars[i] in MATRA_WEIGHT:
                    matra_w = MATRA_WEIGHT[chars[i]]
                    unit += chars[i]; i += 1

                # Check for Anusvara/Visarga on consonant
                while i < n and chars[i] in (ANUSVARA, VISARGA, CHANDRABINDU):
                    if chars[i] in (ANUSVARA, VISARGA): matra_w = 2
                    unit += chars[i]; i += 1
                tokens.append({'unit': unit, 'weight': matra_w})
        else:
            i += 1 # Ignore non-devanagari
    return tokens

def count_matra(text):
    return sum(t['weight'] for t in tokenize(text))

def parse_single_line(line, has_comma=None):
    """
    Parse a single line and return its charan matras.
    
    Args:
        line: A single line of text
        has_comma: If None, auto-detect; if True/False, use that mode
    
    Returns:
        List of matra counts for charans in this line
    """
    line = line.strip()
    if not line:
        return []
    
    # Auto-detect comma in this line if not specified
    if has_comma is None:
        has_comma = ',' in line
    
    charan_matras = []
    
    if has_comma:
        # Parse WITH comma delimiters
        parts = [p.strip() for p in line.split(',') if p.strip()]
        for part in parts:
            charan_matras.append(count_matra(part))
    else:
        # Parse WITHOUT commas: word-by-word accumulation
        words = line.split()  # Split by whitespace
        current_charan_matra = 0
        
        for word in words:
            word_matra = count_matra(word)
            current_charan_matra += word_matra
            
            # If we've reached or exceeded 13 matras, finalize this charan
            if current_charan_matra >= 13:
                charan_matras.append(current_charan_matra)
                current_charan_matra = 0
        
        # Append any remaining matras as a charan (if not zero)
        if current_charan_matra > 0:
            charan_matras.append(current_charan_matra)
    
    return charan_matras

def get_charan_matras(doha_text):
    """
    Parse doha LINE-BY-LINE, checking each line independently for comma presence.
    
    Args:
        doha_text: The full doha string
    
    Returns:
        List of matra counts for all charans across all lines
    """
    text = doha_text.replace('॥', '।').strip()
    lines = [l.strip() for l in text.split('।') if l.strip()]
    
    charan_matras = []
    
    for line in lines:
        # Each line is checked independently for comma presence
        line_matras = parse_single_line(line, has_comma=None)  # None = auto-detect per line
        charan_matras.extend(line_matras)
    
    return charan_matras

def has_comma_in_line(line):
    """
    Check if a single line has comma delimiter.
    
    Returns:
        True if comma found in this line, False otherwise
    """
    return ',' in line.strip()

def compute_mas(cm):
    """Compute Mean Absolute Squared error from ideal charan structure"""
    ideal = [13, 11, 13, 11]
    # Padding with 0 if charans are missing
    cm4 = (cm + [0]*4)[:4]
    return sum(abs(cm4[i] - ideal[i]) for i in range(4))

# --- Execution ---
doha_list = [
    "कोयल की वाणी करे, मन में रस समान। सुरभित करती है सदा , मीठे-मन की मुस्कान ॥",
    "मिट्टी का पानी नहीं, तरु-से शीतल नीर। धरती पर जाती छाती पड़ीं, माटी की धार ॥",
    "राज करे सो चाहिए राज्य बिना न लाज। तजि तरवार भगति कर तो भbramण भयो समाज ॥",  
]

print(f"{'#':<4} {'m1':>4} {'m2':>4} {'m3':>4} {'m4':>4} {'Total':>6} {'MAS':>5} {'Valid':>6}")
print("=" * 60)

results = []
for i, doha in enumerate(doha_list, 1):
    # Each line is checked independently for comma
    cm = get_charan_matras(doha)
    mas = compute_mas(cm)
    cm4 = (cm + [0]*4)[:4]
    total = sum(cm4)
    results.append({'mas': mas, 'total': total})

    valid = "✓" if mas == 0 else "✗"
    print(f"{i:<4} {cm4[0]:>4} {cm4[1]:>4} {cm4[2]:>4} {cm4[3]:>4} {total:>6} {mas:>5} {valid:>6}")

print("=" * 60)
avg_mas = sum(r['mas'] for r in results) / len(results) if results else 0
print(f"Average MAS: {avg_mas:.2f}")

# --- Debug: Show word-by-word breakdown with line-wise comma detection ---
print("\n" + "="*70)
print("DEBUG: Line-by-line parsing (comma detection per line)")
print("="*70)
doha_test = doha_list[2]
text = doha_test.replace('॥', '।').strip()
lines = [l.strip() for l in text.split('।') if l.strip()]

for line_idx, line in enumerate(lines, 1):
    comma_present = has_comma_in_line(line)
    parse_mode = "WITH commas" if comma_present else "Word-by-word accumulation"
    print(f"\nLine {line_idx}: {line}")
    print(f"  Parse Mode: {parse_mode}")
    
    line_matras = parse_single_line(line, has_comma=None)
    print(f"  Charans: {line_matras}")
    
    if not comma_present:
        # Show detailed word breakdown for non-comma lines
        words = line.split()
        current_charan = 0
        charan_num = 1
        
        for word in words:
            word_matra = count_matra(word)
            current_charan += word_matra
            status = ""
            
            if current_charan >= 13:
                status = f" → CHARAN {charan_num} COMPLETE (total: {current_charan})"
                charan_num += 1
                current_charan = 0
            
            print(f"    '{word}' → {word_matra} matra | Running total: {current_charan}{status}")
        
        if current_charan > 0:
            print(f"    *** Remaining: {current_charan} matra ***")
