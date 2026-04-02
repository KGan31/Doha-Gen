# Doha-Gen: Constrained Theme-Based Hindi Doha Generation

**IIIT Hyderabad | Introduction to NLP (Sem 2)**

> Automatic generation of metrically valid, theme-conditioned Hindi Dohas in Devanagari script using fine-tuned Indic language models.

---

## Overview

A **Doha** is a classical two-line Hindi/Braj Bhasha poetic form with a strict syllabic (matra) structure: each line follows a **13–11** matra pattern, giving a total of **13–11–13–11** matras across the two lines. Prominent historical poets of this form include Kabir, Rahim, and Raslin.

**Doha-Gen** addresses the task of generating a new, prosodically valid doha given:
- A **theme** (विषय) — a single broad Hindi word, e.g., *शृंगार* (love), *भक्ति* (devotion), *नीति* (wisdom)
- A **context** (संदर्भ) — a short 2–3 word prompt in colloquial Hindi

The system fine-tunes `ai4bharat/IndicBART` on a curated dataset of ~7,000 annotated dohas, with constrained beam-search decoding that enforces the 13–11–13–11 matra constraint.

---
### Link to Models and Dataset

- Poems Dataset: https://huggingface.co/datasets/KGan31/Doha-Gen-Dataset  
- Poems Complete Merged Dataset: https://www.kaggle.com/datasets/kgan31/complete-kavita-dataset/data
- Stage-1 Trained byT5 model: https://huggingface.co/KGan31/Doha-Gen/tree/main

---

## Authors

| Name | Roll No. |
|---|---|
| Divyanshu Jain | 2025201059 |
| Kavan Gandhi | 2025201078 |
| Nikhil Patidar | 2025201081 |
| Abhinav Jha | 2024201008 |

---

## Repository Structure

```
Doha-Gen/
├── dataset/
│   ├── dohas_final_hindi_dataset.csv       # ~7,000 annotated dohas (Author, Doha, Theme, Meaning, Context)
│   ├── dohas_nlp_ready_simple_lang.csv     # NLP-ready version with short 2–3 word context summaries
│   └── braj_poems_complete.csv             # ~40,000 Braj/Hindi poems for domain adaptation
│
├── scraping/
│   ├── scrapper.py                         # KavitaKosh doha scraper
│   ├── braj_scraper_complete.py            # KavitaKosh Braj Bhasha poetry scraper
│   ├── process_dohas_gemini.py             # Stage 1 annotation: Theme + Meaning via Gemini API
│   └── mssg.py                             # Stage 2 annotation: short Core_Message via Gemini API
│
├── baseline/
│   ├── n-gram.ipynb                        # N-gram LM baseline (char/word, Laplace & Kneser-Ney)
│   ├── lstm-model.ipynb                    # Character-level LSTM baseline
│   ├── gpt-2.ipynb                         # Zero-shot GPT-2 Hindi baseline
│   ├── indicbart-finetuning.ipynb          # Main model: IndicBART fine-tuning
│   └── similarity-checker.ipynb           # Dataset quality analysis via LaBSE embeddings
│
├── dataset_visualization/
│   ├── visual.html                         # Interactive dataset visualizations
│   ├── v2.html
│   └── v3.html
│
├── docs/                                   # Project proposals
└── Report/
    ├── main.tex                            # ACL-format research paper (LaTeX)
    └── custom.bib                          # Bibliography
```

---

## Dataset

