from pymongo import MongoClient
import os
import pandas as pd
import pprint
printer = pprint.PrettyPrinter()

connection_string = f"mongodb+srv://Caua_Marques:cauac1d2l3m4@clusterteste.dkyfftq.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTeste"
client = MongoClient(connection_string)
gestor_ifood_db = client["gestor_ifood"] #conecta a database gestor_ifood
compras = gestor_ifood_db.compras #conecta a collection compras
estoque = gestor_ifood_db.estoque #conecta a collectio estoque
saidas = gestor_ifood_db.saidas #conecta a collection saidas

def get_latest_item_id():
    itens = estoque.find()
    ultimo_codigo = 0
    for item in itens:
        item_int = int(item["codigo"])
        if item_int > ultimo_codigo:
            ultimo_codigo = item_int
    return ultimo_codigo+1

def get_latest_compra_id():
    compra = compras.find()
    ultimo_codigo = 0
    for item in compra:
        if item["codigo_compra"] > ultimo_codigo:
            ultimo_codigo = item["codigo_compra"]
    return ultimo_codigo

def search_stock_by_codigo(codigo_produto):
    return estoque.find_one({"codigo": codigo_produto})

def read_and_display_stock():
    columns = ["Código", "Nome", "Quantidade em Estoque", "Unidade de Medida", "Custo", "Data da Ultima Compra", "Código da Ultima Compra"]
    dataset = []
    itens = estoque.find()
    for item in itens:
        dataset.append([item["codigo"], item["nome"], item["quantidade"], item["unidade_medida"],item["custo"],item["data_ultima_compra"],item["codigo_ultima_compra"]])
    data_frame = pd.DataFrame(dataset, columns=columns)
    print(data_frame.to_string())


