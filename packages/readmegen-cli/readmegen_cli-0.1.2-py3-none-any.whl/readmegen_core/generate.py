import os
from dotenv import load_dotenv
import google.generativeai as genai
from readmegen_core.local_inspector import extract_local_metadata

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # ✅ Configure once

if not os.getenv("GEMINI_API_KEY"):
    raise EnvironmentError("❌ GEMINI_API_KEY not found. Please set it in a .env file.")


model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ No api_key here

def generate_from_local(prompt=""):
    metadata = extract_local_metadata()
    name = metadata["name"]
    languages = metadata["languages"]
    files = metadata["files"]

    gen_prompt = f"""
You are an expert technical writer.

Generate a clean, professional `README.md` for a project.

🔹 **Project Name**: {name}
🧠 **Languages**: {', '.join(languages.keys())}
📝 **Custom Instructions**: {prompt or 'None'}

📄 **Important Files**:
{chr(10).join(['- ' + f['path'] for f in files[:10]])}

🔽 README Must Include:
1. Title
2. Description (2–3 paras)
3. Features
4. Installation
5. Usage with code
6. Technologies table
7. License
8. No folder structure
"""

    response = model.generate_content(gen_prompt)
    return response.text
