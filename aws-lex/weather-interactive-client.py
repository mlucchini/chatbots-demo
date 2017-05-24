import boto3
import os

if not os.environ['AWS_ACCESS_KEY']:
    print('Make sure your AWS access keys (AWS_ACCESS_KEY) are set.')

client = boto3.client('lex-runtime', region_name='us-east-1')
sessionAttributes = {}

while True:
    text = raw_input('You: ')
    if text:
        response = client.post_text(
                botName='Weather',
                botAlias='WeatherWithTempAndWind',
                userId='testUser',
                sessionAttributes=sessionAttributes,
                inputText=text
        )
        sessionAttributes = response['sessionAttributes']
        print('Bot: %s' % response['message'])
