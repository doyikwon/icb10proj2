import folium
import json

# create dummy geojson
dummy_geo = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "id": "1", "properties": {"name": "A", "pop": "100"}, "geometry": {"type": "Point", "coordinates": [0,0]}}
    ]
}

m = folium.Map()
cp = folium.Choropleth(geo_data=dummy_geo, data=[("1", 100)], columns=[0, 1], key_on="feature.id")
cp.add_to(m)

folium.GeoJsonTooltip(
    fields=['name', 'pop'],
    aliases=['Region', 'Population']
).add_to(cp.geojson)

print("Success")
