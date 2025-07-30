import argparse

from json_validator_cli.core import process_json

def main():
    # Setup the argument parser
    parser = argparse.ArgumentParser(
        description='JSON Validator / Beautifier CLI Tool'
    )
    
    # Define the mutually exclusive cli input i.e. we either accept --json or --file
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--json', help='Raw JSON string')
    input_group.add_argument('--file', help='Path of the input JSON File')
    
    # Features we offer
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    parser.add_argument('--minify', action='store_true', help='Minify JSON')
    parser.add_argument('--validate', action='store_true', help='Validate JSON only')
    parser.add_argument('--output', help='Write result to file')
    parser.add_argument('--clipboard', action='store_true', help='Copy output to clipboard')
    parser.add_argument('--color', action='store_true', help='Colorize output using rich')
    
    args = parser.parse_args()
    
    process_json(args)
