import os

with open('.gitignore', 'w', encoding='utf-8') as f:
    f.write(".venv/\n")
    f.write("__pycache__/\n")
    f.write("*.pyc\n")
    f.write(".DS_Store\n")
    
    # Ignore large files
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            try:
                if os.path.getsize(filepath) > 40 * 1024 * 1024:
                    # Convert backslash to slash
                    git_path = filepath.replace('\\', '/').lstrip('./')
                    f.write(f"{git_path}\n")
            except OSError:
                pass
