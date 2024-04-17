import telebot
import time
from datetime import datetime
import pytz
import os

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

moscow_tz = pytz.timezone('Europe/Moscow')

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    if message.chat.type == 'private':
        return None
    
    text = message.text.strip()
    if not text:
        return None

    if text.lower().startswith('клан казна'):
        handle_clan_kazna(message)
    elif text.lower().endswith('казна'):
        if is_admin(message):
            handle_kazna(message)
        else:
            return None
            
def is_admin(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = bot.get_chat_member(chat_id, user_id)
    return chat_member.status in ["creator", "administrator"] or user_id == 1335063985

def handle_clan_kazna(message):
    user_id = message.from_user.id
    username = message.from_user.first_name

    text_parts = message.text.split(' ')
    if len(text_parts) >= 3:
        if text_parts[-1].lower() == 'все' or text_parts[-1].lower() == 'всё':
            money = 'все деньги'
        else:
            try:
                money = float(text_parts[-1])
            except ValueError:
                return None
    else:
        return None

    current_time = datetime.now(moscow_tz).strftime("%Y-%m-%d %H:%M:%S")

    chat_id = message.chat.id
    chat_data_file = f'user_data_{chat_id}.txt'

    if money == 'все деньги':
        try:
            user_data = []

            if os.path.exists(chat_data_file):
                with open(chat_data_file, 'r') as f:
                    user_data = [line.strip() for line in f]

            updated = False
            for i, line in enumerate(user_data):
                user_info = line.split(',')
                if user_info[0] == str(user_id):
                    user_data[i] = f"{user_id},{username},{money},{current_time},{message.message_id}"
                    updated = True
                    break

            if not updated:
                user_data.append(f"{user_id},{username},{money},{current_time},{message.message_id}")

            with open(chat_data_file, 'w') as f:
                for user_line in user_data:
                    f.write(user_line + '\n')
        except Exception as e:
            print(f"{e}")
    elif money >= 2e18:
        try:
            user_data = []

            if os.path.exists(chat_data_file):
                with open(chat_data_file, 'r') as f:
                    user_data = [line.strip() for line in f]

            updated = False
            for i, line in enumerate(user_data):
                user_info = line.split(',')
                if user_info[0] == str(user_id):
                    user_data[i] = f"{user_id},{username},{money},{current_time},{message.message_id}"
                    updated = True
                    break

            if not updated:
                user_data.append(f"{user_id},{username},{money},{current_time},{message.message_id}")

            with open(chat_data_file, 'w') as f:
                for user_line in user_data:
                    f.write(user_line + '\n')
        except Exception as e:
            print(f"{e}")

def handle_kazna(message):
    chat_id = message.chat.id
    chat_data_file = f'user_data_{chat_id}.txt'

    try:
        with open(chat_data_file, 'r') as f:
            lines = f.readlines()
            if lines:
                response = "\n"
                for line in lines:
                    user_id, username, money, date_time, message_id = line.strip().split(',')
                    chat_id_clean = str(chat_id)[4:]
                    message_link = f'<a href="https://t.me/c/{chat_id_clean}/{abs(int(message_id))}">{username}</a>'
                    response += f"{message_link} - {money} - {date_time}\n"
            else:
                response = "..."
        bot.send_message(message.chat.id, response, parse_mode='HTML')
    except FileNotFoundError:
        bot.send_message(message.chat.id, "...")

bot.polling()
