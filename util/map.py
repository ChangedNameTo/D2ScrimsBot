import json

with open('./util/DestinyActivityDefinition.json', 'r') as file:
    full_dict = json.load(file)

def map_name(key, activity_dict=full_dict, *args, **kwargs):

    activity = activity_dict['{}'.format(key)]
    map_name = activity['displayProperties']['name']

    return map_name

if __name__ == '__main__':
    print(map_name(2591737171))
