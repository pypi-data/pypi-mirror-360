import os
import json
import pyperclip

from rich.syntax import Syntax
from rich.console import Console

console = Console()

# Helper function to grab the input raw json eithe from file or string
def load_json_from_source(args):
    # Check if args.json i.e. json is provided as raw string
    if args.json:
        return args.json
    
    elif args.file:
        if not os.path.exists(args.file):
            raise FileNotFoundError(f"Input JSON File '{args.file}' not found.")
        
        with open(args.file, 'r') as f:
            return f.read()

def process_json(args):
    try:
        raw_json = load_json_from_source(args)
        raw_object = json.loads(raw_json)
        
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Invalid JSON:[/red] {e}")
        return
    except Exception as e:
        console.print(f"[red]⚠️ Error:[/red] {e}")
        return

    if args.validate:
        console.print("[green]✅ JSON is valid![/green]")
        return
    
    # Checks for the feature requsted
    output = ''
    if args.pretty:
        output = json.dumps(raw_object, indent=4)
    elif args.minify:
        output = json.dumps(raw_object, separators=(',', ':'))
    else:
        output = json.dumps(raw_object)
    
    if args.color:
        syntax = Syntax(output, "json", theme="monaki", line_numbers=False)
        console.print(syntax)
    else:
        print(output)
        

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
            console.print(f"[green]✔ Output written to {args.output}[/green]")
    
    if args.clipboard:
        pyperclip.copy(output)
        console.print("[blue]📋 Copied output to clipboard[/blue]")
    