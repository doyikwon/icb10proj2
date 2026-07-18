import urllib.request
import json

url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_neighborhoods_geo_simple.json"
try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        print(data['features'][0]['properties'])
except Exception as e:
    print(f"Error: {e}")
