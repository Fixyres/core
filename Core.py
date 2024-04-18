import telebot
from datetime import datetime
import pytz
import os

TOKEN = '6775251060:AAGDYK6eTq70hHX5NVMCSMGmVoNXorZKINY'
bot = telebot.TeleBot(TOKEN)

moscow_tz = pytz.timezone('Europe/Moscow')

def send_data_file(message):
    chat_id = message.chat.id
    chat_data_file = f'user_data_{chat_id}.txt'

    try:
        with open(chat_data_file, 'rb') as f:
            bot.send_document(chat_id, f)
    except FileNotFoundError:
        bot.send_message(chat_id, "Файл не найден")
    except Exception as e:
        bot.send_message(chat_id, f"{e}")

def handle_kazna(message):
    chat_id = message.chat.id
    chat_data_file = f'user_data_{chat_id}.txt'

    try:
        with open(chat_data_file, 'r') as f:
            lines = f.readlines()
            if lines:
                user_data = []  
                for line in lines:
                    user_info = line.strip().split(',')
                    money = float(user_info[2])
                    user_data.append((money, line))  
                user_data.sort(reverse=True)
                response = "<b>Если написать клан казна все то вы не будете в топе!!!</b>\n"
                line_number = 1
                for money, line in user_data:  
                    user_id, username, money, date_time, message_id = line.strip().split(',')
                    chat_id_clean = str(chat_id)[4:]
                    message_link = f'<a href="https://t.me/c/{chat_id_clean}/{abs(int(message_id))}">{username}</a>'
                    response += f"{line_number}) {message_link} - {money} - {date_time}\n"
                    line_number += 1
            else:
                response = "..."
        bot.send_message(message.chat.id, response, parse_mode='HTML')
    except FileNotFoundError:
        bot.send_message(message.chat.id, "...")

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
    	handle_kazna(message)

    elif text.lower() == '/clean':
        if is_admin(message):
            reset_kazna_list(message)
        else:
            return None
            
    elif text.lower() == '/clean@klankazna_bot':        
        if is_admin(message):
            reset_kazna_list(message)
        else:
            return None
            
    elif text.lower() == '/sflie@klankazna_bot' or '/sfile':
    	if is_admin(message):
    		send_data_file(message)
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

    text_parts = message.text.split('    ')  
    if len(text_parts) >= 2:
        text = '    '.join(text_parts[:2]) 
    else:
        text = text_parts[0]  

    text = text.strip()  

    if text.lower().startswith('клан казна'):
        text = text[10:].strip() 
        handle_clan_kazna_internal(message, text)
    elif text.lower().endswith('казна'):
        text = text[:-5].strip()  
        if is_admin(message):
            handle_kazna_internal(message, text)
        else:
            return None

def handle_clan_kazna_internal(message, text):
    user_id = message.from_user.id
    username = message.from_user.first_name

    money = None
    for word in text.split():
        try:
            money = float(word)
            if money < 2e18:                
                return None
            break
        except ValueError:
            continue

    if money is None:
        return None

    current_time = datetime.now(moscow_tz).strftime("%Y-%m-%d %H:%M:%S")

    chat_id = message.chat.id
    chat_data_file = f'user_data_{chat_id}.txt'

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

def handle_kazna_internal(message, text):
    chat_id = message.chat.id
    chat_data_file = f'user_data_{chat_id}.txt'

    try:
        with open(chat_data_file, 'r') as f:
            lines = f.readlines()
            if lines:
                response = "\n"
                line_number = 1  
                for line in lines:
                    user_id, username, money, date_time, message_id = line.strip().split(',')
                    chat_id_clean = str(chat_id)[4:]
                    message_link = f'<a href="https://t.me/c/{chat_id_clean}/{abs(int(message_id))}">{username}</a>'
                    response += f"{line_number}) {message_link} - {money} - {date_time}\n"
                    line_number += 1  
            else:
                response = "..."
        bot.send_message(message.chat.id, response, parse_mode='HTML')
    except FileNotFoundError:
        bot.send_message(message.chat.id, "...")

def reset_kazna_list(message):
    chat_id = message.chat.id
    chat_data_file = f'user_data_{chat_id}.txt'

    try:
        if os.path.exists(chat_data_file):
            os.remove(chat_data_file)
            bot.reply_to(message, "СЭР ДА СЭР!")
        else:
            bot.reply_to(message, "СЭР СПИСОК ПУСТ СЭР!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка")

bot.polling()
