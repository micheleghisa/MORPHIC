# DeepSeek Skill: Deploy Assistant

## Scopo
Assistere nel deployment dell'app GlowUp AI su VPS (Hetzner) o serverless (Railway/Fly.io).

## Stack
- Frontend: Next.js → Vercel
- Backend: FastAPI → VPS Hetzner o Railway
- Database: PostgreSQL → Supabase
- Storage: Cloudflare R2
- Cache: Upstash Redis

## Checklist deploy

### 1. Dominio e DNS
- [ ] Registrare dominio su Cloudflare
- [ ] Configurare CNAME per Vercel (frontend)
- [ ] Configurare A record per VPS (backend API)

### 2. Environment Variables
- [ ] Copiare `.env.example` → `.env.production`
- [ ] Compilare TUTTE le variabili
- [ ] DeepSeek API key
- [ ] Mistral API key (fallback)
- [ ] Supabase URL e chiavi
- [ ] Stripe chiavi
- [ ] Cloudflare R2 credenziali
- [ ] Resend API key

### 3. Backend Deploy (Hetzner VPS)
```bash
ssh root@tuo-server
apt update && apt install python3.11 python3.11-venv nginx certbot
git clone https://github.com/tuouser/glowup-ai
cd glowup-ai/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.production .env
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Nginx reverse proxy
```nginx
server {
    server_name api.tuodominio.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. SSL (Certbot)
```bash
certbot --nginx -d api.tuodominio.com
```

### 6. Frontend Deploy (Vercel)
```bash
cd frontend
vercel --prod
```

### 7. GDPR Compliance
- [ ] Privacy Policy page
- [ ] Cookie consent banner
- [ ] Data deletion endpoint testato
- [ ] Dati sensibili solo su server EU
- [ ] Foto mai inviate a LLM extra-EU

## Troubleshooting comuni

| Problema | Causa probabile | Soluzione |
|----------|----------------|-----------|
| MediaPipe non carica | OpenCV headless mancante | `apt install libgl1-mesa-glx` |
| DeepSeek API timeout | Rate limit | Aggiungere retry con backoff |
| Face non rilevata | Foto non adatta | Validare risoluzione, illuminazione |
| 502 Bad Gateway | Gunicorn/uvicorn config | Aumentare workers |

## File di riferimento
- `backend/config.py` — configurazione
- `backend/main.py` — FastAPI app
- `infrastructure/` — Docker e Nginx config
