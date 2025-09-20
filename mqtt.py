import threading
import context
import time
import paho.mqtt.client as mqtt
import telebot
from telebot import types
import struct
import subprocess
import os

broker = '192.168.0.103'
port = 1883
humiditi_topic = "dht11/humiditi"
temperature_topic = "dht11/temperature"
illuminance_topic = "photores/illuminance"
mypy_topic = "python/mypy"
username = 'mypy'
password = '7777'

bot = telebot.TeleBot('7177996917:AAG2TlV-TvIC7m5ki6j_zqV-9LdWIMBuWDw')
lock = threading.Lock()
temp = 0
humidity = 0
Illumination = 0

##================================================
##===================== MQTT =====================
##================================================
def connect_mqtt() -> mqtt:
    def on_connect(mqttc, obj, flags, reason_code, properties):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", reason_code)
            error_codes = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised"
            }


    def on_message(mqttc, obj, msg):
        global humidity
        global temp
        global Illumination
        global humiditi_topic
        global temperature_topic
        global illuminance_topic
        
        with lock:
            if msg.topic == humiditi_topic:
                print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
                humidity = int.from_bytes(msg.payload)
            elif msg.topic == temperature_topic:
                print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
                temp = int.from_bytes(msg.payload)
            elif msg.topic == illuminance_topic:
                print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
                Illumination = struct.unpack('f', msg.payload[0:4])[0]


    def on_subscribe(mqttc, obj, mid, reason_code_list, properties):
        print("Subscribed: " + str(mid) + " " + str(reason_code_list))


    def on_log(mqttc, obj, level, string):
        print(string)
    
    def on_publish(mqttc, obj, mid, reason_code, properties):
        print("mid: " + str(mid))

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.username_pw_set(username, password)
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_subscribe = on_subscribe
    mqttc.on_log = on_log
    mqtt.on_publish = on_publish
    mqttc.connect(broker, port, 60)
    mqttc.publish(humiditi_topic, "start")
    mqttc.publish(temperature_topic, "start")
    mqttc.publish(illuminance_topic, "start")
    return mqttc

def subscribe(client: mqtt, topic):
    client.subscribe(topic)

def publish(client: mqtt, topic, msg):
    client.publish()

def mqtt_client_thread():
    try:
        client = connect_mqtt()
        subscribe(client, humiditi_topic)
        subscribe(client, temperature_topic)
        subscribe(client, illuminance_topic)
        client.loop_forever()
    except Exception as e:
        print(f"MQTT error: {e}")
##================================================
##==================== ТГ-БОТ ====================
##================================================
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Мультисенсор")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == 'Мультисенсор':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Температура')
        btn2 = types.KeyboardButton('Влажность')
        btn3 = types.KeyboardButton('Освещенность')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup) #ответ бота

    elif message.text == 'Температура':
        with lock:
            bot.send_message(message.from_user.id, f'Температура: {temp}', parse_mode='Markdown')

    elif message.text == 'Влажность':
        with lock:
            bot.send_message(message.from_user.id, f'Влажность: {humidity}', parse_mode='Markdown')

    elif message.text == 'Освещенность':
        with lock:
            bot.send_message(message.from_user.id, f'Освещенность: {Illumination}', parse_mode='Markdown')

def telegram_bot_thread():
    try:
        print("Starting Telegram bot...")
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"Telegram bot error: {e}")
##================================================
##==================== LINUX =====================
##================================================
def run_sudo_nopasswd(cmd):
    """Выполняет команду с sudo"""
    try:

        result = subprocess.run(
            f'sudo {cmd}', 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✓ Команда выполнена: {cmd}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка выполнения: {cmd}")
        print(f"Ошибка: {e.stderr}")
        return None

##================================================
##================================================
def run():
    mqtt_thread = threading.Thread(target=mqtt_client_thread, daemon=True)
    telegram_thread = threading.Thread(target=telegram_bot_thread, daemon=True)
    
    mqtt_thread.start()
    telegram_thread.start()
    
    print("Both services are running...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping services...")


if __name__ == '__main__':
    # run()
    commands = [
        "netbird service uninstall",
        "netbird service install",
        "netbird service start"
    ]
    
    for cmd in commands:
        output = run_sudo_nopasswd(cmd)
        if output:
            print(f"Результат: {output}")
        print("-" * 50)

sudo systemctl start start_process.service
systemctl status start_process.service
##===========================================================
##===========================================================
##===========================================================
# import telebot
# from telebot import types

# bot = telebot.TeleBot('7177996917:AAG2TlV-TvIC7m5ki6j_zqV-9LdWIMBuWDw')

# temp = 0
# humidity = 0
# Illumination = 0

# @bot.message_handler(commands=['start'])
# def start(message):

#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("Мультисенсор")
#     markup.add(btn1)
#     bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)

# @bot.message_handler(content_types=['text'])
# def get_text_messages(message):

#     if message.text == 'Мультисенсор':
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
#         btn1 = types.KeyboardButton('Температура')
#         btn2 = types.KeyboardButton('Влажность')
#         btn3 = types.KeyboardButton('Освещенность')
#         markup.add(btn1, btn2, btn3)
#         bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup) #ответ бота

#     elif message.text == 'Температура':
#         bot.send_message(message.from_user.id, f'Температура: {temp} С', parse_mode='Markdown')

#     elif message.text == 'Влажность':
#         bot.send_message(message.from_user.id, f'Влажность: {humidity} %', parse_mode='Markdown')

#     elif message.text == 'Освещенность':
#         bot.send_message(message.from_user.id, f'Освещенность: {Illumination} люкс', parse_mode='Markdown')


# bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть
##===========================================================
# def on_connect(mqttc, obj, flags, reason_code, properties):
#     if reason_code == 0:
#         print("Connected to MQTT Broker!")
#     else:
#         print("Failed to connect, return code %d\n", rc)
#         error_codes = {
#             1: "Connection refused - incorrect protocol version",
#             2: "Connection refused - invalid client identifier",
#             3: "Connection refused - server unavailable",
#             4: "Connection refused - bad username or password",
#             5: "Connection refused - not authorised"
#         }


# def on_message(mqttc, obj, msg):
#     print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


# def on_subscribe(mqttc, obj, mid, reason_code_list, properties):
#     print("Subscribed: " + str(mid) + " " + str(reason_code_list))


# def on_log(mqttc, obj, level, string):
#     print(string)

# mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# mqttc.username_pw_set(username, password)
# mqttc.on_message = on_message
# mqttc.on_connect = on_connect
# mqttc.on_subscribe = on_subscribe
# mqttc.connect(broker, port, 60)
# mqttc.subscribe(topic)

# mqttc.loop_forever()


