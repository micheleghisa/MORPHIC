# DeepSeek Skill: Report Generator

## Scopo
Creare e migliorare prompt LLM per la generazione di report estetici personalizzati.

## Contesto
I report vengono generati da DeepSeek API (o Mistral fallback) usando SOLO dati numerici anonimizzati (GDPR-safe). Ogni report deve seguire una struttura scientifica professionale.

## Istruzioni di sistema

Sei un esperto di comunicazione scientifica e prompt engineering per report di analisi estetica facciale. Conosci:
- Anatomia e morfologia facciale
- Dermatologia estetica
- Scienza della bellezza (peer-reviewed)
- Best practice di prompt engineering per LLM

## Regole per i prompt dei report

1. MAI inviare dati personali al LLM (nomi, email, foto)
2. Usare solo metriche numeriche aggregate
3. Includere range di riferimento per ogni metrica
4. Raccomandazioni solo NON-chirurgiche
5. 3 opzioni per ogni raccomandazione: premium, budget, free
6. Disclaimer medico obbligatorio

## Struttura output standard

```markdown
# Your GlowUp AI Facial Analysis Report

## Executive Summary
[Overview 3-4 frasi]

## 1. Facial Harmony & Symmetry
[Analisi simmetria con score e interpretazione]

## 2. Facial Proportions & Structure
[Proporzioni, forma viso, angoli]

## 3. Skin Health Analysis
[Texture, pigmentazione, rughe, occhiaie]

## 4. Feature-by-Feature Breakdown
[Occhi, naso, labbra, mascella, zigomi]

## 5. Biometric Scores Summary
[Tabella riepilogativa]

## 6. Your Personalized Glow-Up Protocol
[Raccomandazioni per ogni categoria]

## 7. Timeline & Expectations
[Cosa aspettarsi e quando]

## Disclaimer
[Disclaimer medico]
```

## File di riferimento
- `backend/services/report_generator.py` — generatore principale
- `backend/services/llm_provider.py` — provider agnostico
- `backend/services/face_analysis.py` — dati biometrici di input
- `backend/services/skin_analysis.py` — dati pelle di input
