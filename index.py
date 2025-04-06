import mysql.connector
from tabulate import tabulate
from datetime import datetime, timedelta

# use esse no terminal ↓
# pip install mysql-connector-python
# pip install tabulate


def conectar():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="restaurante"
        )
        return conexao
    except mysql.connector.Error as erro:
        print(f"Erro ao conectar: {erro}")
        return None



def cadastrar_produto():
    db = conectar()
    cursor = db.cursor()
    codigo = input("Código: ")
    nome = input("Nome: ")
    quantidade = float(input("Quantidade: "))
    unidade = input("Unidade (ex: kg, L): ")
    preco = float(input("Preço unitário: "))
    validade = input("Data de validade (AAAA-MM-DD): ")
    cursor.execute("""
        INSERT INTO estoque (codigo, nome, quantidade, unidade, preco_unitario, validade)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (codigo, nome, quantidade, unidade, preco, validade))
    db.commit()
    print("Produto cadastrado com sucesso.")


def listar_estoque():
    db = conectar()
    cursor = db.cursor()
    cursor.execute("SELECT codigo, nome, quantidade, unidade, preco_unitario, validade FROM estoque")
    dados = cursor.fetchall()
    print(tabulate(dados, headers=["Código", "Nome", "Qtd", "Unidade", "Preço", "Validade"], tablefmt="grid"))


def editar_produto():
    db = conectar()
    cursor = db.cursor()
    codigo = input("Informe o código do produto que deseja editar: ")
    cursor.execute("SELECT * FROM estoque WHERE codigo = %s", (codigo,))
    produto = cursor.fetchone()

    if produto:
        campos = ["nome", "quantidade", "unidade", "preco_unitario", "validade"]
        novos_valores = list(produto[2:])

        for i, campo in enumerate(campos):
            editar = input(f"Deseja editar '{campo}' atual ({novos_valores[i]})? (s/n): ").lower()
            if editar == "s":
                valor = input(f"Novo valor para {campo}: ")
                if campo in ["quantidade", "preco_unitario"]:
                    valor = float(valor)
                novos_valores[i] = valor

        cursor.execute("""
            UPDATE estoque
            SET nome=%s, quantidade=%s, unidade=%s, preco_unitario=%s, validade=%s
            WHERE codigo=%s
        """, (*novos_valores, codigo))
        db.commit()
        print("Produto atualizado com sucesso.")
    else:
        print("Produto não encontrado.")


def alertas_estoque():
    db = conectar()
    cursor = db.cursor()

    print("\nProdutos com estoque baixo (<5):")
    cursor.execute("SELECT nome, quantidade FROM estoque WHERE quantidade < 5")
    dados = cursor.fetchall()
    print(tabulate(dados, headers=["Produto", "Quantidade"], tablefmt="grid"))

    print("\nProdutos com validade próxima (até 3 dias):")
    hoje = datetime.today().date()
    limite = hoje + timedelta(days=3)
    cursor.execute("SELECT nome, validade FROM estoque WHERE validade <= %s", (limite,))
    vencendo = cursor.fetchall()
    print(tabulate(vencendo, headers=["Produto", "Validade"], tablefmt="grid"))



def cadastrar_item_cardapio():
    db = conectar()
    cursor = db.cursor()
    nome = input("Nome do prato: ")
    descricao = input("Descrição: ")
    preco = float(input("Preço: "))
    cursor.execute("INSERT INTO cardapio (nome, descricao, preco) VALUES (%s, %s, %s)", (nome, descricao, preco))
    id_cardapio = cursor.lastrowid

    adicionar_ingredientes = input("Deseja adicionar ingredientes a este prato? (s/n): ").lower()
    while adicionar_ingredientes == 's':
        nome_ing = input("Nome do ingrediente: ")
        qtd_ing = float(input("Quantidade usada: "))
        cursor.execute("INSERT INTO ingredientes (id_cardapio, nome_ingrediente, quantidade) VALUES (%s, %s, %s)",
                       (id_cardapio, nome_ing, qtd_ing))
        adicionar_ingredientes = input("Adicionar mais ingredientes? (s/n): ").lower()

    db.commit()
    print("Prato cadastrado com sucesso.")


def listar_cardapio():
    db = conectar()
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, preco FROM cardapio")
    pratos = cursor.fetchall()
    print(tabulate(pratos, headers=["ID", "Nome", "Preço"], tablefmt="grid"))



def menu():
    while True:
        print("\n1. Gestão de Estoque")
        print("2. Gestão de Cardápio")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print("\n1. Cadastrar Produto")
            print("2. Listar Estoque")
            print("3. Editar Produto")
            print("4. Ver Alertas de Estoque")
            sub = input("Escolha: ")
            if sub == "1":
                cadastrar_produto()
            elif sub == "2":
                listar_estoque()
            elif sub == "3":
                editar_produto()
            elif sub == "4":
                alertas_estoque()

        elif opcao == "2":
            print("\n1. Cadastrar Prato")
            print("2. Listar Cardápio")
            sub = input("Escolha: ")
            if sub == "1":
                cadastrar_item_cardapio()
            elif sub == "2":
                listar_cardapio()

        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

menu()
