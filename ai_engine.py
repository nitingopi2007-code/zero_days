import urllib.request
import json

# TODO: Replace with your actual deployed Vercel URL
API_URL = "https://repo-p2rgmo3v6-reachsahil2007-6406.vercel.app/api/diagnose"

def call_gemini(os_context, error_text):
    """Sends the context and error to your Vercel server."""
    payload = json.dumps({"context": os_context, "error": error_text}).encode('utf-8')
    req = urllib.request.Request(API_URL, data=payload, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP Error {e.code}"}
    except Exception as e:
        return {"error": str(e)}

def extract_command(response_dict):
    # The server already parsed the regex, we just grab the dictionary key
    return response_dict.get("command")

def get_clean_explanation(response_dict):
    # Returns the explanation, or the error message if the API failed
    return response_dict.get("explanation", response_dict.get("error", "Unknown API Error"))