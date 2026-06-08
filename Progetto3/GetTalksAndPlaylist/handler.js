// ── LAMBDA λ3 — GetTalksAndPlaylist ──────────────────────────────────────────
// (λ3 + λ4 uniti in una sola Lambda)
//
// Input:  { "category": "technology_ai", "tags": ["AI", "data"], "top_n": 10 }
// Output: { "playlist": [10 talk completi ordinati per tag overlap score] }
//
// Flusso:
//   1. Query MongoDB: trova i talk della categoria con almeno 1 tag in comune
//   2. Calcola score = numero di tag selezionati presenti nel talk
//   3. Ordina per score DESC (parità → publishedAt DESC)
//   4. Restituisce top N talk completi (già in memoria, nessuna join extra)

const connect_to_db = require('./db');
const Talk = require('./Talk');

const DEFAULT_TOP_N = 10;

// ── Calcola il punteggio di un talk rispetto ai tag selezionati ───────────────
function computeScore(talkTags, selectedTags) {
    if (!Array.isArray(talkTags) || talkTags.length === 0) return 0;
    const selectedSet = new Set(selectedTags.map(t => t.toLowerCase()));
    return talkTags.filter(tag => selectedSet.has(tag.toLowerCase())).length;
}

// ── Handler Lambda ────────────────────────────────────────────────────────────
module.exports.get_talks_and_playlist = async (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));

    let body = {};
    if (event.body) {
        body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    } else {
        body = event;
    }

    const category = (body.category || '').trim();
    const tags = body.tags || [];
    const topN = body.top_n || DEFAULT_TOP_N;

    if (!category || !Array.isArray(tags) || tags.length === 0) {
        return callback(null, {
            statusCode: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: "Campi 'category' e 'tags' (array non vuoto) obbligatori" }),
        });
    }

    try {
        await connect_to_db();
        console.log(`=> Cerco talk per categoria: "${category}", tag: [${tags.join(', ')}]`);

        // ── Step 1: Query MongoDB ───────────────────────────────────────────────
        // Recupera tutti i talk della categoria che hanno almeno 1 dei tag selezionati
        // $in su un campo array restituisce i doc che contengono almeno uno degli elementi
        const candidates = await Talk.find(
            {
                best_category: category,
                tags: { $in: tags },
            },
            {
                _id: 1,
                slug: 1,
                title: 1,
                speakers: 1,
                url: 1,
                description: 1,
                duration: 1,
                publishedAt: 1,
                image_url: 1,
                tags: 1,
                best_category: 1,
            }
        );

        console.log(`=> Candidati trovati: ${candidates.length}`);

        if (candidates.length === 0) {
            return callback(null, {
                statusCode: 404,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                body: JSON.stringify({
                    error: `Nessun talk trovato per categoria "${category}" con i tag selezionati`,
                }),
            });
        }

        // ── Step 2+3: Scoring e ordinamento in-memory ──────────────────────────
        const scored = candidates
            .map(talk => ({
                _id: talk._id,
                slug: talk.slug,
                title: talk.title,
                speakers: talk.speakers,
                url: talk.url,
                description: talk.description,
                duration: talk.duration,
                publishedAt: talk.publishedAt,
                image_url: talk.image_url,
                tags: talk.tags,
                best_category: talk.best_category,
                score: computeScore(talk.tags, tags),
            }))
            .sort((a, b) => {
                // Prima per score DESC
                if (b.score !== a.score) return b.score - a.score;
                // Parità → publishedAt DESC (più recente prima)
                const dateA = new Date(a.publishedAt || 0);
                const dateB = new Date(b.publishedAt || 0);
                return dateB - dateA;
            });

        // ── Step 4: Top N ──────────────────────────────────────────────────────
        const playlist = scored.slice(0, topN);

        console.log(`=> Playlist finale: ${playlist.length} talk (top score: ${playlist[0]?.score})`);

        return callback(null, {
            statusCode: 200,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({
                category,
                selected_tags: tags,
                count: playlist.length,
                playlist,
            }),
        });

    } catch (err) {
        console.error('Errore in GetTalksAndPlaylist:', err);
        return callback(null, {
            statusCode: 500,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: err.message }),
        });
    }
};
