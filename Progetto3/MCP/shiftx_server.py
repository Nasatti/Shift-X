"""
Shift-X MCP Server
Provides resources, prompts, and database queries for TEDx playlist recommendations.
"""

import os
import re
import json
import asyncio
from mcp.server.fastmcp import FastMCP
from motor.motor_asyncio import AsyncIOMotorClient
from mcp.server.transport_security import TransportSecuritySettings

# --- MongoDB Atlas Connection Settings ---
MONGO_URI = (
    "mongodb+srv://GiacomoPrevitali:GiacomoPrevitali"
    "@cluster0.to95nu3.mongodb.net/?appName=Cluster0"
)


# Attempt to locate and load the variables.env file from GetTalksAndPlaylist
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_dir, "..", "GetTalksAndPlaylist", "variables.env")

if os.path.exists(env_file_path):
    try:
        with open(env_file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("DB="):
                    MONGO_URI = line.strip().split("=", 1)[1].strip()
                    break
    except Exception as e:
        print(f"Warning: Could not read variables.env: {e}")

# Fallback URI (configured in our workspace)
if not MONGO_URI:
    MONGO_URI = os.environ.get("DB", "")

print(f"Connecting to MongoDB...")
client = AsyncIOMotorClient(MONGO_URI)
db = client["unibg_tedx_2026"]
collection = db["shiftx_data"]

# --- Category structure (exactly as defined in categories.js) ---
CATEGORY_TO_TAGS = {
    "arts_design": ['UX design','animation','architecture','art','dance','design','fashion','film','graphic design','industrial design','media','music','painting','performance','photography','poetry','product design','social media','spoken word','storytelling','street art','theater','typography','writing'],
    "business_management": ['behavioral economics','business','capitalism','career','competition','consumerism','crowdsourcing','economics','entrepreneur','finance','goals','innovation','investing','leadership','marketing','money','productivity','success','urban planning','women in business','work'],
    "data_analytics": ['algorithm','artificial intelligence','cognitive science','data','machine learning','statistics','visualizations'],
    "education_learning": ['Best of the Web','Humanities','Life','TED Books','TED Connects','TED Fellows','TED Membership','TED Prize','TED Residency','TED en Español','TED-Ed','TEDx','body language','books','cancel culture','culture','education','family','kids','language','library','machine learning','memory','motivation','teaching','ted health podcast','youth'],
    "engineering_innovation": ['architecture','driverless cars','drones','electricity','energy','engineering','flight','industrial design','infrastructure','innovation','invention','manufacturing','nuclear energy','product design','renewable energy','robots','rocket science','solar energy','technology','transportation','urban planning','wind energy'],
    "environment_sustainability": ['agriculture','animals','bees','biodiversity','biosphere','climate change','conservation','coral reefs','ecology','environment','farming','gardening','geography','glaciers','natural resources','nature','ocean','plastic','pollution','renewable energy','rivers','solar energy','sustainability','trees','water','weather','wildlife','wind energy'],
    "food_agriculture": ['agriculture','bees','biology','botany','ecology','farming','food','gardening','marine biology','plants','synthetic biology','veganism','water'],
    "health_medicine": ['AIDS','Surgery','Vaccines','Women Health','addiction','brain','cancer','coronavirus','disease','ebola','health','health care','heart','heart health','medical imaging','medical research','medicine','menopause','mental health','neurology','pain','pandemic','public health','reproductive health','sleep','ted health podcast','therapy','virus'],
    "history_heritage": ['Africa','Asia','Egypt','Europe','Middle East','South America','United States','ancient world','anthropology','archaeology','black history','black history month','china','history','india'],
    "law_justice": ['corruption','crime','government','human rights','justice system','law','policy','prison','protest','refugees','surveillance'],
    "media_communication": ['TED Books','TV','body language','books','communication','interview','journalism','language','media','podcast','public speaking','social media','storytelling','ted health podcast','television','writing'],
    "personal_development": ['compassion','emotions','empathy','fear','happiness','humor','identity','meditation','memory','mindfulness','motivation','personal growth','personality','potential','relationships','self','success','trust'],
    "politics_policy": ['activism','behavioral economics','black history','black history month','corruption','democracy','economics','global issues','government','history','international relations','justice system','law','policy','politics','protest','race','terrorism','war'],
    "psychology_therapy": ['PTSD','addiction','cognitive science','depression','mental health','personality','psychology','self','suicide','therapy'],
    "science_research": ['CRISPR','DNA','archaeology','astronomy','bioethics','biology','biomimicry','bionics','biotech','chemistry','cognitive science','evolution','genetics','geology','marine biology','microbiology','neuroscience','paleontology','physics','rocket science','science','science fiction','synthetic biology'],
    "geography_places": ['Antarctica','Asia','Brazil','cities','Europe','Africa','India','Middle East','South America','United States','natural disaster','public space','resources','international development','immigration','refugees','society','culture','environment','maps'],
    "religion_faith": ['Buddhism','Christianity','Hinduism','Islam','Judaism','atheism','religion','spirituality','philosophy','ethics','values','beliefs','community','identity','society','inclusion','diversity','equality','human rights','justice system'],
    "diversity_identity": ['LGBTQIA+','Transgender','gender','feminism','women','women in business','race','black history','black history month','disability','Autism spectrum disorder','inclusion','diversity','equality','human rights','identity','vulnerability','ageing','aging','sexual violence'],
    "social_change": ['activism','cancel culture','corruption','culture','ethics','equality','human rights','inclusion','poverty','politics','policy','social change','society','sociology','terrorism','violence','war','international development','refugees','democracy'],
    "culture_entertainment": ['comedy','entertainment','literature','magic','museums','creativity','friendship','future','gaming','ideas','storytelling','sound','sight','smell','toys','books','music','art','performance','film'],
    "science_popular": ['Big Bang','String theory','dinosaurs','microbes','bacteria','fungi','insects','primates','astrobiology','forensics','science','biology','chemistry','physics','discovery','evolution','genetics','archaeology','natural disaster','disease'],
    "technology_society": ['3D printing','computers','metaverse','nanotechnology','online privacy','gaming','math','technology','AI','Internet','code','blockchain','cyber security','virtual reality','innovation','science fiction','digital','software','robots','robotics'],
    "health_society": ["Alzheimer's",'Women Health','Autism spectrum disorder','ageing','aging','blindness','disability','illness','pregnancy','parenting','special violence','vulnerability','sex','mental health','therapy','disease','virus','pandemic','health','medicine'],
    "space_astronomy": ['Mars','Moon','NASA','Planets','Sun','aliens','asteroid','astronomy','dark matter','public space','rocket science','solar system','space','telescopes','universe'],
    "sports_fitness": ['athletics','competition','exercise','human body','motivation','performance','soccer','sports'],
    "technology_ai": ['AI','Internet','NFTs','algorithm','artificial intelligence','augmented reality','blockchain','code','cryptocurrency','cyber security','data','encryption','machine learning','quantum','software','tech','technology','virtual reality'],
    "transportation_travel": ['exploration','flight','geography','maps','ocean','public space','rocket science','transportation','travel'],
}

# Initialize FastMCP server
mcp = FastMCP(
    "shiftx-server",
    host="0.0.0.0",
    port=8443,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False,),
)

