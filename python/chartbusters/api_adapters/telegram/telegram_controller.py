import requests

api_url = 'https://api.telegram.org/'
bot_key = 'bot5456571295:AAHi7TzIgns2pcipBC_xOjwgtSiVr-cI3lc'
api_params = {
    'chat_id': '-1001743840522',
}
api_method_send_message = '/sendMessage'


def send_message(message: str):
    message_as_param = {'text': message}
    api_params.update(message_as_param)
    response = requests.get(api_url + bot_key + api_method_send_message,
                            params=api_params)
    print(response)
