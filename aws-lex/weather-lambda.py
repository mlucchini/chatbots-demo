import json
import logging
import os
import time
import urllib2

URL = 'http://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=36416a6ebb453dbe55151fbb3310561b'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def try_ex(func):
    try:
        return func()
    except (KeyError, TypeError):
        return None


def close(session_attributes, plain_text_message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': plain_text_message
            }
        }
    }
    logger.debug('close={}'.format(response))
    return response


def elicit_slot(intent_request, slot_to_elicit):
    response = {
        'sessionAttributes': intent_request['sessionAttributes'],
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_request['currentIntent']['name'],
            'slots': intent_request['currentIntent']['slots'],
            'slotToElicit': slot_to_elicit
        }
    }
    logger.debug('elicit_slot={}'.format(response))
    return response


def set_session_attributes(intent_request, city, temp, wind_speed):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    session_attributes['weather'] = json.dumps({
        'City': city,
        'Temperature': temp,
        'WindSpeed': wind_speed
    })

    return session_attributes


def get_weather(intent_request):
    city = try_ex(lambda: intent_request['currentIntent']['slots']['city'])
    if city is None:
        session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] else None
        weather = json.loads(session_attributes['weather']) if session_attributes else None
        city = weather['City'] if weather else None
    if city is None:
        return None, None, None
    else:
        content = urllib2.urlopen(URL % city).read()
        data = json.loads(content)

        city = data['name']
        temp = data['main']['temp']
        wind_speed = data['wind']['speed']

        return city, temp, wind_speed


def temperature(intent_request):
    city, temp, wind_speed = get_weather(intent_request)
    if city is None:
        return elicit_slot(intent_request, 'city')
    else:
        session_attributes = set_session_attributes(intent_request, city, temp, wind_speed)
        return close(session_attributes, 'The temperature is currently %s degrees in %s.' % (temp, city))


def wind(intent_request):
    city, temp, wind_speed = get_weather(intent_request)
    if city is None:
        return elicit_slot(intent_request, 'city')
    else:
        session_attributes = set_session_attributes(intent_request, city, temp, wind_speed)
        return close(session_attributes, 'The wind speed is currently %s km/h in %s.' % (wind_speed, city))


def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}, sessionAttributes={}'.format(
            intent_request['userId'],
            intent_request['currentIntent']['name'],
            intent_request['sessionAttributes']))

    intent_name = intent_request['currentIntent']['name']

    if intent_name == 'Temperature':
        return temperature(intent_request)
    elif intent_name == 'Wind':
        return wind(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def lambda_handler(event, context):
    os.environ['TZ'] = 'Europe/London'
    time.tzset()

    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)


if __name__ == '__main__':
    intent_temperature_city_london = {
        'currentIntent': {
            'name': 'Temperature',
            'slots': {
                'city': 'London'
            }
        },
        'sessionAttributes': {

        },
        'userId': 'testUser'
    }
    intent_wind_city_reuse_session = {
        'currentIntent': {
            'name': 'Wind',
            'slots': {

            },
        },
        'sessionAttributes': {
            'weather': json.dumps({
                'City': 'London',
                'Temperature': 17.5,
                'WindSpeed': 3.5
            })
        },
        'userId': 'testUser'
    }

    print dispatch(intent_temperature_city_london)
    print dispatch(intent_wind_city_reuse_session)
