import telebot
from telebot import types
import random
import logging
import json
import os
from datetime import datetime
import pytz
import threading
import time
import requests
import re

API_KEY = '41d63e00422b4ab1a39a77d6582b79c1'  

moscow_tz = pytz.timezone('Europe/Moscow')

TOKEN = '6775251060:AAF0T9vhrvtmAGEy4FkTL55xE4q9P5-LKRE'
bot = telebot.TeleBot(TOKEN)

BASE_URL = 'https://openexchangerates.org/api/'

def get_exchange_rate(base_currency, target_currency):
    try:
        response = requests.get(f'{BASE_URL}latest.json', params={'app_id': API_KEY})
        data = response.json()
        rates = data['rates']
        if target_currency in rates:
            return rates[target_currency] / rates[base_currency]
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
        
def convert_currency(message):
    try:
        parts = message.text.split()
        if len(parts) != 4:
            bot.send_message(message.chat.id, "🙄 Пример: /c 100 USD EUR")
            return
        
        amount = float(parts[1])
        base_currency = parts[2].upper()
        target_currency = parts[3].upper()

        exchange_rate = get_exchange_rate(base_currency, target_currency)
        if exchange_rate:
            converted_amount = amount * exchange_rate
            bot.send_message(message.chat.id, f"{amount} {base_currency} = {converted_amount:.2f} {target_currency}")
        else:
            bot.send_message(message.chat.id, "...")
    except Exception as e:
        bot.send_message(message.chat.id, "...")
        print(f"{e}")
                
