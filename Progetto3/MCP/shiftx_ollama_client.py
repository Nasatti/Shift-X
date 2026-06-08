"""
Shift-X Ollama + MCP Client
Interacts with the user, queries Ollama for categorization & tags,
and calls the MCP server to retrieve matching talks from MongoDB Atlas.
"""

import asyncio
import json
import ssl
import sys
import re
import httpx
import ollama

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# --- Config ---
SERVER_URL = "https://54.210.221.104:8443/mcp"
OLLAMA_MODEL = "llama3.2:3b"  # Ensure you ran `ollama pull llama3.2`

def insecure_httpx_client(headers=None, timeout=None, auth=None):
    """httpx client factory that skips TLS verification (required for self-signed certificates)."""
    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout if timeout else httpx.Timeout(30.0),
        auth=auth,
        verify=False,
        follow_redirects=True,
    )

def clean_json_response(raw_text: str) -> list[str]:
    """Helper to clean and parse JSON array outputs from LLMs."""
    cleaned = raw_text.strip()
    # Strip markdown code blocks if present
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
        # Regex fallback to find quoted strings
        tags = re.findall(r'"([^"]+)"', cleaned)
        if not tags:
            tags = re.findall(r"'([^']+)'", cleaned)
        return tags

async def run_pipeline(session: ClientSession, job: str):
    print(f"\n🔍 Avvio pipeline Shift-X per: '{job}'...")

    # --- Step 1: Classify Job to Category ---
    print("⏳ Classificazione della macrocategoria...")
    try:
        prompt_res = await session.get_prompt("get_macro_category", arguments={"job": job})
        prompt_text = "".join(
            msg.content.text if hasattr(msg.content, "text") else str(msg.content)
            for msg in prompt_res.messages
        )
    except Exception as e:
        print(f"❌ Errore nel recupero del prompt di classificazione dal server: {e}")
        return

    # Call Ollama for Category
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt_text.strip()}]
    )
    category = response["message"]["content"].strip().lower()
    
    # Basic cleaning
    category = category.replace('"', '').replace("'", "").strip()
    # Remove final dot if LLM added it
    if category.endswith('.'):
        category = category[:-1]

    print(f"🎯 Macrocategoria selezionata dall'LLM: \033[1;32m{category}\033[0m")

    # --- Step 2: Select Relevant Tags ---
    print("⏳ Selezione dei tag più attinenti...")
    try:
        prompt_res = await session.get_prompt("get_relevant_tags", arguments={"job": job, "category": category})
        prompt_text = "".join(
            msg.content.text if hasattr(msg.content, "text") else str(msg.content)
            for msg in prompt_res.messages
        )
    except Exception as e:
        print(f"❌ Errore nel recupero del prompt dei tag dal server: {e}")
        return

    # Call Ollama for Tags
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt_text.strip()}]
    )
    raw_tags = response["message"]["content"].strip()
    tags = clean_json_response(raw_tags)
    
    print(f"🏷️  Tag selezionati dall'LLM ({len(tags)}): \033[1;36m{tags}\033[0m")

    # --- Step 3: Fetch and Display Playlist from MongoDB ---
    print("⏳ Interrogazione del database e ordinamento...")
    try:
        result = await session.call_tool(
            "get_talks_and_playlist",
            arguments={"category": category, "tags": tags, "limit": 10}
        )
    except Exception as e:
        print(f"❌ Errore durante la chiamata al tool get_talks_and_playlist: {e}")
        return

    # Parse and display the results
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

    if not talks:
        print("\n📭 Nessun talk trovato nel database per i tag selezionati in questa categoria.")
        return

    print(f"\n🎧 \033[1;35mPLAYLIST SHIFT-X SUGGERITA ({len(talks)} talk):\033[0m")
    print("=" * 80)
    for idx, talk in enumerate(talks, 1):
        print(f"{idx}. \033[1m{talk['title']}\033[0m")
        print(f"   👤 Speaker: {talk['speakers']} | ⏱️ Durata: {talk['duration']} sec | 📈 Overlap Score: {talk['score']}")
        print(f"   🏷️ Tag: {', '.join(talk['tags'])}")
        print(f"   🔗 URL: {talk['url']}")
        print(f"   📝 Descrizione: {talk['description'][:140]}...")
        print("-" * 80)

async def main():
    print(f"Connessione al server MCP di Shift-X ({SERVER_URL})...")
    try:
        async with streamablehttp_client(
            SERVER_URL,
            httpx_client_factory=insecure_httpx_client,
        ) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✓ Connesso con successo al server MCP.")
                print(f"✓ Modello locale impostato su Ollama: {OLLAMA_MODEL}\n")

                while True:
                    try:
                        job = input("Inserisci un ruolo lavorativo (o premi Invio/scrivi 'exit' per uscire): ").strip()
                        if not job or job.lower() == 'exit':
                            print("Arrivederci!")
                            break
                        await run_pipeline(session, job)
                        print("\n" + "="*80 + "\n")
                    except KeyboardInterrupt:
                        print("\nUscito.")
                        break
                    except Exception as e:
                        print(f"Errore durante l'esecuzione del ciclo: {e}")
    except Exception as e:
        print(f"\n❌ Impossibile connettersi al server MCP su {SERVER_URL}.")
        print("Assicurati che shiftx_server.py sia in esecuzione in un altro terminale.")
        print(f"Dettaglio errore: {e}")

if __name__ == "__main__":
    # Disable SSL Insecure warning since we use self-signed certificates
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Run the client
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
