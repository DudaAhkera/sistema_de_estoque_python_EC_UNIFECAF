import mysql.connector
import hashlib
import tkinter as tk
from tkinter import messagebox, ttk
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

# Classe principal do sistema
class SistemaEstoque:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Estoque")
        self.root.geometry("600x500")
        self.conexao = criar_conexao()
        if not self.conexao:
            exit()
        self.cursor = self.conexao.cursor()
        self.usuario_atual = None
        self.perfil_atual = None
        self.tela_login()

    # Tela de login
    def tela_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Login", font=("Arial", 16)).pack(pady=20)

        tk.Label(self.root, text="Usuário:").pack()
        self.username_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.username_var).pack()

        tk.Label(self.root, text="Senha:").pack()
        self.senha_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.senha_var, show="*").pack()

        tk.Button(self.root, text="Entrar", command=self.validar_login).pack(pady=10)

    # Validação de login
    def validar_login(self):
        username = self.username_var.get().strip()
        senha = self.senha_var.get().strip()

        if not username or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        senha_hash = hash_senha(senha)
        self.cursor.execute(
            "SELECT username, perfil FROM usuarios WHERE username=%s AND senha=%s",
            (username, senha_hash)
        )
        resultado = self.cursor.fetchone()

        if resultado:
            self.usuario_atual, self.perfil_atual = resultado
            self.tela_principal()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    # Tela principal
    def tela_principal(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Bem-vindo, {self.usuario_atual}", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Cadastrar Produto", command=self.cadastrar_produto).pack(fill="x", padx=20, pady=5)
        if self.perfil_atual == "administrador":
            tk.Button(self.root, text="Cadastrar Usuário", command=self.cadastrar_usuario).pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="Listar Produtos", command=self.listar_produtos).pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="Sair", command=self.tela_login).pack(fill="x", padx=20, pady=5)

    # Cadastro de produto
    def cadastrar_produto(self):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastrar Produto")

        tk.Label(janela, text="Nome:").grid(row=0, column=0)
        nome_var = tk.StringVar()
        tk.Entry(janela, textvariable=nome_var).grid(row=0, column=1)

        tk.Label(janela, text="Quantidade:").grid(row=1, column=0)
        quantidade_var = tk.StringVar()
        tk.Entry(janela, textvariable=quantidade_var).grid(row=1, column=1)

        tk.Label(janela, text="Quantidade Mínima:").grid(row=2, column=0)
        quantidade_minima_var = tk.StringVar()
        tk.Entry(janela, textvariable=quantidade_minima_var).grid(row=2, column=1)

        def salvar_produto():
            nome = nome_var.get().strip()
            quantidade = quantidade_var.get().strip()
            quantidade_minima = quantidade_minima_var.get().strip()

            if not nome or not quantidade or not quantidade_minima:
                messagebox.showerror("Erro", "Preencha todos os campos.")
                return

            try:
                quantidade = int(quantidade)
                quantidade_minima = int(quantidade_minima)
                if quantidade < 0 or quantidade_minima < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Quantidades devem ser números positivos.")
                return

            try:
                self.cursor.execute(
                    "INSERT INTO produtos (nome, quantidade, quantidade_minima) VALUES (%s, %s, %s)",
                    (nome, quantidade, quantidade_minima)
                )
                self.conexao.commit()
                messagebox.showinfo("Sucesso", f"Produto '{nome}' cadastrado com sucesso!")
                janela.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar produto: {e}")

        tk.Button(janela, text="Salvar", command=salvar_produto).grid(row=3, column=0, columnspan=2, pady=10)
    # Adicionando função de saída de produtos
