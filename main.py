import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Systems Engineer CLI"
    )

    parser.add_argument(
        "--log",
        metavar="FILE",
        help="Read the last 30 lines of a log file"
    )

    parser.add_argument(
        "command",
        nargs="*",
        help="Command to execute"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.log:
        print(read_log_tail(args.log))

    elif args.command:
        result = run_subprocess(args.command)
        print(result)

    else:
        print("No command or --log argument provided.")


if __name__ == "__main__":
    main()

import subprocess

def run_subprocess(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "success": False
        }

def read_log_tail(filepath, lines=30):
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as file:
            return "".join(file.readlines()[-lines:])

    except FileNotFoundError:
        return f"Error: Log file not found: {filepath}"

    except PermissionError:
        return f"Error: Permission denied: {filepath}"

    except OSError as e:
        return f"Error reading log file: {e}"

import os
import platform

def get_os_context():
    context = {
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "shell": os.environ.get("SHELL", "Unknown")
    }

    # Detect WSL
    if "microsoft" in platform.release().lower():
        context["environment"] = "WSL"
    else:
        context["environment"] = "Native"

    # Get Linux distribution information
    try:
        with open("/etc/os-release", "r") as file:
            for line in file:
                if line.startswith("PRETTY_NAME="):
                    context["distribution"] = line.strip().split("=", 1)[1].strip('"')
                    break
    except (FileNotFoundError, PermissionError):
        context["distribution"] = "Unknown"

    return context