// ── LAMBDA λ1 — GetMacroCategory ─────────────────────────────────────────────
// Input:  { "job": "Developer" }
// Output: { "job": "...", "category": "technology_ai" }
//
// Classifica il ruolo lavorativo nella macrocategoria più adatta usando
// un algoritmo deterministico a 3 livelli. Nessuna chiamata a AWS Bedrock.
//
// Algoritmo:
//   1. Tokenizza il job in parole (lowercase, rimuove punteggiatura)
//   2. [Opzione 2] Espande i token con un alias layer: mappa parole tipiche
//      dei titoli di lavoro → parole che esistono nei tag del dataset
//   3. [Opzione 3] Stemming leggero: riduce le parole alla radice comune
//      (es. "teacher" → "teach", trova corrispondenza con il tag "teaching")
//   4. Per ogni categoria calcola uno score basato su:
//        - match diretto (peso 1.0): token del job nei tag della categoria
//        - match da alias (peso 0.9): token espanso nei tag della categoria
//        - match da stem (peso 0.8): radice comune con un tag della categoria
//        - match sul nome categoria (peso 0.5): token nel nome della categoria
//      I tag multi-parola che matchano integralmente valgono il doppio.
//   5. Restituisce la categoria con score massimo.
//      Se score = 0 per tutte → errore 400 (nessuna corrispondenza).

const { CATEGORY_TO_TAGS, VALID_CATEGORIES } = require('./categories');

