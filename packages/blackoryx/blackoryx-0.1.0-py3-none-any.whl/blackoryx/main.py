from blackoryx.parser import parse_oryx_script
from blackoryx.engine import run_oryx
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: blackoryx <path-to-.oryx-script>")
        return

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    print(f"📜 Parsing Oryx script: {filepath}")
    commands = parse_oryx_script(filepath)

    if not commands:
        print("⚠️ No commands found or missing Run().")
        return

    run_oryx(commands)
