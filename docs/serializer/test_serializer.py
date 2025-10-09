"""
Test/Example file for the GeneWeb serializer.

Usage:
    python test_serializer.py input.json output.gw

This serves as both a test and an example of how to use the GWSerializer class.
"""

import argparse
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server" / "src" / "serializer"))
from gw_serializer import GWSerializer


def main():
    parser = argparse.ArgumentParser(description="Convert structured JSON to GeneWeb .gw file")
    parser.add_argument("input", help="Input .json file path")
    parser.add_argument("output", help="Output .gw file path")
    args = parser.parse_args()

    print(f"🔄 Serializing {args.input}...")

    # Load JSON file
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create serializer instance
    serializer = GWSerializer(data)
    serializer.to_file(args.output)

    print(f"✅ Successfully serialized {args.input} -> {args.output}")
    print(f"   📄 Output written to: {args.output}")


if __name__ == "__main__":
    main()
