import argparse
from readmegen_core.generate import generate_from_local

def main():
    parser = argparse.ArgumentParser(description="Generate README.md from local project using AI")
    parser.add_argument('--prompt', default="", help="Custom instructions")

    args = parser.parse_args()

    try:
        readme = generate_from_local(args.prompt)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme)
        print("✅ README.md generated successfully!")
    except Exception as e:
        print("❌ Error:", e)
