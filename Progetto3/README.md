# Progetto 3 — AWS Lambda Functions & MCP Server Integration

Questo modulo contiene il backend logico di **Shift-X**, strutturato in due componenti indipendenti e complementari:
1. **Pipeline Serverless su AWS Lambda (Full AWS Serverless)**: Una pipeline deterministica ed efficiente eseguita nel cloud.
2. **Integrazione Conversazionale (MCP Server & Ollama)**: Un'architettura AI-native locale che sfrutta un modello LLM per determinare categorie e tag.

---

## 🛰️ PARTE 1 — Pipeline AWS Serverless (Full Lambda Functions)

Questa sezione implementa l'estrazione deterministica dei talk TEDx memorizzati su MongoDB Atlas a partire dal ruolo lavorativo dell'utente, orchestrando 5 funzioni Lambda.

### 1.1 Architettura e Componenti (5 Lambda Functions)

```
Progetto3/
├── GetMacroCategory/     # λ1 — Classifica il job inserito in una macrocategoria (algoritmo a 3 livelli)
├── GetRelevantTags/      # λ2 — Calcola i top 5 tag più rilevanti nel DB per quel lavoro
├── GetTalksAndPlaylist/  # λ3 — Trova i talk della categoria ordinati per overlap score e data
├── GetWatchNext/         # λ  — Recupera i video correlati ("Watch Next") precalcolati per un talk
└── CareerPathMaster/     # λ Master — Orchestratore centrale che chiama λ1 → λ2 → λ3
```

- **`shiftx-get-macro-category` (λ1)**: Classifica il ruolo lavorativo dell'utente in una delle macrocategorie disponibili nel dataset (es. `technology_ai`, `data_analytics`). Utilizza un algoritmo deterministico basato su alias layer, stemming leggero e punteggi di matching senza chiamare LLM esterni, per massimizzare la velocità.
- **`shiftx-get-relevant-tags` (λ2)**: Conta la frequenza di ciascun tag nel database all'interno della macrocategoria selezionata e calcola uno score di overlap con il nome del lavoro, restituendo i **top 5 tag** reali presenti nel dataset.
- **`shiftx-get-talks-and-playlist` (λ3)**: Interroga MongoDB Atlas per estrarre i talk che contengono almeno uno dei tag selezionati. Calcola in-memory l'overlap score, ordina i risultati per punteggio (e data in caso di parità) e restituisce i top 10 talk.
- **`shiftx-get-watch-next`**: Recupera i dettagli dei talk consigliati presenti nell'array `related_videos` (relazioni precalcolate dal Glue Job nel Progetto 2) per un determinato talk.
- **`shiftx-career-path-master` (Lambda Master)**: Orchestratore principale esposto al pubblico che invoca sequenzialmente λ1 ➔ λ2 ➔ λ3 tramite l'AWS SDK e formatta la risposta finale.

### 1.2 Endpoint API Gateway

| Endpoint | Lambda | Descrizione |
|---|---|---|
| `POST /career-path` | `CareerPathMaster` | Pipeline completa: job ➔ playlist di 10 talk |
| `POST /watch-next` | `GetWatchNext` | Recupero dei video correlati a un talk specifico |

### 1.3 Ottimizzazione tramite Lambda Layer

Per evitare di includere dipendenze pesanti in ogni singola Lambda (velocizzando i tempi di cold start), sono stati implementati **3 Layer condivisi**:
- **`shiftx-mongoose-layer`**: Contiene `mongoose` e `dotenv` per le connessioni a MongoDB Atlas.
- **`shiftx-bedrock-layer`**: Contiene l'SDK di Amazon Bedrock per funzionalità future.
- **`shiftx-lambda-layer`**: Contiene `@aws-sdk/client-lambda`, utilizzato dalla Lambda Master per invocare le funzioni lavoratrici.

### 1.4 Configurazione e Deploy

#### Variabili d'Ambiente richieste:
- **Lambda con MongoDB** (`GetMacroCategory`, `GetRelevantTags`, `GetTalksAndPlaylist`, `GetWatchNext`):
  - `DB`: URI di connessione a MongoDB Atlas.
