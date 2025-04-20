import csv
import subprocess
import customtkinter as ctk
from tkinter import filedialog

def transformar_dados():
    arquivo_csv = input_arquivo_sicoob.get()
    arquivo_xml = input_arquivo_assuncao.get()

    try:
        # Chama o script externo
        subprocess.run(["python", "tratar_dados.py", arquivo_csv, arquivo_xml], check=True)

        # Exibe sucesso
        resultado.configure(text='Arquivo transformado com sucesso!', text_color='green')

    except subprocess.CalledProcessError:
        resultado.configure(text='Erro ao executar transformacao.', text_color='red')

def abrir_cadastro_clientes():
    janela = ctk.CTkToplevel(app)
    janela.title("Cadastro de Clientes")
    janela.geometry("700x500")

    clientes = []

    frame_clientes = ctk.CTkScrollableFrame(janela, label_text="Clientes Cadastrados")
    frame_clientes.pack(pady=20, padx=20, fill="both", expand=True)

    def adicionar_cliente():
        linha_frame = ctk.CTkFrame(frame_clientes)
        linha_frame.pack(pady=5, padx=10, fill="x")

        nome = ctk.CTkEntry(linha_frame, width=150, placeholder_text="Nome")
        nome.pack(side="left", padx=5)

        codigo = ctk.CTkEntry(linha_frame, width=100, placeholder_text="Código")
        codigo.pack(side="left", padx=5)

        valor = ctk.CTkEntry(linha_frame, width=100, placeholder_text="Valor Total")
        valor.pack(side="left", padx=5)

        cpf = ctk.CTkEntry(linha_frame, width=150, placeholder_text="CPF")
        cpf.pack(side="left", padx=5)

        clientes.append((nome, codigo, valor, cpf))

    def gerar_csv():
        with open("customizados/clientes.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["nome_cliente", "codigo_cliente", "valor_total", "cpf"])
            for nome, codigo, valor, cpf in clientes:
                writer.writerow([
                    nome.get(),
                    codigo.get(),
                    valor.get(),
                    cpf.get()
                ])

        resultado_local.configure(text="CSV gerado com sucesso!", text_color="green")

    # Botões da janela de cadastro
    ctk.CTkButton(janela, text="Adicionar Cliente", command=adicionar_cliente).pack(pady=10)
    ctk.CTkButton(janela, text="Gerar CSV", command=gerar_csv).pack(pady=10)
    resultado_local = ctk.CTkLabel(janela, text="")
    resultado_local.pack()

    adicionar_cliente()  # começa com uma linha já criada

def gerar_notas():
    arquivo_final = input_arquivo_notas.get()

    try:
        subprocess.run(['python', 'automacao.py', arquivo_final], check=True)
        resultado2.configure(text='Notas geradas com sucesso!', text_color='green')

    except subprocess.CalledProcessError:
        resultado2.configure(text='Erro ao gerar notas.', text_color='red')

def selecionar_arquivo_sicoob():
    caminho = filedialog.askopenfilename(title="Selecione o arquivo Sicoob CSV", filetypes=[("Arquivos CSV", "*.csv")])
    if caminho:
        input_arquivo_sicoob.delete(0, ctk.END)
        input_arquivo_sicoob.insert(0, caminho)

def selecionar_arquivo_assuncao():
    caminho = filedialog.askopenfilename(title="Selecione o arquivo Assunção XML", filetypes=[("Arquivos XML", "*.xml")])
    if caminho:
        input_arquivo_assuncao.delete(0, ctk.END)
        input_arquivo_assuncao.insert(0, caminho)

def selecionar_arquivo_notas():
    caminho = filedialog.askopenfilename(title="Selecione o arquivo notas tratadas", filetypes=[("Arquivos CSV", "*.csv")])
    if caminho:
        input_arquivo_notas.delete(0, ctk.END)
        input_arquivo_notas.insert(0, caminho)

# Setup da janela principal
ctk.set_appearance_mode('dark')
app = ctk.CTk()
app.title('Gerados de notas fiscais')
app.geometry('560x600')

# ===== BLOCO SICOOB =====
label_arquivo_sicoob_csv = ctk.CTkLabel(app, text='Arquivo Sicoob CSV')
label_arquivo_sicoob_csv.pack(pady=(20, 5))

frame_sicoob = ctk.CTkFrame(app, fg_color="transparent")
frame_sicoob.pack(pady=5, padx=10)

input_arquivo_sicoob = ctk.CTkEntry(frame_sicoob, width=370, placeholder_text='Endereço do arquivo Sicoob')
input_arquivo_sicoob.grid(row=0, column=0, padx=(0, 10))

botao_sicoob = ctk.CTkButton(frame_sicoob, text="📁", width=40, command=selecionar_arquivo_sicoob)
botao_sicoob.grid(row=0, column=1)

# ===== BLOCO ASSUNÇÃO =====
label_arquivo_assuncao_xml = ctk.CTkLabel(app, text='Arquivo Assunção XML')
label_arquivo_assuncao_xml.pack(pady=(20, 5))

frame_assuncao = ctk.CTkFrame(app, fg_color="transparent")
frame_assuncao.pack(pady=5, padx=10)

input_arquivo_assuncao = ctk.CTkEntry(frame_assuncao, width=370, placeholder_text='Endereço do arquivo Assunção')
input_arquivo_assuncao.grid(row=0, column=0, padx=(0, 10))

botao_assuncao = ctk.CTkButton(frame_assuncao, text="📁", width=40, command=selecionar_arquivo_assuncao)
botao_assuncao.grid(row=0, column=1)




# ===== BOTÃO COMBINAR + RESULTADO =====
botao_combinar = ctk.CTkButton(app, text="Combinar", command=transformar_dados)
botao_combinar.pack(pady=15)

resultado = ctk.CTkLabel(app, text='')
resultado.pack()


# ===== BLOCO GERAR ARQUIVO ======
botao_nova_janela = ctk.CTkButton(app, text="Cadastrar Clientes", command=abrir_cadastro_clientes)
botao_nova_janela.pack(pady=10)

# ===== BLOCO GERAR NOTAS =====

label_arquivo_csv = ctk.CTkLabel(app, text='Arquivo das notas tratadas csv')
label_arquivo_csv.pack(pady=(20, 5))

frame_notas = ctk.CTkFrame(app, fg_color="transparent")
frame_notas.pack(pady=5, padx=10)

input_arquivo_notas = ctk.CTkEntry(frame_notas, width=370, placeholder_text='Endereço do arquivo das notas tratadas csv')
input_arquivo_notas.grid(row=0, column=0, padx=(0, 10))

botao_notas = ctk.CTkButton(frame_notas, text="📁", width=40, command=selecionar_arquivo_notas)
botao_notas.grid(row=0, column=1)


# ===== BOTÃO GERAR NOTAS =====
botao_combinar = ctk.CTkButton(app, text="Combinar", command=gerar_notas)
botao_combinar.pack(pady=15)

resultado2 = ctk.CTkLabel(app, text='')
resultado2.pack()
# Inicia o app
app.mainloop()
