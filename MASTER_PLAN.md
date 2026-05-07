# GLOWUP AI — MASTER PLAN COMPLETO

## Clone AI-powered di QOVES — One-Person Company

---

## SEZIONE 1: VISIONE E PARAMETRI

### 1.1 Cosa stiamo costruendo
Una piattaforma web che **analizza scientificamente il viso** tramite AI, genera un report estetico dettagliato e un protocollo glow-up personalizzato **totalmente automatico, senza intervento umano**.

### 1.2 Differenziatori vs QOVES

| Fattore | QOVES | GlowUp AI (noi) |
|---------|-------|-----------------|
| Analisi | AI + team umano | **100% AI** |
| Tempi | 28 giorni | **5-15 minuti** |
| Prezzo | $150/anno | **Freemium / low-cost** |
| Visualizzazioni | Proprietarie, realistiche | Morfing matematico + inpainting |
| Fiducia | Volto umano (Shafee Hassan) | Trasparenza "AI-powered" |
| Volume | Limitato dal team | **Illimitato** |

### 1.3 Compromessi accettati
- ❌ Visualizzazioni non al livello QOVES (usiamo morphing + inpainting open-source)
- ❌ Nessuna validazione umana (confidence score + flag automatici)
- ❌ Nessun volto umano (brand trasparente: "AI-powered beauty science")
- ✅ Vantaggi: velocità, prezzo, volume

---

## SEZIONE 2: ARCHITETTURA TECNICA

### 2.1 Stack tecnologico

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14)                  │
│  • TypeScript + TailwindCSS + shadcn/ui                  │
│  • Stripe Elements (pagamenti)                           │
│  • React Query (data fetching)                           │
│  • Hosting: Vercel (free tier → Pro $20/mese)            │
├─────────────────────────────────────────────────────────┤
│                    BACKEND (Python FastAPI)               │
│  • MediaPipe Face Mesh (478 landmark 3D)                 │
│  • OpenCV + scikit-image (analisi pelle)                 │
│  • InsightFace (età, genere, etnia)                      │
│  • DeepSeek API (report generation)                      │
│  • Face morphing (geometrico) + Stable Diffusion Inpainting │
│  • Hosting: Railway / Fly.io / Hetzner VPS               │
├─────────────────────────────────────────────────────────┤
│                    DATA LAYER                             │
│  • PostgreSQL (Supabase free tier → Pro $25/mese)        │
│  • Cloudflare R2 (immagini, $0.015/GB)                   │
│  • Redis (Upstash free tier, task queue)                 │
├─────────────────────────────────────────────────────────┤
│                    AI / LLM LAYER                         │
│  • DeepSeek API (primario, ~$0.005/report)               │
│  • Mistral API (fallback EU, ~$0.01/report)              │
│  • Architettura LLM-agnostic (switch in 10 min)          │
├─────────────────────────────────────────────────────────┤
│                    SOCIAL / ADS                          │
│  • DeepSeek API (generazione contenuti)                  │
│  • Meta Marketing API (pubblicazione ads)                │
│  • ElevenLabs API (voice-over video)                     │
│  • MoviePy (montaggio automatico)                        │
├─────────────────────────────────────────────────────────┤
│                    GDPR COMPLIANCE                        │
│  • Server EU (Hetzner Germania / OVH Francia)            │
│  • Foto MAI inviate a DeepSeek (solo dati numerici)      │
│  • Crittografia at-rest (AES-256) e in-transit (TLS 1.3) │
│  • Data deletion su richiesta (GDPR Art. 17)             │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Flusso dati completo

```
USER                    FRONTEND              BACKEND               AI SERVICES
 │                         │                     │                      │
 │ 1. Signup + Payment     │                     │                      │
 ├────────────────────────►│                     │                      │
 │                         │ 2. Create user      │                      │
 │                         ├────────────────────►│                      │
 │                         │                     │                      │
 │ 3. Upload 6 foto        │                     │                      │
 ├────────────────────────►│                     │                      │
 │                         │ 4. Upload to R2     │                      │
 │                         ├────────────────────►│                      │
 │                         │                     │ 5. Queue analysis    │
 │                         │                     │──┐                   │
 │                         │                     │  │ Worker            │
 │                         │                     │◄─┘                   │
 │                         │                     │                      │
 │                         │                     │ 6. MediaPipe         │
 │                         │                     ├─────────────────────►│
 │                         │                     │◄─────────────────────┤
 │                         │                     │   478 landmark 3D    │
 │                         │                     │                      │
 │                         │                     │ 7. Skin Analysis     │
 │                         │                     │   (OpenCV locale)    │
 │                         │                     │                      │
 │                         │                     │ 8. InsightFace       │
 │                         │                     │   (età/genere/etnia) │
 │                         │                     │                      │
 │                         │                     │ 9. Calcoli metriche  │
 │                         │                     │   (geometria Python) │
 │                         │                     │                      │
 │                         │                     │ 10. Dati numerici →  │
 │                         │                     ├─────────────────────►│
 │                         │                     │         DeepSeek API │
 │                         │                     │◄─────────────────────┤
 │                         │                     │    Report generato   │
 │                         │                     │                      │
 │                         │                     │ 11. Visualizzazione  │
 │                         │                     │    (morphing locale) │
 │                         │                     │                      │
 │                         │ 12. Store report    │                      │
 │                         │◄────────────────────┤                      │
 │                         │                     │                      │
 │ 13. Report disponibile  │                     │                      │
 │◄────────────────────────┤                     │                      │
 │                         │                     │                      │
 │ 14. Chat con team AI    │                     │                      │
 │◄───────────────────────►│◄───────────────────►│                      │
 │                         │                     │     (DeepSeek API)   │
```

