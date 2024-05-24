from pymongo import MongoClient
import os
import pandas as pd

connection_string: str = f"mongodb+srv://Caua_Marques:cauac1d2l3m4@clusterteste.dkyfftq.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTeste"
client = MongoClient(connection_string)
gestor_ifood_db = client["gestor_ifood"] #conecta a database gestor_ifood
compras = gestor_ifood_db.compras #conecta a collection compras
estoque = gestor_ifood_db.estoque #conecta a collection estoque
saidas = gestor_ifood_db.saidas #conecta a collection saidas
perdas = gestor_ifood_db.perdas #conecta a collection perdas

def get_latest_item_id() -> int:
    itens = estoque.find()
    ultimo_codigo: int = 0
    for item in itens:
        item_int: int = int(item["codigo"])
        if item_int > ultimo_codigo:
            ultimo_codigo = item_int
    return ultimo_codigo+1

def get_latest_compra_id() -> int:
    compra = compras.find()
    ultimo_codigo: int = 0
    for item in compra:
        if item["codigo_compra"] > ultimo_codigo:
            ultimo_codigo = item["codigo_compra"]
    return ultimo_codigo

def search_stock_by_codigo(codigo_produto: int) -> list:
    return estoque.find_one({"codigo": codigo_produto})

def read_and_display_collection(mongo_collection: str) -> bool:
    """
    mongo_collection: a connection to a mongo_db collection
    If the collection is empty, it returns False
    """
    dataset: list = []
    if mongo_collection == "estoque":
        keys: list[str] = ["codigo", "nome", "quantidade", "unidade_medida", "custo","data_ultima_compra","codigo_ultima_compra"]
        itens = estoque.find()
        for item in itens:
            dataset.append([item[keys[0]], item[keys[1]], item[keys[2]], item[keys[3]],item[keys[4]],item[keys[5]],item[keys[6]]])
        if not dataset:
            print("Nada encontrado. Tente cadastrar alguns itens!")
            return False
    elif mongo_collection == "compras":
        keys: list[str] =["codigo_compra", "nome_item", "codigo_item", "quantidade_comprada", "unidade_medida", "data_compra", "local_compra", "custo"]
        itens = compras.find()
        for item in itens:
            dataset.append([item[keys[0]], item[keys[1]],item[keys[2]],item[keys[3]],item[keys[4]],item[keys[5]],\
                            item[keys[6]], item[keys[7]]]) 
        if not dataset:
            print("Nada encontrado. Tente cadastrar alguns itens!")
            return False 
    elif mongo_collection == "saidas":
        keys: list[str] = ["codigo_venda_ifood", "data"]
        itens = saidas.find()
        for item in itens:
            dataset.append([item[keys[0]], item[keys[1]]])
        if not dataset:
            print("Nada encontrado. Tente cadastrar alguns itens!")
            return False
    else:
        raise ValueError("A coleção MONGO_DB informada não é reconhecida internamente.")
    
    print(pd.DataFrame(dataset, columns=keys).to_string())
    return True

def ask_for_multiple_input(*args: str) -> tuple | bool:
    response = []
    print("Para sair do programa não digite nada e aperte Enter!")
    for msg in args:
        r = input(f"{msg}\n")
        if r == "":
            return False
        response.append(r)
    return tuple(response)

def display_options(*args: str) -> str:
    counter = 1
    print("Para sair do programa não digite nada e aperte Enter!")
    for msg in args:
        print(f"{counter} - {msg}")
        counter+=1
    r = input()
    return r

