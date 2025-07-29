import os
import re
from typing import Dict, List, Optional

def extract_local_metadata(base_path: str = ".") -> Dict:
    """
    Extract comprehensive metadata from a project directory.
    Returns a dictionary with project structure, key files, and technology insights.
    """
    metadata = {
        "name": os.path.basename(os.path.abspath(base_path)),
        "description": "",
        "languages": {},
        "dependencies": set(),
        "entry_points": [],
        "key_files": {
            "config": [],
            "source": [],
            "build": [],
            "docs": [],
            "tests": []
        },
        "file_stats": {
            "total_files": 0,
            "total_lines": 0
        }
    }

    # Common file patterns to look for
    KEY_FILE_PATTERNS = {
        "config": [r'^package\.json$', r'^pyproject\.toml$', r'^setup\.py$', r'^requirements\.txt$'],
        "build": [r'^Dockerfile$', r'^Makefile$', r'^build\.gradle$'],
        "docs": [r'^docs?/', r'^README\.md$', r'^CHANGELOG\.md$'],
        "tests": [r'^tests?/', r'^specs?/', r'^__tests__/']
    }

    def classify_file(path: str) -> Optional[str]:
        """Classify files into categories based on patterns"""
        rel_path = os.path.relpath(path, base_path)
        for category, patterns in KEY_FILE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, rel_path, re.IGNORECASE):
                    return category
        if any(ext in path.lower() for ext in ['.py', '.js', '.ts', '.java', '.go', '.rs']):
            return "source"
        return None

    for root, _, files in os.walk(base_path):
        # Skip common directories
        if any(dir in root for dir in ['__pycache__', 'node_modules', '.git', '.venv']):
            continue

        for f in files:
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, base_path)
            
            # Skip hidden files and large files
            if f.startswith('.') or os.path.getsize(file_path) > 100000:
                continue

            metadata["file_stats"]["total_files"] += 1
            
            # Classify and process file
            file_category = classify_file(file_path)
            if file_category:
                metadata["key_files"][file_category].append(rel_path)
                
                # Special processing for certain files
                if file_category == "config":
                    process_config_file(file_path, metadata)
                elif file_category == "source":
                    process_source_file(file_path, metadata)
            
            # Count lines and extract basic info
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    metadata["file_stats"]["total_lines"] += len(lines)
                    
                    # Detect language from file extension
                    ext = os.path.splitext(f)[1][1:]
                    if ext:
                        metadata["languages"][ext] = metadata["languages"].get(ext, 0) + 1
            except:
                continue

    return metadata

def process_config_file(file_path: str, metadata: Dict) -> None:
    """Extract dependencies and metadata from config files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Python projects
            if file_path.endswith('requirements.txt'):
                deps = [line.strip() for line in content.split('\n') 
                       if line.strip() and not line.startswith('#')]
                metadata["dependencies"].update(deps)
            
            # Node.js projects
            elif file_path.endswith('package.json'):
                if '"dependencies"' in content:
                    deps = re.findall(r'"dependencies"\s*:\s*\{([^}]+)\}', content)
                    if deps:
                        dep_matches = re.findall(r'"([^"]+)"\s*:\s*"[^"]+"', deps[0])
                        metadata["dependencies"].update(dep_matches)
    except:
        pass

def process_source_file(file_path: str, metadata: Dict) -> None:
    """Analyze source files for important patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Detect entry points (main functions, app declarations)
            if re.search(r'(def\s+main\(|if\s+__name__\s*==\s*[\'"]__main__[\'"])', content):
                metadata["entry_points"].append(os.path.relpath(file_path, metadata["name"]))
                
            # Detect class and function definitions
            class_matches = re.findall(r'class\s+(\w+)', content)
            fn_matches = re.findall(r'def\s+(\w+)', content)
            if class_matches or fn_matches:
                if "code_structure" not in metadata:
                    metadata["code_structure"] = []
                metadata["code_structure"].extend(class_matches + fn_matches)
    except:
        pass