// ── [OPZIONE 2] Alias layer ───────────────────────────────────────────────────
// Mappa: parola-chiave del titolo di lavoro → parole che esistono nei tag del dataset
// Copre ~50 professioni comuni. Ogni job keyword viene espansa prima del matching.
const JOB_KEYWORD_ALIASES = {
    // ── Tech / Software ──────────────────────────────────────────────────────
    'developer':       ['software', 'code', 'technology', 'algorithm'],
    'programmer':      ['software', 'code', 'algorithm', 'technology'],
    'coder':           ['code', 'software', 'technology'],
    'frontend':        ['software', 'code', 'technology', 'UX design'],
    'backend':         ['software', 'code', 'technology', 'infrastructure'],
    'fullstack':       ['software', 'code', 'technology'],
    'devops':          ['infrastructure', 'engineering', 'software', 'technology'],
    'cloud':           ['infrastructure', 'engineering', 'technology'],
    'architect':       ['architecture', 'engineering', 'infrastructure'],
    'cybersecurity':   ['cyber security', 'encryption', 'technology'],
    'security':        ['cyber security', 'encryption', 'surveillance'],
    'hacker':          ['cyber security', 'encryption', 'code'],
    'analyst':         ['data', 'statistics', 'algorithm', 'visualizations'],
    'scientist':       ['science', 'data', 'statistics', 'machine learning'],
    'researcher':      ['science', 'research', 'data', 'biology'],
    // ── AI / Data ────────────────────────────────────────────────────────────
    'ml':              ['machine learning', 'artificial intelligence', 'algorithm'],
    'nlp':             ['machine learning', 'artificial intelligence', 'algorithm'],
    'ai':              ['artificial intelligence', 'machine learning', 'algorithm'],
    'robotics':        ['robots', 'engineering', 'artificial intelligence'],
    'automation':      ['robots', 'engineering', 'technology', 'manufacturing'],
    // ── Design / Creative ────────────────────────────────────────────────────
    'designer':        ['design', 'UX design', 'art', 'graphic design'],
    'ux':              ['UX design', 'design', 'product design'],
    'ui':              ['UX design', 'design', 'product design'],
    'creative':        ['art', 'design', 'creativity', 'storytelling'],
    'artist':          ['art', 'painting', 'photography', 'music'],
    'musician':        ['music', 'performance', 'art'],
    'filmmaker':       ['film', 'storytelling', 'media'],
    'photographer':    ['photography', 'art', 'media'],
    'writer':          ['writing', 'books', 'storytelling', 'journalism'],
    'author':          ['writing', 'books', 'literature', 'storytelling'],
    'journalist':      ['journalism', 'media', 'writing', 'communication'],
    // ── Business / Management ────────────────────────────────────────────────
    'manager':         ['leadership', 'business', 'productivity', 'goals'],
    'executive':       ['leadership', 'business', 'entrepreneur'],
    'ceo':             ['leadership', 'entrepreneur', 'business', 'innovation'],
    'cto':             ['technology', 'leadership', 'innovation', 'engineering'],
    'cfo':             ['finance', 'money', 'investing', 'economics'],
    'entrepreneur':    ['entrepreneur', 'business', 'innovation', 'startup'],
    'founder':         ['entrepreneur', 'business', 'innovation'],
    'marketer':        ['marketing', 'social media', 'business', 'advertising'],
    'consultant':      ['business', 'leadership', 'economics', 'innovation'],
    'accountant':      ['finance', 'money', 'investing', 'economics'],
    'hr':              ['work', 'career', 'leadership', 'productivity'],
    'recruiter':       ['career', 'work', 'leadership'],
    'salesperson':     ['business', 'marketing', 'money'],
    'sales':           ['business', 'marketing', 'money'],
    // ── Science ──────────────────────────────────────────────────────────────
    'biologist':       ['biology', 'genetics', 'science', 'evolution'],
    'chemist':         ['chemistry', 'science', 'biotech'],
    'physicist':       ['physics', 'science', 'astronomy'],
    'geologist':       ['geology', 'science', 'geography'],
    'astronomer':      ['astronomy', 'space', 'science', 'physics'],
    'ecologist':       ['ecology', 'environment', 'biology', 'nature'],
    'neuroscientist':  ['neuroscience', 'brain', 'science', 'psychology'],
    'psychologist':    ['psychology', 'mental health', 'therapy', 'cognitive science'],
    'sociologist':     ['sociology', 'society', 'social change', 'culture'],
    'anthropologist':  ['anthropology', 'history', 'culture', 'society'],
    'archaeologist':   ['archaeology', 'history', 'science', 'ancient world'],
    // ── Health / Medicine ────────────────────────────────────────────────────
    'doctor':          ['medicine', 'health', 'medical research', 'science'],
    'physician':       ['medicine', 'health', 'medical research'],
    'surgeon':         ['Surgery', 'medicine', 'health', 'medical research'],
    'nurse':           ['health', 'medicine', 'public health', 'health care'],
    'pharmacist':      ['medicine', 'health', 'chemistry'],
    'psychiatrist':    ['mental health', 'psychology', 'therapy', 'medicine'],
    'therapist':       ['therapy', 'mental health', 'psychology'],
    'nutritionist':    ['health', 'food', 'medicine'],
    'dentist':         ['medicine', 'health'],
    'paramedic':       ['health', 'medicine', 'public health'],
    // ── Education ────────────────────────────────────────────────────────────
    'teacher':         ['teaching', 'education', 'learning', 'kids'],
    'professor':       ['teaching', 'education', 'science', 'university'],
    'educator':        ['teaching', 'education', 'learning'],
    'librarian':       ['library', 'books', 'education'],
    'coach':           ['motivation', 'leadership', 'sports', 'performance'],
    'trainer':         ['teaching', 'education', 'sports', 'performance'],
    // ── Law / Government ─────────────────────────────────────────────────────
    'lawyer':          ['law', 'justice system', 'government', 'human rights'],
    'attorney':        ['law', 'justice system', 'government'],
    'judge':           ['law', 'justice system', 'government'],
    'politician':      ['politics', 'government', 'democracy', 'policy'],
    'diplomat':        ['international relations', 'politics', 'government'],
    'activist':        ['activism', 'social change', 'human rights', 'protest'],
    'ngo':             ['human rights', 'social change', 'international development'],
    // ── Environment ──────────────────────────────────────────────────────────
    'environmentalist': ['environment', 'sustainability', 'climate change', 'ecology'],
    'agronomist':      ['agriculture', 'farming', 'food', 'environment'],
    'chef':            ['food', 'farming', 'culture'],
    'cook':            ['food', 'farming'],
    // ── Engineering ──────────────────────────────────────────────────────────
    'engineer':        ['engineering', 'technology', 'innovation', 'infrastructure'],
    'mechanic':        ['engineering', 'manufacturing', 'transportation'],
    'electrician':     ['electricity', 'energy', 'engineering'],
    // ── Finance ──────────────────────────────────────────────────────────────
    'banker':          ['finance', 'money', 'investing', 'economics'],
    'trader':          ['finance', 'investing', 'money', 'economics'],
    'investor':        ['investing', 'finance', 'money', 'economics'],
    'economist':       ['economics', 'finance', 'money', 'policy'],
    // ── Space / Defense ──────────────────────────────────────────────────────
    'astronaut':       ['space', 'astronomy', 'rocket science', 'NASA'],
    'pilot':           ['flight', 'transportation', 'engineering'],
    'soldier':         ['war', 'government', 'terrorism', 'history'],
};

