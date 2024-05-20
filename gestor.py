import mysql.connector


connect = mysql.connector.connect(user="root",host="localhost", password="123456", database="estoque_ifood")
mycursor = connect.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS estoque_ifood")
mycursor.execute("CREATE TABLE IF NOT EXISTS estoque (id INT PRIMARY KEY AUTO_INCREMENT, nome VARCHAR(50), quantidade INT(50))")


#Main Loop
while True:
    print("Seja bem vindo ao sistema ")