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
#################

import os  # Importa módulo os para operações de sistema
import customtkinter as ctk  # Importa biblioteca de interface gráfica
import threading  # Importa threading para rodar processos em paralelo (evita travar a tela)
from src.core.tracking import track_single_object  # Importa a função principal de tracking
from src.io.logger import get_app_logger  # Importa o logger
from src.io.paths import get_data_dir  # Importa gerenciador de caminhos
from customtkinter import filedialog  # Importa diálogo de seleção de arquivos

logger = get_app_logger("ui")  # Inicializa logger da UI

def create_tabs(app):  # Função para criar o sistema de abas
    
    my_values = ["Medição de Objeto"]  # Lista de abas disponíveis
    app.my_seg_button = ctk.CTkSegmentedButton(  # Cria botão segmentado (abas)
        app.new_window,  # Define a janela que receberá o conjunto de abas
        selected_hover_color="#8A2431",  # Cor de destaque quando o mouse passa sobre uma aba ativa
        selected_color="#8A2431",  # Cor aplicada à aba selecionada
        unselected_color="#8A2431",  # Cor aplicada às abas que não estão selecionadas
        fg_color="#8A2431",  # Cor de fundo geral do componente de abas
        font=("Arial", 14),  # Tipografia aplicada ao texto das abas
        values=my_values,  # Lista de textos que aparecerão como opções de aba
        command=lambda value: tab_change(value, app)  # Função ao trocar aba
    )
    app.my_seg_button.pack(pady=10)  # Adiciona à tela

    tab_object_measurement(app)  # Carrega a aba inicial

