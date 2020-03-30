import telebot
import config
import mysql.connector
from telebot import types
bot = telebot.TeleBot(config.TOKEN)

db = config.DB
cursor = db.cursor()

apteka_dict = {}

class Apteka:
    def __init__(self, name):
        self.name = name
        self.adress = None
        self.region = None
        self.selection = None
        self.sear_name = None
        self.constant = None
@bot.message_handler(commands=['start'])
def welcome(message):
    msg = bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAI3eV56Cj5ob-7NfqeTZ4HBdwvTZXhbAAJlAgADOKAKtGgxreR2qoYYBA')
    
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('👩🏻‍⚕️ Продавец-фармацевт', '🧴 Покупатель')
    bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный чтобы помочь, Вам!".format(message.from_user, bot.get_me()),
    parse_mode='html', reply_markup=markup)

    
@bot.message_handler(content_types=['text'])
def buyer(message):
    if message.text == '🧴 Покупатель' or message.text== '🚪 Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('👩🏻‍⚕️ Аптеки в Районах Бишкека', '🧴 Поиск Маски по названию и адресу','🚪 Выйти')
        send = bot.send_message(message.chat.id, "Выберите пожалуйста:", reply_markup=markup)
        bot.register_next_step_handler(send, discripe)
    if message.text == '👩🏻‍⚕️ Продавец-фармацевт':
        msg = bot.reply_to(message, "Название вашей аптеки?",reply_markup = types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        apteka = Apteka(name)
        apteka_dict[chat_id] = apteka
        msg = bot.reply_to(message, "Адрес вашей Аптеки?")
        bot.register_next_step_handler(msg, process_adress_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')
def process_adress_step(message):
    try:
        chat_id = message.chat.id
        adress = message.text
        apteka = apteka_dict[chat_id]
        apteka.adress = adress
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
        markup.add('Ленинский', 'Свердловский','Первомайский', 'Октябрьский')
        msg = bot.reply_to(message, 'Район вашей аптеки?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_desss_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')
def process_desss_step(message):
    try:
        chat_id = message.chat.id
        region = message.text
        apteka = apteka_dict[chat_id]
        apteka.region = region
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
        markup.add('Да', 'Нет',)
        msg = bot.send_message(chat_id, 'Название вашей аптеки: ' + apteka.name + '\n Адрес вашей аптеки: ' + 
        apteka.adress + '\n Ваш район: ' + apteka.region + '\nАптека успешно создана!', reply_markup=markup)
        bot.send_message(chat_id,'У вас имеются маски?')
        bot.register_next_step_handler(msg, mask)

    except Exception as e:
        bot.reply_to(message, 'oooops')


def mask(message):
    
    if message.text == 'Нет':
        Apteka.constant = False
        bot.send_message(message.chat.id,'Спасибо! Данные сохранены!')
        register(message)

    elif message.text == 'Да':
        Apteka.constant = True
        msg = bot.send_message(message.chat.id,'Введите количество:')
        bot.register_next_step_handler(msg,register)


def register(message):
    try:
        if Apteka.constant:
            chat_id = message.chat.id
            selection = message.text
        elif Apteka.constant == False:
            chat_id = message.chat.id
            selection = 0
        apteka = apteka_dict[chat_id]
        apteka.selection = selection
        sql = "INSERT INTO pharmacy (user_id, name, adress, region, mask) VALUES (%s, %s, %s, %s, %s)"
        val = (message.chat.id, apteka.name, apteka.adress, apteka.region, selection)
        cursor.execute(sql, val)
        db.commit()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
        markup.add('/start')
        msg = bot.send_message(chat_id, 'Можете нажать на кнопку и начнется чудо😄', reply_markup=markup)
        bot.register_next_step_handler(msg, welcome)
    except:
        bot.reply_to(message, 'oooops')



def discripe(message):
    if message.text == '👩🏻‍⚕️ Аптеки в Районах Бишкека':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Ленинский', 'Свердловский','Первомайский', 'Октябрьский','🚪 Назад')
        send = bot.send_message(message.chat.id, "Выберите пожалуйста:", reply_markup=markup)
        bot.register_next_step_handler(send, des)
    elif message.text == '🧴 Поиск Маски по названию и адресу':
        msg = bot.send_message(message.chat.id, 'Введите пожалуйста название аптеки:',reply_markup = types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg,search_names)
    elif message.text == '🚪 Выйти':
        exit_(message)
        
def search_names(message):
    sql = "SELECT * FROM pharmacy WHERE name LIKE %s"
    val = ('%'+ message.text +'%', )
    cursor.execute(sql,val)
    sear_name = cursor.fetchall()
    Apteka.sear_name = sear_name
    msg = bot.send_message(message.chat.id, 'Введите пожалуйста адрес аптеки:')
    bot.register_next_step_handler(msg,search_adress)

def search_adress(message):
    try:
        x = 0
        sql = "SELECT * FROM pharmacy WHERE adress LIKE %s"
        val = ('%'+ message.text +'%', )
        cursor.execute(sql,val)
        search = cursor.fetchall()
        for result in search:
            if result in Apteka.sear_name:
                bot.send_message(message.chat.id,"Название: " + result[0] +
                "\nАдрес: " + result[2] + "\nНаличие масок: " + str(result[4]))
                x+=1
        if x == 0:
            bot.send_message(message.chat.id, "Аптека с такими данными не зарегистрированна!")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('🚪 Назад')
        send = bot.send_message(message.chat.id, "Желаете вернуться назад?", reply_markup=markup)
        bot.register_next_step_handler(send, buyer)
    except:
        bot.reply_to(message, 'oooops')

def des(message):
    if message.text == "🚪 Назад":
        buyer(message)
    else:
        try:
            sql = "SELECT * FROM pharmacy WHERE region LIKE %s"
            val = (message.text,)
            cursor.execute(sql,val)
            regions = cursor.fetchall()
            for region_ in regions:
                bot.send_message(message.chat.id,"Название: " + region_[0] +
                "\nАдрес: " + region_[2] + "\nНаличие масок: " + str(region_[4]))
        except:
            bot.reply_to(message, 'oooops')

def exit_(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('/start')  
    msg = bot.send_message(message.chat.id, 'Можете нажать на кнопку и начнется чудо😄', reply_markup=markup)
    bot.register_next_step_handler(msg, welcome)



# RUN
# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()

bot.polling(none_stop=True)