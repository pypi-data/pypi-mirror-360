import argparse
import os
from typing import Optional
from readmegen_core.generate import generate_from_local
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description="Generate professional README.md files using AI analysis",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory"
    )
    parser.add_argument(
        "--prompt",
        default="",
        help="Additional instructions for README generation"
    )
    parser.add_argument(
        "--output",
        default="README.md",
        help="Output file name/path"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing README without backup"
    )
    
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: Path '{args.path}' is not a valid directory")
        return 1

    output_path = os.path.join(args.path, args.output)
    
    # Handle existing README
    if os.path.exists(output_path) and not args.overwrite:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{output_path}.bak.{timestamp}"
        os.rename(output_path, backup_path)
        print(f"Existing README backed up to: {backup_path}")

    try:
        print(f"Analyzing project at: {os.path.abspath(args.path)}")
        print("This may take a moment...")
        
        readme_content = generate_from_local(args.prompt)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
            
        print(f"Successfully generated: {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
        return 0
        
    except Exception as e:
        print(f"Error generating README: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())