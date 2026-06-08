// ── LAMBDA — GetWatchNext ─────────────────────────────────────────────────────
// Input:  { "id": "talk_id" }
// Output: { "id": "...", "title": "...", "related_videos": [{ id, slug, title, speaker, duration }] }
//
// Restituisce i video "watch next" associati a un talk specifico.
// I related_videos sono stati pre-calcolati e salvati in MongoDB dal Glue Job.

const connect_to_db = require('./db');
const Talk = require('./Talk');

// ── Handler Lambda ────────────────────────────────────────────────────────────
module.exports.get_watch_next = async (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));

    let body = {};
    if (event.body) {
        body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    } else {
        body = event;
    }

    const id = (body.id || '').trim();

    if (!id) {
        return callback(null, {
            statusCode: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: "Campo 'id' mancante o vuoto" }),
        });
    }

    try {
        await connect_to_db();
        console.log(`=> Cerco related_videos per talk id: "${id}"`);

        // Proiezione diretta sul campo related_videos — nessun dato extra caricato
        const talk = await Talk.findOne(
            { _id: id },
            { _id: 1, title: 1, related_videos: 1 }
        );

        if (!talk) {
            return callback(null, {
                statusCode: 404,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                body: JSON.stringify({ error: `Talk non trovato con id: ${id}` }),
            });
        }

        const relatedVideos = talk.related_videos || [];
        console.log(`=> Related videos trovati: ${relatedVideos.length}`);

        return callback(null, {
            statusCode: 200,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({
                id: talk._id,
                title: talk.title,
                related_videos: relatedVideos,
            }),
        });

    } catch (err) {
        console.error('Errore in GetWatchNext:', err);
        return callback(null, {
            statusCode: 500,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: err.message }),
        });
    }
};
