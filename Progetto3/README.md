# Progetto 3 — SHIFT-X Lambda Functions

Pipeline serverless Node.js per la generazione di playlist TEDx personalizzate.

## Struttura

```
Progetto3/
├── GetMacroCategory/     # λ1 — job → macrocategoria (Bedrock)
├── GetRelevantTags/      # λ2 — job + categoria → tag rilevanti (Bedrock + MongoDB)
├── GetTalksAndPlaylist/  # λ3 — categoria + tag → playlist top 10 (MongoDB + scoring)
├── GetWatchNext/         # λ  — talk id → related_videos (MongoDB)
└── CareerPathMaster/     # λ Master — orchestratore (API Gateway pubblico)
```

## Endpoint API Gateway

| Endpoint | Lambda | Descrizione |
|---|---|---|
| `POST /career-path` | CareerPathMaster | Pipeline completa: job → playlist |
| `POST /watch-next` | GetWatchNext | Video correlati a un talk |

## Variabili d'Ambiente

### Lambda con MongoDB (GetMacroCategory, GetRelevantTags, GetTalksAndPlaylist, GetWatchNext)
| Variabile | Descrizione |
|---|---|
| `DB` | URI MongoDB Atlas |

### Lambda Master (CareerPathMaster)
| Variabile | Descrizione |
|---|---|
| `LAMBDA_GET_MACRO_CATEGORY` | Nome Lambda AWS di GetMacroCategory |
| `LAMBDA_GET_RELEVANT_TAGS` | Nome Lambda AWS di GetRelevantTags |
| `LAMBDA_GET_TALKS_AND_PLAYLIST` | Nome Lambda AWS di GetTalksAndPlaylist |

## Deploy (per ogni Lambda)

```bash
# Installa dipendenze
npm install

# Crea lo zip per il deploy
zip -r function.zip .

# Deploy su AWS Lambda (sostituire NOME_FUNZIONE e ARN_RUOLO)
aws lambda create-function \
  --function-name NOME_FUNZIONE \
  --runtime nodejs18.x \
  --role ARN_RUOLO \
  --handler handler.NOME_HANDLER \
  --zip-file fileb://function.zip
```

## Input/Output

### POST /career-path
```json
// Request
{ "job": "Data Scientist" }

// Response
{
  "job": "Data Scientist",
  "category": "data_analytics",
  "tags": ["data", "machine learning", "AI", "statistics"],
  "count": 10,
  "playlist": [
    {
      "_id": "...",
      "title": "...",
      "speakers": "...",
      "url": "...",
      "duration": "...",
      "publishedAt": "...",
      "image_url": "...",
      "tags": [...],
      "best_category": "data_analytics",
      "score": 3
    }
  ]
}
```

### POST /watch-next
```json
// Request
{ "id": "talk_id" }

// Response
{
  "id": "talk_id",
  "title": "Talk Title",
  "related_videos": [
    { "id": "...", "slug": "...", "title": "...", "speaker": "...", "duration": "..." }
  ]
}
```
