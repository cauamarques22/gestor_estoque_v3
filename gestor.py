#Objetivo: pegar as funcionalidades do programa e transformar em classes.
from gestor import read_and_display_collection, get_latest_item_id
from pymongo import MongoClient
import os
import pandas as pd

connection_string: str = f"mongodb+srv://Caua_Marques:cauac1d2l3m4@clusterteste.dkyfftq.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTeste"
client = MongoClient(connection_string)
gestor_ifood_db = client["gestor_ifood"] #conecta a database gestor_ifood
compras = gestor_ifood_db.compras #conecta a collection compras
perdas = gestor_ifood_db.perdas #conecta a collection perdas

class GlobalFunctions:
    
    def display_options_to_user(self,*args: str) -> str:
        #Recebe strings empacotadas, e retorna a resposta do user.
        _counter: int = 1
        print("Por favor escolha uma das opções abaixo")
        for x in args:
            print(f"{_counter} - {x}")
            _counter += 1
        print("Para sair do programa não digite nada e aperte Enter!")
        _user_response: str = input("\n")
        if not _user_response:
            return False
        return _user_response

    def ask_for_multiple_input(self,*args: tuple) -> tuple | bool:
        #Recebe uma tupla de argumentos composta por: (pergunta, tipo de variável esperada)
        #Retorna uma tupla com as respostas das perguntas.
        response = []
        print("Para sair do programa não digite nada e aperte Enter!")
        for msg, tipo in args:
            r: str = input(f"{msg}\n")
            if not isinstance(r, tipo):
                raise ValueError("O VALOR INFORMADO ESTÁ INCORRETO.")
            if not r:
                return False
            response.append(r)
        return tuple(response)
    
    def function_caller(self,user_input: str, functions: tuple) -> None:
        lookup_table: dict = {}
        counter: int = 1
        for function in functions:
            lookup_table[str(counter)] = function
            counter+=1
        lookup_table[user_input]()

class Estoque(GlobalFunctions):
    OP1: str = "Mostrar estoque"
    OP2: str = "Cadastrar estoque"
    OP3: str = "Alterar informações dos produtos cadastrados"
    OP4: str = "Deletar itens do estoque"
    def __init__(self):
        #mainloop
        self._estoque_collection = gestor_ifood_db.estoque #conecta a collection estoque
        __user_response: str = self.display_options_to_user(self.OP1,self.OP2,self.OP3,self.OP4)
        if __user_response:
            self.function_caller(__user_response, (self.mostrar_estoque, self.cadastrar_estoque, self.alterar_estoque, self.deletar_estoque))

    def mostrar_estoque(self):
        if not read_and_display_collection("estoque"):
            input()
            return
    def cadastrar_estoque(self):
        Q1: str = "Por favor, informe o nome do item que deseja cadastrar"
        Q2: str = "Você deseja armazenar esse item em G ou UN?"
        Q3: str = "Por favor, informe a quantidade do item em estoque"
        try:
            response_tuple: tuple|bool= self.ask_for_multiple_input((Q1, str), (Q2, str), (Q3, int))
            if not response_tuple:
                return
        except ValueError:
            input("O VALOR INFORMADO ESTÁ INCORRETO")
            return
        nome_item, unidade_medida, quantidade = response_tuple
        codigo_item: int = get_latest_item_id() + 1
        self._estoque_collection.insert_one({"codigo":codigo_item, "nome": nome_item, "quantidade": quantidade, "unidade_medida": unidade_medida, "custo": 0.0,
                                             "data_ultima_compra": "", "codigo_ultima_compra": 0})
        print("\nInserção realizada com sucesso!")

    def alterar_estoque(self):
        ...
    
    def deletar_estoque(self):
        ...
        
class SaidaEstoque(GlobalFunctions):
    OP1: str = "Histórico de saídas"
    OP2: str = "Criar Saídas"
    OP3: str = "Alterar saídas"
    OP4: str = "Deletar saídas"
    def __init__(self):
        #mainloop
        self._saidas = gestor_ifood_db.saidas #conecta a collection saidas
        __user_response: str = self.display_options_to_user(self.OP1, self.OP2, self.OP3, self.OP4)
        if __user_response:
            self.function_caller(__user_response,...)

    def mostrar_historico_saidas(self):
        ...
    def criar_saidas(self):
        Q1: str = "Digite a data da saída"
        Q2: str = "Digite o código da Venda do Ifood"
        Q3: str = "Informe o código do item a dar saída"
        Q4: str = "Informe a quantidade utilizada"
        response_tuple_1: tuple = self.ask_for_multiple_input((Q1, str), (Q2, int))
        if not response_tuple_1:
            return
        data, codigo_venda_ifood = response_tuple_1
        itens_saida: list = []
        while True:
            read_and_display_collection("saidas")
            response_tuple_2: tuple = self.ask_for_multiple_input((Q3, int), (Q4,int))
            if not response_tuple_2:
                break
            
            codigo_item, quantidade = response_tuple_2
            itens_saida.append(codigo_item, quantidade)
        documento: dict = {"codigo_venda_ifood": codigo_venda_ifood,"data":data , "codigos_item_saida":{}}
        for codigo, quantidade in itens_saida:
            #vai olhar no dicionário codigos_item_saida se o codigo_item está presente, 
            #caso positivo, vai apenas somar o valor pela nova quantidade informada
            if documento["codigos_item_saida"].get(codigo): 
                documento["codigos_item_saida"][codigo] += quantidade
                continue
            #caso negativo, vai criar o par de chave-valor no dicionário
            documento["codigos_item_saida"][codigo] = quantidade
            
    def alterar_saidas(self):
        Q1 = "Digite o código da venda Ifood"
        Q2 = "Por favor, informe o código do item que deseja alterar"
        Q3 = "Informe a quantidade que deseja inserir"
        if not read_and_display_collection("saidas"):
            input()
            return
        while True:
            try:
                print("\nPara sair da seção não digite nada e aperte Enter!")
                codigo_venda_ifood: str = input(f"{Q1}\n")
                if not codigo_venda_ifood:
                    break
                codigo_venda_ifood = int(codigo_venda_ifood)
                saida_colletions: list = [x for x in self._saidas.find({"codigo_venda_ifood": codigo_venda_ifood})]
                if not saida_colletions:
                    raise ValueError
            except ValueError:
                input("\nO código informado não é valido. Por favor tente novamente.\n")
                continue
            for codigo, quantidade in saida_colletions[0]["codigos_item_saida"].items():
                print(f"{codigo=} | {quantidade=}")
            response_tuple = self.ask_for_multiple_input((Q2,int),(Q3,int))
            if not response_tuple:
                continue
            codigo_item, quantidade = response_tuple
            self._saidas.update_one({"codigo_venda_ifood": codigo_venda_ifood}, {"$set":{f"codigos_item_saida.{codigo_item}": quantidade}})
            input("\nSaída alterada com sucesso!")
            break

    def deletar_saidas(self):
        ...
Estoque()