import mysql.connector
import os
import pandas as pd

connection = mysql.connector.connect(user="root",host="localhost", password="123456", database="estoque_ifood")
mycursor = connection.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS estoque_ifood")
mycursor.execute("CREATE TABLE IF NOT EXISTS estoque (id INT PRIMARY KEY AUTO_INCREMENT, nome VARCHAR(255), quantidade INT,\
                  unidade_medida VARCHAR(255), custo VARCHAR(50), ultima_compra VARCHAR(50) )")

with open("gestor_estoque_COMPRAS.txt", "a+") as arquivo:
        ...

def read_and_display(table):
    mycursor.execute(f"SELECT * FROM {table}")
    query_return = []
    for x in mycursor.fetchall():
        query_return.append(x)
    df = pd.DataFrame(query_return, columns=["ID", "Nome do Produto", "Quantidade em Estoque", "Unidade de Medida"])
    print(df)


#Main Loop
while True:
    print("Seja bem vindo ao sistema!")
    print("Por favor, escolha uma opção.")
    print("1 - Mostrar estoque")
    print("2 - Cadastrar Estoque")
    print("3 - Saída do Estoque")
    print("4 - Compra de Material")
    print("5 - Informar Perdas")
    print("6 - Sair do Programa")
    choice = input("")

    if choice == "6":
        break
    elif choice == "1":
        os.system("cls")
        read_and_display("estoque")
        input("Digite qualquer coisa para sair.")

    elif choice == "2":
        os.system("cls")
        while True:
            print("Para sair do programa digite SAIR")
            print("Por favor, informe o nome do item que deseja cadastrar")
            
            entrada = input("")
            if entrada.upper() == "SAIR":
                break

            print("Você deseja armazenar esse item em G ou UN?")
            measure = input("").upper()

            if measure == "G":
                print("Por favor, informe a quantidade em G do item. Ex.: 100, 2150")
                quantidade = input("")
                quantidade = int(quantidade)
                mycursor.execute(f"INSERT INTO estoque_ifood.estoque (nome, quantidade, unidade_medida) VALUES ('{entrada}', {quantidade},'{measure}' )")
                connection.commit()

            elif measure == "UN":
                print("Por favor, informe a quantidade em G do item. Ex.: 15, 20")
                quantidade = input("")
                mycursor.execute(f"INSERT INTO estoque_ifood.estoque (nome, quantidade, unidade_medida) VALUES ('{entrada}', {quantidade},'{measure}' )")
                connection.commit()
            else:
                print("Unidade desconhecida, por favor, tente novamente.")

    elif choice == "4":
        os.system("cls")
        print("Seção de cadastro de compra de material")
        print("Por favor informe a data da compra. Ex.: 10/05/2024")
        data = input("")

        #Loop para pegar informações dos itens comprados.
        itens_comprados = []
        while True:
            print("Digite 'estoque' para visualizar o estoque. Digite 'sair' para sair do loop.")
            id_item = input("Por favor informe o id do item comprado.\n").lower()
            if id_item == "estoque":
                read_and_display("estoque")
                continue
            if id_item == "sair":
                break
            quantidade = input("\nPor favor digite a quantidade (G ou UN) do item comprado.\n")
            preco = input("\nPor favor digite o preço pago no produto (Ex.: 10.73)\n")
            local = input("\nPor favor informe o local onde o produto foi comprado.")
            itens_comprados.append((id_item, quantidade, preco, local))
            mycursor.execute(f"UPDATE estoque SET custo = {preco} WHERE id = {id_item}")
            connection.commit()
        
        #Abre o arquivo do histórico de compras e lê informações do id da compra, e escreve as informações dos itens comprados.
        with open("gestor_estoque_COMPRAS.txt", "a+") as arquivo:
            last_id = ""
            arquivo.seek(0,0)
            for x in arquivo.readlines():
                if "ID COMPRA" in x:
                    y = list(x)
                    last_id = y[-2]
            if last_id == "":
                arquivo.write(f"\n\nID COMPRA: 1\n")
            else:
                arquivo.write(f"ID COMPRA: {int(last_id) + 1}\n")
            arquivo.write(f"DATA COMPRA: {data}\n")
            arquivo.write("ITENS DA COMPRA:\n")
            for x in itens_comprados:
                arquivo.write(f"{x[0]},{x[1]},{x[2]},{x[3]}\n")
        input("Digite qualquer coisa para sair")
