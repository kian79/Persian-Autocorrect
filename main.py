import requests
import yaml


def get_token(file_path='token.yml'):
    bot_token_file = open(file_path)
    bot_token = yaml.safe_load(bot_token_file)
    return bot_token['token']

class BotHandler():

    def __init__(self,token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.api_url + method, params)
        result = response.json()['result']
        return result

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        response = requests.post(self.api_url + method, params)
        return response

    def get_last_update(self):
        result = self.get_updates()
        if len(result) > 0:
            last_update = result[-1]
        else:
            last_update = result[len(result)]
        return last_update

if __name__ == '__main__':
    my_bot = BotHandler(get_token())
    offset = None
    while True:
        my_bot.get_updates(offset=offset)
        last_update = my_bot.get_last_update()
        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text'].lower()
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name'].lower()
        last_chat_username = last_update['message']['chat']['username'].lower()
        # print(f"last id : {last_update_id} , last text : {last_chat_text} , last chat id : {last_chat_id} , last name : {last_chat_name}")
        if last_chat_username == 'kiankr79':
            my_bot.send_message(last_chat_id,"سلام کیان خوشگلم")
            print(f"sent to {last_chat_name}")
        if last_chat_username == 'pariya_md':
            my_bot.send_message(last_chat_id,"سلام پریای خوشگلم کیان خیلی دوستت داره")
            print(f"sent to {last_chat_name}")
        offset = last_update_id+1


