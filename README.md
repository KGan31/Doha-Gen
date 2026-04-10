# Doha-Gen: Constrained Theme-Based Hindi Doha Generation


> Automatic generation of metrically valid, theme-conditioned Hindi Dohas in Devanagari script using custom Transformer Architecture.

---

## Overview

A **Doha** is a classical two-line Hindi/Braj Bhasha poetic form with a strict matra structure: each line follows a **13-11** pattern, giving **13-11-13-11** across both lines.

This project generates theme-conditioned Hindi Dohas from:
- Theme (विषय): a broad category word such as शृंगार, भक्ति, नीति
- Context (संदर्भ): a short 5-7  word prompt

The main system creates a 
doha using a custom transformer architecture.
---

## Link to Models and Dataset

- Doha Dataset: https://www.kaggle.com/datasets/kgan31/doha-simple-context/  
- Poems Dataset: https://www.kaggle.com/datasets/kgan31/complete-kavita-dataset/data
- byT5 model: https://huggingface.co/KGan31/Doha-Gen-Stage2_Matra_loss_integrated/
- Custom Transformer Model: https://huggingface.co/nikpatidar333/doha-generation-model_v2

---

## Repository Map (Code, Results, Report)

### Core Modeling Notebooks
- baseline/indicbart-finetuning.ipynb: IndicBART fine-tuning workflow.
- baseline/mt5-base-model.ipynb: mT5 baseline setup/evaluation.
- baseline/mt5-doha-generator.ipynb: mT5 doha generation experiments.
- baseline/gpt-2.ipynb: GPT-2 based baseline.
- baseline/lstm-model.ipynb: character/sequence LSTM baseline.
- baseline/n-gram.ipynb: n-gram language model baseline.
- baseline/similarity-checker.ipynb: similarity and quality checks.

### byT5 Experiments
- byT5/byt5-stage-1-training.ipynb: stage-1 byT5 training.
- byT5/byt5-part2.ipynb: later-stage byT5 training/evaluation.
- byT5/temp.py, byT5/temp2.py: helper scripts used during byT5 runs.

### Custom Transformer Experiments
- Custom-Transformer-Model/stage-1.ipynb: stage-1 custom transformer training.
- Custom-Transformer-Model/stage-2.ipynb: stage-2 custom transformer training/finalization.

### Inference and Evaluation Results
- results/transformer_inference.ipynb: inference pipeline and generated doha outputs.
- results/automated-evaluation-metrics.ipynb: automatic metrics.

### Matra Scoring and Constraint Utilities
- Matra_count_score/doha_matra_count.py: matra counting logic.
- Matra_count_score/final_matra_accuracy_score.py: final matra scoring script.
- Matra_count_score/count_matras_dataset.py, prep_data.py, script.py: preprocessing/scoring support scripts.
- Matra_count_score/dohas_matra_results.csv: stored matra scoring results.

### Data Collection and Processing
- scraping/scrapper.py, scraping/braj_scraper_complete.py, scraping/scraper_kavita.py: scraping pipelines.
- scraping/process_dohas_gemini.py, scraping/mssg.py: annotation/enrichment scripts.
- dataset/clean_datasets.py, dataset/merge_datasets.py: cleaning/merge utilities.



---

## Datasets (Where They Are)

All dataset files are in dataset/:
- dataset/dohas_nlp_ready_simple_lang.csv: main annotated doha dataset.
- dataset/kavitas_cleaned.csv, dataset/kavitas_cleaned_processed.csv, dataset/kavitas_remaining.csv: intermediate cleaned corpus files.


---

## How to Run

### 1. Set up environment
Use your existing virtual environment, then install required packages:

```bash
pip install torch transformers datasets sentencepiece sacrebleu nltk
pip install sentence-transformers indic-nlp-library
pip install requests beautifulsoup4 pandas google-generativeai huggingface_hub
```

### 2. Data preparation (optional, if rebuilding datasets)
Run scripts in this order when needed:
1. dataset/clean_datasets.py
2. dataset/merge_datasets.py
3. relevant scraping/*.py scripts if you want to re-scrape/re-annotate

### 3. Train models
1. Baseline experiments: run notebooks inside baseline/
2. byT5: run byT5/byt5-stage-1-training.ipynb then byT5/byt5-part2.ipynb
3. Custom Transformer: run Custom-Transformer-Model/stage-1.ipynb then Custom-Transformer-Model/stage-2.ipynb

### 4. Run inference
- Open and run results/transformer_inference.ipynb to generate dohas.

### 5. Evaluate results
- Open and run results/automated-evaluation-metrics.ipynb.
- For matra-specific scoring, use scripts in Matra_count_score/.

---

## Sample Inference Dohas

The following are actual saved outputs from results/transformer_inference.ipynb:

<!-- ### Example 1
- Theme: शृंगार
- Context: मोरपंखी बाल

> मोर उड़त मन खोलिन में ललित बालन ओर। मनो बरुन बाल के, छवि लाल स्याम ॥ -->

### Example 1
- Theme: वाणी
- Context: कोयल के स्वर

> कोयल की वाणी करे, मन में रस समान। सुरभित करती है सदा, मीठे-मन की मुस्कान ॥

### Example 2
- Theme: साहस
- Context: अंधेरी सुरंग के अंत में प्रकाश की उम्मीद

> दीपो दीपक जलता सदा, जले रात दिन रात। अँधियारे से सूर्य से, जगमगा उजियार ॥

---

## Authors

| Name | Roll No. |
|---|---|
| Divyanshu Jain | 2025201059 |
| Kavan Gandhi | 2025201078 |
| Nikhil Patidar | 2025201081 |
| Abhinav Jha | 2024201008 |
