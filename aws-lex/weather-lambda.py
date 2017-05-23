import json
import logging
import os
import time
import urllib2

URL = 'http://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=36416a6ebb453dbe55151fbb3310561b'
DEFAULT_INTENT = {'currentIntent': {'slots': {'city': 'London'}}, 'sessionAttributes': {}}

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def try_ex(func):
    try:
        return func()
    except KeyError:
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
    content = urllib2.urlopen(URL % city).read()
    data = json.loads(content)

    city = data['name']
    temp = data['main']['temp']
    wind_speed = data['wind']['speed']

    return city, temp, wind_speed


def temperature(intent_request=DEFAULT_INTENT):
    city, temp, wind_speed = get_weather(intent_request)
    session_attributes = set_session_attributes(intent_request, city, temp, wind_speed)
    return close(session_attributes, 'The temperature is currently %s degrees in %s.' % (temp, city))


def wind(intent_request=DEFAULT_INTENT):
    city, temp, wind_speed = get_weather(intent_request)
    session_attributes = set_session_attributes(intent_request, city, temp, wind_speed)
    return close(session_attributes, 'The wind speed is currently %s km/h in %s.' % (wind_speed, city))


def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

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
    print temperature()
    print wind()
