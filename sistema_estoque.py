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

#funcão para criptografar a senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

#funcão para cadastrar um novo usuário (somente para administradores)
def cadastrar_usuario(cursor):
    username = simpledialog.askstring("Cadastro", "Nome de usuário:")
    if not username:
        return "Cadastro cancelado."
    
    senha = obter_senha()
    if not senha:
        return "Cadastro cancelado."
    
    perfil = obter_perfil()
    senha_hash = hash_senha(senha)

    try:
        cursor.execute("INSERT INTO usuarios (username, senha, perfil) VALUES (%s, %s, %s )", (username, senha_hash, perfil))
        cursor.connection.commit()
        return f"Usuário '{username}' cadastrado com sucesso!"
    except mysql.connector.Error as e:
        raise ValueError(f"Erro ao cadastrar usuário: {e}")
        
def obter_senha():
    #validacão de senha
    while True:
        senha = simpledialog.askstring("Senha", "Digite a senha (4 caracteres, 1 número):", show="*")
        if not senha:
            return None
        confirmar_senha = simpledialog.askstring("Senha", "Confirme a senha:", show="*")
        
        #verifica se as senhas coincidem.
        if senha != confirmar_senha:
            messagebox.showerror("Erro", "As senhas não coincidem. Tente novamente.")
            continue
        #verifica se a senha tem 4 caracteres
        if len(senha) != 4 or not any(char.isdigit() for char in senha):
            messagebox.showerror("Erro", "A senha deve ter 4 caracteres e conter pelo menos um número.")
            continue
        return senha
    
    #solicita o perfil do usuário
def obter_perfil(): 
    while True:
        perfil = simpledialog.askstring("Cadastro", "Perfil (administrador/comum):").strip().lower()
        if perfil in ['administrador', 'comum']:
            return perfil
        else:
            messagebox.showerror("Erro", "Perfil inválido. Digite 'administrador' ou 'comum'.")
    
#funcão para cadastrar produtos no estoque
def cadastrar_produto(cursor):
    nome = simpledialog.askstring("Cadastro de Produto", "Nome do produto:")
    if not nome:
        return "Cadastro cancelado."

    quantidade = obter_quantidade("Quantidade inicial: ")

    quantidade_minima = obter_quantidade("Quantidade mínima: ")
    
    try:        
        cursor.execute(
            "INSERT INTO produtos (nome, quantidade, quantidade_minima) VALUES (%s, %s, %s)",
            (nome, quantidade, quantidade_minima)
        )
        cursor.connection.commit()
        return f"Produto '{nome}' cadastro com sucesso!"
    except mysql.connector.Error as e:
        raise ValueError(f"Erro ao cadastrar produto: {e}")
    
# Obter quantidade com validacão 
def obter_quantidade(mensagem):
    while True:
        try:
            quantidade = int(simpledialog.askstring("Quantidade", mensagem))
            if quantidade is None:
                return None
            if quantidade < 0:
                messagebox.showerror("Erro", "A quantidade não pode ser negativa.")
                continue
            return quantidade
        except ValueError:
            messagebox.showerror("Erro", "Insira um número válido.")

#funcão para listar produtos e alertas sobre baixa qualidade
def listar_produtos(cursor):
    cursor.execute("SELECT nome, quantidade, quantidade_minima FROM produtos")
    produtos = cursor.fetchall()
    
    if not produtos:
        return "Nenhum produto cadastrado."
    
    resultado = ""
    for nome, quantidade, quantidade_minima in produtos:
        alerta = " - ALERTA: Estoque baixo!" if quantidade < quantidade_minima else ""
        resultado += f"{nome}: {quantidade} unidades (Min: {quantidade_minima}){alerta}"
    return resultado

#Funcão para registrar saída de produtos
def saida_produtos(cursor):
    nome = simpledialog.askstring("Saída de Produto", "Nome do produto:")
    if not nome:
        return "Saída cancelada."
    
    #verifica a quantidade em estoque
    cursor.execute("SELECT quantidade, quantidade_minima FROM produtos WHERE nome = %s", (nome,))
    produto = cursor.fetchone()
    
    if not produto:
        raise ValueError("Produto não encontrado.")
    
    quantidade_atual, quantidade_minima = produto
    
    quantidade_saida = obter_quantidade("Quantidade de saída: ")
    if not quantidade_saida:
        return "Saída cancelada."
    
    if quantidade_saida > quantidade_atual:
        raise ValueError("Quantidade insuficiente no estoque.")
        
    nova_quantidade = quantidade_atual - quantidade_saida
    cursor.execute("UPDATE produtos SET quantidade = %s WHERE nome = %s", (nova_quantidade, nome))
    cursor.connection.commit()
    
    #Exibe alerta se a quantidade estiver abaixo do mínimo
    alerta = ""
    if nova_quantidade < quantidade_minima:
        alerta = " Estoque abaixo do mínimo permitido."
    return f"Saída de {quantidade_saida} unidades de '{nome}' registrada com sucesso.{alerta}"

#funcão principal do sistema de estoque
def sistema_estoque():
    conexao = criar_conexao()
    if not conexao:
        return
    
    cursor = conexao.cursor()
    root = tk.Tk()
    root.title("Sistema de Estoque")
    
    #Menu de opcões do sistema
    def executar(opcao):
        try:
            if opcao == "Cadastrar Produto":
                mensagem = cadastrar_produto(cursor)
            elif opcao == "Listar Produtos":
                mensagem = listar_produtos(cursor)
            elif opcao == "Registrar Saída":
                mensagem = saida_produtos(cursor)
            elif opcao == "Cadastrar Usuário":
                mensagem = cadastrar_usuario(cursor)
            elif opcao == "Sair":
                root.quit()
                return
            messagebox.showinfo("Resultado", mensagem)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    botoes = ["Cadastrar Produto", "Listar Produtos", "Registrar Saída", "Cadastrar Usuário", "Sair"]
    for botao in botoes:
        tk.Button(root, text=botao, command=lambda b=botao: executar(b)).pack(pady=10)

    #Fechar a conexão com o banco de dados
    root.mainloop()
    cursor.close()
    conexao.close()
    
#Executar o sistema
sistema_estoque()

            
            


