import os
import re
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError
from rich.console import Console

client = genai.Client()
console = Console()

SYSTEM_PROMPT = """
You are an expert system administrator debugging terminal errors.
Analyze the provided error log and the user's OS/Environment context.

Respond strictly in two parts:
1. A concise, 1-2 sentence explanation. You MUST wrap the core root cause of the error in <HL> tags so the UI can highlight it.
2. If a terminal command can fix it, provide the exact command wrapped in <EXEC> tags. 
   CRITICAL: The command MUST be native to the user's environment. If the context says Windows/PowerShell, provide a PowerShell command. If Linux/macOS, provide bash.

Example format:
The system blocked the script execution because <HL>the execution policy restricts unsigned scripts</HL>.
<EXEC>Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser</EXEC>
"""

def call_gemini(os_context, error_text, retries=3):
    """Sends the context and error to the SDK with automatic retries for 503s."""
    prompt = f"Environment Context:\n{os_context}\n\nError Output:\n{error_text}"
    
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash', # Upgraded to the faster 3.5 model
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    # THIS LINE KILLS THE ANNOYING AFC WARNING:
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                )
            )
            return response.text.strip()
            
        except APIError as e:
            # If the server is busy, wait and try again silently
            if "503" in str(e) and attempt < retries - 1:
                time.sleep(2 ** attempt) # Waits 1s, then 2s, then gives up
                continue
            return f"API Error: {str(e)}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"

def extract_command(response_text):
    match = re.search(r'<EXEC>(.*?)</EXEC>', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def get_clean_explanation(response_text):
    return re.sub(r'<EXEC>.*?</EXEC>', '', response_text, flags=re.DOTALL).strip()


if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not found in environment.")
        exit(1)
        
    console.print("[cyan]Testing hardened API connection...[/cyan]")
    
    mock_context = "Windows 11 running PowerShell 7"
    mock_error = "File C:\\script.ps1 cannot be loaded because running scripts is disabled on this system."
    
    raw_response = call_gemini(mock_context, mock_error)
    extracted_cmd = extract_command(raw_response)
    explanation_with_hl = get_clean_explanation(raw_response)
    
    print("\n--- WHAT HACKER 3 WILL RENDER TO THE USER ---")
    
    formatted_explanation = explanation_with_hl.replace('<HL>', '[bold red]').replace('</HL>', '[/bold red]')
    console.print(f"[yellow]Explanation:[/yellow] {formatted_explanation}")
    
    if extracted_cmd:
        console.print(f"\n[bold green][?] Suggested Fix (Ready to run):[/bold green]")
        console.print(f"    [bold white on black] {extracted_cmd} [/bold white on black]")