Для установки MQTT брокера необходимо на любой системе линукс установить следующие программы:
- sudo apt mosquitto mosquitto-clients -y
Далее открыть доступ к порту:
- sudo ufw allow 1883/tcp
После добавиь в файл mosquitto.conf следующие строки (sudo nano /etc/mosquitto/mosquitto.conf)
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd

И перезапустить mosquitto (sudo systemctl restart mosquitto)
Для создания пользователя необходимо создать файл с логином и паролем:
sudo mosquitto_passwd -b /etc/mosquitto/passwd username1 password1
Список основных команд по упарвлению mosquitto
sudo mosquitto_passwd -b /etc/mosquitto/passwd username1 password1      (добавление пользователя)
sudo mosquitto_passwd -D /etc/mosquitto/passwd username1                (удаление пользователя)

mosquitto_sub -h localhost(192.168.0.0) -t "test/topic" -u username1 -P password1                    (подписка на топик)
mosquitto_pub -h localhost(192.168.0.0) -t "test/topic" -m "Auth message" -u username1 -P password1  (публикация в топик)

sudo systemctl status(stop, start, resturt) mosquitto (управление демоном mosquitto)
sudo nano /etc/mosquitto/passwd             (чтение файла паролей)
sudo nano /etc/mosquitto/mosquitto.conf     (чтение файла конфигурации)