- **Lambda Master** (`CareerPathMaster`):
  - `LAMBDA_GET_MACRO_CATEGORY`: Nome della Lambda λ1.
  - `LAMBDA_GET_RELEVANT_TAGS`: Nome della Lambda λ2.
  - `LAMBDA_GET_TALKS_AND_PLAYLIST`: Nome della Lambda λ3.

#### Deploy di una Lambda (Esempio via AWS CLI):
```bash
# Entra nella cartella della funzione desiderata ed installa i pacchetti
npm install

# Comprimi i file in uno zip
zip -r function.zip .

# Carica lo zip su AWS Lambda (personalizzare NOME_FUNZIONE e ARN_RUOLO)
aws lambda create-function \
  --function-name NOME_FUNZIONE \
  --runtime nodejs18.x \
  --role ARN_RUOLO \
  --handler handler.NOME_HANDLER \
  --zip-file fileb://function.zip
```

---

## 🧠 PARTE 2 — Integrazione Conversazionale (MCP Server & Ollama)

Questa sezione introduce l'intelligenza artificiale generativa locale per gestire la classificazione del lavoro e la scelta dei tag tramite un modello LLM locale, sfruttando lo standard MCP per l'interrogazione sicura del database.

### 2.1 Architettura Shift-X MCP
L'architettura AI-Native locale è suddivisa in 4 script posizionati in `Progetto3/MCP/`:

1. **Il Server MCP (`shiftx_server.py`)**:
   In ascolto sulla porta **8443** (tramite HTTPS/SSL). Si collega a MongoDB Atlas ed espone:
   - **Risorsa (`shiftx://categories`)**: Mappa completa delle categorie e tag di Shift-X.
   - **Prompt `get_macro_category`**: Istruzioni per far classificare all'LLM il job in una singola categoria valida.
   - **Prompt `get_relevant_tags`**: Istruzioni per far selezionare all'LLM i tag attinenti dalla categoria scelta.
   - **Tool `get_talks_and_playlist`**: Interroga MongoDB, calcola l'overlap dei tag ed estrae i top 10 talk.
2. **Il Client CLI (`shiftx_ollama_client.py`)**:
   Interfaccia a riga di comando per testare la pipeline locale interrogando il modello **Ollama** (`llama3.2:3b`) per determinare categoria/tag e invocando i tool del server MCP.
3. **L'Orchestratore Backend API (`shiftx_backend_api.py`)**:
   Server **FastAPI** (porta **8000**) che funge da ponte resiliente tra il client mobile Flutter e il server MCP/Ollama:
   - Gestisce la riconnessione automatica in caso di scadenza della sessione MCP.
   - Include un parser intelligente per pulire e formattare le risposte JSON prodotte dall'LLM.
4. **Lo Script di Test (`test_api.py`)**:
   Invia richieste HTTP POST per validare il funzionamento dell'orchestratore FastAPI.

---

## 🔄 Riepilogo dei Flussi a Confronto

| Passaggio | Pipeline AWS Serverless (Parte 1) | Integrazione MCP & Ollama (Parte 2) |
| :--- | :--- | :--- |
| **Innesco** | Chiamata HTTP a `POST /career-path` su API Gateway | Chiamata HTTP a `POST /career-path` su FastAPI locale |
| **Orchestrazione** | Lambda Master (`CareerPathMaster`) | FastAPI Backend Orchestrator |
| **Job ➔ Categoria** | Algoritmo deterministico a 3 livelli (Node.js) | Modello LLM locale (Ollama Llama 3.2) |
| **Job ➔ Tag** | Algoritmo di frequenza + match deterministico | Ragionamento cognitivo dell'LLM (Ollama) |
| **Estrazione Playlist** | Lambda `GetTalksAndPlaylist` (Mongoose) | Tool MCP `get_talks_and_playlist` (Motor) |
| **Sorgente Dati** | MongoDB Atlas (`tedx_data`) | MongoDB Atlas (`shiftx_data`) |

---

## 📬 Formato Richieste/Risposte API

### POST /career-path
```json
// Richiesta
{ "job": "Data Scientist" }

// Risposta
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
// Richiesta
{ "id": "talk_id" }

// Risposta
{
  "id": "talk_id",
  "title": "Titolo del Talk",
  "related_videos": [
    { "id": "...", "slug": "...", "title": "...", "speaker": "...", "duration": "..." }
  ]
}
```
