maps_dict = {
    332234118 : "Vostok",
    399506119 : "Endless Vale",
    532383918 : "Radiant Cliffs",
    750001803 : "Altar of Flame",
    777592567 : "Midtown",
    778271008 : "Emperor's Respite",
    1448435553 : "Emperor's Respite",
    806094750 : "Javelin-4",
    1003889713 : "Javelin-4",
    2233665874 : "Eternity",
    3734723183 : "Eternity",
    2262757213 : "Solitude",
    2473919228 : "Meltdown",
    2591737171 : "Gambler's Ruin",
    2666761222 : "Distant Shore",
    2748633318 : "Wormhaven",
    2810171920 : "Bannerfall",
    3164915257 : "The Dead Cliffs",
    3292922825 : "Firebase Echo",
    3404623499 : "The Citadel",
    3849796864 : "Retribution",
    4012915511 : "The Burnout",
    1153409123 : "Convergence",
    1583254851 : "The Fortress",
    1673114595 : "Pacifica",
    3233852802 : "Pacifica",
    1711620427 : "Legion's Gulch",
    1815340083 : "Equinox"
}

modes_dict = {
    15 : "Crimson Doubles",
    19 : "IronBanner",
    25 : "Mayhem",
    31 : "Supremacy",
    32 : "PrivateMatchesAll",
    37 : "Survival",
    38 : "Countdown",
    39 : "Trials",
    41 : "Trials Countdown",
    42 : "Trials Survival",
    43 : "IB Control",
    44 : "IB Clash",
    45 : "IB Supremacy",
    48 : "Rumble",
    49 : "All Doubles",
    50 : "Doubles",
    51 : "PM Clash",
    52 : "PM Control",
    53 : "PM Supremacy",
    54 : "PM Countdown",
    55 : "PM Survival",
    56 : "PM Mayhem",
    57 : "PM Rumble",
    59 : "Showdown",
    60 : "Lockdown",
    61 : "Scorched",
    62 : "ScorchedTeam",
    65 : "Breakthrough",
    67 : "Salvage",
    68 : "IB Salvage",
    69 : "Comp",
    70 : "Quickplay",
    71 : "QP Clash",
    72 : "Comp Clash",
    73 : "QP Control",
    74 : "Comp Control"
}
if __name__ == '__main__':

    # import requests
    # from secrets import *
    import json
    # base_url = 'https://www.bungie.net/'
    # manifest = json.loads(requests.get(base_url+'Platform/Destiny2/Manifest', headers=headers).content)
    #
    # data = json.loads(requests.get(base_url+'/common/destiny2_content/json/en/aggregate-89d70fba-f402-4c33-a6a2-3cc5f92bdb82.json', headers=headers).content)
    # data = data['DestinyActivityDefinition']
    # with open('DestinyActivityDefinition.json', 'w') as outfile:
    #     json.dump(data, outfile)

    with open('DestinyActivityDefinition.json', 'r') as outfile:
        data = json.load(outfile)
        pass