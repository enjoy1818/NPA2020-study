import requests
import datetime
import time
def main():
    command = ''
    
    message_response = {}
    while command.lower() != "end":
        message = get_message(webex_bearer_token, webex_room_id)
        if message_response == message:
            print(message)
        else:
            message_response = message
            command = message['items'][0]['text']
            print(command)
        if "/weather/" in command:
            city = command.split("/")[2]
            weather_header = {"Content-Type":"application/json"}
            weather_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric".format(city, weather_api_key)
            weather_response = requests.get(weather_url).json()
            weather = "Current {} weather, {} temp {}".format(city, weather_response['weather'][0]['description'], weather_response['main']['temp'])
            webex_response = sent_to_webex(webex_bearer_token, webex_room_id, weather)
            print(webex_response)
        elif "/quote" in command:
            quote_url = "https://quotes15.p.rapidapi.com/quotes/random/"
            quote_headers = {
                
                }
            quote_response = requests.get(url=quote_url, headers=quote_headers).json()
            quote = "{} by {}".format(quote_response['content'], quote_response['originator']['name'])
            webex_response = sent_to_webex(webex_bearer_token, webex_room_id, quote)
            print(webex_response)
        elif command[0] == "/":
            map_url = "http://open.mapquestapi.com/geocoding/v1/address?key={}&location={}".format(map_api_key, command[1:])
            location = requests.get(map_url).json()["results"][0]["locations"][0]["latLng"]
            iss_url = "http://api.open-notify.org/iss-pass.json?lat={}&lon={}&n={}".format(location['lat'], location['lng'], 1)
            iss_data = requests.get(iss_url).json()["response"][0]
            iss_date = datetime.datetime.fromtimestamp(iss_data['risetime']).strftime("%Y-%m-%d %H:%M:%S")
            iss_text = "ISS will pass {} by {} duration {} second".format(command[1:].capitalize(), iss_date, iss_data['duration'])
            webex_response = sent_to_webex(webex_bearer_token, webex_room_id, iss_text)
            print(webex_response)
  
def sent_to_webex(webex_bearer_token, webex_room_id, text):
    webex_url = "https://webexapis.com/v1/messages"
    webex_auth = {"Content-Type":"application/json", "Authorization":"Bearer {}".format(webex_bearer_token)}
    webex_payload = {"roomId":webex_room_id, 'text':text}
    webex_response = requests.post(url=webex_url, headers=webex_auth, json=webex_payload).json()
    return webex_response

def get_message(webex_bearer_token, webex_room_id):
    webex_url = "https://webexapis.com/v1/messages"
    webex_auth = {"Content-Type":"application/json", "Authorization":"Bearer {}".format(webex_bearer_token)}
    webex_param = {"roomId":webex_room_id, 'max':1}
    webex_response = requests.get(url=webex_url, headers=webex_auth, params=webex_param).json()
    return webex_response
    # print(webex_response)

main()

