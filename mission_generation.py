import random
import math
import json

from categories import categories

import googlemaps


GMAPS_API_KEY = 'AIzaSyDHqBdySdfEGwzje_-LFwMbv7R5PLWnTac'
EARTH_RADIUS = 6371000

MISSION_MODEL = 'api.mission'
OBJECTIVE_MODEL = 'api.objective'

NUM_OBJECTIVES_MIN = 1
NUM_OBJECTIVES_MAX = 7

OBJECTIVE_RADIUS = 3000

STARTING_MISSION_ID = 1
STARTING_OBJECTIVE_ID = 1


OUTPUT_FILE_MISSIONS = 'Missions.json'
OUTPUT_FILE_OBJECTIVES = 'Objectives.json'


# https://jordinl.com/posts/2019-02-15-how-to-generate-random-geocoordinates-within-given-radius
def _get_random_coordinate_within_radius(lat, lon, radius):
    lat = math.radians(lat)
    lon = math.radians(lon)

    distance = math.sqrt(random.random() * (radius ** 2))

    delta_lat = math.cos(random.random() * math.pi) * distance / EARTH_RADIUS
    sign = random.choice([-1, 1])
    delta_lon = sign * math.acos((math.cos(distance / EARTH_RADIUS) - math.cos(delta_lat)) / (math.cos(lat) * math.cos(delta_lat + lat)) + 1)

    return_lat = math.degrees(lat + delta_lat)
    return_lon = math.degrees(lon + delta_lon)

    return return_lat, return_lon


def _generate_objective(lat, lon, search_term):
    gmaps = googlemaps.Client(key=GMAPS_API_KEY)

    search = gmaps.places(search_term, location=(lat, lon), radius=OBJECTIVE_RADIUS)

    search_choice = random.choice(search['results'])

    gmaps_id = search_choice['id']
    name = search_choice['name']
    formatted_address = search_choice['formatted_address']
    location_lat = search_choice['geometry']['location']['lat']
    location_lon = search_choice['geometry']['location']['lng']

    objective = {
        gmaps_id: {
            'name': name,
            'formatted_address': formatted_address,
            'latitude': location_lat,
            'longitude': location_lon
    }}

    return objective


def _generate_mission(lat, lon, radius):

    # Pick a random category and number of objectives
    category = random.choice(categories)
    num_objectives = random.randrange(NUM_OBJECTIVES_MIN, NUM_OBJECTIVES_MAX + 1)
    print(f'DEBUG: Category: {category["name"]}, {num_objectives} objectives')

    # Get random coordinate within radius
    gen_lat, gen_long = _get_random_coordinate_within_radius(lat, lon, radius)
    print(f'DEBUG: Gen coordinates: ({gen_lat}, {gen_long})')

    # Generate unique set of objectives
    objectives = []
    while len(objectives) < num_objectives:
        search_term = random.choice(category['types'])
        objective = _generate_objective(gen_lat, gen_long, search_term.replace('_', ' '))

        if objective not in objectives:
            objectives.append(objective)

    # Re-format dictionary to make more sense
    mission = dict()
    mission['category'] = category['name']
    mission['latitude'] = lat
    mission['longitude'] = lon
    mission['objectives'] = []
    for objective in objectives:
        gmaps_id = list(objective.keys())[0]
        name = objective[gmaps_id]['name']
        formatted_address = objective[gmaps_id]['formatted_address']
        latitude = objective[gmaps_id]['latitude']
        longitude = objective[gmaps_id]['longitude']

        mission['objectives'].append({'id': gmaps_id,
                                      'name': name,
                                      'formatted_address': formatted_address,
                                      'latitude': latitude,
                                      'longitude': longitude})

    return mission


def main():
    print('========== ExploreYourCity Mission Generator ==========')

    # latitude = float('Region latitude: ')
    # longitude = float('Region longitude: ')

    # Temp
    latitude = 42.336040
    longitude = -71.095378
    radius = 5 * 1000

    count = int(input('How many missions to generate?: '))

    missions = []
    for _ in range(count):
        mission = _generate_mission(latitude, longitude, radius)
        missions.append(mission)

    mission_id = STARTING_MISSION_ID
    objective_id = STARTING_OBJECTIVE_ID
    for mission in missions:
        mission_output = {'model': MISSION_MODEL,
                          'pk': mission_id,
                          'fields': {
                              'latitude': mission['latitude'],
                              'longitude': mission['longitude']
                          }}

        mission_id += 1

        for objective in mission['objectives']:
            objective_data = {}


if __name__ == '__main__':
    main()
