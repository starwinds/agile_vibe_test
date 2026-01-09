import requests
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = "nomic-embed-text"

def check_ollama():
    print(f"Checking Ollama at {OLLAMA_BASE_URL}...")
    try:
        # Check tags
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            model_names = [m['name'] for m in models]
            print(f"Available models: {model_names}")
            
            # Check for nomic-embed-text (could be 'nomic-embed-text:latest')
            found = any(OLLAMA_MODEL in m for m in model_names)
            if found:
                print(f"Model '{OLLAMA_MODEL}' found.")
                return True
            else:
                print(f"Model '{OLLAMA_MODEL}' NOT found. Please pull it.")
                return False
        else:
            print(f"Failed to list tags. Status: {resp.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return False

if __name__ == "__main__":
    check_ollama()
