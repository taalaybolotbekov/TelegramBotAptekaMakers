import mysql.connector


TOKEN = '880477033:AAGbz8FgikJuOIS71b_amWMlXmD_ym6CYg8'  #bot token  @BotFather
DB = mysql.connector.connect(
  host=" 127.0.0.1",
  user="root",
  passwd="root",
  port="3306",
  database="pharmacist"
)

