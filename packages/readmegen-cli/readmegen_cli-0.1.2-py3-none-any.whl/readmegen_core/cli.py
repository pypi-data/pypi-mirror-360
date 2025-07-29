# readmegen_core/cli.py

import argparse
from readmegen_core.generate import generate_from_local
import os

def main():
    parser = argparse.ArgumentParser(description="Generate README.md from a local project using Gemini AI")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    parser.add_argument(
        "--prompt",
        default="",
        help="Custom instructions to include in the README"
    )
    args = parser.parse_args()

    # Change the working directory
    if not os.path.isdir(args.path):
        print(f"❌ The path {args.path} is not a valid directory.")
        return

    try:
        print(f"📁 Scanning directory: {args.path}")
        os.chdir(args.path)  # Change to the specified directory
        readme = generate_from_local(args.prompt)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme)
        print("✅ README.md generated successfully in:", os.getcwd())
    except Exception as e:
        print("❌ Error:", e)
