import mysql.connector
import hashlib
from getpass import getpass
import tkinter as tk
from tkinter import messagebox, simpledialog
import os

#configuracão de conexão com o banco de dados
conexao = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Zulenice20@',
    database='sistema_estoque'
)

cursor = conexao.cursor()

#funcao de interface gráfica
def interface_grafica(funcao, **kwargs):
    #criar janela oculta para diálogo
    root = tk.tk()
    root.withdraw() #oculta a janela principal
    
    try:
        resultado = funcao(**kwargs)
        if resultado:
            messagebox.showinfo("Sucesso", resultado)
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        root.destroy() #fecha a janela oculta

#funcão para criptografar a senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

#funcão para cadastrar um novo usuário (somente para administradores)
def cadastrar_usuario():
    print("\n=== Cadastro de Novo usuário ===")
    username = input("Nome de usuário: ")
    print("Para cadastrar a senha é necessário ter 4 caracteres e pelo menos 1 número")
    
    #validacão de senha
    while True:
        senha = getpass("Senha: ")
        confirmar_senha = getpass("Confirme a senha: ")
        
        #verifica se as senhas coincidem.
        if senha != confirmar_senha:
            print("As senhas não coincidem. Tente novamente")
            continue
        #verifica se a senha tem 4 caracteres
        if len(senha) > 4:
            print("A senha deve ter 4 caracteres, tente novamente!")
            continue
        break
    
    #solicita o perfil do usuário
    while True:
        
        perfil = input("Perfil (administrador/comum): ").strip().lower()
        if perfil in ['administrador', 'comum']:
            break
        else:
            print("Perfil inválido. Digite 'administrador' ou 'comum': ")
            return
    
    #criptografa a senha e insere o usuário no banco de dados
    senha_hash = hash_senha(senha)
    try:
        cursor.execute("INSERT INTO usuarios (username, senha, perfil) VALUES (%s, %s, %s )", (username, senha_hash, perfil))
        conexao.commit()
        print("Usuário cadastrado com sucesso!")
    except mysql.connector.Error as err:
        print(f"Erro ao cadastrar usuário: {err}")

#funcão para realizar login do usuário
def login():
    print("\n=== Login ===")
    username = input("Usuário: ")
    senha = getpass("Senha: ")
    senha_hash = hash_senha(senha)
    cursor.execute("SELECT id, perfil FROM usuarios WHERE username = %s AND senha = %s", (username, senha_hash))
    usuario = cursor.fetchone()
    if usuario:
        print(f"Bem-vindo(a), {username}!")
        return {'id': usuario[0], 'perfil': usuario[1]}
    else:
        print("Credenciais inválidas. Tente novamente.")
        return None
    
#funcão para cadastrar produtos no estoque
def cadastrar_produto():
    print("\n=== Cadastro de Produto ===")
    nome = input("Nome do produto: ")
    while True:
        try:
            quantidade = int(input("Quantidade inicial: "))
            if quantidade < 0:
                print("A quantidade inicial não pode ser negativa")
                continue
            break
        except ValueError:
            print("Por favor, insira um número válido para a quantidade")
    
    while True:
        try:
            quantidade_minima = int(input("Quantidade minima: "))
            if quantidade_minima < 0:
                print("A quantidade mínima não pode ser negativa.")
                continue
            break
        except ValueError:
            print("Por favor, insira um número válido para a quantidade mínima")
            
    cursor.execute("INSERT INTO produtos (nome, quantidade, quantidade_minima) VALUES (%s, %s, %s)",
                   (nome, quantidade, quantidade_minima))
    conexao.commit()
    print(f"Produto '{nome}' cadastro com sucesso!")

#Funcão para registrar saída de produtos
def saida_produtos():
    print("\n=== Saída de produto ===")
    nome = input("Nome do produto para dar saída: ")
    
    #verifica a quantidade em estoque
    cursor.execute("SELECT quantidade, quantidade_minima FROM produtos WHERE nome = %s", (nome,))
    produto = cursor.fetchone()
    
    if produto is None:
        print("Produto não encontrado!")
        return
    
    quantidade_atual, quantidade_minima = produto
    print(f"Quantidade atual de '{nome}': {quantidade_atual}")
    
    while True:
        try:
            quantidade_saida = int(input("Quantidade de saída: "))
            if quantidade_saida <= 0:
                print("A quantidade de saída deve ser positiva")
                continue
            break
        except ValueError:
            print("Por favor, insira um número válido para a quantidade de saída")
            
    if quantidade_saida > quantidade_atual:
        print("Quantidade insuficiente no estoque para a saída solicitada.")
        return
    
    #Atualiza a quantidade no banco de dados
    nova_quantidade = quantidade_atual - quantidade_saida
    cursor.execute("UPDATE produtos SET quantidade = %s WHERE nome = %s", (nova_quantidade, nome))
    conexao.commit()
    print(f"Saída de {quantidade_saida} unidades de '{nome}' registrada com sucesso!")
    
    #Exibe alerta se a quantidade estiver abaixo do mínimo
    if nova_quantidade < quantidade_minima:
        print(f"ALERTA: Quantidade de '{nome}' está abaixo do mínimo permitido. Considere reabastecer.")
   
#funcão para listar produtos e alertas sobre baixa qualidade
def listar_produtos():
    print("\n=== Produtos em estoque ===")
    cursor.execute("SELECT nome, quantidade, quantidade_minima FROM produtos")
    produtos = cursor.fetchall()
    
    if not produtos:
        print("Nenhum produto cadastrado no estoque.")
        return
    
    for nome, quantidade, quantidade_minima in produtos:
        alerta = " - ALERTA: Estoque baixo!" if quantidade < quantidade_minima else ""
        print(f"{nome}: {quantidade} unidades (Min: {quantidade_minima}){alerta}")

#funcão principal do sistema de estoque
def sistema_estoque():
    print("Bem-vindo(a) ao sistema de estoque.")
    
    #verificar se há usuários; se não, criar um administrador inicial
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        print("Nenhum usuário encontrado. Crie um administrador inicial.")
        cadastrar_usuario()
        
    #Login do usuário
    usuario = None
    while not usuario:
        usuario = login()
        
    #verificar se o usuário é administrador
    eh_administrador = usuario['perfil'] == 'administrador'
    
    #Menu de opcões do sistema
    while True:
        print("\n=== Menu ===")
        print("\n=== 1. Cadastrar produto ===")
        print("\n=== 2. Listar produto ===")
        print("\n=== 3. Saída de produto ===")
        if eh_administrador:
            print("\n===4. Cadastrar novo usuário ===")
        print("=== 0. Sair ===")
        
        opcao = input("Escolha uma opcão: ").strip()
        if opcao == "1":
            interface_grafica(cadastrar_produto)
        elif opcao == "2":
            interface_grafica(listar_produtos)
        elif opcao == "3":
            interface_grafica(saida_produtos)
        elif opcao == "4" and eh_administrador:
            interface_grafica(cadastrar_usuario)
        elif opcao == "0":
            print("Saindo do sistema...")
            break
        else:
            print("Opcão inválida. Tente novamente.")
            
#Executar o sistema
sistema_estoque()

#Fechar a conexão com o banco de dados
conexao.close()

            
            


