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

        tk.Label(self.root, text=f"Olá, {self.usuario_atual}", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Cadastrar Produto", command=self.cadastrar_produto).pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="Listar Produtos", command=self.listar_produtos).pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="Dar Saída de Produto", command=self.dar_saida_produto).pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="Incluir Quantidade", command=self.incluir_quantidade).pack(fill="x", padx=20, pady=5)
        if self.perfil_atual == "administrador":
            tk.Button(self.root, text="Cadastrar Usuário", command=self.cadastrar_usuario).pack(fill="x", padx=20, pady=5)
            tk.Button(self.root, text="Listar Usuário", command=self.listar_usuarios).pack(fill="x", padx=20, pady=5)
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
        janela.title("Saída de Produto")

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
            
                # Verificar se a nova quantidade está abaixo do mínimo
            self.cursor.execute("SELECT quantidade_minima FROM produtos WHERE nome = %s", (nome,))
            quantidade_minima = self.cursor.fetchone()[0]

            if nova_quantidade < quantidade_minima:
                messagebox.showwarning("Atenção", f"A quantidade de '{nome}' está abaixo do valor mínimo!")

            messagebox.showinfo("Sucesso", f"Saída registrada! Nova quantidade de '{nome}': {nova_quantidade}")
            janela.destroy()

        tk.Button(janela, text="Registrar Saída", command=registrar_saida).grid(row=2, column=0, columnspan=2, pady=10)
    
        # Listagem de produtos
    def listar_produtos(self):
        janela = tk.Toplevel(self.root)
        janela.title("Produtos em Estoque")

        # Criação do Treeview para exibir os produtos
        tree = ttk.Treeview(janela, columns=("nome", "quantidade", "quantidade_minima"), show="headings")
        tree.heading("nome", text="Nome")
        tree.heading("quantidade", text="Quantidade")
        tree.heading("quantidade_minima", text="Quantidade Mínima")

        tree.column("nome", width=200)
        tree.column("quantidade", width=100, anchor="center")
        tree.column("quantidade_minima", width=150, anchor="center")

        tree.pack(expand=True, fill="both")

        # Populando o Treeview com dados do banco
        try:
            self.cursor.execute("SELECT nome, quantidade, quantidade_minima FROM produtos")
            produtos = self.cursor.fetchall()

            for nome, quantidade, quantidade_minima in produtos:
                tree.insert("", "end", values=(nome, quantidade, quantidade_minima))
        except mysql.connector.Error as e:
            messagebox.showerror("Erro", f"Erro ao listar produtos: {e}")
            
    def incluir_quantidade(self):
        janela = tk.Toplevel(self.root)
        janela.title("Incluir Quantidade")

        # Obter todos os nomes dos produtos do banco de dados
        self.cursor.execute("SELECT nome FROM produtos")
        produtos = [produto[0] for produto in self.cursor.fetchall()]

        # Criar um combobox para selecionar o produto
        label_produto = tk.Label(janela, text="Produto:")
        label_produto.grid(row=0, column=0, sticky="w")  # Alinha à esquerda
        produto_var = tk.StringVar()
        produto_combobox = tk.ttk.Combobox(janela, textvariable=produto_var, values=produtos)
        produto_combobox.grid(row=0, column=0, columnspan=2)

        # Campo para a quantidade a ser adicionada
        tk.Label(janela, text="Quantidade a Adicionar:").grid(row=2, column=0, padx=10, pady=5)
        quantidade_var = tk.StringVar()
        tk.Entry(janela, textvariable=quantidade_var).grid(row=2, column=1, padx=10, pady=5)

        def adicionar_quantidade():
            produto = produto_var.get()
            quantidade = quantidade_var.get()

            if not produto or not quantidade:
                messagebox.showerror("Erro", "Preencha todos os campos.")
                return

            try:
                quantidade = int(quantidade)
                if quantidade <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "A quantidade deve ser um número inteiro positivo.")
                return

            try:
                self.cursor.execute("UPDATE produtos SET quantidade = quantidade + %s WHERE nome = %s",
                                    (quantidade, produto))
                self.conexao.commit()
                messagebox.showinfo("Sucesso", f"Quantidade adicionada ao produto '{produto}' com sucesso!")
                janela.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Erro", f"Erro ao adicionar quantidade: {e}")

        tk.Button(janela, text="Adicionar", command=adicionar_quantidade).grid(row=3, column=0, columnspan=2, pady=10)
    
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


    # Listar e gerenciar usuários (somente para administradores)
    def listar_usuarios(self):
        if self.perfil_atual != "administrador":
            messagebox.showerror("Erro", "Apenas administradores podem acessar essa funcionalidade.")
            return

        janela = tk.Toplevel(self.root)
        janela.title("Usuários Cadastrados")

        # Criação do Treeview para exibir os usuários
        tree = ttk.Treeview(janela, columns=("username", "perfil"), show="headings")
        tree.heading("username", text="Usuário")
        tree.heading("perfil", text="Perfil")

        tree.column("username", width=200)
        tree.column("perfil", width=100, anchor="center")

        tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Populando o Treeview com dados do banco
        try:
            self.cursor.execute("SELECT username, perfil FROM usuarios")
            usuarios = self.cursor.fetchall()

            for username, perfil in usuarios:
                tree.insert("", "end", values=(username, perfil))
        except mysql.connector.Error as e:
            messagebox.showerror("Erro", f"Erro ao listar usuários: {e}")

        # Função para excluir usuário
        def excluir_usuario():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showerror("Erro", "Selecione um usuário para excluir.")
                return

            username = tree.item(selecionado[0], "values")[0]
            if username == self.usuario_atual:
                messagebox.showerror("Erro", "Você não pode excluir seu próprio usuário.")
                return

            confirmacao = messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir o usuário '{username}'?")
            if confirmacao:
                try:
                    self.cursor.execute("DELETE FROM usuarios WHERE username = %s", (username,))
                    self.conexao.commit()
                    tree.delete(selecionado)
                    messagebox.showinfo("Sucesso", f"Usuário '{username}' excluído com sucesso!")
                except mysql.connector.Error as e:
                    messagebox.showerror("Erro", f"Erro ao excluir usuário: {e}")

        # Botão para excluir usuário
        tk.Button(janela, text="Excluir Usuário", command=excluir_usuario).pack(pady=10)

        # Adicionar botão na tela principal para listar usuários
        if self.perfil_atual == "administrador":
            tk.Button(self.root, text="Listar Usuários", command=self.listar_usuarios).pack(fill="x", padx=20, pady=5)

# Execução do sistema
if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaEstoque(root)
    root.mainloop()
            
            


