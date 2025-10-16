"""
Test/Example file for the GeneWeb parser.

Usage:
    python test_parser.py input.gw output.json

This serves as both a test and an example of how to use the GWParser class.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server" / "src"))
from gw_parser import GWParser


def main():
    parser = argparse.ArgumentParser(description="Convert GeneWeb .gw file to structured JSON")
    parser.add_argument("input", help="Input .gw file path")
    parser.add_argument("output", help="Output .json file path")
    args = parser.parse_args()

    print(f"🔄 Parsing {args.input}...")

    # Create parser instance and parse the file
    gw = GWParser(args.input)
    data = gw.parse()

    # Output to JSON file
    gw.to_json(args.output)

    # Print some basic statistics
    families_count = len(data.get("families", []))
    people_count = len(data.get("people", []))
    notes_count = len(data.get("notes", []))

    print(f"✅ Successfully parsed {args.input} -> {args.output}")
    print(f"   📊 Found: {families_count} families, {people_count} people, {notes_count} notes")


if __name__ == "__main__":
    main()
