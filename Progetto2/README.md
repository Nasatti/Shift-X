# Progetto 2 — ETL & Data Enrichment Pipeline with AWS Glue & Spark

Questo modulo implementa la pipeline di **Estrazione, Trasformazione e Caricamento (ETL)** di Shift-X. Utilizza **Apache Spark** su **AWS Glue** per pulire, correlare e arricchire i dati grezzi dei talk TEDx memorizzati in un Data Lake su Amazon S3, per poi caricarli strutturati su MongoDB Atlas.

---

## 🛰️ Architettura dei Dati e Flusso ETL

Il job PySpark esegue le seguenti operazioni in modo distribuito:

```mermaid
graph TD
    subgraph S3 Data Lake (Input CSV)
        A[final_list.csv]
        B[details.csv]
        C[tags.csv]
        D[images.csv]
        E[related_videos.csv]
    end
    
    subgraph AWS Glue (Spark Engine)
        F[Pulizia Testi & Join dei Dati]
        G[Risoluzione Relazioni Watch Next]
        H[UDF: Categorizzazione Deterministica]
    end
    
    A & B & C & D & E --> F
    F --> G
    G --> H
    H -->|Scrittura via Spark Connector| I[(MongoDB Atlas: tedx_data)]
```

1. **Lettura dei Dataset**: Carica 5 file CSV da Amazon S3 (`s3://shiftx-data-2026/`):
   - `final_list.csv`: Elenco principale dei talk.
   - `details.csv`: Descrizione, durata e data di pubblicazione.
   - `tags.csv`: Elenco piatto di tag associati a ciascun talk.
   - `images.csv`: URL delle immagini di copertina dei talk.
   - `related_videos.csv`: Elenco piatto di raccomandazioni basate sullo slug.
2. **Pulizia e Normalizzazione**:
   - Rimuove i caratteri speciali (`\n`, `\r`, `\t`) dalle descrizioni dei talk.
   - Filtra i talk sprovvisti di ID validi.
3. **Aggregazioni e Join**:
   - Raggruppa le immagini per talk prendendo la prima copertina valida (`image_url`).
   - Raggruppa i tag associati a ciascun talk in un set/array unico (`tags`).
4. **Risoluzione "Watch Next" (Video Correlati)**:
   - Risolve la relazione "slug ➔ ID" effettuando un join tra i video correlati e la lista principale di talk.
   - Raggruppa i video correlati in un array di oggetti strutturati (`related_videos`) pronti per essere inseriti come sotto-documenti in MongoDB.
5. **Classificazione nelle Macrocategorie (UDF)**:
   - Applica una **User Defined Function (UDF)** personalizzata chiamata `choose_best_category`.
   - Analizza la lista di tag del talk e calcola il punteggio di sovrapposizione con i tag associati a **27 macro-categorie** predefinite.
   - Applica un ordine di priorità (`CATEGORY_ORDER`) per risolvere i casi di pareggio nel punteggio, assegnando a ciascun talk la sua `best_category` ideale.
6. **Scrittura su MongoDB Atlas**:
   - Converte il DataFrame Spark in un AWS Glue `DynamicFrame`.
   - Scrive i documenti risultanti direttamente sulla collezione `tedx_data` del database `unibg_tedx_2026` in MongoDB Atlas usando il connettore Spark-MongoDB ufficiale.

---

## 📋 Schema del Documento MongoDB Finale

Ogni documento inserito in MongoDB Atlas assume la seguente struttura arricchita:

```json
{
  "_id": "talk_id",
  "slug": "titolo-talk-slug",
  "title": "Titolo del Talk",
  "speakers": "Nome dello Speaker",
  "url": "https://www.ted.com/talks/...",
  "description": "Descrizione testuale pulita del talk...",
  "duration": "Durata in secondi/minuti",
  "publishedAt": "Data di pubblicazione",
  "image_url": "https://images.ted.com/...",
  "tags": ["tag1", "tag2", "tag3"],
  "best_category": "technology_ai",
  "related_videos": [
    {
      "id": "correlato_id",
      "slug": "correlato-slug",
      "title": "Titolo Correlato",
      "speaker": "Speaker Correlato",
      "duration": "Durata Correlato"
    }
  ]
}
```

---

## 🛠️ Script del Job Glue

Il codice sorgente principale si trova nel file:
- [ShiftX_Glue_Job.py](./ShiftX_Glue_Job.py): Script Python contenente l'intera logica di trasformazione PySpark.

### Prerequisiti per l'Esecuzione su AWS
1. Creare un bucket S3 denominato `shiftx-data-2026` e caricare i CSV di input.
2. Configurare un ruolo IAM per AWS Glue con permessi di lettura su S3 e connettività di rete VPC verso MongoDB Atlas.
3. Configurare la connessione MongoDB in AWS Glue Console inserendo l'URI di connessione MongoDB Atlas.
