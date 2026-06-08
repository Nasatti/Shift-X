# Relazione e Guida Completa — Progetto 3 (SHIFT-X)

Questa documentazione descrive in dettaglio l'architettura, le scelte tecnologiche e i passaggi di configurazione eseguiti per la realizzazione del **Progetto 3 (Shift-X)**. Il progetto è strutturato in due componenti principali e indipendenti:
1. **Pipeline Serverless su AWS Lambda (Full Lambda Functions)**
2. **Integrazione Conversazionale (MCP Server & Ollama)**

---

## 🛰️ PARTE 1 — Pipeline AWS Serverless (Full Lambda Functions)

Questa sezione implementa una pipeline serverless deterministica per classificare il lavoro di un utente, estrarre i tag più affini e generare una playlist personalizzata di 10 talk TEDx memorizzati in MongoDB Atlas.

### 1.1 Architettura e Componenti (5 Lambda Functions)
La pipeline è composta da 5 funzioni Lambda, ciascuna con compiti dedicati ed isolati:

1.  **`shiftx-get-macro-category` (λ1)**:
    *   **Input**: `{ "job": "NomeLavoro" }`
    *   **Responsabilità**: Classifica il ruolo lavorativo in una delle macrocategorie disponibili nel dataset (es. `technology_ai`, `data_analytics`). Applica un algoritmo deterministico a 3 livelli (alias layer, stemming leggero dei termini e punteggio di matching con i tag delle categorie) senza chiamate ad LLM esterni per massima efficienza.
    *   **Output**: `{ "job": "NomeLavoro", "category": "macrocategoria" }`
2.  **`shiftx-get-relevant-tags` (λ2)**:
    *   **Input**: `{ "job": "NomeLavoro", "category": "macrocategoria" }`
    *   **Responsabilità**: Trova i tag più rilevanti nel database per quel lavoro all'interno della macrocategoria. Conta la frequenza di ogni tag nel DB e calcola uno score di overlap con il nome del lavoro per restituire i **top 5 tag** reali.
    *   **Output**: `{ "job": "NomeLavoro", "category": "macrocategoria", "tags": [...] }`
3.  **`shiftx-get-talks-and-playlist` (λ3)**:
    *   **Input**: `{ "category": "macrocategoria", "tags": [...], "top_n": 10 }`
    *   **Responsabilità**: Interroga MongoDB Atlas per trovare i talk della categoria che contengono almeno uno dei tag selezionati. Calcola in-memory l'overlap score dei tag per ciascun talk, li ordina (in caso di parità posiziona prima i più recenti tramite `publishedAt`) e restituisce i top 10.
    *   **Output**: `{ "playlist": [...] }` (10 talk completi)
4.  **`shiftx-get-watch-next` (GetWatchNext)**:
    *   **Input**: `{ "id": "talk_id" }`
    *   **Responsabilità**: Esegue una query su MongoDB per recuperare un talk specifico e restituisce i dettagli dei talk consigliati presenti nell'array `related_videos` (relazioni precalcolate dal Glue Job).
    *   **Output**: `{ "id": "...", "related_videos": [...] }`
5.  **`shiftx-career-path-master` (Lambda Master)**:
    *   **Input**: `{ "job": "NomeLavoro" }`
    *   **Responsabilità**: Orchestratore centrale della pipeline. Espone l'endpoint pubblico e invoca in sequenza λ1 → λ2 → λ3 utilizzando l'AWS SDK, assemblando la risposta finale.

### 1.2 Ottimizzazione tramite Lambda Layer
Per evitare di caricare pacchetti npm pesanti in ogni singola Lambda (che rallenterebbero i caricamenti e supererebbero i limiti di peso di AWS), abbiamo implementato **3 Layer condivisi**:
*   **`shiftx-mongoose-layer`**: Contiene `mongoose` e `dotenv`. Associato a λ1, λ2, λ3 e GetWatchNext per la connessione a MongoDB Atlas.
*   **`shiftx-bedrock-layer`**: Contiene l'SDK di Bedrock (utilizzato in versioni alternative/future).
*   **`shiftx-lambda-layer`**: Contiene `@aws-sdk/client-lambda`, utilizzato solo dal Master per orchestrare le altre funzioni.

### 1.3 Permessi IAM e API Gateway
*   **Permessi di Invocazione**: Al ruolo IAM del Master (`shiftx-career-path-master-role`) è stata associata una *Inline Policy* che concede il permesso `lambda:InvokeFunction` sulle tre Lambda interne (λ1, λ2, λ3).
*   **API Gateway**: È stata creata un'API HTTP (`shiftx-api`) che espone al pubblico due endpoint integrati con le rispettive Lambda:
    *   `POST /career-path` ➔ integrato con il Master (`shiftx-career-path-master`).
    *   `POST /watch-next` ➔ integrato con `shiftx-get-watch-next`.
    *   **CORS**: Abilitato con origine `*` per consentire le chiamate dal frontend.

