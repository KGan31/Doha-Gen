"""
Batch Matra Counter for Doha Dataset
=====================================
Reads dohas from dohas_final_hindi_dataset.csv (column 'Doha'),
counts matras per charan and total, and saves results to a new CSV.
"""

import csv
import unicodedata
from doha_matra_count import count_matra

INPUT_CSV  = "dohas_final_hindi_dataset.csv"
OUTPUT_CSV = "dohas_matra_results.csv"


def count_doha_matras(doha_text):
    """
    Given a doha string (potentially multi-line), return a dict with
    per-charan matra counts and total matra count.

    A doha has 2 lines, each split by ',' into 2 charans.
    Ideal pattern: 13, 11, 13, 11  →  total = 48.
    """
    lines = [l.strip() for l in doha_text.strip().split('\n') if l.strip()]

    charan_counts = []
    total = 0

    for line in lines:
        parts = line.split(',')
        for part in parts:
            words = part.split()
            part_matras = sum(count_matra(w) for w in words)
            charan_counts.append(part_matras)
            total += part_matras

    # Pad to 4 charans if needed (some dohas may be malformed)
    while len(charan_counts) < 4:
        charan_counts.append(0)

    return {
        'charan_1': charan_counts[0],
        'charan_2': charan_counts[1],
        'charan_3': charan_counts[2],
        'charan_4': charan_counts[3],
        'total_matras': total,
    }


def main():
    rows_processed = 0
    results = []

    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doha_text = row['Doha']
            if not doha_text or not doha_text.strip():
                continue

            matras = count_doha_matras(doha_text)
            results.append({
                'Author': row.get('Author', ''),
                'Doha': doha_text.replace('\n', ' | '),
                'Charan_1_Matras': matras['charan_1'],
                'Charan_2_Matras': matras['charan_2'],
                'Charan_3_Matras': matras['charan_3'],
                'Charan_4_Matras': matras['charan_4'],
                'Total_Matras': matras['total_matras'],
                'Is_Valid_48': 'Yes' if matras['total_matras'] == 48 else 'No',
            })
            rows_processed += 1

    # Write output CSV
    fieldnames = [
        'Author', 'Doha',
        'Charan_1_Matras', 'Charan_2_Matras',
        'Charan_3_Matras', 'Charan_4_Matras',
        'Total_Matras', 'Is_Valid_48',
    ]
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    valid_count = sum(1 for r in results if r['Is_Valid_48'] == 'Yes')
    print(f"Processed {rows_processed} dohas.")
    print(f"Valid (48 matras): {valid_count} / {rows_processed}")
    print(f"Results saved to {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