def dar_saida_produto(self):
    janela = tk.Toplevel(self.root)
    janela.title("Dar Saída de Produto")

    tk.Label(janela, text="Nome do Produto:").grid(row=0, column=0, padx=10, pady=5)
    nome_var = tk.StringVar()
    tk.Entry(janela, textvariable=nome_var).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(janela, text="Quantidade:").grid(row=1, column=0, padx=10, pady=5)
    quantidade_var = tk.StringVar()
    tk.Entry(janela, textvariable=quantidade_var).grid(row=1, column=1, padx=10, pady=5)

    def registrar_saida():
        nome = nome_var.get().strip()
        quantidade_saida = quantidade_var.get().strip()

        if not nome or not quantidade_saida:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        try:
            quantidade_saida = int(quantidade_saida)
            if quantidade_saida <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número inteiro positivo.")
            return

        try:
            self.cursor.execute("SELECT quantidade FROM produtos WHERE nome = %s", (nome,))
            produto = self.cursor.fetchone()

            if not produto:
                messagebox.showerror("Erro", "Produto não encontrado.")
                return

            quantidade_atual = produto[0]

            if quantidade_saida > quantidade_atual:
                messagebox.showerror("Erro", "Quantidade em estoque insuficiente.")
                return

            nova_quantidade = quantidade_atual - quantidade_saida
            self.cursor.execute(
                "UPDATE produtos SET quantidade = %s WHERE nome = %s",
                (nova_quantidade, nome)
            )
            self.conexao.commit()
            messagebox.showinfo("Sucesso", f"Saída registrada! Nova quantidade de '{nome}': {nova_quantidade}")
            janela.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("Erro", f"Erro ao registrar saída: {e}")

    tk.Button(janela, text="Registrar Saída", command=registrar_saida).grid(row=2, column=0, columnspan=2, pady=10)
    
    # Cadastro de usuário (somente administrador)
    def cadastrar_usuario(self):
        if self.perfil_atual != "administrador":
            messagebox.showerror("Erro", "Apenas administradores podem cadastrar usuários.")
            return

        janela = tk.Toplevel(self.root)
        janela.title("Cadastrar Usuário")

        tk.Label(janela, text="Usuário:").grid(row=0, column=0)
        username_var = tk.StringVar()
        tk.Entry(janela, textvariable=username_var).grid(row=0, column=1)

        tk.Label(janela, text="Senha:").grid(row=1, column=0)
        senha_var = tk.StringVar()
        tk.Entry(janela, textvariable=senha_var, show="*").grid(row=1, column=1)

        tk.Label(janela, text="Perfil:").grid(row=2, column=0)
        perfil_var = tk.StringVar(value="comum")
        ttk.Combobox(janela, textvariable=perfil_var, values=["administrador", "comum"]).grid(row=2, column=1)

        def salvar_usuario():
            username = username_var.get().strip()
            senha = senha_var.get().strip()
            perfil = perfil_var.get()

            if not username or not senha:
                messagebox.showerror("Erro", "Preencha todos os campos.")
                return

            senha_hash = hash_senha(senha)
            try:
                self.cursor.execute(
                    "INSERT INTO usuarios (username, senha, perfil) VALUES (%s, %s, %s)",
                    (username, senha_hash, perfil)
                )
                self.conexao.commit()
                messagebox.showinfo("Sucesso", f"Usuário '{username}' cadastrado com sucesso!")
                janela.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}")

        tk.Button(janela, text="Salvar", command=salvar_usuario).grid(row=3, column=0, columnspan=2, pady=10)

    # Listagem de produtos
    def listar_produtos(self):
        janela = tk.Toplevel(self.root)
        janela.title("Produtos em Estoque")

        texto = tk.Text(janela, wrap="word")
        texto.pack(expand=True, fill="both")

        self.cursor.execute("SELECT nome, quantidade, quantidade_minima FROM produtos")
        produtos = self.cursor.fetchall()

        for nome, quantidade, quantidade_minima in produtos:
            alerta = " - ALERTA: Estoque baixo!" if quantidade < quantidade_minima else ""
            texto.insert(tk.END, f"{nome}: {quantidade} unidades (Min: {quantidade_minima}){alerta}\n")

# Execução do sistema
if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaEstoque(root)
    root.mainloop()
            
            


