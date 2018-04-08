from chalice import Chalice
from chalicelib import *
import json, requests

app = Chalice(app_name='bart-bot')


@app.route('/', methods=['POST'])
def index():
    event = app.current_request.json_body

    station = get_station(event)
    direction = get_direction(event)
    direction_abbr = get_abbr_direction(direction)
    api_key = 'MW9S-E7SL-26DU-VV8V'

    # make api request
    parameters = {'cmd': 'etd', 'orig': station['abbr'], 'key': api_key, 'dir': direction_abbr, 'json': 'y'}
    response = requests.get('http://api.bart.gov/api/etd.aspx', params=parameters)

    #process api response
    destinations = get_destinations(response.json())
    soonest_trains = extract_times_destinations(destinations)

    #generate spoken and written answers
    result = create_answer(direction, station, soonest_trains)

    return result
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {'Content-Type': 'application/json'}
    }