---

## SEZIONE 3: PIANO DI SVILUPPO — 10 GIORNI

### GIORNO 1 — Fondamenta
- [x] Struttura progetto
- [ ] Configurazione ambiente (Python venv, Node, API keys)
- [ ] .env, .gitignore, requirements.txt, package.json
- [ ] Docker Compose per sviluppo locale
- [ ] Schema database PostgreSQL (tabelle users, analyses, reports)

### GIORNO 2 — Backend Core
- [ ] FastAPI main app + CORS + health check
- [ ] MediaPipe Face Mesh integration
- [ ] Servizio landmark extraction (6 foto → 478 punti x foto)
- [ ] Calcoli di simmetria facciale
- [ ] Calcoli proporzioni (terzi facciali, rapporti)

### GIORNO 3 — Analisi Pelle + Attributi
- [ ] Skin analysis (GLCM texture, clustering colore, rughe edge detection)
- [ ] InsightFace integration (età, genere, etnia percepita)
- [ ] Aggregazione metriche in JSON strutturato
- [ ] Test unitari su tutte le metriche

### GIORNO 4 — LLM Provider + Report Generation
- [ ] LLM Provider agnostico (DeepSeek / Mistral / OpenAI)
- [ ] Template prompt per report estetico
- [ ] Sistema di raccomandazioni (database categorie)
- [ ] Generazione report in Markdown + JSON

### GIORNO 5 — Visualizzazioni Before/After
- [ ] Face morphing geometrico (sposta landmark → warp immagine)
- [ ] Inpainting localizzato (pelle, rughe) con Stable Diffusion
- [ ] Overlay confronto prima/dopo
- [ ] Export visualizzazioni

### GIORNO 6 — Frontend (Next.js)
- [ ] Setup Next.js + Tailwind + shadcn/ui
- [ ] Landing page (hero, features, pricing, FAQ)
- [ ] Signup/Login (Supabase Auth)
- [ ] Stripe Checkout integration

### GIORNO 7 — Frontend App
- [ ] Upload foto (6 angolazioni guidate)
- [ ] Dashboard utente con analisi in corso
- [ ] Report viewer interattivo
- [ ] Chat AI (assistente estetico)

### GIORNO 8 — Pipeline Completa
- [ ] Worker asincrono (task queue)
- [ ] Hook end-to-end: upload → processing → report → notifica email
- [ ] Email notification (Resend API)
- [ ] Error handling + retry queue

### GIORNO 9 — Social Media AI
- [ ] Content generator per TikTok/Reels (DeepSeek API)
- [ ] Script automation (script → voice-over ElevenLabs → MoviePy montaggio)
- [ ] Meta Marketing API integration (pubblicazione ads programmatica)
- [ ] Scheduler contenuti

### GIORNO 10 — Deploy + GDPR + Monitoring
- [ ] Deploy frontend su Vercel
- [ ] Deploy backend su Hetzner VPS
- [ ] GDPR compliance (cancellazione dati, cookie consent, privacy policy)
- [ ] Monitoring (Sentry + UptimeRobot)
- [ ] Test end-to-end

---

## SEZIONE 4: DEEPSEEK SKILLS

### 4.1 Cosa sono le skill
Moduli specializzati di DeepSeek per task ripetitivi. Si configurano come file `.md` nella cartella `skills/` con istruzioni di sistema specifiche.

### 4.2 Skill 1: `facial-pipeline-builder`
**Scopo:** Assistere nella scrittura e debug del codice Python per l'analisi facciale.
**File:** `skills/facial-pipeline-builder.md`

### 4.3 Skill 2: `report-generator`
**Scopo:** Generare e migliorare i prompt LLM per i report estetici.
**File:** `skills/report-generator.md`

### 4.4 Skill 3: `deploy-assistant`
**Scopo:** Assistere nel deploy su VPS/serverless e configurazione infrastruttura.
**File:** `skills/deploy-assistant.md`

---

## SEZIONE 5: STIMA COSTI MENSILI

| Servizio | Free Tier | Produzione (1k utenti) | Produzione (10k utenti) |
|----------|-----------|------------------------|--------------------------|
| **Vercel** | $0 | $0-20 | $20-100 |
| **Hetzner VPS** | - | €6 (CX22) | €25 (CPX31) |
| **Supabase** | $0 | $0-25 | $25-75 |
| **Cloudflare R2** | $0 (10GB) | ~$2 | ~$20 |
| **DeepSeek API** | $0 per dev | ~$5 (1000 report) | ~$50 |
| **Stripe** | 2.9% + 0.30 | ~3% revenue | ~3% revenue |
| **ElevenLabs** | $0 (10 min) | $5 | $22 |
| **Upstash Redis** | $0 | $0 | $0-10 |
| **Sentry** | $0 | $0 | $0-26 |
| **Dominio** | - | $10/anno | $10/anno |
| **TOTALE** | **~$0** | **~$40/mese** | **~$220/mese** |

---

## SEZIONE 6: METRICHE DI SUCCESSO

- Tempo analisi: < 15 minuti dall'upload
- Qualità landmark: accuratezza > 95% su dataset standard
- Soddisfazione utente: NPS > 30
- Costo per report: < $0.03
- Uptime: > 99.5%
- GDPR Compliance: 100% (nessun dato sensibile a server extra-EU)
