"""
Shift-X FastAPI Backend Orchestrator
Acts as the REST API gateway for Flutter.
Connects locally to Ollama and remotely to the MCP Server on AWS EC2.
"""

import os
import re
import json
import httpx
import ollama
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# --- Config ---
SERVER_URL = "https://54.210.221.104:8443/mcp"
OLLAMA_MODEL = "llama3.2:3b"

# Global variables to store the session context
mcp_session = None
client_context = None

def insecure_httpx_client(headers=None, timeout=None, auth=None):
    """httpx client factory that skips TLS verification (required for remote self-signed certs)."""
    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout if timeout else httpx.Timeout(45.0),
        auth=auth,
        verify=False,
        follow_redirects=True,
    )

def clean_json_response(raw_text: str) -> list[str]:
    """Cleans and parses a JSON array output from Ollama."""
    cleaned = raw_text.strip()
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
            
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            # If LLM wrapped it in a dict (e.g. {"cuoco": [...]}), extract the list value
            for val in data.values():
                if isinstance(val, list):
                    return val
            return list(data.keys())
        return data if isinstance(data, list) else [str(data)]
    except Exception:
        # Regex fallback
        tags = re.findall(r'"([^"]+)"', cleaned)
        if not tags:
            tags = re.findall(r"'([^']+)'", cleaned)
        return tags

# Helpers to manage dynamic connection and reconnection
async def get_mcp_session():
    global mcp_session, client_context
    if mcp_session is None:
        print(f"🔗 Connessione al server MCP remoto ({SERVER_URL})...")
        client_context = streamablehttp_client(
            SERVER_URL,
            httpx_client_factory=insecure_httpx_client,
        )
        read, write, _ = await client_context.__aenter__()
        mcp_session = ClientSession(read, write)
        await mcp_session.__aenter__()
        await mcp_session.initialize()
        print("✓ Connessione al server MCP riuscita ed inizializzata.")
    return mcp_session

async def close_mcp_session():
    global mcp_session, client_context
    print("🔌 Chiusura sessione MCP...")
    try:
        if mcp_session:
            await mcp_session.__aexit__(None, None, None)
    except Exception as e:
        print(f"Non-critical error closing session: {e}")
    try:
        if client_context:
            await client_context.__aexit__(None, None, None)
    except Exception as e:
        print(f"Non-critical error closing context: {e}")
    mcp_session = None
    client_context = None

# Lifespan context manager to manage MCP connection startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await get_mcp_session()
    except Exception as e:
        print(f"⚠️ Errore nel tentativo di connessione iniziale: {e}")
    yield
    await close_mcp_session()
    print("✓ Risorse liberate.")

app = FastAPI(lifespan=lifespan)

# Enable CORS so the Android Emulator (or web frontend) can query this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobRequest(BaseModel):
    job: str

@app.get("/health")
def health():
    return {"status": "ok", "mcp_connected": mcp_session is not None}

@app.post("/career-path")
async def get_career_playlist(req: JobRequest):
    job = req.job.strip()
    
    if not job:
        raise HTTPException(status_code=400, detail="Il parametro 'job' è obbligatorio e non può essere vuoto.")
        
    try:
        session = await get_mcp_session()
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Impossibile stabilire la connessione con l'MCP server: {e}"
        )
        
    print(f"\n⚡ Ricevuto job: '{job}'")
    
    try:
        # --- Step 1: Classify job to category using local Ollama ---
        try:
            print("⏳ Classificazione macrocategoria...")
            prompt_res = await session.get_prompt("get_macro_category", arguments={"job": job})
        except Exception as e:
            print(f"⚠️ Sessione MCP persa o scaduta ({e}). Tentativo di riconnessione in corso...")
            await close_mcp_session()
            session = await get_mcp_session()
            print("⏳ Classificazione macrocategoria (riprovato)...")
            prompt_res = await session.get_prompt("get_macro_category", arguments={"job": job})
            
        prompt_text = "".join(
            msg.content.text if hasattr(msg.content, "text") else str(msg.content)
            for msg in prompt_res.messages
        )
        
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt_text.strip()}]
        )
        category = response["message"]["content"].strip().lower()
        category = category.replace('"', '').replace("'", "").strip()
        if category.endswith('.'):
            category = category[:-1]
            
        print(f"🎯 Categoria determinata: {category}")
        
        # --- Step 2: Select tags using local Ollama ---
        print("⏳ Selezione tag attinenti...")
        prompt_res = await session.get_prompt("get_relevant_tags", arguments={"job": job, "category": category})
        prompt_text = "".join(
            msg.content.text if hasattr(msg.content, "text") else str(msg.content)
            for msg in prompt_res.messages
        )
        
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt_text.strip()}]
        )
        raw_tags = response["message"]["content"].strip()
        tags = clean_json_response(raw_tags)
        
        print(f"🏷️  Tag selezionati: {tags}")
        
        # --- Step 3: Call the tool on the remote MCP Server to fetch talks ---
        print("⏳ Query al database remoto...")
        result = await session.call_tool(
            "get_talks_and_playlist",
            arguments={"category": category, "tags": tags, "limit": 10}
        )
        
        talks = []
        for item in result.content:
            if hasattr(item, "text"):
                try:
                    talk_data = json.loads(item.text)
                    if isinstance(talk_data, list):
                        talks.extend(talk_data)
                    else:
                        talks.append(talk_data)
                except Exception as e:
                    print(f"⚠️ Errore nel parsing di un talk: {e}")
                    
        print(f"✓ Playlist generata con successo. Trovati {len(talks)} talk.")
        
        # Return format matches exactly the format of Project 3
        return {
            "job": job,
            "category": category,
            "tags": tags,
            "count": len(talks),
            "playlist": talks
        }
        
    except Exception as e:
        print(f"❌ Errore durante la generazione della playlist: {e}")
        # Make sure to reset session if it failed due to a protocol/network error mid-flight
        if "terminated" in str(e).lower():
            await close_mcp_session()
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

if __name__ == "__main__":
    # Disable SSL Insecure Warnings (for self-signed cert on remote EC2)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("Avvio del server backend API di Shift-X...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