# ============================================================
# RESOURCES
# ============================================================

@mcp.resource("shiftx://categories")
async def get_categories() -> str:
    """Exposes all macrocategories and their associated tag arrays in JSON."""
    return json.dumps(CATEGORY_TO_TAGS, indent=2)

# ============================================================
# PROMPTS
# ============================================================

@mcp.prompt()
def get_macro_category(job: str) -> str:
    """Template to classify a job into a single macrocategory."""
    categories_list = list(CATEGORY_TO_TAGS.keys())
    return (
        f"Sei un classificatore di ruoli professionali per Shift-X.\n"
        f"Dato il lavoro '{job}', individua a quale delle seguenti macrocategorie appartiene:\n"
        f"{categories_list}\n\n"
        f"Rispondi fornendo ESCLUSIVAMENTE il nome della macrocategoria (es. 'technology_ai'). "
        f"Non aggiungere commenti, spiegazioni, virgolette o formattazione markdown."
    )

@mcp.prompt()
def get_relevant_tags(job: str, category: str) -> str:
    """Template to select relevant tags for a job within a given category."""
    tags_list = CATEGORY_TO_TAGS.get(category, [])
    return (
        f"Sei un analizzatore di competenze per Shift-X.\n"
        f"Dato il lavoro '{job}' classificato nella macrocategoria '{category}', "
        f"seleziona i tag più attinenti tra quelli disponibili:\n"
        f"{tags_list}\n\n"
        f"Regole:\n"
        f"1. Seleziona SOLO tag presenti nella lista sopra.\n"
        f"2. Decidi tu il numero di tag (N) basandoti solo sulla reale attinenza.\n"
        f"3. Rispondi ESCLUSIVAMENTE con un array JSON contenente le stringhe dei tag (es. [\"AI\", \"machine learning\"]). "
        f"Non includere blocchi di codice markdown (tipo ```json) o altro testo."
    )

