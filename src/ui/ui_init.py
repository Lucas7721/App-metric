# ===================================================================
# Cabeçalho do Programa
# Nome e RAs: Lucas Soares - 324155365, Robert Zica - , Leonardo Vieira - 323119033, Asafe Orneles -, Bruno Eduardo - 
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


import sys
import os
import customtkinter as ctk
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.io.paths import get_project_root 

class AppMetricApp:
    def __init__(self):
        self.main_window = ctk.CTk()
        self.main_window.geometry("1080x580")
        self.main_window.resizable(width=False, height=False)
        self.main_window.title("app-metric")

        self.image_paths = []      
        self.output_folder = None  
        self.progress_bar = None   

        logo_path = os.path.join(get_project_root(), "assets", "logo", "logo_app_metric.png")
        self.image_logo = None
        try:
            if os.path.exists(logo_path):
                pil_image = Image.open(logo_path)
                self.image_logo = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(250, 250))
            else:
                print(f"Aviso: Logo não encontrada em {logo_path}")
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")

        if self.image_logo:
            self.label_logo = ctk.CTkLabel(
                self.main_window,
                image=self.image_logo,
                text=""
            )
            self.label_logo.pack(pady=80)
        else:
            self.label_logo = ctk.CTkLabel(
                self.main_window,
                text="app-metric",
                font=("Arial", 32, "bold")
            )
            self.label_logo.pack(pady=80)

        self.button_enter = ctk.CTkButton(
            self.main_window,
            text="Entrar",
            fg_color="#8A2431",
            hover_color="#D93D5F",
            width=200,
            height=50,
            font=("Arial", 16),
            command=self.open_main_window
        )
        self.button_enter.pack(pady=50)

        self.main_window.mainloop()

    def open_main_window(self):

        self.main_window.destroy()
        self.new_window = ctk.CTk()
        self.new_window.configure(fg_color="#2F2F2F")
        self.new_window.geometry("1080x580")
        self.new_window.resizable(width=False, height=False)
        self.new_window.title("app-metric")

        from src.ui.ui_tabs import create_tabs
        create_tabs(self)  

        self.new_window.mainloop()