// ── [OPZIONE 3] Stemming leggero ──────────────────────────────────────────────
// Rimuove i suffissi più comuni dell'inglese per ridurre le parole alla radice.
// Non usa librerie esterne — implementazione minima ma efficace per titoli di lavoro.
const SUFFIXES = [
    'ologist', 'ologist', // biologist → biolog
    'tion', 'sion',        // automation → automat
    'ment',                // management → manag (min 4 chars)
    'ness', 'ity',         // happiness → happi
    'ist',                 // scientist → scienti (poi cerca "science")
    'ian',                 // musician → musici
    'ing',                 // marketing → market ✓ (tag esistente!)
    'er', 'or',            // developer → develop, director → direct
    'ive', 'ary',
    'al',                  // medical → medic
];

function stem(word) {
    for (const suffix of SUFFIXES) {
        if (word.endsWith(suffix) && word.length - suffix.length >= 4) {
            return word.slice(0, word.length - suffix.length);
        }
    }
    return word;
}

// ── Pre-calcola strutture per il matching ─────────────────────────────────────

// Map: category → array di { original, tokens[], stem } per ogni tag
const CATEGORY_TAG_ENTRIES = {};
for (const [cat, tags] of Object.entries(CATEGORY_TO_TAGS)) {
    CATEGORY_TAG_ENTRIES[cat] = tags.map(tag => {
        const tagLower = tag.toLowerCase().trim();
        const tagTokens = tagLower.split(/\s+/);
        return {
            original: tag,
            full: tagLower,                          // tag completo (per phrase match)
            tokens: tagTokens,                       // singole parole del tag
            stems: tagTokens.map(t => stem(t)),      // radici delle parole del tag
        };
    });
}

// Map: category → Set di token del nome (es. "technology_ai" → ["technology", "ai"])
const CATEGORY_NAME_TOKENS = {};
for (const cat of VALID_CATEGORIES) {
    CATEGORY_NAME_TOKENS[cat] = new Set(cat.split('_').filter(t => t.length > 1));
}

// ── Tokenizza una stringa ─────────────────────────────────────────────────────
function tokenize(text) {
    return text
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ')
        .split(/\s+/)
        .filter(t => t.length > 1);
}

