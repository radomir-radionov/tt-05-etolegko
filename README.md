# Keitaro Wrapper (test_radionov_)

Обёртка над Keitaro Admin API: создатель кампаний (geo → Google + offer stream) и редактор офферов в одном offer-потоке со статистикой из Keitaro.

## Стек

- **Backend:** FastAPI, SQLAlchemy 2, Alembic, httpx
- **Frontend:** React, TypeScript, Vite, React Router
- **Tests:** pytest + respx, Vitest + Testing Library

## Prerequisites

- Python 3.9+
- Node.js 20+
- Keitaro Admin API key (`tlgk.host` → Profile → API keys)

## Configuration

```bash
cp .env.example .env
# заполните KEITARO_API_KEY (см. docs/keitaro-notes.md)
```

Основные переменные:

| Variable | Default | Description |
|----------|---------|-------------|
| `KEITARO_BASE_URL` | `https://tlgk.host/admin_api/v1` | Admin API |
| `KEITARO_DOMAIN_ID` | `1813` | `kylovoa.com` on test stand |
| `KEITARO_GROUP_ID` | `10332` | `FORTESTS` |
| `KEITARO_TRAFFIC_SOURCE_ID` | `836` | `FORTESTS` |
| `CAMPAIGN_NAME_PREFIX` | `test_radionov_` | обязательный префикс имён |

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Migrations

```bash
cd backend
alembic upgrade head      # apply
alembic downgrade -1      # rollback one step
```

### Backend tests

```bash
cd backend
pytest -m "not keitaro_live"
```

Live-интеграция (опционально, с реальным Keitaro):

```bash
export KEITARO_API_KEY=...
pytest -m keitaro_live tests/integration/test_keitaro_live.py
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Dev-сервер проксирует `/api` на `http://127.0.0.1:8000`.

### Frontend tests

```bash
cd frontend
npm test
```

## Docker (optional)

```bash
docker compose up --build
```

По умолчанию SQLite в volume backend; для Postgres см. `docker-compose.yml`.

## API (local)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/campaigns` | `{ name, geo, offer_id }` |
| GET | `/api/offers?q=` | Поиск офферов |
| GET | `/api/campaigns/{id}` | Состояние + stats |
| POST | `/api/campaigns/{id}/offers` | Добавить оффер |
| DELETE | `/api/campaigns/{id}/offers/{offer_id}` | Удалить оффер |

## Acceptance checklist

- [ ] Имя кампании `test_radionov_*` в Keitaro
- [ ] Поток 1: страны из geo → `https://www.google.com/`
- [ ] Поток 2: выбранный offer
- [ ] Редактор add/remove синхронен с Keitaro
- [ ] Статистика clicks / unique / bots из report API

Подробности API: [docs/keitaro-notes.md](docs/keitaro-notes.md)