#Main Loop
if __name__ == "__main__":
    while True:
        os.system("cls")
        print("Seja bem vindo ao sistema!")
        user_input: str = display_options("Mostrar estoque","Cadastrar Estoque", "Saída do Estoque",\
                                    "Compra de Material","Informar Perdas")

        if not user_input: #Sair do programa
            break
        elif user_input == "1": #Mostrar estoque
            os.system("cls")
            read_and_display_collection("estoque")
            input()

        elif user_input == "2": #Cadastrar estoque (OK)
            os.system("cls")
            while True:
                multiple_user_input: tuple | bool = ask_for_multiple_input("Por favor, informe o nome do item que deseja cadastrar",
                                                                           "Você deseja armazenar esse item em G ou UN?",
                                                                           "Por favor, informe a quantidade do item. Ex.: 100, 2150")

                if not multiple_user_input:
                    break
                try:
                    nome_item, measure, quantidade = multiple_user_input
                    measure: str = measure.upper()
                    if measure not in ("G","UN"):
                        raise ValueError
                    quantidade: int = int(quantidade)
                except ValueError:
                    input("O VALOR INFORMADO ESTÁ INCORRETO. TENTE NOVAMENTE")
                    continue
                codigo_item: int = get_latest_item_id() + 1
                estoque.insert_one({"codigo":codigo_item, "nome": nome_item, "quantidade": quantidade, "unidade_medida": measure, "custo": 0.0,
                                    "data_ultima_compra": "", "codigo_ultima_compra": 0})
                print("\nInserção realizada com sucesso!")

        elif user_input == "3": #Saída do estoque ()
            os.system("cls")
            user_input: str = display_options("Criar saídas","Alterar saídas", "Deletar saídas","Histórico de saídas")

            if user_input == "1": #CRIAR SAÍDAS (OK)
                user_multiple_input: tuple | bool = ask_for_multiple_input("Digite a data da saída", "Digite o Código da Venda do Ifood")
                if not user_multiple_input:
                    continue

                data: str = user_multiple_input[0]
                try:
                    codigo_venda_ifood: int = int(user_multiple_input[1])
                    itens_saida: list[tuple[int]] = []
                    while True:
                        if not read_and_display_collection("estoque"):
                            input()
                            break
                        
                        user_multiple_input: tuple | bool = ask_for_multiple_input("Informe o código do item a dar saída", "Informe a quantidade utilizada")
                        if not user_multiple_input:
                            break
                        #Para fins de readability do código, deixarei desta forma, poderia dar append(int(user_multiple)).
                        codigo_item = int(user_multiple_input[0])
                        quantidade = int(user_multiple_input[1])
                        itens_saida.append((codigo_item, quantidade))
                except ValueError:
                    input("UM VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")
                    continue

                documento: dict = {"codigo_venda_ifood": codigo_venda_ifood,"data":data , "codigos_item_saida":{}}
                for codigo, quantidade in itens_saida:
                    #vai olhar no dicionário codigos_item_saida se o codigo_item está presente, 
                    #caso positivo, vai apenas somar o valor pela nova quantidade informada
                    if documento["codigos_item_saida"].get(codigo): 
                        documento["codigos_item_saida"][codigo] += quantidade
                        continue
                    #caso negativo, vai criar o par de chave-valor no dicionário
                    documento["codigos_item_saida"][codigo] = quantidade
                saidas.insert_one(documento)

            elif user_input == "2": #ALTERAR SAÍDAS (OK)
                while True:
                    os.system("cls")
                    print("Histórico de saídas:")
                    if not read_and_display_collection("saidas"):
                        input()
                        break
                    codigo_venda_ifood = input("Para sair, digite 'sair'.\nDigite o Código da Venda do Ifood\n").lower()
                    if codigo_venda_ifood == "sair":
                        break
                    try:
                        codigo_venda_ifood: int = int(codigo_venda_ifood)
                    except ValueError:
                        input("O VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")
                    saida: list[dict] = [x for x in saidas.find({"codigo_venda_ifood": codigo_venda_ifood})]
                    if not saida:
                        input("Não há nenhum registro de saída para esse código de venda")
                        continue

                    print("\ncodigos_item_saida: ")
                    for chave, valor in saida[0]["codigos_item_saida"].items():
                        print("codigo_item:",chave,"quantidade:",valor)

                    user_multiple_input: tuple | bool = ask_for_multiple_input("Por favor, informe o código do item que deseja alterar",
                                                                                "Informe a quantidade que deseja inserir")
                    if not user_multiple_input:
                        continue
                    try:
                        codigo_item = int(user_multiple_input[0] )
                        quantidade = int(user_multiple_input[1])
                    except ValueError:
                        input("UM VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")
                    saidas.update_one({"codigo_venda_ifood": codigo_venda_ifood}, {"$set":{f"codigos_item_saida.{codigo_item}": quantidade}})
                    input("Saída alterada com sucesso")

            elif user_input == "3": #DELETAR SAIDAS (OK)
                if not read_and_display_collection("saidas"):
                    input()
                    continue
                print("Para sair não digite nada e aperte Enter")
                codigo_venda_ifood: str = input("\nPor favor, digite o código de venda do ifood\n")
                if not codigo_venda_ifood:
                    continue
                try:
                    saidas.delete_one({"codigo_venda_ifood":int(codigo_venda_ifood)})
                except ValueError:
                    input("O VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")

            elif user_input == "4": #LISTAR SAIDAS (OK)
                while True:
                    os.system("cls")
                    print("Histórico de saídas:")
                    if not read_and_display_collection("saidas"):
                        input()
                        break
                    codigo_venda_ifood: str = input("Para sair, digite 'sair'.\nDigite o Código da Venda do Ifood\n").lower()
                    if codigo_venda_ifood == "sair":
                        break
                    try:
                        saida: list[dict] = [x for x in saidas.find({"codigo_venda_ifood": int(codigo_venda_ifood)})]
                    except ValueError:
                        input("O VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")
                    if not saida:
                        input("Não há nenhum registro de saída para esse código de venda")
                        continue

                    print("\ncodigos_item_saida: ")
                    for chave, valor in saida[0]["codigos_item_saida"].items():
                        print("codigo_item:",chave,"quantidade:",valor)
                    input()

        elif user_input == "4": #Compra de material ()
            os.system("cls")
            print("Seção de cadastro de compra de material")
            user_input: str = display_options("Cadastrar uma nova compra. (novo código de compra)", \
                                        "Acrescentar itens a uma compra existente", "Deletar compra",\
                                            "Ver histórico de compras")
            if not user_input:
                continue

            elif user_input == "1": #Cadastrar nova compra
                os.system("cls")
                itens_comprados: list[tuple] = []
                while True:
                    if not read_and_display_collection("estoque"):
                        input()
                        break
                    multiple_user_input: tuple | bool = ask_for_multiple_input("Por favor, informe a data da compra!",
                                                                "Por favor informe o codigo do item comprado",
                                                                "Por favor digite a QUANTIDADE em gramas ou em unidade do item comprado",
                                                                "Por favor digite o preço pago no produto (Ex.: 10.73)",
                                                                "Por favor informe o local onde o produto foi comprado")
                    if not multiple_user_input:
                        break
                    data, codigo_item, quantidade, preco, local = multiple_user_input
                    try:
                        itens_comprados.append((int(codigo_item), int(quantidade), float(preco), local))
                    except ValueError:
                        input("O VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")
                    os.system("cls")

                codigo_compra: int = get_latest_compra_id()
                for item in itens_comprados:
                    search: list = search_stock_by_codigo(item[0])
                    documento = {"codigo_compra": codigo_compra, "nome_item":search["nome"], "codigo_item": item[0], "quantidade_comprada": item[1] ,\
                                "unidade_medida": search["unidade_medida"], "data_compra": data, "local_compra": item[3], "custo": item[2]}
                    compras.insert_one(documento)

                os.system("cls")
                print("\nCompra cadastrada com sucesso!")
                input()

            elif user_input == "2": #Acrescentar itens a uma compra existente (REFATORAR)
                os.system("cls")
                if not read_and_display_collection("compras"):
                    input()
                    continue
                print("Para sair da seção, não digite nada e aperte Enter.")
                codigo_compra: str = input("Por favor informe o código da compra\n")
                if not codigo_compra:
                    continue
                
                os.system("cls")
                if not read_and_display_collection("estoque"):
                    input()
                    continue
                multiple_user_input: tuple | bool = ask_for_multiple_input("Por favor digite o código do item que você deseja alterar",\
                                                                            "Por favor digite qual chave você deseja alterar",\
                                                                            "Por favor digite qual valor você quer nessa chave")
                codigo_item, chave, valor = ask_for_multiple_input
                try:
                    compras.update_one({"codigo_compra": int(codigo_compra), "codigo_item": int(codigo_item)}, {"$set": {chave:valor}})
                except ValueError:
                    input("O VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")

            elif user_input == "3": #Deletar uma compra existente
                os.system("cls")
                if not read_and_display_collection("compras"):
                    continue
                codigo_compra: str = input("Para sair da seção, não digite nada e aperte Enter.\nPor favor informe o código da compra\n")
                if not codigo_compra:
                    continue 
                try:
                    compras.delete_many({"codigo_compra": int(codigo_compra)})
                except ValueError:
                    input("O VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")
                input("Histórico da compra deletada.")

            elif user_input == "4": #Mostrar o histórico de compras
                os.system("cls")
                if not read_and_display_collection("compras"):
                    input()
                    continue

        elif user_input == "5": #Perda de material (FALTA FUNCIONALIDADE)
            os.system("cls")
            if not read_and_display_collection("estoque"):
                input()
                continue
            codigo_item: str = input("Por favor informe o código do item\n")
            if not codigo_item:
                continue
            
            lista_perdas: list[dict] = [x for x in perdas.find({"codigo_item":codigo_item})]
            os.system("cls")
            user_multiple_input: tuple | bool = ask_for_multiple_input("Informe a data da perda", "Informe a quantidade perdida", "Por favor, informe alguma observação")
            if not user_multiple_input:
                continue
            try:
                codigo_item = int(codigo_item)
                quantidade = int(user_multiple_input[1])
                data, _, observacao = user_multiple_input
            except ValueError:
                input("O VALOR INFORMADO ESTÁ INCORRETO, POR FAVOR TENTE NOVAMENTE")

            if lista_perdas: #Verifica se o codigo_item informado já tem um documento criado na coleção
                datas_cadastradas: list[str] = [data for data in lista_perdas[0["perdas"]]]
                if data in datas_cadastradas: #Verifica se a data que o usuário informou já existe na coleção
                    perdas.update_one({"codigo_item":codigo_item}, {"$inc":{f"perdas.{data}.quantidade_perdida": quantidade},"$set":{f"perdas.{data}.observacao": observacao}})
                    os.system("cls")
                    input("Perda cadastrada!")
                    continue

                #Caso a data não exista, ele irá criar uma data na coleção
                perdas.update_one({"codigo_item":codigo_item}, {"$set":{f"perdas.{data}.quantidade_perdida": quantidade},"$set":{f"perdas.{data}.observacao": observacao}})
                os.system("cls")
                input("Perda cadastrada!")
                continue
        
            #Caso o codigo_item informado não tenha um documento na coleção, será criado um.
            item: list = search_stock_by_codigo(codigo_item)
            document: dict = {"codigo_item":codigo_item, "nome": item["nome"], "perdas":{data:{"quantidade_perdida":quantidade,"observacao":observacao}}}
            perdas.insert_one(document)
            os.system("cls")
            input("Perda cadastrada!")
            continue
