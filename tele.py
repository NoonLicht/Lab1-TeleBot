import telebot
from telebot import types
import requests
import shutil
import httplib2
import os
import random
import string
import spotipy
from spotipy.oauth2 import SpotifyOAuth

TOKEN = '6980617701:AAExpxjyPe6-ZnqwlZsjaMjKzms27saDmCI'
bot = telebot.TeleBot(TOKEN)

INVALID = [0, 503, 5082, 4939, 4940, 4941, 12003, 5556, 3771]
THREAD_AMOUNT = 12

def scrape_pictures(thread, chat_id):
    while True:
        url = 'https://i.paste.pics/'
        length = random.choice((4, 6))
        if length == 4:
            url += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))
        else:
            url += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
            url += ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))
            url += '.png'

            filename = url.rsplit('/', 1)[-1]

            h = httplib2.Http('.cache' + thread)
            response, content = h.request(url)
            out = open(filename, 'wb')
            out.write(content)
            out.close()
 
            file_size = os.path.getsize(filename)
            if file_size in INVALID:
                print("[-] Invalid: " + url)
                os.remove(filename)
            else:
                print("[+] Valid: " + url)
                bot.send_photo(chat_id, open(filename, 'rb'))
                return True 

# Add your Spotify API credentials
SPOTIPY_CLIENT_ID = 'ac9870ca445645efa2cd7d40a5d9bea0'
SPOTIPY_CLIENT_SECRET = '26e74f1d517140fa968e695cf34108d9'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SPOTIPY_USERNAME = 'MoonToon'
SPOTIPY_PLAYLIST_ID = '6NGzM4pblUDTV7rn8zP8UK'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope="user-library-read playlist-read-private"))

def generate_audio(message):
    try:
        # Получает треки из указанного списка воспроизведения
        playlist_tracks = sp.playlist_tracks(SPOTIPY_PLAYLIST_ID)
        if not playlist_tracks['items']:
            bot.send_message(message.from_user.id, 'The playlist is empty.')
            return

        # Выбирает случайный трек из плейлиста
        random_track = random.choice(playlist_tracks['items'])
        track_name = random_track['track']['name']
        artist_name = random_track['track']['artists'][0]['name']
        audio_url = random_track['track']['preview_url']

        # Скачивает и кидает в бота
        audio_path = './music.mp3'
        download_audio(audio_url, audio_path)
        bot.send_audio(message.from_user.id, open(audio_path, 'rb'),
                        caption=f'Now playing: {track_name} by {artist_name}')

    except Exception as e:
        print(f"Ошибка: {e}")
        bot.send_message(message.from_user.id, 'Произошла ошибка.')

# Функция для загрузки изображения из интернета
def download_image(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

# Функция для загрузки аудиофайла из интернета
def download_audio(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = types.ReplyKeyboardMarkup()
    user_markup.row('Изображение', 'Песня')
    user_markup.row('Репозиторий')
    bot.send_message(message.from_user.id, 'Добро пожаловать!', reply_markup=user_markup)

# Обработчик команды изображение
@bot.message_handler(commands=['Изображение'])
def handle_generate_image(message):
    try:
        success = scrape_pictures('1', message.chat.id)
        if not success:
            bot.send_message(message.from_user.id, 'Не удалось загрузить изображение.')
    except Exception as e:
        print(f"Error generating image: {e}")
        bot.send_message(message.from_user.id, 'Произошла ошибка.')

# Обработчик команды песня
@bot.message_handler(commands=['Песня'])
def handle_generate_audio(message):
    generate_audio(message)

# Обработчик команды репозиторий
@bot.message_handler(commands=['Репозиторий'])
def handle_repo_link(message):
    repo_link = 'https://github.com/NoonLicht/Lab1-TeleBot'
    bot.send_message(message.from_user.id, f'Ссылка на репозиторий: {repo_link}')

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == 'Изображение':
        handle_generate_image(message)
    elif message.text == 'Песня':
        handle_generate_audio(message)
    elif message.text == 'Репозиторий':
        handle_repo_link(message)
    else:
        bot.send_message(message.from_user.id, 'Неизвестная команда. Используйте кнопки.')

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)