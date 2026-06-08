// ── LAMBDA λ2 — GetRelevantTags ──────────────────────────────────────────────
// Input:  { "job": "Data Scientist", "category": "data_analytics" }
// Output: { "job": "...", "category": "...", "tags": ["data", "machine learning", ...] }
//
// Seleziona i tag più pertinenti per il job tra quelli REALI presenti nel DB
// usando un algoritmo deterministico. Nessuna chiamata a AWS Bedrock.
//
// Algoritmo:
//   1. Interroga MongoDB: recupera tutti i talk della categoria
//   2. Calcola la frequenza di ogni tag (quanti talk lo contengono)
//   3. Assegna ad ogni tag uno score:
//        score = (100 × match_con_job) + frequenza_nel_db
//      dove match_con_job = 1 se almeno un token del job compare nel tag, 0 altrimenti
//      (i tag multi-parola che matchano integralmente valgono 2 invece di 1)
//   4. Ordina per score DESC e restituisce i top 5 tag

const connect_to_db = require('./db');
const Talk = require('./Talk');

const TOP_N_TAGS = 5;

// ── Tokenizza una stringa ─────────────────────────────────────────────────────
function tokenize(text) {
    return text
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ')
        .split(/\s+/)
        .filter(t => t.length > 1);
}

// ── Step 1+2: recupera tag reali e la loro frequenza dalla categoria ──────────
async function getTagFrequencies(category) {
    const talks = await Talk.find(
        { best_category: category },
        { tags: 1, _id: 0 }
    );

    // Map: tag (case originale) → numero di talk in cui compare
    const freqMap = new Map();
    for (const talk of talks) {
        if (Array.isArray(talk.tags)) {
            for (const tag of talk.tags) {
                if (tag) {
                    freqMap.set(tag, (freqMap.get(tag) || 0) + 1);
                }
            }
        }
    }

    return freqMap; // Map<string, number>
}

// ── Step 3: calcola lo score di ogni tag rispetto al job ─────────────────────
function scoreTag(tag, jobTokens, jobPhrases) {
    const tagLower = tag.toLowerCase().trim();
    const tagTokens = tagLower.split(/\s+/);

    let matchScore = 0;

    // Controlla se il tag completo (es. "machine learning") è una frase del job
    if (jobPhrases.has(tagLower)) {
        matchScore = tagTokens.length > 1 ? 2 : 1; // multi-parola vale di più
    } else {
        // Controlla se almeno un token del job compare in un token del tag
        for (const jobToken of jobTokens) {
            for (const tagToken of tagTokens) {
                if (tagToken === jobToken || tagToken.includes(jobToken) || jobToken.includes(tagToken)) {
                    matchScore = 1;
                    break;
                }
            }
            if (matchScore > 0) break;
        }
    }

    return matchScore; // 0, 1 o 2
}

// ── Handler Lambda ────────────────────────────────────────────────────────────
module.exports.get_relevant_tags = async (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));

    let body = {};
    if (event.body) {
        body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    } else {
        body = event;
    }

    const job = (body.job || '').trim();
    const category = (body.category || '').trim();

    if (!job || !category) {
        return callback(null, {
            statusCode: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: "Campi 'job' e 'category' obbligatori" }),
        });
    }

    try {
        await connect_to_db();

        // 1+2. Frequenze dei tag nel DB per questa categoria
        const freqMap = await getTagFrequencies(category);

        if (freqMap.size === 0) {
            return callback(null, {
                statusCode: 404,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                body: JSON.stringify({ error: `Nessun tag trovato per la categoria: ${category}` }),
            });
        }

        console.log(`Tag unici trovati per "${category}": ${freqMap.size}`);

        // Prepara i token e le frasi del job per il matching
        const jobTokens = tokenize(job);
        const jobPhrases = new Set(jobTokens);
        // Bigrams
        for (let i = 0; i < jobTokens.length - 1; i++) {
            jobPhrases.add(`${jobTokens[i]} ${jobTokens[i + 1]}`);
        }
        // Trigrams
        for (let i = 0; i < jobTokens.length - 2; i++) {
            jobPhrases.add(`${jobTokens[i]} ${jobTokens[i + 1]} ${jobTokens[i + 2]}`);
        }

        // 3. Calcola lo score per ogni tag
        const scored = [];
        for (const [tag, freq] of freqMap.entries()) {
            const matchScore = scoreTag(tag, jobTokens, jobPhrases);
            // Score finale: la corrispondenza col job è il criterio primario,
            // la frequenza nel DB è il criterio di spareggio
            const totalScore = (100 * matchScore) + freq;
            scored.push({ tag, freq, matchScore, totalScore });
        }

        // 4. Ordina per score DESC e prendi i top N
        scored.sort((a, b) => b.totalScore - a.totalScore || b.freq - a.freq);
        const selectedTags = scored.slice(0, TOP_N_TAGS).map(item => item.tag);

        console.log(`Tag selezionati per "${job}" in "${category}":`, selectedTags);

        return callback(null, {
            statusCode: 200,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ job, category, tags: selectedTags }),
        });

    } catch (err) {
        console.error('Errore in GetRelevantTags:', err);
        return callback(null, {
            statusCode: 500,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: err.message }),
        });
    }
};
