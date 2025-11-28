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
Este módulo gerencia a lógica das abas da interface gráfica, especificamente a aba de "Medição de Objeto".
Ele define os elementos visuais (botões, labels, barras de progresso) e conecta as ações do usuário
(como selecionar vídeo e pasta) com a lógica de processamento (tracking) que roda em segundo plano (threading).
É aqui que a interação principal do usuário com o sistema acontece.
'''
# ################


import os
import customtkinter as ctk
import threading
from src.core.tracking import track_single_object
from src.io.logger import get_app_logger
from src.io.paths import get_data_dir 
from customtkinter import filedialog

logger = get_app_logger("ui")

def create_tabs(app):
    
    my_values = ["Medição de Objeto"]
    app.my_seg_button = ctk.CTkSegmentedButton(
        app.new_window,
        selected_hover_color="#8A2431",
        selected_color="#8A2431",
        unselected_color="#8A2431",
        fg_color="#8A2431",
        font=("Arial", 14),
        values=my_values,
        command=lambda value: tab_change(value, app)
    )
    app.my_seg_button.pack(pady=10)

    tab_object_measurement(app)   

def tab_object_measurement(app):
    clean_window(app)

    label_format = ctk.CTkLabel(
        app.new_window,
        text="Formato de vídeo suportado:",
        font=("Arial", 21),
        fg_color="#2F2F2F"
    )
    label_format.place(x=64, y=60)

    label_format_ext = ctk.CTkLabel(
        app.new_window,
        text=".mp4, .avi, .mkv",
        font=("Arial", 19),
        fg_color="#2F2F2F"
    )
    label_format_ext.place(x=64, y=95)

    label_video = ctk.CTkLabel(
        app.new_window,
        text="Selecionar vídeo para análise",
        font=("Arial", 21),
        fg_color="#2F2F2F"
    )
    label_video.place(x=64, y=160)

    label_folder = ctk.CTkLabel(
        app.new_window,
        text="Selecionar pasta para salvar resultados",
        font=("Arial", 21),
        fg_color="#2F2F2F"
    )
    label_folder.place(x=64, y=300)

    label_video_path = ctk.CTkLabel(
        app.new_window,
        text="Nenhum vídeo selecionado",
        font=("Arial", 14),
        fg_color="#2F2F2F"
    )
    label_video_path.place(x=64, y=255)

    label_folder_select = ctk.CTkLabel(
        app.new_window,
        text="Nenhuma pasta selecionada",
        font=("Arial", 14),
        fg_color="#2F2F2F"
    )
    label_folder_select.place(x=64, y=395)

    label_result_process = ctk.CTkLabel(
        app.new_window,
        text="",
        font=("Arial", 14),
        fg_color="#2F2F2F"
    )
    label_result_process.place(x=380, y=490)

    label_selected_option = ctk.CTkLabel(
        app.new_window,
        text="",
        font=("Arial", 14),
        fg_color="#2F2F2F"
    )
    label_selected_option.place(x=480, y=160)

    app.progress_bar = ctk.CTkProgressBar(
        app.new_window, width=300, progress_color="#8A2431"
    )
    app.progress_bar.place(x=380, y=520)
    app.progress_bar.set(0)

    if not hasattr(app, "video_path"):
        app.video_path = None
    if not hasattr(app, "output_folder"):
        app.output_folder = None

    def select_video():
        video_path = filedialog.askopenfilename(
            initialdir=get_data_dir("raw"),
            title="Selecione o vídeo",
            filetypes=[
                ("Vídeos suportados", "*.mp4;*.avi;*.mkv;*.mov"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if video_path:
            _, ext = os.path.splitext(video_path)
            ext = ext.lower()
            supported_formats = [".mp4", ".avi", ".mkv", ".mov"]

            if ext in supported_formats and os.path.isfile(video_path):
                app.video_path = video_path

                if app.video_path:
                    logger.info(f"Vídeo selecionado pelo usuário: {app.video_path}")
                
                label_video_path.configure(
                    text=f"Vídeo selecionado:\n{app.video_path}",
                    font=("Arial", 14),
                    text_color="green",
                    fg_color="#2F2F2F"
                )
            else:
                app.video_path = None
                label_video_path.configure(
                    text="Formato de vídeo não suportado",
                    font=("Arial", 17),
                    text_color="red",
                    fg_color="#2F2F2F"
                )
        else:
            app.video_path = None
            label_video_path.configure(
                text="Nenhum vídeo selecionado",
                font=("Arial", 14),
                text_color="red",
                fg_color="#2F2F2F"
            )

    def select_output_folder():
        folder_path = filedialog.askdirectory(
            initialdir=get_data_dir("results"),
            title="Selecione a pasta"
        )

        if folder_path and os.path.isdir(folder_path):
            app.output_folder = folder_path
            app.folder = folder_path 

            label_folder_select.configure(
                text=f"Pasta selecionada\n{app.output_folder}",
                font=("Arial", 17),
                text_color="green",
                fg_color="#2F2F2F"
            )
        else:
            label_folder_select.configure(
                text="Não é uma pasta válida",
                font=("Arial", 17),
                text_color="red",
                fg_color="#2F2F2F"
            )

    def run_video_analysis():

        if not app.video_path:
            label_result_process.configure(
                text="Selecione um vídeo primeiro.",
                text_color="red"
            )
            return

        if not app.output_folder:
            label_result_process.configure(
                text="Selecione uma pasta para salvar os resultados.",
                text_color="red"
            )
            return

        app.progress_bar.set(0.2)
        label_result_process.configure(
            text="Iniciando análise...",
            text_color="white"
        )
        app.new_window.update_idletasks()

        def worker():
            try:
                stats = track_single_object(
                    video_path=app.video_path,
                    output_dir=app.output_folder,
                    tracker_type="CSRT",
                    save_video=True,
                    save_csv=True,
                )

                def update_success():
                    app.progress_bar.set(1.0)

                    msg = "Tracking concluído. Consulte o relatório na pasta selecionada."
                    label_result_process.configure(
                        text=msg,
                        text_color="green"
                    )

                app.new_window.after(0, update_success)

            except Exception as e:
                def update_error():
                    app.progress_bar.set(0.0)
                    label_result_process.configure(
                        text=f"Erro na análise: {e}",
                        text_color="red"
                    )
                app.new_window.after(0, update_error)


        threading.Thread(target=worker, daemon=True).start()


    button_select_video = ctk.CTkButton(
        app.new_window,
        hover_color="#D93D5F",
        fg_color="#8A2431",
        text="Selecionar vídeo",
        width=140,
        height=50,
        font=("Arial", 16),
        command=select_video
    )
    button_select_video.place(x=64, y=195)

    button_select_folder = ctk.CTkButton(
        app.new_window,
        hover_color="#D93D5F",
        fg_color="#8A2431",
        text="Selecionar pasta",
        width=140,
        height=50,
        font=("Arial", 16),
        command=select_output_folder
    )
    button_select_folder.place(x=64, y=345)

    button_run_analysis = ctk.CTkButton(
        app.new_window,
        hover_color="#D93D5F",
        fg_color="#8A2431",
        text="Executar análise",
        width=160,
        height=50,
        font=("Arial", 20),
        command=run_video_analysis
    )
    button_run_analysis.place(x=455, y=440)

def clean_window(app):
    for widget in app.new_window.winfo_children():
        if widget not in [app.my_seg_button]:
            widget.destroy()

def tab_change(value, app):
    clean_window(app)

    if value == "Medição de Objeto":
        tab_object_measurement(app)
