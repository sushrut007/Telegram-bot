import convertapi
import os
import telebot
import tempfile
import requests
import logging
from io import BytesIO

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
print(logger)

token = 'TELEGRAM_APIKEY'
convertapi.api_secret = 'CONVERTAPI_APIKEY'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Please send me your files this bot will convert into PDF')

@bot.message_handler(content_types=['document', 'audio', 'photo', 'video'])
def convert_to_pdf(message):
    bot.send_message(message.chat.id, 'Converting...')
    send_photo_warning = False
    content_type = message.content_type

    documents = getattr(message, content_type)
    if not isinstance(documents, list):
        documents = [documents]

    for doc in documents:
        file_id = doc.file_id
        file_info = bot.get_file(file_id)
        file_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path)

        file_data = BytesIO(requests.get(file_url).content)
        try:
            file_name = doc.file_name
        except:
            file_name = file_info.file_path.replace("/", "_")
            send_photo_warning = True
        upload_io = convertapi.UploadIO(file_data, filename=file_name)
        converted_result = convertapi.convert('pdf', {'File': upload_io})
        converted_files = converted_result.save_files(tempfile.gettempdir())

    converted_files.reverse()
    bot.send_document(message.chat.id, open(converted_files[0], 'rb'))

    if send_photo_warning:
        bot.send_message(message.chat.id, 'You sent this file as a photo. If you require better quality, please send it as a document.')

bot.polling()
