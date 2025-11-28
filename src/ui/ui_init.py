# ===================================================================
# Cabeçalho do Programa
# Nome e RAs: Lucas Soares - 324155365, Robert Zica - 323112024, Leonardo Vieira - 323119033, Asafe Orneles - 324172578, Bruno Eduardo - 322123429
# Data: 27/11/2025
# Curso: Ciência da Computação
# Professor: EUZÉBIO D. DE SOUZA
# Trabalho: Detecção de Movimento usando Filtros Espaciais
# ===================================================================
# ANOTAÇÕES
# ===================================================================
'''
Este módulo é responsável pela inicialização da interface gráfica do usuário (GUI).
Ele cria a janela principal da aplicação, exibe a tela de boas-vindas com a logo do projeto
e gerencia a transição para a tela principal de funcionalidades (abas de medição).
Utiliza a biblioteca CustomTkinter para criar uma interface moderna e responsiva.
'''
#################

import sys  # Importa sys para manipulação do sistema
import os  # Importa os para manipulação de arquivos
import customtkinter as ctk  # Importa a biblioteca gráfica CustomTkinter
from PIL import Image  # Importa a classe Image do Pillow para manipulação de imagens

# Adiciona a raiz do projeto ao path para permitir imports absolutos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.io.paths import get_project_root  # Importa função para achar a raiz do projeto

class AppMetricApp:  # Define a classe principal da aplicação
    def __init__(self):  # Construtor da classe
        self.main_window = ctk.CTk()  # Cria a janela principal
        self.main_window.geometry("1080x580")  # Define o tamanho da janela
        self.main_window.resizable(width=False, height=False)  # Impede redimensionamento
        self.main_window.title("app-metric")  # Define o título da janela

        self.image_paths = []  # Inicializa lista de caminhos de imagem (não usado aqui, mas preparado)
        self.output_folder = None  # Inicializa variável de pasta de saída
        self.progress_bar = None  # Inicializa variável de barra de progresso

        # Define o caminho da logo usando a função de raiz do projeto (portabilidade)
        logo_path = os.path.join(get_project_root(), "assets", "logo", "logo_app_metric.png")
        self.image_logo = None  # Inicializa variável da imagem da logo
        try:
            if os.path.exists(logo_path):  # Verifica se o arquivo da logo existe
                pil_image = Image.open(logo_path)  # Abre a imagem com Pillow
                # Cria objeto CTkImage para exibição na interface
                self.image_logo = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(250, 250))
            else:
                print(f"Aviso: Logo não encontrada em {logo_path}")  # Aviso se não achar
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")  # Erro se falhar ao abrir

        if self.image_logo:  # Se a logo foi carregada com sucesso
            self.label_logo = ctk.CTkLabel(  # Cria um label com a imagem
                self.main_window,
                image=self.image_logo,
                text=""  # Sem texto, só imagem
            )
            self.label_logo.pack(pady=80)  # Adiciona à janela com espaçamento vertical
        else:  # Se não carregou a logo
            self.label_logo = ctk.CTkLabel(  # Cria um label de texto simples
                self.main_window,
                text="app-metric",
                font=("Arial", 32, "bold")
            )
            self.label_logo.pack(pady=80)  # Adiciona à janela

        self.button_enter = ctk.CTkButton(  # Cria o botão "Entrar"
            self.main_window,
            text="Entrar",
            fg_color="#8A2431",  # Cor do botão
            hover_color="#D93D5F",  # Cor ao passar o mouse
            width=200,
            height=50,
            font=("Arial", 16),
            command=self.open_main_window  # Função a chamar ao clicar
        )
        self.button_enter.pack(pady=50)  # Adiciona à janela

        self.main_window.mainloop()  # Inicia o loop principal da interface (mantém a janela aberta)

    def open_main_window(self):  # Função para trocar para a tela principal

        self.main_window.destroy()  # Fecha a janela de boas-vindas
        self.new_window = ctk.CTk()  # Cria uma nova janela
        self.new_window.configure(fg_color="#2F2F2F")  # Define cor de fundo
        self.new_window.geometry("1080x580")  # Define tamanho
        self.new_window.resizable(width=False, height=False)  # Impede redimensionamento
        self.new_window.title("app-metric")  # Define título

        from src.ui.ui_tabs import create_tabs  # Importa função para criar as abas
        create_tabs(self)  # Cria as abas na nova janela

        self.new_window.mainloop()  # Inicia o loop da nova janela
