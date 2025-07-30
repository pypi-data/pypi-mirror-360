import re

def parse_oryx_script(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()

    commands = []
    current_block = {}
    inside_block = False
    current_func = ""

    for line in lines:
        line = line.strip()

        # Skip comments and blanks
        if not line or line.startswith(">="):
            continue

        # Check for Run();
        if line.startswith("Run"):
            if not line.endswith(";"):
                print("❌ Error: Missing semicolon in Run();")
                return []
            commands.append({"type": "run"})
            break

        # Match functions: Add(), Merge(), Del(), Loop()
        func_match = re.match(r"(Add|Del|Merge|Loop)\((.*?)\);", line, re.IGNORECASE)
        if func_match:
            current_func = func_match.group(1).lower()
            func_target = func_match.group(2).strip()

            # Direct commands like Del(), Merge()
            if current_func in ["del", "merge", "loop"]:
                commands.append({
                    "type": current_func,
                    "target": func_target
                })
                continue

            # Start of Add() block
            if current_func == "add":
                current_block = {
                    "type": func_target  # Example: txt, aud, trsn, etc.
                }
                inside_block = True
                continue

        # Inside Add() block, parse [key: value]
        if inside_block and line.startswith("[") and line.endswith("]"):
            content = line[1:-1].strip()

            if ":" in content:
                key, value = content.split(":", 1)
                key = key.strip().lower()
                value = value.strip().strip('"')

                # Handle numbers and time
                if value.endswith("s"):
                    try:
                        value = float(value.replace("s", ""))
                    except:
                        pass
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)

                current_block[key] = value
            continue

        # End of Add() block with semicolon
        if inside_block and line.strip() == ";":
            commands.append(current_block)
            current_block = {}
            inside_block = False
            continue

        print(f"⚠️ Unrecognized or malformed line: {line}")

    return commands
