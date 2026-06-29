# Progetto 4 — Shift-X Mobile Client (Flutter)

Questo modulo contiene l'applicazione mobile multipiattaforma di **Shift-X** realizzata in **Flutter**. L'app offre un'interfaccia utente premium per l'interazione con il sistema di raccomandazione dei talk TEDx basato sul percorso professionale.

---

## 📱 Funzionalità Principali

- **Ricerca di Ruoli Professionali (Search Screen)**:
  - Barra di ricerca animata per inserire qualsiasi job title (es. *Data Scientist*, *Cuoco*, *Growth Hacker*).
  - Cronologia delle ricerche recenti salvata in-memory per una navigazione rapida.
  - Indicatore di caricamento (Skeleton loaders/Circular progress) durante il processing della pipeline cloud/LLM.
- **Visualizzazione Playlist Personalizzata (Playlist Screen)**:
  - Lista ordinata dei **Top 10 Talk** TEDx più rilevanti.
  - Badge colorati per ciascuna categoria di talk.
  - Espansione della descrizione testuale del talk in un click per leggerne i dettagli.
  - Tag visualizzati sotto forma di chip per un'identificazione immediata degli argomenti.
  - Integrazione multimediale con caricamento automatico delle immagini di copertina dei talk, con un fallback grafico di qualità in caso di immagini mancanti.
- **Player & Collegamento Esterno**:
  - Pulsante per riprodurre il video che lancia la pagina ufficiale di TEDx nel browser del dispositivo tramite il pacchetto `url_launcher`.
- **Raccomandazioni Watch Next**:
  - Tassello interattivo che consente di caricare al volo i video correlati ("Watch Next") per ogni talk selezionato, interrogando l'endpoint dedicato.

---

## 🎨 Design System & Estetica

L'applicazione segue linee guida grafiche curate e moderne:
- **Tema Scuro Premium**: Colore di sfondo scuro carbonio (`#090505`) e dettagli rosso fuoco (`#E50914`), ispirati al brand **TEDx** e a piattaforme di streaming come **Netflix**.
- **Card e Ombreggiature**: Bordi arrotondati, contorni sfumati rossi per indicare l'elevazione e layout flessibili sia per smartphone che per tablet.
- **Micro-animazioni**: Transizioni fluide tra la schermata di ricerca e la schermata dei risultati.

---

## 🛠️ Struttura del Progetto Flutter

La cartella di codice sorgente `shift_x_flutter/` è organizzata come segue:

```
shift_x_flutter/
├── lib/
│   ├── models/
│   │   └── talk.dart            # Modelli dati strongly-typed: Talk, RelatedVideo, CareerPath
│   ├── talk_repository.dart     # Chiamate HTTP client a AWS API Gateway / Backend locale
│   └── main.dart                # Entrypoint, Navigation, Schermate UI (Search & Playlist)
├── logo/                        # Asset grafici e loghi personalizzati di Shift-X
├── pubspec.yaml                 # Dipendenze Flutter (http, url_launcher, cupertino_icons)
└── README.md                    # Questa guida
```

---

## 🚀 Come Eseguire l'Applicazione

### Prerequisiti
- **Flutter SDK** installato (versione consigliata: `>=3.11.0`).
- Un emulatore (Android/iOS) o un dispositivo fisico collegato in modalità debug.

### Passaggi
1. Spostati nella cartella del progetto Flutter:
   ```bash
   cd shift_x_flutter
   ```
2. Installa le dipendenze dichiarate in `pubspec.yaml`:
   ```bash
   flutter pub get
   ```
3. Avvia l'applicazione sul dispositivo/emulatore collegato:
   ```bash
   flutter run
   ```

---

## 🔗 Configurazione degli Endpoint

All'interno di [talk_repository.dart](./shift_x_flutter/lib/talk_repository.dart), l'applicazione punta agli endpoint di produzione ospitati su **AWS API Gateway**:
- **Generazione Playlist**: `https://msyavs3hs4.execute-api.us-east-1.amazonaws.com/default/Carrer_Path_Master`
- **Watch Next**: `https://e3q93kdqyj.execute-api.us-east-1.amazonaws.com/default/Get_Watch_next`

*Nota: Se si desidera testare l'app in locale con la pipeline AI-Native (Ollama ed MCP Server del Progetto 3), modificare gli indirizzi URL configurando l'IP locale della propria macchina (es. `http://10.0.2.2:8000/career-path` per emulatore Android).*
