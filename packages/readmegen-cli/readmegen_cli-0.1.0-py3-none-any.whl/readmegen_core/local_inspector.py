import os

def extract_local_metadata(base_path="."):
    metadata = {
        "name": os.path.basename(os.path.abspath(base_path)),
        "description": "",
        "languages": {},
        "files": []
    }

    ext_count = {}
    for root, _, files in os.walk(base_path):
        for f in files:
            if f.startswith('.') or len(f) > 60:
                continue
            path = os.path.join(root, f)
            if f.endswith(('.py', '.js', '.md', '.json', '.toml', '.sh', '.txt')):
                try:
                    with open(path, encoding='utf-8') as file:
                        content = file.read()
                    metadata["files"].append({
                        "path": os.path.relpath(path, base_path),
                        "content": content[:1000]
                    })
                except:
                    continue

                ext = f.split('.')[-1]
                ext_count[ext] = ext_count.get(ext, 0) + 1

    metadata["languages"] = ext_count
    return metadata