// ── Classifica il job nella macrocategoria più adatta ─────────────────────────
function classifyJob(job) {
    const jobTokens = tokenize(job);
    if (jobTokens.length === 0) return { category: null, score: 0 };

    // ── Costruisce il set di frasi originali (bigram + trigram) ──────────────
    const jobPhrases = new Set(jobTokens);
    for (let i = 0; i < jobTokens.length - 1; i++) {
        jobPhrases.add(`${jobTokens[i]} ${jobTokens[i + 1]}`);
    }
    for (let i = 0; i < jobTokens.length - 2; i++) {
        jobPhrases.add(`${jobTokens[i]} ${jobTokens[i + 1]} ${jobTokens[i + 2]}`);
    }

    // ── [OPZIONE 2] Espande i token originali tramite alias layer ────────────
    // alias: parole aggiuntive suggerite dagli alias, con flag per ridurre il peso
    const aliasTokens = new Set();
    const aliasPhrases = new Set();
    for (const token of jobTokens) {
        const aliases = JOB_KEYWORD_ALIASES[token];
        if (aliases) {
            for (const alias of aliases) {
                const a = alias.toLowerCase();
                aliasPhrases.add(a);           // aggiunge anche come frase (es. "machine learning")
                for (const w of a.split(/\s+/)) {
                    if (w.length > 1) aliasTokens.add(w);
                }
            }
        }
    }

    // ── [OPZIONE 3] Calcola le radici (stem) dei token del job ───────────────
    const jobStems = jobTokens.map(t => stem(t));

    // ── Scoring per categoria ─────────────────────────────────────────────────
    let bestCategory = null;
    let bestScore = 0;

    for (const cat of VALID_CATEGORIES) {
        const tagEntries = CATEGORY_TAG_ENTRIES[cat];
        const nameTokens = CATEGORY_NAME_TOKENS[cat];
        let score = 0;

        for (const entry of tagEntries) {
            const { full, tokens, stems } = entry;
            const isMultiWord = tokens.length > 1;

            // ─ Livello 1: match diretto — frase del job nel tag (peso 1.0 o 2.0)
            if (jobPhrases.has(full)) {
                score += isMultiWord ? 2.0 : 1.0;
                continue; // già trovato il miglior match per questo tag
            }
            for (const tok of tokens) {
                if (jobPhrases.has(tok)) {
                    score += 1.0;
                    break;
                }
            }

            // ─ Livello 2: match da alias — frase alias nel tag (peso 0.9)
            if (aliasPhrases.has(full)) {
                score += isMultiWord ? 1.8 : 0.9;
                continue;
            }
            for (const tok of tokens) {
                if (aliasTokens.has(tok)) {
                    score += 0.9;
                    break;
                }
            }

            // ─ Livello 3: match da stem — radice comune (peso 0.8)
            // Controlla se la radice di un token del job coincide con
            // la radice di un token del tag (es. "teacher"→"teach" ≈ "teaching"→"teach")
            let stemMatched = false;
            for (const jobStem of jobStems) {
                if (jobStem.length < 4) continue;
                for (const tagStem of stems) {
                    if (
                        tagStem === jobStem ||
                        tagStem.startsWith(jobStem) ||
                        jobStem.startsWith(tagStem)
                    ) {
                        score += 0.8;
                        stemMatched = true;
                        break;
                    }
                }
                if (stemMatched) break;
            }
        }

        // ─ Bonus sul nome della categoria (peso 0.5 per token)
        for (const token of jobTokens) {
            if (nameTokens.has(token)) score += 0.5;
        }
        for (const token of aliasTokens) {
            if (nameTokens.has(token)) score += 0.3; // alias sul nome vale meno
        }

        if (score > bestScore) {
            bestScore = score;
            bestCategory = cat;
        }
    }

    return { category: bestCategory, score: bestScore };
}

// ── Handler Lambda ────────────────────────────────────────────────────────────
module.exports.get_macro_category = async (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));

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

    const { category, score } = classifyJob(job);

    // Se score = 0 → nessuna corrispondenza trovata, nessun fallback
    if (!category || score === 0) {
        console.warn(`Nessuna categoria trovata per il job: "${job}"`);
        return callback(null, {
            statusCode: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({
                error: `Nessuna categoria trovata per il ruolo: "${job}". Prova con un termine più specifico (es. "software developer", "data scientist").`,
            }),
        });
    }

    console.log(`Job: "${job}" → Categoria: "${category}" (score: ${score})`);

    return callback(null, {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        body: JSON.stringify({ job, category }),
    });
};