#Main Loop
while True:
    os.system("cls")
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
        read_and_display_stock()
        input("Digite qualquer coisa para sair.")

    elif choice == "2":
        os.system("cls")
        while True:
            print("Para sair do programa digite SAIR")
            print("Por favor, informe o nome do item que deseja cadastrar")
            
            codigo_compra = input("")
            if codigo_compra.upper() == "SAIR":
                break

            print("Você deseja armazenar esse item em G ou UN?")
            measure = input("").upper()
            codigo = get_latest_item_id()
            codigo +=1
      
            print("Por favor, informe a quantidade do item. Ex.: 100, 2150")
            quantidade = input("")
            quantidade = int(quantidade)
            document = {"codigo":codigo, "nome": codigo_compra, "quantidade": quantidade, "unidade_medida": measure, "custo": " ",\
                        "data_ultima_compra": " ", "codigo_ultima_compra": " "}
            inserted_id = estoque.insert_one(document).inserted_id
            print("\nInserção realizada com sucesso!")
            print(inserted_id)

    elif choice == "3":
        print("Por favor, escolha uma opção")
        print("1 - Criar saídas")
        print("2 - Alterar saídas")
        print("3 - Deletar saídas")
        print("4 - Histórico de saídas")
        print("Digite qualquer outro número para sair da seção.")

        choice = input("")

        if choice == "1":#CRIAR SAÍDAS
            print("Digite o Código da Venda do Ifood: ")
            codigo_venda_ifood = input("")
            print("Digite a data da saída: ")
            data = input("")

            itens_saida = []
            while True:
                print("Digite 'estoque' para ver o estoque. Digite 'sair' para sair do loop.")
                print("Informe o código do item a dar saída: ")
                codigo_item = input("")
                while codigo_item == "estoque":
                    read_and_display_stock()
                    print("Digite 'estoque' para ver o estoque. Digite 'sair' para sair do loop.")
                    print("Informe o código do item a dar saída: ")
                    codigo_item = input("")

                if codigo_item == "sair":
                    break

                print("Informe a quantidade utilizada: ")
                quantidade = input("")
                itens_saida.append((codigo_item, quantidade))
            document = {"codigo_venda_ifood": codigo_venda_ifood,"data":data , "codigos_item_saida":{}}
            for item in itens_saida:
                if document["codigos_item_saida"].get(item[0]):
                    document["codigos_item_saida"][item[0]] = str(int(document["codigos_item_saida"][item[0]]) + int(item[1]))
                else:
                    document["codigos_item_saida"][item[0]] = item[1]
            saidas.insert_one(document)

        elif choice == "2": #ALTERAR SAÍDAS
            print("Digite o Código da Venda do Ifood: ")
            codigo_venda_ifood = input("")
            saida = saidas.find({"codigo_venda_ifood": codigo_venda_ifood})
            columns = ["codigo_venda_ifood", ]
            for doc in saida:
                print("codigos_item_saida: ")
                for chave, valor in doc["codigos_item_saida"].items():
                    print("codigo_item:",chave,"Quantidade:",valor)
            print("\nPor favor, informe o código do item que deseja alterar")
            codigo_item = input("\n")
            print("Informe a quantidade que deseja inserir")
            quantidade = input("\n")
            saidas.update_one({"codigo_venda_ifood": codigo_venda_ifood}, {"$set":{f"codigos_item_saida.{codigo_item}": quantidade}})

        elif choice == "3": #DELETAR SAIDAS
            print("Digite o Código da Venda do Ifood: ")
            codigo_venda_ifood = input("")
            saidas.delete_one({"codigo_venda_ifood":codigo_venda_ifood})

        elif choice == "4": #LISTAR SAIDAS
            
            while True:
                os.system("cls")
                saida = saidas.find()
                for x in saida:
                    print("Código Venda Ifood:",x["codigo_venda_ifood"],"|","Data:", x["data"])
                print("Digite 'sair' para sair da seção")
                print("\nDigite o código da venda que você deseja ver os itens: ")
                entrada = input("")
                if entrada == "sair":
                    break
                saida = saidas.find({"codigo_venda_ifood":entrada})
                for x in saida:
                    for chave, valor in x["codigos_item_saida"].items():
                        print("codigo_item:", chave, "|","quantidade:",valor)
                input()

    elif choice == "4":
        os.system("cls")
        def get_item_comprado():
            itens_comprados = []
            while True:
                print("Digite 'estoque' para visualizar o estoque. Digite 'sair' para sair do loop.")
                codigo_item = input("Por favor informe o id do item comprado.\n").lower()
                if codigo_item == "estoque":
                    read_and_display_stock()
                    continue
                if codigo_item == "sair":
                    break
                quantidade = input("\nPor favor digite a quantidade (G ou UN) do item comprado.\n")
                preco = input("\nPor favor digite o preço pago no produto (Ex.: 10.73)\n")
                local = input("\nPor favor informe o local onde o produto foi comprado.")
                itens_comprados.append((int(codigo_item), quantidade, preco, local))
            return itens_comprados

        print("Seção de cadastro de compra de material")
        print("1 - Cadastrar uma nova compra. (novo código de compra)")
        print("2 - Acrescentar itens a uma compra existente")
        print("3 - Deletar compra")
        print("4 - Ver histórico de compras")
        print("Digite qualquer outro número para sair desta seção")
        choice = input("")
    
        if choice == "1":
            os.system("cls")
            print("Por favor informe a data da compra. Ex.: 10/05/2024 (digite 'sair' para sair)")
            data = input("")
            if data == "sair":
                continue
            itens_comprados = get_item_comprado()
            codigo_compra = get_latest_compra_id()
            
            for item in itens_comprados:
                response = search_stock_by_codigo(item[0])
                documento = {"codigo_compra": codigo_compra, "nome_item":response["nome"], "codigo_item": item[0], "quantidade_comprada": item[1] ,\
                            "unidade_medida": response["unidade_medida"], "data_compra": data, "local_compra": item[3], "custo": item[2]}
                compras.insert_one(documento)
            print("\nCompra cadastrada com sucesso!")

        elif choice == "2":
            os.system("cls")
     
            print("Digite 'historico' para ver o histórico de compras. Digite 'sair' para sair desta seção.")
            print("Por favor informe o código da compra")
            codigo_compra = input()
            while codigo_compra == "historico":
                os.system("cls")
                compra = compras.find()
                columns = ["codigo_compra", "nome_item", "codigo_item", "quantidade_comprada", "unidade_medida", "data_compra", "local_compra", "custo"]
                dataset = []
                for item in compra:
                    dataset.append([item["codigo_compra"], item["nome_item"],item["codigo_item"],item["quantidade_comprada"],item["unidade_medida"],item["data_compra"],
                                    item["local_compra"], item["custo"]])
                data_frame = pd.DataFrame(dataset, columns=columns)
                print(data_frame.to_string())
                input("Digite qualquer coisa para sair.")

                os.system("cls")
                print("Por favor informe o código da compra")
                print("Digite 'historico' para ver o histórico de compras. Digite 'sair' para sair desta seção.")
                codigo_compra = input()

            if codigo_compra == "sair":
                continue

            os.system("cls")
            compra = compras.find({"codigo_compra":int(codigo_compra)})
            columns = ["codigo_compra", "nome_item", "codigo_item", "quantidade_comprada", "unidade_medida", "data_compra", "local_compra", "custo"]
            dataset = []
            for item in compra:
                dataset.append([item["codigo_compra"], item["nome_item"],item["codigo_item"],item["quantidade_comprada"],item["unidade_medida"],item["data_compra"],
                                    item["local_compra"], item["custo"]])
            data_frame = pd.DataFrame(dataset, columns=columns)
            print(data_frame.to_string())
            print("\nPor favor digite o código do item que você deseja alterar: ")
            codigo_item = input("")
            print("Por favor digite qual chave você deseja alterar: ")
            chave = input("")
            print("Por favor digite qual valor você quer nessa chave: ")
            valor = input("")
            compras.update_one({"codigo_compra": int(codigo_compra), "codigo_item": int(codigo_item)}, {"$set": {chave:valor}})
        
        elif choice == "3":
            os.system("cls")
            while True:
                print("Digite 'historico' para ver o histórico de compras")
                print("Por favor informe o código da compra")
                codigo_compra = input()
                if codigo_compra != "historico":
                    break
                if codigo_compra == "historico":
                    compra = compras.find()
                    columns = ["codigo_compra", "nome_item", "codigo_item", "quantidade_comprada", "unidade_medida", "data_compra", "local_compra", "custo"]
                    dataset = []
                    for item in compra:
                        dataset.append([item["codigo_compra"], item["nome_item"],item["codigo_item"],item["quantidade_comprada"],item["unidade_medida"],item["data_compra"],
                                        item["local_compra"], item["custo"]])
                    data_frame = pd.DataFrame(dataset, columns=columns)
                    print(data_frame.to_string())
                    input("Digite qualquer coisa para sair.")
            compras.delete_many({"codigo_compra": int(codigo_compra)})
            print("Histórico da compra deletada.")

        elif choice == "4":
            compra = compras.find()
            columns = ["codigo_compra", "nome_item", "codigo_item", "quantidade_comprada", "unidade_medida", "data_compra", "local_compra", "custo"]
            dataset = []
            for item in compra:
                dataset.append([item["codigo_compra"], item["nome_item"],item["codigo_item"],item["quantidade_comprada"],item["unidade_medida"],item["data_compra"],
                                item["local_compra"], item["custo"]])
            data_frame = pd.DataFrame(dataset, columns=columns)
            print(data_frame.to_string())
            input("Digite qualquer coisa para sair")
