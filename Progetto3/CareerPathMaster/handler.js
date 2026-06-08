// ── LAMBDA MASTER — CareerPathMaster ─────────────────────────────────────────
// Unico endpoint pubblico esposto su API Gateway.
// Orchestratore della pipeline: chiama λ1 → λ2 → λ3 in sequenza
// usando l'AWS SDK e restituisce la playlist finale al client.
//
// Input:  POST /career-path   { "job": "Data Scientist" }
// Output: { "job", "category", "tags", "count", "playlist": [10 talk] }

const { LambdaClient, InvokeCommand } = require('@aws-sdk/client-lambda');

const lambda = new LambdaClient({ region: 'us-east-1' });

// ── Helper: invoca una Lambda interna e parsa il risultato ────────────────────
async function invokeLambda(functionName, payload) {
    console.log(`=> Invoco Lambda: ${functionName}`);

    const command = new InvokeCommand({
        FunctionName: functionName,
        InvocationType: 'RequestResponse',
        Payload: Buffer.from(JSON.stringify(payload)),
    });

    const response = await lambda.send(command);

    // Decodifica il payload della risposta Lambda
    const resultString = Buffer.from(response.Payload).toString('utf-8');
    const result = JSON.parse(resultString);

    if (result.statusCode !== 200) {
        const errorBody = typeof result.body === 'string' ? JSON.parse(result.body) : result.body;
        throw new Error(`${functionName} ha restituito errore ${result.statusCode}: ${errorBody.error || 'errore sconosciuto'}`);
    }

    return typeof result.body === 'string' ? JSON.parse(result.body) : result.body;
}

// ── Handler Lambda Master ─────────────────────────────────────────────────────
module.exports.career_path = async (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('CareerPathMaster — Received event:', JSON.stringify(event, null, 2));

    // Leggi il job dall'input
    let body = {};
    if (event.body) {
        body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    } else {
        body = event;
    }

    const job = (body.job || '').trim();

    if (!job) {
        return callback(null, {
            statusCode: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: "Campo 'job' mancante o vuoto" }),
        });
    }

    try {
        // ── Step 1: job → categoria (λ1 GetMacroCategory) ──────────────────────
        console.log(`Step 1: classificazione job "${job}"`);
        const step1 = await invokeLambda(
            process.env.LAMBDA_GET_MACRO_CATEGORY,
            { job }
        );
        const category = step1.category;
        console.log(`Step 1 OK → categoria: "${category}"`);

        // ── Step 2: job + categoria → tag rilevanti (λ2 GetRelevantTags) ───────
        console.log(`Step 2: selezione tag per "${job}" in "${category}"`);
        const step2 = await invokeLambda(
            process.env.LAMBDA_GET_RELEVANT_TAGS,
            { job, category }
        );
        const tags = step2.tags;
        console.log(`Step 2 OK → tag selezionati: [${tags.join(', ')}]`);

        // ── Step 3: categoria + tag → playlist top 10 (λ3 GetTalksAndPlaylist) ─
        console.log(`Step 3: costruzione playlist`);
        const step3 = await invokeLambda(
            process.env.LAMBDA_GET_TALKS_AND_PLAYLIST,
            { category, tags, top_n: 10 }
        );
        const playlist = step3.playlist;
        console.log(`Step 3 OK → playlist: ${playlist.length} talk`);

        // ── Risposta finale ─────────────────────────────────────────────────────
        return callback(null, {
            statusCode: 200,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({
                job,
                category,
                tags,
                count: playlist.length,
                playlist,
            }),
        });

    } catch (err) {
        console.error('Errore in CareerPathMaster:', err);
        return callback(null, {
            statusCode: 500,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: err.message }),
        });
    }
};
