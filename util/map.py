import json

with open('DestinyActivityDefinition.json', 'r') as file:
    full_dict = json.load(file)

def map_name(key, dict=full_dict, *args, **kwargs):

    activity = dict['{}'.format(key)]
    map_name = activity['displayProperties']['name']

    return map_name

if __name__ == '__main__':
    print(map_name(2591737171))
