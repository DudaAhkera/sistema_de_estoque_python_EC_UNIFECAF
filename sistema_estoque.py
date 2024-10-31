import mysql.connector
import hashlib
from getpass import getpass
import re

#configuracão de conexão com o banco de dados
conexao = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Zulenice20@',
    database='sistema_estoque'
)

cursor = conexao.cursor()

#funcão para criptografar a senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

#funcão para cadastrar um novo usuário (somente para administradores)
def cadastrar_usuario():
    print("\n=== Cadastro de Novo usuário ===")
    username = input("Nome de usuário: ")
    #validacão de senha
    while True:
        senha = getpass("Senha: ")
        confirmar_senha = getpass("Confirme a senha: ")
        
        #verifica se as senhas coincidem.
        if senha != confirmar_senha:
            print("As senhas não coincidem. Tente novamente")
            continue
        #verifica se a senha tem 6 caracteres
        if len(senha) < 6 and len(senha) > 6:
            print("A senha deve ter 6 caracteres, tente novamente!")
            continue
        if not re.search(r"\d", senha):
            print("A senha deve conter pelo menos  1 número. Tente novamente")
            continue
        break
    
    perfil = input("Perfil (administrador/comum): ").strip().lower()
    if perfil not in ['administrador', 'comum']:
        print("Perfil inválido. Digite 'administrador' ou 'comum': ")
        return
    
    senha_hash = hash_senha(senha)
    cursor.execute("INSERT INTO usuarios (username, senha, perfil) VALUES (%s, %s, %s )", (username, senha_hash, perfil))
    conexao.commit()
    print("Usuário cadastrado com sucesso!")

#funcão para realizar login do usuário
def login():
    print("\n=== Login ===")
    username = input("Usuário: ")
    senha = getpass("Senha: ")
    senha_hash = hash_senha(senha)
    cursor.execute("SELECT id, perfil FROM usuarios WHERE username = %s AND senha = %s", (username, senha_hash))
    usuario = cursor.fetchone()
    if usuario:
        print(f"Bem-vindo, {username}!")
        return {'id': usuario[0], 'perfil': usuario[1]}
    else:
        print("Credenciais inválidas. Tente novamente.")
        return None
    
#funcão para cadastrar produtos no estoque
def cadastrar_produto():
    print("\n=== Cadastro de Produto ===")
    nome = input("Nome do produto: ")
    quantidade = int(input("Quantidade inicial: "))
    quantidade_minima = int(input("Quantidade minima: "))
    cursor.execute("INSERT INTO produtos (nome, quantidade, quantidade_minima) VALUES (%s, %s, %s)",
                   (nome, quantidade, quantidade_minima))
    conexao.commit()
    print(f"Produto '{nome}' cadastro com sucesso!")
    
#funcão para listar produtos e alertas sobre baixa qualidade
def listar_produtos():
    print("\n=== Produtos em estoque ===")
    cursor.execute("SELECT nome, quantidade, quantidade_minima FROM produtos")
    produtos = cursor.fetchall()
    for nome, quantidade, quantidade_minima in produtos:
        alerta = " - ALERTA: Estoque baixo!" if quantidade < quantidade_minima else ""
        print(f"{nome}: {quantidade} unidades (Min: {quantidade_minima}){alerta}")

#funcão principal do sistema de estoque
def sistema_estoque():
    print("Bem-vindo ao sistema de estoque.")
    
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
        print("\n===1. Cadastrar produto ===")
        print("\n===2. Listar produtos ===")
        if eh_administrador:
            print("\n===3. Cadastrar novo usuário ===")
        print("0. Sair")
        
        opcao = input("Escolha uma opcão: ").strip()
        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            listar_produtos()
        elif opcao == "3" and eh_administrador:
            cadastrar_usuario()
        elif opcao == "0":
            print("Saindo do sistema...")
            break
        else:
            print("Opcão inválida. Tente novamente.")
            
#Executar o sistema
sistema_estoque()

#Fechar a conexão com o banco de dados
conexao.close()

            
            


