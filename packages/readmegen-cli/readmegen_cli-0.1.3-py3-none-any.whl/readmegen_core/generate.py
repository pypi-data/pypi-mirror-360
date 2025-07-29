import os
from dotenv import load_dotenv
import google.generativeai as genai
from readmegen_core.local_inspector import extract_local_metadata
from typing import Dict

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_from_local(prompt: str = "") -> str:
    """Generate a comprehensive README based on project analysis"""
    metadata = extract_local_metadata()
    
    # Prepare the AI prompt with structured project information
    gen_prompt = f"""
You are an expert technical writer specialized in creating professional README files for open source projects.

# Project Analysis Summary:
- **Project Name**: {metadata.get('name', 'Untitled Project')}
- **Primary Languages**: {', '.join(metadata.get('languages', {}).keys()) or 'Not detected'}
- **Total Files**: {metadata.get('file_stats', {}).get('total_files', 0)}
- **Total Lines of Code**: {metadata.get('file_stats', {}).get('total_lines', 0)}
- **Key Dependencies**: {', '.join(metadata.get('dependencies', [])) or 'None detected'}

# Key Files Detected:
{format_key_files(metadata.get('key_files', {}))}

# Custom Instructions:
{prompt or 'No additional instructions provided'}

# README Generation Guidelines:
1. Create a comprehensive, professional README.md file
2. Structure should include:
   - Project title with badge placeholders
   - Clear, concise description (2-3 paragraphs)
   - Features section with bullet points
   - Installation instructions (multiple methods if applicable)
   - Usage examples with code blocks
   - Configuration options if any config files found
   - API documentation if applicable
   - Contribution guidelines
   - License information
3. Use markdown formatting with proper headings
4. Include placeholders for CI/CD badges if appropriate
5. Make it engaging and professional
6. For CLI tools, include command examples
7. For libraries, include import/usage examples
8. Keep technical level appropriate for the project type
"""
    response = model.generate_content(gen_prompt)
    return response.text

def format_key_files(key_files: Dict) -> str:
    """Format key files information for the prompt"""
    sections = []
    for category, files in key_files.items():
        if files:
            sections.append(f"## {category.upper()} FILES:")
            sections.extend(f"- {f}" for f in files[:5])  # Limit to top 5 per category
            if len(files) > 5:
                sections.append(f"- ...and {len(files)-5} more")
    return '\n'.join(sections) if sections else "No key files detected"