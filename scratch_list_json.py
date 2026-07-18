import urllib.request
import json

url = "https://api.github.com/repos/southkorea/seoul-maps/git/trees/master?recursive=1"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        for file in data['tree']:
            if 'json' in file['path'].lower():
                print(file['path'])
except Exception as e:
    print(f"Error: {e}")
