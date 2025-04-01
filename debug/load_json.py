import json

# Load JSON data from a file
with open('data.json', 'r') as file:
    data = json.load(file)

print(data["key1"])