The dataset was built through a multi-stage pipeline sourcing from [KavitaKosh](https://kavitakosh.org), a large open Hindi literary repository.

### Doha Corpus (`dohas_final_hindi_dataset.csv` / `dohas_nlp_ready_simple_lang.csv`)

| Column | Description |
|--------|-------------|
| `Author` | Historical poet (Kabir, Rahim, Raslin, etc.) |
| `Doha` | Braj Bhasha doha text in Devanagari script |
| `Theme` | Single Hindi word from a controlled vocabulary of ~70 categories |
| `Meaning` | 20–40 word Hindi explanation of the doha |
| `Context` | Ultra-short 2–3 word colloquial Hindi summary (user query simulation) |

**Theme vocabulary** spans categories such as:
- Love/Romance: शृंगार, प्रेम, विरह, सौंदर्य
- Devotion: भक्ति, ईश्वर, कृष्ण
- Wisdom/Ethics: नीति, ज्ञान, दर्शन
- Emotions: करुण, वीर, हास्य
- Nature: प्रकृति, ऋतु

### Hindi Poetry Corpus (`braj_poems_complete.csv`)

~40,000 poems (ghazals, nazms, free-verse) used for Stage 1 domain adaptation.

---

## Methodology

The system uses a **two-stage training + constrained inference** pipeline.

### Stage 1 — Domain Adaptation

IndicBART is further pre-trained on ~40,000 Hindi poems using a **denoising objective** (30% span masking + line permutation → reconstruct original):

$$\mathcal{L}_{\text{denoise}} = -\sum_t \log P_\theta(w_t \mid w_{<t},\ \text{Enc}(\tilde{p}))$$

| Hyperparameter | Value |
|---|---|
| Learning rate | 5e-5 |
| Batch size | 32 (effective) |
| Epochs | 3–5 |
| Precision | FP16 |

### Stage 2 — Supervised Fine-tuning

Fine-tuned on (Theme + Context → Doha) pairs with **stochastic input augmentation** — each training sample randomly uses:
- Context only (1/3 probability)
- Meaning only (1/3 probability)
- Context + Meaning (1/3 probability)

**Input format:**
```
vishay: <theme> | sandarbh: <context> <2hi>
```

**Loss:** Cross-entropy with label smoothing (ε = 0.1)

| Hyperparameter | Value |
|---|---|
| Learning rate | 5e-5 |
| Batch size | 32 (effective) |
| Max epochs | 15 |
| Early stopping patience | 4 |

### Constrained Inference

1. Generate **k = 5** candidates via beam search (`no_repeat_ngram_size=3`, forced BOS `<2hi>`)
2. Apply a rule-based **Matra Validator** that checks the 13–11–13–11 pattern
3. Select the best candidate within ±1 matra tolerance

---

## Baselines

| Model | Approach |
|-------|----------|
| **N-gram LM** | Char/word-level N-gram with Laplace & Kneser-Ney smoothing |
| **Character-level LSTM** | 2-layer LSTM (256 hidden units, dropout 0.5, embedding 64) |
| **GPT-2 Hindi (zero-shot)** | `surajp/gpt2-hindi` with 3 prompt templates |
| **TF-IDF Retrieval** | Cosine similarity over TF-IDF index |
| **IndicBART (fine-tuned)** | Primary system — seq2seq, 244M parameters |

---

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **MAS** (Matra Accuracy Score) | $\|m_1 - 13\| + \|m_2 - 11\|$ per line; lower is better |
| **RCS** (Rhyme Consistency Score) | Phonetic similarity of final words across lines; higher is better |
| **NS** (Novelty Score) | $1 - \text{Self-BLEU}$; measures output diversity |
| **BLEU-1/2/4** | Character-level n-gram overlap with reference dohas |

---

## Models & Libraries

| Component | Tool / Model |
|-----------|-------------|
| Primary model | `ai4bharat/IndicBART` (mBART-based, 244M params, 11 Indian languages) |
| GPT-2 baseline | `surajp/gpt2-hindi` |
| Semantic similarity | `sentence-transformers/LaBSE` |
| Dataset annotation | Google Gemini 2.5 Flash API |
| Training framework | PyTorch + HuggingFace Transformers |
| Hindi tokenization | `indic-nlp-library`, `sentencepiece` |
| Evaluation | `nltk` (BLEU), `sacrebleu` |
| Web scraping | `requests`, `BeautifulSoup` |

---

## Setup

### Requirements

```bash
pip install torch transformers datasets sentencepiece sacrebleu nltk
pip install sentence-transformers indic-nlp-library
pip install requests beautifulsoup4 pandas google-generativeai
```

### Running the Notebooks

All notebooks in `baseline/` are designed to run on **Kaggle** (GPU-enabled environment). Update dataset paths if running locally:

```python
# Kaggle path (default in notebooks)
"/kaggle/input/datasets/kgan31/..."

# Replace with your local path
"./dataset/..."
```

### Data Collection (Optional)

To re-scrape and re-annotate the dataset:

```bash
# 1. Scrape dohas from KavitaKosh
python scraping/scrapper.py

# 2. Scrape Braj Bhasha poetry corpus
python scraping/braj_scraper_complete.py

# 3. Annotate with Theme + Meaning (requires Gemini API key)
python scraping/process_dohas_gemini.py

# 4. Generate short context summaries
python scraping/mssg.py
```

> **Note:** Set your Gemini API key as an environment variable `GEMINI_API_KEY` before running annotation scripts.

---

## Related Work

- **Chandomitra** (Jagadeeshan, 2025) — English→Sanskrit Anustubh meter generation
- **The Mechanical Bard** (Agnew et al., 2023) — GPT-2 constrained Shakespearean sonnet generation
- **IndicBART** (Dabre et al., 2022) — Multilingual seq2seq model for Indian languages
- **mBART** (Liu et al., 2020) — Denoising pre-training formulation

---

## License

This project was developed for academic purposes as part of the Introduction to NLP course at IIIT Hyderabad. The doha texts are sourced from [KavitaKosh](https://kavitakosh.org).
