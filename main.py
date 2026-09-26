import sys
import argparse
import subprocess
import platform
import os
import ai_engine  # Hacker 2's masterpiece
from rich.console import Console

console = Console()

def get_system_context():
    """Gathers OS and Shell details to help the AI write the correct commands."""
    os_name = f"{platform.system()} {platform.release()}"
    
    # Try to guess the shell (Bash, Zsh, PowerShell)
    shell = os.environ.get('SHELL', '')
    if not shell:
        shell = os.environ.get('COMSPEC', 'Unknown Shell')
        
    return f"OS: {os_name} | Shell: {shell}"

def read_log_tail(filepath, lines=30):
    """Reads the last N lines of a log file for the --log feature."""
    try:
        with open(filepath, 'r') as f:
            return "".join(f.readlines()[-lines:])
    except FileNotFoundError:
        return f"Error: The log file {filepath} does not exist."
    except Exception as e:
        return f"Error reading log file: {str(e)}"

def handle_ai_response(error_text, context):
    """Passes data to Hacker 2's engine and handles Hacker 3's UI & execution."""
    console.print("\n[bold red]🚨 Error Detected![/bold red] [dim]Analyzing with AI...[/dim]")
    
    raw_response = ai_engine.call_gemini(context, error_text)
    
    extracted_cmd = ai_engine.extract_command(raw_response)
    clean_explanation = ai_engine.get_clean_explanation(raw_response)
    
    # Hacker 3's UI Formatting
    formatted_explanation = clean_explanation.replace('<HL>', '[bold red]').replace('</HL>', '[/bold red]')
    console.print(f"\n[yellow]Diagnosis:[/yellow] {formatted_explanation}")
    
    # The Auto-Execute Engine
    if extracted_cmd:
        console.print(f"\n[bold green][?] Suggested Fix:[/bold green]")
        console.print(f"    [bold white on black] {extracted_cmd} [/bold white on black]\n")
        
        try:
            choice = input("Run this command automatically? [Y/n]: ").strip().lower()
            if choice == 'y' or choice == '':
                console.print("[dim]Executing...[/dim]")
                subprocess.run(extracted_cmd, shell=True)
        except KeyboardInterrupt:
            console.print("\n[dim]Aborted by user.[/dim]")

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Terminal Error Interpreter")
    parser.add_argument("--log", help="Analyze the end of a specific log file instead of a command")
    # REMAINDER catches everything else (e.g., 'gcc main.c -o main')
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The command you want to wrap")
    
    args = parser.parse_args()
    context = get_system_context()

    # PATH A: The Log Analyzer
    if args.log:
        console.print(f"[dim]Analyzing log file: {args.log}[/dim]")
        log_data = read_log_tail(args.log)
        
        if log_data.startswith("Error"):
            console.print(f"[bold red]{log_data}[/bold red]")
            sys.exit(1)
            
        handle_ai_response(log_data, context)
        sys.exit(0)

    # PATH B: The Subprocess Wrapper
    if args.command:
        # Rebuild the command list into a single string if needed, or pass as list
        # We pass as string with shell=True to respect local aliases and paths
        cmd_str = " ".join(args.command)
        
        try:
            # Run the command and let stdout flow normally to the terminal
            # Only capture stderr so we can analyze it if it fails
            result = subprocess.run(
                cmd_str, 
                shell=True, 
                text=True, 
                stderr=subprocess.PIPE
            )
            
            if result.returncode != 0:
                # Command failed! Send the intercepted stderr to the AI.
                error_output = result.stderr.strip()
                # Sometimes errors print to stdout instead, fallback check:
                if not error_output: 
                    error_output = f"Command exited with code {result.returncode}"
                    
                handle_ai_response(error_output, context)
            
        except Exception as e:
            console.print(f"[bold red]Failed to execute command:[/bold red] {str(e)}")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()