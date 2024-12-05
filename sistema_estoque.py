import mysql.connector
import hashlib
from getpass import getpass
import tkinter as tk
from tkinter import messagebox, simpledialog
import os

#configuracão de conexão com o banco de dados
def criar_conexao():
    try:
        conexao = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password=os.getenv('MYSQL_PASSWORD', 'Zulenice20@'),
            database='sistema_estoque'
        )
        return conexao
    except mysql.connector.Error as e:
        print(f"Erro de conexão: {e}")
        return None

#funcao de interface gráfica
def interface_grafica(funcao, **kwargs):
    #criar janela oculta para diálogo
    root = tk.Tk()
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
def cadastrar_usuario(cursor):
    username = simpledialog.askstring("Cadastro", "Nome de usuário:")
    if not username:
        raise ValueError("Nome de usuário é obrigatório")
    
    senha = obter_senha()
    perfil = obter_perfil()
    senha_hash = hash_senha(senha)

    try:
        cursor.execute("INSERT INTO usuarios (username, senha, perfil) VALUES (%s, %s, %s )", (username, senha_hash, perfil))
        cursor.connection.commit()
        print("Usuário cadastrado com sucesso!")
    except mysql.connector.Error as e:
        print(f"Erro ao cadastrar usuário: {e}")
        
def obter_senha():
    #validacão de senha
    while True:
        senha = simpledialog.askstring("Cadastro", "Senha:", show="*")
        confirmar_senha = simpledialog.askstring("Cadastro", "Confirme a senha:", show="*")
        
        #verifica se as senhas coincidem.
        if senha != confirmar_senha:
            print("As senhas não coincidem. Tente novamente")
            continue
        #verifica se a senha tem 4 caracteres
        if len(senha) != 4 or not any(char.isdigit() for char in senha):
            messagebox.showwarning("A senha deve ter 4 caracteres, tente novamente!")
            continue
        return senha
    
    #solicita o perfil do usuário
def obter_perfil(): 
    while True:
        perfil = simpledialog.askstring("Cadastro", "Perfil (administrador/comum):").strip().lower()
        if perfil in ['administrador', 'comum']:
            return perfil
        else:
            messagebox.showwarning("Erro", "Perfil inválido. Digite 'administrador' ou 'comum'.")

#funcão para realizar login do usuário
def login(cursor):
    username = simpledialog.askstring("Login", "Usuário:")
    senha = simpledialog.askstring("Login", "Senha:", show="*")
    senha_hash = hash_senha(senha)
    cursor.execute("SELECT id, perfil FROM usuarios WHERE username = %s AND senha = %s", (username, senha_hash))
    usuario = cursor.fetchone()
    if usuario:
        return {'id': usuario[0], 'perfil': usuario[1]}
    else:
        messagebox.showerror("Erro", "Credenciais inválidas.")
        return None
    
#funcão para cadastrar produtos no estoque
def cadastrar_produto(cursor):
    nome = simpledialog.askstring("Cadastro de Produto", "Nome do produto:")

    quantidade = obter_quantidade("Quantidade inicial: ")

    quantidade_minima = obter_quantidade("Quantidade mínima: ")
            
    cursor.execute(
        "INSERT INTO produtos (nome, quantidade, quantidade_minima) VALUES (%s, %s, %s)",
        (nome, quantidade, quantidade_minima)
    )
    cursor.connection.commit()
    return f"Produto '{nome}' cadastro com sucesso!"

# Obter quantidade com validacão 
def obter_quantidade(mensagem):
    while True:
        try:
            quantidade = int(simpledialog.askstring("Quantidade", mensagem))
            if quantidade < 0:
                messagebox.showwarning("Erro", "A quantidade não pode ser negativa.")
                continue
            return quantidade
        except ValueError:
            messagebox.showwarning("Erro", "Por favor, insira um número válido.")

#Funcão para registrar saída de produtos
def saida_produtos(cursor):
    nome = simpledialog.askstring("Saída de Produto", "Nome do produto:")
    
    #verifica a quantidade em estoque
    cursor.execute("SELECT quantidade, quantidade_minima FROM produtos WHERE nome = %s", (nome,))
    produto = cursor.fetchone()
    
    if not produto:
        raise ValueError("Produto não encontrado.")
    
    quantidade_atual, quantidade_minima = produto
    
    quantidade_saida = obter_quantidade("Quantidade de saída: ")
    
    if quantidade_saida > quantidade_atual:
        raise ValueError("Quantidade insuficiente no estoque para a saída solicitada.")
        
    nova_quantidade = quantidade_atual - quantidade_saida
    cursor.execute("UPDATE produtos SET quantidade = %s WHERE nome = %s", (nova_quantidade, nome))
    cursor.connection.commit()
    
    #Exibe alerta se a quantidade estiver abaixo do mínimo
    alerta = ""
    if nova_quantidade < quantidade_minima:
        alerta = f" Estoque abaixo do mínimo permitido."
    return f"Saída de {quantidade_saida} unidades de '{nome}' registrada com sucesso.{alerta}"
    
   
#funcão para listar produtos e alertas sobre baixa qualidade
def listar_produtos(cursor):
    cursor.execute("SELECT nome, quantidade, quantidade_minima FROM produtos")
    produtos = cursor.fetchall()
    
    if not produtos:
        raise ValueError("Nenhum produto cadastrado no estoque.")
    
    resultado = ""
    for nome, quantidade, quantidade_minima in produtos:
        alerta = " - ALERTA: Estoque baixo!" if quantidade < quantidade_minima else ""
        resultado += f"{nome}: {quantidade} unidades (Min: {quantidade_minima}){alerta}"
    return resultado

#funcão principal do sistema de estoque
def sistema_estoque():
    conexao = criar_conexao()
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    #verificar se há usuários; se não, criar um administrador inicial
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        interface_grafica(cadastrar_usuario, cursor=cursor)
        
    #Login do usuário
    usuario = None
    while not usuario:
        usuario = interface_grafica(login, cursor=cursor)
        
    #verificar se o usuário é administrador
    eh_administrador = usuario['perfil'] == 'administrador'
    
    #Menu de opcões do sistema
    while True:
        menu = "=== Menu ===\n1. Cadastrar produto\n2. Listar produtos\n3. Registrar saída de produto\n"
        if eh_administrador:
            menu += "4. Cadastrar novo usuário \n"
        menu += "0. Sair\nEscolha uma opção:"
        opcao = simpledialog.askstring("Menu", menu)
        
        if opcao == "1":
            interface_grafica(cadastrar_produto, cursor = cursor)
        elif opcao == "2":
            interface_grafica(listar_produtos, cursor = cursor)
        elif opcao == "3":
            interface_grafica(saida_produtos, cursor = cursor)
        elif opcao == "4" and eh_administrador:
            interface_grafica(cadastrar_usuario, cursor = cursor)
        elif opcao == "0":
            break
        else:
            messagebox.showwarning("Erro", "Opção inválida.")

    #Fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()
    
#Executar o sistema
sistema_estoque()

            
            