def xz(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = bot.get_chat_member(chat_id, user_id)
    return chat_member.status in ["creator", "administrator"] or user_id == 1335063985
    
def rewrite_data_file(message, new_data):
    chat_id = message.chat.id
    chat_data_file = f'user_data_{chat_id}.txt'

    try:
        with open(chat_data_file, 'w') as f:
            f.write(new_data)
        bot.reply_to(message, "СЭР ДА СЭР!")
    except Exception as e:
        bot.reply_to(message, f"{e}")

def remove_user_from_list(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    text_parts = message.text.split()
    if len(text_parts) != 2 or not text_parts[1].isdigit():
        return None

    position_to_remove = int(text_parts[1])

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

                if 0 < position_to_remove <= len(user_data):
                    removed_line = user_data.pop(position_to_remove - 1)[1]

                    with open(chat_data_file, 'w') as fw:
                        fw.writelines(line for _, line in user_data)

                    bot.reply_to(message, f"СЭР ДА СЭР!")
                else:
                    bot.reply_to(message, "СЭР НЕТ СЭР!")
            else:
                bot.reply_to(message, "...")
    except FileNotFoundError:
        bot.reply_to(message, "...")
    except Exception as e:
        bot.reply_to(message, f"{e}")

def send_data_file(message):
    chat_id = message.chat.id
    with open(CHATS_FILE, 'r') as f:
        all_chats = json.load(f)

    for chat in all_chats:
        chat_data_file = f'user_data_{chat}.txt'
        try:
            with open(chat_data_file, 'rb') as f:
                bot.send_document(chat_id, f)
                time.sleep(1)  
        except FileNotFoundError:
            bot.send_message(chat_id, f"Файл {chat_data_file} не найден")
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка при отправке файла {chat_data_file}: {e}")


def send_stata_file(message):
    chat_id = message.chat.id
    svo = f'stata.txt'

    try:
        with open(svo, 'rb') as f:
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

ALLOWED_USER_ID = 1335063985
VIDEO_URL = 'https://raw.githubusercontent.com/Fixyres/core/main/IMG_20240525_210542_447.jpg'
MESSAGE_TEXT = '🍞 Дать денег на хлеб: \n\n💎 TON: <code>UQBJMIRk8ylArSR64lzPVvsbl3LMJOIkoRuBYas7v_Lbp7e3</code>\n\n💳 Банк: <code>5167803243664047</code>'
CHATS_FILE = 'chats.json'

if os.path.exists(CHATS_FILE):
    with open(CHATS_FILE, 'r') as f:
        chats = json.load(f)
else:
    chats = []

def save_chats():
    with open(CHATS_FILE, 'w') as f:
        json.dump(chats, f)

def send_video_to_all_chats():
    for chat_id in chats:
        try:
            chat_type = bot.get_chat(chat_id).type
            if chat_type != 'private':
                bot.send_photo(chat_id, VIDEO_URL, caption=MESSAGE_TEXT, parse_mode='HTML')
                time.sleep(3)
        except Exception as e:
            print(f"Не удалось отправить в чат {chat_id}: {e}")

def periodic_video_sender():
    while True:
        send_video_to_all_chats()
        time.sleep(3 * 60 * 60)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.id not in chats:
        chats.append(message.chat.id)
        save_chats()
    else:
        text = message.text.strip()
        if not text:
            return None

        if text.lower().startswith('/rfile'):
            if xz(message):
                new_data = text[6:].strip()
                rewrite_data_file(message, new_data)
            else:
                return None
        elif text.lower().startswith('клан казна'):
            handle_clan_kazna(message)
        elif text.lower().endswith('казна'):
            handle_kazna(message)
        elif text.lower() == '/clean':
            if xz(message):
                reset_kazna_list(message)
            else:
                return None
        elif text.lower() == '/clean@klankazna_bot':        
            if xz(message):
                reset_kazna_list(message)
            else:
                return None
        elif text.lower() == '/sfile':
            if xz(message):
                send_data_file(message)
                send_stata_file(message)
        elif text.lower() == '/sflie@klankazna_bot':
            if xz(message):
                send_data_file(message) 
                send_stata_file(message)
        elif text.lower() == '/t':
            start_game(message)
        elif text.lower() == '/t@klankazna_bot':
            start_game(message)    
        elif text.lower() == '/myid':
            get_my_id(message)
        elif text.lower() == '/myid@klankazna_bot':
            get_my_id(message)    
        elif text.lower() == '/leave':
            leave_game(message)
        elif text.lower() == '/leave@klankazna_bot':
            leave_game(message)
        elif text.lower() == '/stata':
            view_statistics(message)
        elif text.lower() == '/stata@klankazna_bot':
            view_statistics(message)
        elif text.lower().startswith('удалить'):
            if xz(message):
                remove_user_from_list(message)
        elif text.lower().startswith('/donate'):
            if message.from_user.id == ALLOWED_USER_ID:
                send_video_to_all_chats()
            else:
                return None
        elif text.lower().startswith('/c'):
            convert_currency(message)
        else:
            return None

threading.Thread(target=periodic_video_sender, daemon=True).start()
        
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
        
logging.basicConfig(level=logging.INFO)

admins_file = 'admin.txt'
blocked_file = 'block.txt'
users_file = 'users.txt'
stata_file = 'stata.txt'
admins = set()
blacklisted_users = set()
added_users = set()

def is_admin(user_id):
    return user_id in admins

with open(admins_file, 'r') as file:
    admins = set(map(int, file.read().splitlines()))

with open(blocked_file, 'r') as file:
    blacklisted_users = set(map(int, file.read().splitlines()))
    
def save_to_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write('\n'.join(map(str, data)))

def get_user_id_from_command(command):
    try:
        user_param = command.split()[1]

        if user_param.startswith('@'):
            user_info = bot.get_chat_member(message.chat.id, user_param)
            return user_info.user.id
        else:
            return int(user_param)
    except (IndexError, ValueError):
        return None

@bot.message_handler(commands=['myid'])
def get_my_id(message):
    bot.reply_to(message, f"<code>{message.from_user.id}</code>", parse_mode='HTML')

STATISTICS_FILE = 'stata.txt'
STATUS_FILE = 'status.txt'

def load_user_statuses():
    try:
        with open(STATUS_FILE, 'r') as file:
            lines = file.readlines()
            return {int(line.split()[0]): line.split(maxsplit=1)[1].strip() for line in lines}
    except FileNotFoundError:
        return {}

def save_user_statuses(statuses):
    with open(STATUS_FILE, 'w') as file:
        for user_id, status in statuses.items():
            file.write(f"{user_id} {status}\n")

def update_statistics(user_id, result):
    with open(STATISTICS_FILE, 'a') as file:
        file.write(f"{user_id} {result}\n")

user_statuses = load_user_statuses()

@bot.message_handler(commands=['status'])
def set_user_status(message):
    if is_admin(message.from_user.id):
        try:
            user_id = get_user_id_from_command(message.text)
            status = message.text.split(maxsplit=2)[2]
            user_statuses[user_id] = status
            save_user_statuses(user_statuses)
            bot.reply_to(message, f"Статус для пользователя {user_id} установлен: {status}")
        except (IndexError, ValueError):
            bot.reply_to(message, "Неправильный формат команды. Используйте: /status @username ваш_статус")
    else:
        bot.reply_to(message, "Нет прав доступа.")

def get_user_statistics(user_id):
    try:
        with open(STATISTICS_FILE, 'r') as file:
            lines = file.readlines()
            user_stats = [line.split() for line in lines if line.startswith(str(user_id))]
            return user_stats, user_statuses.get(user_id)
    except FileNotFoundError:
        return [], None
        
@bot.message_handler(commands=['stata'])
def view_statistics(message):
    user_id = message.from_user.id
    user_stats, user_status = get_user_statistics(user_id)

    if user_stats:
        total_games = len(user_stats)
        total_wins = sum(1 for _, result in user_stats if result == 'win')
        total_draws = sum(1 for _, result in user_stats if result == 'draw')
        total_losses = sum(1 for _, result in user_stats if result == 'loss')
        total_leaves = sum(1 for _, result in user_stats if result == 'leave')

        reply_text = (
            f"📊 Ваша статистика:\n"
            f"🏆 Побед: {total_wins}\n"
            f"😐 Ничьих: {total_draws}\n"
            f"😞 Проигрышей: {total_losses}\n"
            f"🚪 Выходов из игр: {total_leaves}"
        )
        if user_status:
            reply_text += f"\n{user_status}"
        
        bot.reply_to(message, reply_text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📊 У тебя её нет...", parse_mode="Markdown")

board_sizes = {
    "3*3": {"size": 3, "win_condition": [3]},
    "4*4": {"size": 4, "win_condition": [3, 4]},
    "5*5": {"size": 5, "win_condition": [3, 4, 5]},
    "6*6": {"size": 6, "win_condition": [3, 4, 5, 6]},
    "7*7": {"size": 7, "win_condition": [3, 4, 5, 6, 7]},
    "8*8": {"size": 8, "win_condition": [3, 4, 5, 6, 7, 8]}
}

games = {}

class TicTacToeGame:
    def __init__(self, game_id, player_x, size, win_condition):
        self.game_board = [[' ' for _ in range(size)] for _ in range(size)]
        self.players = {'X': player_x, 'O': None}
        self.current_player = None
        self.player_symbols = {'X': '', 'O': ''}
        self.player_names = {'X': '', 'O': ''}
        self.game_active = False
        self.leave_button_added = False
        self.game_id = game_id
        self.size = size
        self.win_condition = win_condition
        self.message_id = None
        games[game_id] = {'win_condition': None}
        
    def set_win_condition(self, win_condition):
        games[self.game_id]['win_condition'] = win_condition
        
    def render_board(self):
        keyboard = types.InlineKeyboardMarkup()
        for row in range(self.size):
            buttons = []
            for col in range(self.size):
                symbol = self.player_symbols[self.game_board[row][col]] if self.game_board[row][col] in self.player_symbols else ' '
                callback_data = f"move:{row}:{col}:{self.game_id}"
                buttons.append(types.InlineKeyboardButton(text=symbol, callback_data=callback_data))
            keyboard.row(*buttons)

        return keyboard

    def check_winner(self, sign):        
        win_condition = games[self.game_id]['win_condition']
        for row in range(self.size):
            for col in range(self.size - self.win_condition + 1):
                if all(self.game_board[row][col + i] == sign for i in range(self.win_condition)):
                    update_statistics(self.players[sign], 'win')
                    update_statistics(self.players['O' if sign == 'X' else 'X'], 'loss')
                    return True

        for col in range(self.size):
            for row in range(self.size - self.win_condition + 1):
                if all(self.game_board[row + i][col] == sign for i in range(self.win_condition)):
                    update_statistics(self.players[sign], 'win')
                    update_statistics(self.players['O' if sign == 'X' else 'X'], 'loss')
                    return True

        for row in range(self.size - self.win_condition + 1):
            for col in range(self.size - self.win_condition + 1):
                if all(self.game_board[row + i][col + i] == sign for i in range(self.win_condition)):
                    update_statistics(self.players[sign], 'win')
                    update_statistics(self.players['O' if sign == 'X' else 'X'], 'loss')
                    return True

                if all(self.game_board[row + self.win_condition - 1 - i][col + i] == sign for i in range(self.win_condition)):
                    update_statistics(self.players[sign], 'win')
                    update_statistics(self.players['O' if sign == 'X' else 'X'], 'loss')
                    return True

        return False

    def check_draw(self):
        if all(self.game_board[row][col] != ' ' for row in range(self.size) for col in range(self.size)):
            update_statistics(self.players['X'], 'draw')
            update_statistics(self.players['O'], 'draw')
            return True
        return False

    def reset_game(self):
        self.game_board = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.players = {'X': None, 'O': None}
        self.current_player = None
        self.player_names = {'X': '', 'O': ''}
        self.game_active = False
        self.leave_button_added = False
        self.message_id = None

@bot.message_handler(commands=['t'])
def start_game(message):
    chat_id = message.chat.id

    if chat_id not in games:
        games[chat_id] = {'count': 0, 'data': {}}

    markup = types.InlineKeyboardMarkup(row_width=2)
    for size_label, size_info in board_sizes.items():
        callback_data = f'choose_size:{size_info["size"]}'
        button = types.InlineKeyboardButton(size_label, callback_data=callback_data)
        markup.add(button)

    bot.send_message(chat_id, "🔮 Размер игрового поля:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_size'))
def choose_size(call):
    chat_id = call.message.chat.id

    size = int(call.data.split(':')[1])

    game_id = games[chat_id]['count']
    games[chat_id]['count'] += 1

    win_condition = 3
    new_game = TicTacToeGame(game_id, call.from_user.id, size, win_condition)
    games[chat_id]['data'][game_id] = new_game

    user = call.from_user
    new_game.player_names['X'] = user.first_name

    win_condition_buttons = types.InlineKeyboardMarkup(row_width=3)
    for win_condition in board_sizes[f"{size}*{size}"]["win_condition"]:
        callback_data = f'choose_win_condition:{win_condition}:{game_id}'
        button = types.InlineKeyboardButton(str(win_condition), callback_data=callback_data)
        win_condition_buttons.add(button)

    text = f"🏆 В ряд для победы:"
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=win_condition_buttons, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_win_condition'))
def choose_win_condition(call):
    chat_id = call.message.chat.id

    win_condition = int(call.data.split(':')[1])
    game_id = int(call.data.split(':')[2])

    current_game = games[chat_id]['data'].get(game_id)
    if current_game:
        current_game.win_condition = win_condition

        join_button = types.InlineKeyboardButton('🤝 Присоединиться', callback_data=f'join:{game_id}')
        markup = types.InlineKeyboardMarkup().add(join_button)
        text = f"🎮 [{call.from_user.first_name}](tg://user?id={call.from_user.id}), ожидание второго игрока... 🕒\n⬜ Размер поля: {current_game.size}x{current_game.size}\n🚧 {win_condition} в ряд!"
        message = bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='Markdown')
        current_game.message_id = message.message_id

@bot.callback_query_handler(func=lambda call: call.data.startswith('join'))
def join_game(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    game_id = int(call.data.split(':')[1])

    current_game = games[chat_id]['data'].get(game_id)

    if current_game and not current_game.game_active and current_game.players['O'] is None and user_id != current_game.players['X']:
        current_game.players['O'] = user_id
        current_game.player_names['O'] = call.from_user.first_name
        current_game.current_player = random.choice(['X', 'O'])
        current_game.player_symbols['X'] = '❌' if random.random() < 0.5 else '⭕'
        current_game.player_symbols['O'] = '⭕' if current_game.player_symbols['X'] == '❌' else '❌'

        markup = current_game.render_board()

        text = f"🔪  [{current_game.player_names['X']}](tg://user?id={current_game.players['X']}) {current_game.player_symbols['X']} против [{current_game.player_names['O']}](tg://user?id={current_game.players['O']})  {current_game.player_symbols['O']} 🗡️\n\n⏳ Текущий ход: [{current_game.player_names[current_game.current_player]}](tg://user?id={current_game.players[current_game.current_player]})\n🚧 {current_game.win_condition} в ряд!"

        message = bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='Markdown')
        current_game.message_id = message.message_id
        current_game.game_active = True
    else:
        bot.answer_callback_query(call.id, "Игра уже началась или вы уже участвуете. 🚫")
    return
    
@bot.message_handler(commands=['leave'])
def leave_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in games or 'data' not in games[chat_id]:
        return

    for game_id, current_game in games[chat_id]['data'].items():
        if current_game and current_game.game_active and (user_id == current_game.players['X'] or user_id == current_game.players['O']):
            if user_id == current_game.players['X']:
                update_statistics(current_game.players['X'], 'leave')
                update_statistics(current_game.players['O'], 'total_games')
            elif user_id == current_game.players['O']:
                update_statistics(current_game.players['O'], 'leave')
                update_statistics(current_game.players['X'], 'total_games')

            text = f"👋 [{message.from_user.first_name}](tg://user?id={message.from_user.id}) покинул(а) игру!\n😞 Игра окончена.\n\n🔪 [{current_game.player_names['X']}](tg://user?id={current_game.players['X']}) {current_game.player_symbols['X']} против [{current_game.player_names['O']}](tg://user?id={current_game.players['O']}) {current_game.player_symbols['O']} 🗡️\n🚧 {current_game.win_condition} в ряд!"

            markup = None
            if not current_game.check_winner(current_game.current_player) and not current_game.check_draw():
                markup = current_game.render_board()

            bot.edit_message_text(chat_id=chat_id, message_id=current_game.message_id, text=text, reply_markup=markup, parse_mode='Markdown')
            del games[chat_id]['data'][game_id]
            current_game.reset_game()
            return
            
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if chat_id not in games or 'data' not in games[chat_id]:
        return

    query_data = call.data.split(':')
    action = query_data[0]

    if action == 'join':
        game_id = int(query_data[1])
        current_game = games[chat_id]['data'].get(game_id)

        if current_game and not current_game.game_active and current_game.players['O'] is None and user_id != current_game.players['X']:
            current_game.players['O'] = user_id
            current_game.player_names['O'] = call.from_user.first_name
            current_game.current_player = random.choice(['X', 'O'])
            current_game.player_symbols['X'] = '❌' if random.random() < 0.5 else '⭕'
            current_game.player_symbols['O'] = '⭕' if current_game.player_symbols['X'] == '❌' else '❌'

            markup = current_game.render_board()

            text = f"🔪  [{current_game.player_names['X']}](tg://user?id={current_game.players['X']}) {current_game.player_symbols['X']} против [{current_game.player_names['O']}](tg://user?id={current_game.players['O']})  {current_game.player_symbols['O']} 🗡️\n\n⏳ Текущий ход: [{current_game.player_names[current_game.current_player]}](tg://user?id={current_game.players[current_game.current_player]})\n🚧 {current_game.win_condition} в ряд!"

            message = bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='Markdown')
            current_game.message_id = message.message_id
            current_game.game_active = True
        else:
            bot.answer_callback_query(call.id, "Игра уже началась или вы уже участвуете. 🚫")
        return

    if action == 'leave':
        game_id = int(query_data[1])
        current_game = games[chat_id]['data'].get(game_id)

        if current_game and current_game.game_active and (user_id == current_game.players['X'] or user_id == current_game.players['O']):
            text = f"👋 [{call.from_user.first_name}](tg://user?id={call.from_user.id}) покинул(а) игру!\n😞 Игра окончена.\n\n🔪 [{current_game.player_names['X']}](tg://user?id={current_game.players['X']}) {current_game.player_symbols['X']} против [{current_game.player_names['O']}](tg://user?id={current_game.players['O']}) {current_game.player_symbols['O']} 🗡️\n🚧 {current_game.win_condition} в ряд!"

            markup = None
            if not current_game.check_winner(current_game.current_player) and not current_game.check_draw():
                markup = current_game.render_board()

            bot.edit_message_text(chat_id=chat_id, message_id=current_game.message_id, text=text, reply_markup=markup, parse_mode='Markdown')
            del games[chat_id]['data'][game_id]
            current_game.reset_game()
        return

    if action == 'move':
        game_id = int(query_data[3])
        current_game = games[chat_id]['data'].get(game_id)

        if current_game and current_game.game_active:
            row, col = map(int, query_data[1:3])
            if current_game.players[current_game.current_player] != user_id:
                bot.answer_callback_query(call.id, "⛔ Сейчас не ваш ход или вы не участвыете в этой игре!")
                return
            if current_game.game_board[row][col] != ' ':
                bot.answer_callback_query(call.id, "#️⃣ Клетка уже занята!")
                return

            current_game.game_board[row][col] = current_game.current_player
            if current_game.check_winner(current_game.current_player):
                winner_name = current_game.player_names[current_game.current_player]
                text = f"🏆 [{winner_name}](tg://user?id={current_game.players[current_game.current_player]}) победил(а)!\n\n🔪 [{current_game.player_names['X']}](tg://user?id={current_game.players['X']}) {current_game.player_symbols['X']} против [{current_game.player_names['O']}](tg://user?id={current_game.players['O']}) {current_game.player_symbols['O']} 🗡️\n🚧 {current_game.win_condition} в ряд!"
                bot.edit_message_text(chat_id=chat_id, message_id=current_game.message_id, text=text, reply_markup=current_game.render_board(), parse_mode='Markdown')
                del games[chat_id]['data'][game_id]
                current_game.reset_game()
                return

            if current_game.check_draw():
                text = f"😐 Ничья!\n\n🔪 [{current_game.player_names['X']}](tg://user?id={current_game.players['X']}) {current_game.player_symbols['X']} против [{current_game.player_names['O']}](tg://user?id={current_game.players['O']}) {current_game.player_symbols['O']} 🗡️\n🚧 {current_game.win_condition} в ряд!"
                bot.edit_message_text(chat_id=chat_id, message_id=current_game.message_id, text=text, reply_markup=current_game.render_board(), parse_mode='Markdown')
                del games[chat_id]['data'][game_id]
                current_game.reset_game()
                return

            current_game.current_player = 'X' if current_game.current_player == 'O' else 'O'
            markup = current_game.render_board()
            text = f"🔪 [{current_game.player_names['X']}](tg://user?id={current_game.players['X']})  {current_game.player_symbols['X']} против [{current_game.player_names['O']}](tg://user?id={current_game.players['O']}) {current_game.player_symbols['O']} 🗡️\n\n⏳ Текущий ход: [{current_game.player_names[current_game.current_player]}](tg://user?id={current_game.players[current_game.current_player]})\n🚧 {current_game.win_condition} в ряд!"
            bot.edit_message_text(chat_id=chat_id, message_id=current_game.message_id, text=text, reply_markup=markup, parse_mode='Markdown')

with open(admins_file, 'r') as file:
    admins = set(map(int, file.read().splitlines()))

with open(blocked_file, 'r') as file:
    blacklisted_users = set(map(int, file.read().splitlines()))

def save_user_info_to_file(username, user_id):
    if username not in added_users:
        with open(users_file, 'a') as file:
            file.write(f"@{username} - {user_id}\n")
        added_users.add(username)
        
@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    username = message.from_user.username
    user_id = message.from_user.id
    save_user_info_to_file(username, user_id)

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"{e}")
