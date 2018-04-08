"""Optional helper function """
import random
from chalicelib.stations import stations

def get_station_name(event):
    """get the station name from the event
    
    Args:
        event (dict): Dictionary from DialogFlow that contains all information for api request
        
    Returns:
        A string for the name of the current station"""

    return event['result']['parameters']['station']


def get_direction(event):
    """get the direction from the event
    
    Args:
        event (dict): Dictionary from DialogFlow that contains all information for api request
        
    Returns:
        A string for the direction of the requested trains"""

    return event['result']['parameters']['direction']

def get_station(event):
    """get the station from the event
    
    Args:
        event (dict): Dictionary from DialogFlow that contains all information for api request
        
    Returns:
        station (dict): Dictionary that contains all information about the current station"""

    current_station = get_station_name(event)
    for station in stations:
        if current_station == station['api_ai_value']:
            return station

def get_abbr_direction(direction):
    """return 'n' for north or 's' for south for use in api request
    
    Args:
        direction (str): the direction of the requested train
        
    Returns:
        A string abbreviation of the direction"""

    if direction == 'north':
        return 'n'
    if direction == 'south':
        return 's'
    return None

def get_destinations(response):
    """get the destinations
    
    Args:
        response (dict): json format of the api response

    Returns:
        A list of destinations from the current stations"""

    return response['root']['station'][0]['etd']

def extract_times_destinations(destinations):
    """get the next two trains' destinations and times
    
    Args:
        destinations (list): an array of dictionaries of destinations and times of the next trains
        
    Returns:
        soonest_trains (list): an array of (destination, time) tuples of the soonest future trains"""

    soonest_trains = []
    count = 2
    if len(destinations) < 2:
        count = len(destinations)
    for i in range(count):
        destination_dict = destinations[i]
        destination = destination_dict['destination']
        time = destination_dict['estimate'][0]['minutes']
        soonest_trains.append((destination, time))
    return soonest_trains

def create_answer(direction, station, soonest_trains):
    """generate the spoken and written answers from the next train list
    
    Args:
        direction (str): the direction of the requested trains
        station (dict): all information of the current station
        soonest_trains (list): an array of (destination, time) tuples of the soonest future trains
        
    Returns:
        result (dict): A dictionary of spoken and written answers to be passed back to DialogFlow"""

    result = {}
    time_statement = ' in ' + soonest_trains[0][1] + ' minutes'
    if (soonest_trains[0][1] == 0):
        time_statement = ' right now'
    
    spoken_answers = ['The next ' + direction + ' bound train leaves ' + station['spoken_name'] + ' for ' + soonest_trains[0][0] + time_statement + '.',
        'The next ' + direction + ' bound train is arriving at ' + station['spoken_name'] + time_statement + ' and is heading for ' + soonest_trains[0][0] + '.']
    written_answers = ['The next ' + direction + '-bound train leaves ' + station['written_name'] + ' for ' + soonest_trains[0][0] + time_statement + '.',
        'The next ' + direction + '-bound train is arriving at ' + station['written_name'] + time_statement + ' and is heading for ' + soonest_trains[0][0] + '.']
    index = random.randint(0, 1)

    result['speech'] = spoken_answers[index]
    result['display API'] = written_answers[index]
    result['source'] = 'BART API'

    if (len(soonest_trains) > 1):
        result['speech'] += 'Then, another ' + direction + ' bound train will depart for ' + soonest_trains[1][0] + ' in ' + soonest_trains[1][1] + ' minutes.'
        result['display API'] += 'Then, another ' + direction + '-bound train will depart for ' + soonest_trains[1][0] + ' in ' + soonest_trains[1][1] + ' minutes.'
    return result