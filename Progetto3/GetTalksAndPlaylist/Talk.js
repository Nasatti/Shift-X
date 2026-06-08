// Schema Mongoose del documento TEDx (output del Glue Job Progetto 2)
// Collección: unibg_tedx_2026.tedx_data

const mongoose = require('mongoose');

const talk_schema = new mongoose.Schema({
    _id: String,
    slug: String,
    title: String,
    speakers: String,
    url: String,
    description: String,
    duration: String,
    publishedAt: String,
    image_url: String,
    tags: [String],
    best_category: String,
    related_videos: [
        {
            id: String,
            slug: String,
            title: String,
            speaker: String,
            duration: String,
        }
    ],
}, { collection: 'tedx_data' });

module.exports = mongoose.model('talk', talk_schema);