# ============================================================
# TOOLS
# ============================================================

@mcp.tool()
async def get_talks_and_playlist(category: str, tags: list[str], limit: int = 10) -> list[dict]:
    """
    Queries MongoDB for talks matching a category and tags.
    Calculates overlap scores and returns a sorted playlist.
    """
    print(f"Tool called: get_talks_and_playlist(category={category}, tags={tags})")
    
    # Normalize tags to lowercase for consistent comparison
    normalized_tags = [t.lower() for t in tags]
    
    # Fetch talks matching the category and containing at least one of the tags
    cursor = collection.find(
        {
            "best_category": category,
            "tags": {"$in": tags}
        },
        {
            "_id": 1,
            "slug": 1,
            "title": 1,
            "speakers": 1,
            "url": 1,
            "description": 1,
            "duration": 1,
            "publishedAt": 1,
            "image_url": 1,
            "tags": 1,
            "best_category": 1
        }
    )
    
    candidates = await cursor.to_list(length=100)
    if not candidates:
        return []
        
    scored_candidates = []
    for talk in candidates:
        talk_tags = talk.get("tags", [])
        if not isinstance(talk_tags, list):
            talk_tags = []
            
        talk_tags_lower = {t.lower() for t in talk_tags if t}
        overlap = len(talk_tags_lower.intersection(normalized_tags))
        
        scored_candidates.append({
            "_id": str(talk["_id"]),
            "slug": talk.get("slug", ""),
            "title": talk.get("title", ""),
            "speakers": talk.get("speakers", ""),
            "url": talk.get("url", ""),
            "description": talk.get("description", ""),
            "duration": talk.get("duration", ""),
            "publishedAt": talk.get("publishedAt", ""),
            "image_url": talk.get("image_url", ""),
            "tags": talk_tags,
            "best_category": talk.get("best_category", ""),
            "score": overlap
        })
        
    # Sort by score (descending) and publishedAt (descending)
    scored_candidates.sort(key=lambda x: (x["score"], x.get("publishedAt") or "1970-01-01"), reverse=True)
    
    return scored_candidates[:limit]

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    ssl_key = "key.pem"
    ssl_cert = "cert.pem"
    
    # Check/Generate Self-Signed SSL Certificates
    if not os.path.exists(ssl_key) or not os.path.exists(ssl_cert):
        print("Generating self-signed SSL certificates for HTTPS local dev...")
        try:
            # Programs often have openssl installed via Git Bash
            import subprocess
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:4096", "-nodes",
                "-keyout", ssl_key, "-out", ssl_cert, "-days", "365",
                "-subj", "/CN=127.0.0.1", "-addext", "subjectAltName=IP:127.0.0.1"
            ], check=True)
            print("✓ Certificates generated successfully (key.pem, cert.pem).")
        except Exception as e:
            print(f"Could not generate certificates automatically: {e}")
            print("Please generate key.pem and cert.pem manually using openssl or disable SSL configuration in uvicorn.")
            
    print("Starting Shift-X MCP Server...")
    uvicorn.run(
        mcp.streamable_http_app(),
        host="0.0.0.0",
        port=8443,
        ssl_keyfile=ssl_key if os.path.exists(ssl_key) else None,
        ssl_certfile=ssl_cert if os.path.exists(ssl_cert) else None,
    )
