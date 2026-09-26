import subprocess
import platform
import ai_engine  # This imports YOUR file!
from rich.console import Console

console = Console()

def run_mock_test():
    # 1. A command guaranteed to fail on any computer (Windows, Mac, or Linux)
    bad_command = ['python', '-c', 'import missing_library_123']
    
    console.print(f"[dim]Simulating user running: {' '.join(bad_command)}[/dim]")
    
    # 2. Run it and trap the error (This is a preview of Hacker 1's job)
    result = subprocess.run(bad_command, capture_output=True, text=True)
    
    if result.returncode != 0:
        error_text = result.stderr.strip()
        console.print("[bold red]🚨 Terminal Error Intercepted![/bold red] Routing to AI...\n")
        
        # Automatically detect your actual OS (e.g., Windows, Linux, Darwin)
        os_context = f"OS: {platform.system()} {platform.release()}"
        
        # 3. Call YOUR engine
        raw_response = ai_engine.call_gemini(os_context, error_text)
        
        # 4. Extract and Format (Preview of Hacker 3's job)
        extracted_cmd = ai_engine.extract_command(raw_response)
        clean_explanation = ai_engine.get_clean_explanation(raw_response)
        
        # Swap the <HL> tags you generated into real terminal colors
        formatted_explanation = clean_explanation.replace('<HL>', '[bold red]').replace('</HL>', '[/bold red]')
        
        console.print(f"[yellow]AI Diagnosis:[/yellow] {formatted_explanation}")
        
        if extracted_cmd:
            console.print(f"\n[bold green][?] Auto-Fix Command Available:[/bold green]")
            console.print(f"    [bold white on black] {extracted_cmd} [/bold white on black]\n")
    else:
        console.print("[green]Command succeeded (Wait, that wasn't supposed to happen!)[/green]")

if __name__ == "__main__":
    run_mock_test()