---

## 🧠 PARTE 2 — Integrazione Conversazionale (MCP Server & Ollama)

Questa sezione introduce l'intelligenza artificiale generativa locale per gestire la classificazione del lavoro e la scelta dei tag tramite un modello LLM locale, sfruttando lo standard MCP per l'interrogazione sicura del database.

### 2.1 Teoria: Cos'è un MCP Server?
Il **Model Context Protocol (MCP)** è uno standard che definisce una connessione uniforme tra LLM e sorgenti dati.
*   **Host (Client)**: L'applicazione che esegue l'LLM (Ollama locale) ed avvia il flusso.
*   **Server**: Il componente che espone in modo sicuro risorse, prompt e tool. L'LLM non tocca direttamente il database, ma chiede al server di eseguire query per suo conto.
*   **Primitiva Prompt**: Template di istruzioni pronti che dicono all'LLM come comportarsi (es. come classificare un lavoro).
*   **Primitiva Tool**: Funzioni eseguibili (es. query MongoDB) che l'LLM decide di invocare quando ha bisogno di dati reali.

### 2.2 Architettura Shift-X MCP implementata
Abbiamo implementato l'architettura AI-Native con 4 script dedicati nella cartella `Progetto3/MCP/`:

#### 1. Il Server MCP (`shiftx_server.py`)
Eseguito in ascolto su porta **8443** (tramite HTTPS con certificati SSL auto-firmati per simulare il deploy EC2). Si collega a MongoDB Atlas (database `unibg_tedx_2026`, collezione `shiftx_data`) ed espone:
*   **Risorsa (`shiftx://categories`)**: Espone la mappa completa delle categorie e dei tag di Shift-X.
*   **Prompt `get_macro_category`**: Genera le istruzioni affinché l'LLM classifichi il job inserito in una sola categoria valida.
*   **Prompt `get_relevant_tags`**: Genera le istruzioni affinché l'LLM selezioni da 1 a N tag attinenti dalla categoria scelta.
*   **Tool `get_talks_and_playlist`**: Accetta `category` e `tags` selezionati dall'LLM, interroga MongoDB, calcola l'overlap dei tag in memoria e restituisce i top 10 talk.

#### 2. Il Client CLI (`shiftx_ollama_client.py`)
Un'applicazione a riga di comando per testare la pipeline:
*   Prende il job in input dall'utente.
*   Scarica i prompt dal server MCP ed interroga il modello locale **Ollama** (`llama3.2:3b`) per determinare la categoria e i tag.
*   Chiama il tool dell'MCP server e formatta a video la playlist risultante.

#### 3. L'Orchestratore Backend API (`shiftx_backend_api.py`)
Per consentire il collegamento dell'app mobile **Flutter** (che gira sul PC o su emulatore Android) con l'MCP server (remoto su EC2) e Ollama (locale), abbiamo creato un server **FastAPI** locale in ascolto su porta **8000**:
*   **Connessione Resiliente**: Implementa una strategia di riconnessione automatica. Se la sessione MCP scade a causa di inattività, il backend la ricrea all'istante senza fallire la richiesta.
*   **Robustezza dei Tag**: Include un parser intelligente (`clean_json_response`). Se Ollama restituisce l'elenco di tag avvolto in un oggetto/dizionario (es. `{"cuoco": ["food", "farming"]}`), il parser estrae automaticamente la lista interna dei tag.
*   **CORS**: Abilitato su tutte le origini per consentire le chiamate dall'emulatore.

#### 4. Lo Script di Test (`test_api.py`)
Un semplice script in Python che invia una richiesta HTTP POST a `http://127.0.0.1:8000/career-path` con `{ "job": "cuoco" }` per validare l'intera pipeline e stampare il JSON di risposta compatibile con Flutter.

---

## 🔄 Riepilogo dei Flussi di Lavoro a Confronto

| Passaggio | Pipeline AWS Serverless (Parte 1) | Integrazione MCP & Ollama (Parte 2) |
| :--- | :--- | :--- |
| **Innesco** | Chiamata HTTP a `POST /career-path` su API Gateway | Chiamata HTTP a `POST /career-path` su FastAPI locale |
| **Orchestrazione** | Lambda Master (`CareerPathMaster`) | FastAPI Backend Orchestrator |
| **Job ➔ Categoria** | Algoritmo deterministico a 3 livelli (Node.js) | Modello LLM locale (Ollama Llama 3.2) |
| **Job ➔ Tag** | Algoritmo di frequenza + match deterministico | Ragionamento cognitivo dell'LLM (Ollama) |
| **Estrazione Playlist** | Lambda `GetTalksAndPlaylist` (Mongoose) | Tool MCP `get_talks_and_playlist` (Motor) |
| **Sorgente Dati** | MongoDB Atlas (`tedx_data`) | MongoDB Atlas (`shiftx_data`) |