def tab_object_measurement(app):  # Função que desenha a aba de medição
    clean_window(app)  # Limpa widgets anteriores

    label_format = ctk.CTkLabel(  # Label informativo
        app.new_window,  # Define a janela que exibirá o texto do rótulo
        text="Formato de vídeo suportado:",  # Conteúdo textual exibido para o usuário
        font=("Arial", 21),  # Tamanho e estilo da fonte utilizada
        fg_color="#2F2F2F"  # Cor de fundo do rótulo (compatível com o tema)
    )
    label_format.place(x=64, y=60)  # Posiciona na tela

    label_format_ext = ctk.CTkLabel(  # Label com extensões
        app.new_window,  # Referência da janela onde o rótulo será exibido
        text=".mp4, .avi, .mkv",  # Lista das extensões suportadas apresentada ao usuário
        font=("Arial", 19),  # Define o estilo do texto desse rótulo
        fg_color="#2F2F2F"  # Cor de fundo do rótulo
    )
    label_format_ext.place(x=64, y=95)  # Posiciona a linha de extensões

    label_video = ctk.CTkLabel(  # Label instrução vídeo
        app.new_window,  # Indica onde o rótulo será posicionado
        text="Selecionar vídeo para análise",  # Mensagem que orienta o usuário
        font=("Arial", 21),  # Define a fonte para manter o padrão visual
        fg_color="#2F2F2F"  # Cor de fundo harmonizada com a interface
    )
    label_video.place(x=64, y=160)  # Posiciona o rótulo da instrução do vídeo

    label_folder = ctk.CTkLabel(  # Label instrução pasta
        app.new_window,  # Janela que recebe o rótulo
        text="Selecionar pasta para salvar resultados",  # Texto exibido ao usuário
        font=("Arial", 21),  # Fonte utilizada no rótulo
        fg_color="#2F2F2F"  # Cor de fundo do rótulo
    )
    label_folder.place(x=64, y=300)  # Define a posição da instrução de pasta

    label_video_path = ctk.CTkLabel(  # Label status vídeo
        app.new_window,  # Elemento pai do rótulo informativo
        text="Nenhum vídeo selecionado",  # Mensagem inicial indicando ausência de seleção
        font=("Arial", 14),  # Define o tamanho da fonte do rótulo
        fg_color="#2F2F2F"  # Cor de fundo alinhada ao layout
    )
    label_video_path.place(x=64, y=255)  # Posiciona a mensagem de status do vídeo

    label_folder_select = ctk.CTkLabel(  # Label status pasta
        app.new_window,  # Define onde o rótulo será desenhado
        text="Nenhuma pasta selecionada",  # Mensagem inicial exibida ao usuário
        font=("Arial", 14),  # Fonte utilizada para o texto do rótulo
        fg_color="#2F2F2F"  # Aplica a mesma cor de fundo do restante da interface
    )
    label_folder_select.place(x=64, y=395)  # Coloca o status da pasta no layout

    label_result_process = ctk.CTkLabel(  # Label status processo
        app.new_window,  # Janela onde o rótulo de status será mostrado
        text="",  # Inicia sem mensagem até o processamento começar
        font=("Arial", 14),  # Define a fonte usada para exibir o status
        fg_color="#2F2F2F"  # Cor de fundo do rótulo de status
    )
    label_result_process.place(x=380, y=490)  # Posiciona o rótulo de mensagens gerais

    label_selected_option = ctk.CTkLabel(  # Label opção selecionada (placeholder)
        app.new_window,  # Janela onde o rótulo ficará visível
        text="",  # Deixa o texto vazio até que alguma opção seja selecionada
        font=("Arial", 14),  # Define a fonte do rótulo auxiliar
        fg_color="#2F2F2F"  # Cor de fundo compatível com o restante da UI
    )
    label_selected_option.place(x=480, y=160)  # Reserva espaço para feedback adicional

    app.progress_bar = ctk.CTkProgressBar(  # Barra de progresso
        app.new_window,  # Define a janela que abriga a barra
        width=300,  # Controla o tamanho horizontal do componente
        progress_color="#8A2431"  # Define a cor da barra conforme identidade visual
    )
    app.progress_bar.place(x=380, y=520)  # Posiciona a barra logo abaixo das mensagens
    app.progress_bar.set(0)  # Zera a barra

    if not hasattr(app, "video_path"):  # Garante atributo video_path
        app.video_path = None  # Inicializa ausência de vídeo
    if not hasattr(app, "output_folder"):  # Garante atributo output_folder
        app.output_folder = None  # Inicializa ausência de diretório

    def select_video():  # Função interna para selecionar vídeo
        video_path = filedialog.askopenfilename(  # Abre diálogo de arquivo
            initialdir=get_data_dir("raw"),  # Começa na pasta raw pré-configurada
            title="Selecione o vídeo",  # Título da janela de escolha
            filetypes=[
                ("Vídeos suportados", "*.mp4;*.avi;*.mkv;*.mov"),  # Filtro com formatos aceitos
                ("Todos os arquivos", "*.*")  # Filtro alternativo para qualquer arquivo
            ]
        )

        if video_path:  # Se usuário selecionou algo
            _, ext = os.path.splitext(video_path)  # Pega extensão
            ext = ext.lower()  # Normaliza para minúsculas
            supported_formats = [".mp4", ".avi", ".mkv", ".mov"]  # Lista de extensões válidas

            if ext in supported_formats and os.path.isfile(video_path):  # Valida formato
                app.video_path = video_path  # Salva caminho

                if app.video_path:  # Reforça a existência antes de registrar
                    logger.info(f"Vídeo selecionado pelo usuário: {app.video_path}")  # Loga seleção
                
                label_video_path.configure(  # Atualiza label visual
                    text=f"Vídeo selecionado:\n{app.video_path}",  # Mostra o caminho escolhido
                    font=("Arial", 14),  # Mantém a fonte padrão de status
                    text_color="green",  # Indica sucesso na seleção
                    fg_color="#2F2F2F"  # Garante fundo consistente
                )
            else:  # Formato inválido
                app.video_path = None  # Revoga o caminho inválido
                label_video_path.configure(
                    text="Formato de vídeo não suportado",  # Mensagem de erro
                    font=("Arial", 17),  # Fonte maior para chamar atenção
                    text_color="red",  # Indica falha
                    fg_color="#2F2F2F"  # Mantém fundo neutro
                )
        else:  # Cancelou seleção
            app.video_path = None  # Garante limpeza do estado
            label_video_path.configure(
                text="Nenhum vídeo selecionado",  # Feedback após cancelar
                font=("Arial", 14),  # Retoma a fonte padrão
                text_color="red",  # Mantém alerta visual
                fg_color="#2F2F2F"  # Fundo padronizado
            )

    def select_output_folder():  # Função interna para selecionar pasta
        folder_path = filedialog.askdirectory(  # Abre diálogo de pasta
            initialdir=get_data_dir("results"),  # Sugere a pasta de resultados
            title="Selecione a pasta"  # Define o título da janela modal
        )

        if folder_path and os.path.isdir(folder_path):  # Se pasta válida
            app.output_folder = folder_path  # Registra caminho para exportar arquivos
            app.folder = folder_path  # Mantém consistência com outros trechos já existentes

            label_folder_select.configure(  # Atualiza label visual
                text=f"Pasta selecionada\n{app.output_folder}",  # Mostra o destino escolhido
                font=("Arial", 17),  # Usa fonte maior para destaque
                text_color="green",  # Indica seleção bem-sucedida
                fg_color="#2F2F2F"  # Preserva a estética do layout
            )
        else:  # Pasta inválida
            label_folder_select.configure(
                text="Não é uma pasta válida",  # mensagem de erro
                font=("Arial", 17),  # Fonte padrão de alerta
                text_color="red",  # Sinaliza problema visualmente
                fg_color="#2F2F2F"  # Fundo neutro
            )

    def run_video_analysis():  # Função principal de execução

        if not app.video_path:  # Valida se tem vídeo
            label_result_process.configure(
                text="Selecione um vídeo primeiro.",  # Mensagem para orientar o usuário
                text_color="red"  # Uso de vermelho para enfatizar a validação
            )
            return  # Interrompe a execução por falta de vídeo

        if not app.output_folder:  # Valida se tem pasta
            label_result_process.configure(
                text="Selecione uma pasta para salvar os resultados.",  # Solicita destino
                text_color="red"  # Indica que falta informação
            )
            return  # Interrompe para aguardar a seleção da pasta

        app.progress_bar.set(0.2)  # Inicia progresso visual
        label_result_process.configure(
            text="Iniciando análise...",  # Atualiza feedback textual
            text_color="white"  # Usa branco para indicar estado neutro em execução
        )
        app.new_window.update_idletasks()  # Força atualização da tela

        def worker():  # Função worker para rodar em thread separada
            try:
                stats = track_single_object(  # Chama a função pesada de tracking
                    video_path=app.video_path,  # Caminho do vídeo selecionado
                    output_dir=app.output_folder,  # Diretório onde os resultados serão salvos
                    tracker_type="CSRT",  # Algoritmo de rastreamento escolhido
                    save_video=True,  # Habilita salvamento do vídeo anotado
                    save_csv=True,  # Gera arquivo CSV com medições
                )

                def update_success():  # Função para atualizar UI após sucesso
                    app.progress_bar.set(1.0)  # Completa barra

                    msg = "Tracking concluído. Consulte o relatório na pasta selecionada."  # Mensagem pública final
                    label_result_process.configure(
                        text=msg,  # Mensagem final de sucesso
                        text_color="green"  # Cor verde reforça a conclusão positiva
                    )

                app.new_window.after(0, update_success)  # Agenda atualização na thread principal

            except Exception as e:  # Captura erros
                def update_error():  # Função para atualizar UI após erro
                    app.progress_bar.set(0.0)  # Reseta a barra para indicar falha
                    label_result_process.configure(
                        text=f"Erro na análise: {e}",  # Mostra a exceção ao usuário
                        text_color="red"  # Indica problema com destaque
                    )
                app.new_window.after(0, update_error)  # Agenda atualização na thread principal


        threading.Thread(target=worker, daemon=True).start()  # Inicia a thread


    button_select_video = ctk.CTkButton(  # Botão selecionar vídeo
        app.new_window,  # Define a janela que receberá o botão
        hover_color="#D93D5F",  # Cor quando o mouse passa por cima
        fg_color="#8A2431",  # Cor padrão do botão
        text="Selecionar vídeo",  # Texto apresentado ao usuário
        width=140,  # Largura do botão
        height=50,  # Altura do botão
        font=("Arial", 16),  # Fonte utilizada no texto
        command=select_video  # Função chamada no clique
    )
    button_select_video.place(x=64, y=195)  # Posiciona o botão abaixo da instrução

    button_select_folder = ctk.CTkButton(  # Botão selecionar pasta
        app.new_window,  # Janela onde o botão será exibido
        hover_color="#D93D5F",  # Cor de destaque ao passar o mouse
        fg_color="#8A2431",  # Mantém a cor padrão da identidade visual
        text="Selecionar pasta",  # Texto do botão
        width=140,  # Define largura
        height=50,  # Define altura
        font=("Arial", 16),  # Fonte idêntica ao botão de vídeo
        command=select_output_folder  # Associa a função de seleção
    )
    button_select_folder.place(x=64, y=345)  # Posiciona o botão na seção das pastas

    button_run_analysis = ctk.CTkButton(  # Botão executar
        app.new_window,  # Janela que receberá o acionador principal
        hover_color="#D93D5F",  # Cor ao passar o mouse
        fg_color="#8A2431",  # Cor base compatível com a UI
        text="Executar análise",  # Texto do botão
        width=160,  # Largura maior para indicar destaque
        height=50,  # Altura do botão principal
        font=("Arial", 20),  # Fonte maior para chamar atenção
        command=run_video_analysis  # Aciona a lógica de processamento
    )
    button_run_analysis.place(x=455, y=440)  # Posiciona o botão próximo aos feedbacks

def clean_window(app):  # Função para limpar widgets da janela
    for widget in app.new_window.winfo_children():  # Itera sobre filhos da janela
        if widget not in [app.my_seg_button]:  # Mantém o botão de abas
            widget.destroy()  # Destrói os outros

def tab_change(value, app):  # Função de troca de aba
    clean_window(app)  # Limpa tela

    if value == "Medição de Objeto":  # Se aba selecionada for medição
        tab_object_measurement(app)  # Carrega conteúdo