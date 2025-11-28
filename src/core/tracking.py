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
Este módulo contém o núcleo da lógica de rastreamento de objetos (Tracking).
Ele utiliza algoritmos do OpenCV (como CSRT e KCF) para seguir um objeto selecionado pelo usuário frame a frame.
Além do rastreamento visual, este arquivo é responsável por calcular métricas cinemáticas (velocidade, distância, trajetória),
gerar o vídeo processado com as anotações visuais e exportar os relatórios estatísticos (.txt) e de dados (.csv).
'''
#################

import os  # Importa o módulo os para interagir com o sistema operacional (criar pastas, verificar arquivos)
import csv  # Importa o módulo csv para ler e escrever arquivos CSV (planilhas)
import math  # Importa o módulo math para funções matemáticas (cálculo de distância, hipotenusa)
import cv2  # Importa a biblioteca OpenCV para processamento de imagem e vídeo
import numpy as np  # Importa a biblioteca NumPy para manipulação eficiente de arrays e matrizes numéricas
from src.io.logger import get_app_logger  # Importa a função personalizada para obter o logger da aplicação
from datetime import datetime  # Importa a classe datetime para manipular datas e horas
from typing import List, Tuple, Dict, Optional  # Importa tipos para anotação de tipagem (Type Hinting)

logger = get_app_logger("tracking")  # Inicializa o logger específico para este módulo com o nome "tracking"

def _create_tracker(tracker_type: str = "CSRT"):  # Define uma função auxiliar privada para criar o objeto Tracker do OpenCV
    
    t = tracker_type.upper()  # Converte o tipo de tracker solicitado para maiúsculas para padronização

    if t == "CSRT":  # Verifica se o tipo solicitado é CSRT (mais preciso, porém mais lento)
        if hasattr(cv2, "TrackerCSRT_create"):  # Verifica se a função de criação existe na raiz do cv2 (versões antigas)
            return cv2.TrackerCSRT_create()  # Cria e retorna o tracker CSRT
        if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):  # Verifica se está no submódulo legacy (versões novas)
            return cv2.legacy.TrackerCSRT_create()  # Cria e retorna o tracker CSRT do módulo legacy
    elif t == "KCF":  # Verifica se o tipo solicitado é KCF (mais rápido, menos preciso)
        if hasattr(cv2, "TrackerKCF_create"):  # Verifica se a função existe na raiz do cv2
            return cv2.TrackerKCF_create()  # Cria e retorna o tracker KCF
        if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerKCF_create"):  # Verifica se está no submódulo legacy
            return cv2.legacy.TrackerKCF_create()  # Cria e retorna o tracker KCF do módulo legacy

    # Se nenhum tracker for encontrado ou o tipo for inválido, lança um erro explicativo
    raise RuntimeError(
        f"Não foi possível criar o tracker '{tracker_type}'. "
        "Instale 'opencv-contrib-python'."
    )

def track_single_object(  # Define a função principal de tracking que será chamada pela interface
    video_path: str,  # Caminho do arquivo de vídeo de entrada
    output_dir: str,  # Diretório onde os resultados serão salvos
    tracker_type: str = "CSRT",  # Algoritmo de tracking a ser usado (padrão CSRT)
    save_video: bool = True,  # Flag para decidir se salva o vídeo processado
    save_csv: bool = False,  # Flag para decidir se salva o arquivo CSV com a trajetória
    pixels_per_meter: Optional[float] = None,  # Valor de calibração para converter pixels em metros (opcional)
    save_debug_images: bool = True,  # Flag para decidir se salva imagens de debug (bordas, movimento)
) -> Dict:  # A função retorna um dicionário com as estatísticas

    if not os.path.isfile(video_path):  # Verifica se o arquivo de vídeo existe no caminho especificado
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")  # Lança erro se o vídeo não existir

    os.makedirs(output_dir, exist_ok=True)  # Cria o diretório de saída se ele não existir (exist_ok=True evita erro se já existir)

    cap = cv2.VideoCapture(video_path)  # Abre o arquivo de vídeo para leitura usando OpenCV
    if not cap.isOpened():  # Verifica se o vídeo foi aberto com sucesso
        raise RuntimeError(f"Não foi possível abrir o vídeo: {video_path}")  # Lança erro se falhar ao abrir

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0  # Obtém a taxa de quadros por segundo (FPS) do vídeo
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Obtém a largura dos quadros do vídeo
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Obtém a altura dos quadros do vídeo

    max_disp_w = 960  # Define a largura máxima para a janela de exibição (para não ocupar a tela toda)
    max_disp_h = 540  # Define a altura máxima para a janela de exibição
    scale = min(max_disp_w / width, max_disp_h / height, 1.0)  # Calcula o fator de escala para redimensionar o vídeo na tela

    disp_w = int(width * scale)  # Calcula a largura de exibição baseada na escala
    disp_h = int(height * scale)  # Calcula a altura de exibição baseada na escala

    ret, frame = cap.read()  # Lê o primeiro quadro do vídeo para permitir a seleção do objeto
    if not ret or frame is None:  # Verifica se a leitura falhou
        cap.release()  # Libera o recurso de vídeo
        raise RuntimeError("Não foi possível ler o primeiro frame do vídeo.")  # Lança erro

    if scale < 1.0:  # Se a escala for menor que 1 (precisa reduzir)
        frame_disp = cv2.resize(frame, (disp_w, disp_h), interpolation=cv2.INTER_AREA)  # Redimensiona o frame para exibição
    else:
        frame_disp = frame.copy()  # Caso contrário, usa o frame original

    # Abre uma janela para o usuário selecionar a Região de Interesse (ROI) - o objeto a rastrear
    roi_scaled = cv2.selectROI(
        "Selecione o objeto (ENTER/ESP para confirmar)",  # Título da janela
        frame_disp,  # Imagem onde será feita a seleção
        fromCenter=False,  # A seleção não começa do centro
        showCrosshair=True,  # Mostra uma cruz para ajudar na mira
    )
    cv2.destroyWindow("Selecione o objeto (ENTER/ESP para confirmar)")  # Fecha a janela de seleção após confirmar

    if roi_scaled == (0, 0, 0, 0):  # Verifica se a seleção foi vazia (usuário cancelou ou não selecionou nada)
        cap.release()  # Libera o vídeo
        raise RuntimeError("ROI inválida (talvez o usuário cancelou).")  # Lança erro

    # Converte as coordenadas da ROI da escala de exibição de volta para a escala original do vídeo
    x_s, y_s, w_s, h_s = roi_scaled  # Desempacota as coordenadas da ROI selecionada
    x = int(x_s / scale)  # Calcula x original
    y = int(y_s / scale)  # Calcula y original
    w = int(w_s / scale)  # Calcula largura original
    h = int(h_s / scale)  # Calcula altura original
    roi = (x, y, w, h)  # Cria a tupla da ROI original
    initial_box = roi  # Armazena a caixa inicial para referência futura

    tracker = _create_tracker(tracker_type)  # Cria a instância do tracker escolhido
    tracker.init(frame, roi)  # Inicializa o tracker com o primeiro frame e a caixa delimitadora

    base_name = os.path.splitext(os.path.basename(video_path))[0]  # Extrai o nome do arquivo de vídeo sem extensão
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Gera um timestamp atual para nomear arquivos únicos

    debug_dir = None  # Inicializa a variável do diretório de debug como None
    if save_debug_images:  # Se a opção de salvar imagens de debug estiver ativa
        debug_dir = os.path.join(output_dir, f"{base_name}_debug_{timestamp}")  # Define o caminho da pasta de debug
        os.makedirs(debug_dir, exist_ok=True)  # Cria a pasta de debug
    
    logger.info(f"Iniciando tracking: vídeo={video_path}, tracker={tracker_type}")  # Registra no log o início do processo

    video_out_path: Optional[str] = None  # Inicializa o caminho do vídeo de saída
    writer = None  # Inicializa o objeto de escrita de vídeo
    if save_video:  # Se a opção de salvar vídeo estiver ativa
        video_filename = f"{base_name}_tracking_{timestamp}.mp4"  # Define o nome do arquivo de vídeo de saída
        video_out_path = os.path.join(output_dir, video_filename)  # Define o caminho completo
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Define o codec de compressão (MP4V)
        writer = cv2.VideoWriter(  # Cria o objeto VideoWriter
            video_out_path,  # Caminho de saída
            fourcc,  # Codec
            fps if fps > 0 else 30.0,  # FPS (usa 30 se não detectado)
            (width, height),  # Resolução
        )

    trajectory: List[Dict] = []  # Lista para armazenar os dados da trajetória frame a frame
    prev_center: Optional[Tuple[float, float]] = None  # Variável para guardar o centro do objeto no frame anterior
    speeds_px: List[float] = []  # Lista para armazenar as velocidades instantâneas
    total_distance_px = 0.0  # Acumulador da distância total percorrida
    frame_idx = 0  # Contador de frames processados
    success_frames = 0  # Contador de frames onde o tracking foi bem-sucedido

    prev_gray: Optional[np.ndarray] = None  # Variável para guardar o frame anterior em escala de cinza (para debug)
    debug_indices = set()  # Conjunto para armazenar os índices dos frames que serão salvos como debug
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)  # Obtém o total de frames do vídeo
    if save_debug_images and total_frames > 0:  # Se debug ativo e vídeo tem frames
        debug_indices.update(  # Adiciona frames específicos (início, meio, fim, quartos) para salvar
            {
                0,
                max(0, total_frames // 4),
                max(0, total_frames // 2),
                max(0, 3 * total_frames // 4),
                max(0, total_frames - 1),
            }
        )

    cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)  # Cria a janela de exibição do tracking
    cv2.resizeWindow("Tracking", disp_w, disp_h)  # Redimensiona a janela para o tamanho calculado

    while True:  # Loop principal de processamento frame a frame
        ret, frame = cap.read()  # Lê o próximo frame do vídeo
        if not ret or frame is None:  # Se não houver mais frames ou erro de leitura
            break  # Sai do loop
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Converte o frame atual para escala de cinza (usado no debug)
        success, box = tracker.update(frame)  # Atualiza o tracker com o novo frame para encontrar o objeto

        if success:  # Se o objeto foi encontrado com sucesso
            success_frames += 1  # Incrementa contador de sucesso
            x, y, w, h = [int(v) for v in box]  # Extrai as coordenadas da caixa delimitadora
            cx = x + w / 2.0  # Calcula a coordenada X do centro
            cy = y + h / 2.0  # Calcula a coordenada Y do centro

            speed_px = 0.0  # Inicializa velocidade instantânea
            if prev_center is not None:  # Se houver um centro anterior (não é o primeiro frame detectado)
                dx = cx - prev_center[0]  # Calcula deslocamento em X
                dy = cy - prev_center[1]  # Calcula deslocamento em Y
                speed_px = float(math.hypot(dx, dy))  # Calcula a distância euclidiana (velocidade em px/frame)
                speeds_px.append(speed_px)  # Adiciona à lista de velocidades
                total_distance_px += speed_px  # Soma à distância total

            prev_center = (cx, cy)  # Atualiza o centro anterior para o atual

            trajectory.append(  # Adiciona os dados do frame atual à lista de trajetória
                {
                    "frame": frame_idx,
                    "x": cx,
                    "y": cy,
                    "speed_px_per_frame": speed_px,
                }
            )

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Desenha o retângulo verde ao redor do objeto
            cv2.circle(frame, (int(cx), int(cy)), 4, (0, 0, 255), -1)  # Desenha um ponto vermelho no centro do objeto

            speed_px_s = speed_px * fps if fps > 0 else 0.0  # Calcula velocidade em pixels por segundo
            hud_lines = [  # Prepara as linhas de texto para o HUD (Heads-Up Display)
                f"Frame: {frame_idx}",
                f"Vel: {speed_px:.2f} px/frame  ({speed_px_s:.2f} px/s)",
            ]
            y0 = 25  # Posição Y inicial do texto
            for i, text in enumerate(hud_lines):  # Itera sobre as linhas de texto
                cv2.putText(  # Escreve o texto no frame
                    frame,
                    text,
                    (10, y0 + i * 22),  # Posição
                    cv2.FONT_HERSHEY_SIMPLEX,  # Fonte
                    0.6,  # Tamanho
                    (255, 255, 255),  # Cor (Branco)
                    2,  # Espessura
                )
        else:  # Se o tracking falhou neste frame
            cv2.putText(  # Escreve aviso de falha
                frame,
                "Tracking perdido",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),  # Cor (Vermelho)
                2,
            )
        
        # Bloco para salvar imagens de debug (se ativado e for um frame selecionado)
        if save_debug_images and debug_dir is not None and (frame_idx in debug_indices):
            edges = cv2.Canny(gray, 100, 200)  # Aplica filtro de Canny para detectar bordas
            edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)  # Converte bordas para BGR para poder juntar com imagem colorida

            if prev_gray is not None:  # Se houver frame anterior
                diff = cv2.absdiff(gray, prev_gray)  # Calcula a diferença absoluta entre frames (movimento)
                diff_norm = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)  # Normaliza para visualizar melhor
            else:
                diff_norm = np.zeros_like(gray)  # Se não, cria imagem preta
            diff_bgr = cv2.cvtColor(diff_norm, cv2.COLOR_GRAY2BGR)  # Converte diferença para BGR

            panel = np.hstack([frame, edges_bgr, diff_bgr])  # Junta as 3 imagens horizontalmente (Original, Bordas, Movimento)
            
            txt = f"frame={frame_idx} | vel={speed_px:.2f}"  # Texto informativo
            cv2.putText(panel, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)  # Escreve no painel

            debug_name = os.path.join(debug_dir, f"debug_frame_{frame_idx:05d}.png")  # Define nome do arquivo
            cv2.imwrite(debug_name, panel)  # Salva a imagem no disco
        
        prev_gray = gray  # Atualiza o frame anterior para a próxima iteração

        if writer is not None:  # Se estiver gravando vídeo
            writer.write(frame)  # Escreve o frame processado no arquivo de vídeo

        if scale < 1.0:  # Se precisar redimensionar para exibir na tela
            frame_disp = cv2.resize(frame, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
        else:
            frame_disp = frame

        cv2.imshow("Tracking", frame_disp)  # Mostra o frame na janela

        key = cv2.waitKey(1) & 0xFF  # Aguarda 1ms por uma tecla
        if key == 27:  # Se a tecla for ESC (código 27)
            break  # Interrompe o loop

        if cv2.getWindowProperty("Tracking", cv2.WND_PROP_VISIBLE) < 1:  # Se a janela for fechada pelo 'X'
            break  # Interrompe o loop

        frame_idx += 1  # Incrementa o contador de frames

    cap.release()  # Libera o arquivo de vídeo de entrada
    if writer is not None:  # Se houver gravador de vídeo
        writer.release()  # Finaliza e salva o arquivo de vídeo
    cv2.destroyAllWindows()  # Fecha todas as janelas do OpenCV

    # Cálculos finais de estatísticas
    mean_speed_px = float(np.mean(speeds_px)) if speeds_px else 0.0  # Calcula velocidade média em pixels
    max_speed_px = float(np.max(speeds_px)) if speeds_px else 0.0  # Calcula velocidade máxima em pixels

    if fps > 0:  # Se FPS for válido
        mean_speed_px_per_s = mean_speed_px * fps  # Converte média para px/s
        max_speed_px_per_s = max_speed_px * fps  # Converte máxima para px/s
        duracao_segundos = frame_idx / fps  # Calcula duração total
    else:
        mean_speed_px_per_s = 0.0
        max_speed_px_per_s = 0.0
        duracao_segundos = 0.0

    straight_distance_px = 0.0  # Inicializa distância em linha reta
    path_efficiency = 0.0  # Inicializa eficiência da trajetória
    if len(trajectory) >= 2:  # Se houver pelo menos 2 pontos
        x0, y0 = trajectory[0]["x"], trajectory[0]["y"]  # Ponto inicial
        x1, y1 = trajectory[-1]["x"], trajectory[-1]["y"]  # Ponto final
        straight_distance_px = float(math.hypot(x1 - x0, y1 - y0))  # Distância euclidiana entre início e fim
        if total_distance_px > 0:
            path_efficiency = straight_distance_px / total_distance_px  # Razão entre deslocamento útil e total percorrido

    success_rate = (success_frames / frame_idx) if frame_idx > 0 else 0.0  # Taxa de sucesso do tracking

    # Conversão para unidades físicas (se fornecido pixels_per_meter)
    mean_speed_m_s = None
    max_speed_m_s = None
    mean_speed_km_h = None
    max_speed_km_h = None

    if pixels_per_meter and pixels_per_meter > 0 and fps > 0:  # Se houver calibração
        mean_speed_m_s = mean_speed_px_per_s / pixels_per_meter  # Converte para m/s
        max_speed_m_s = max_speed_px_per_s / pixels_per_meter
        mean_speed_km_h = mean_speed_m_s * 3.6  # Converte para km/h
        max_speed_km_h = max_speed_m_s * 3.6

    # Monta o dicionário de estatísticas finais
    stats = {
        "video_input": video_path,  # Caminho do vídeo original analisado
        "tracker_type": tracker_type,  # Tipo de algoritmo de rastreamento utilizado (CSRT/KCF)
        "num_frames": frame_idx,  # Número total de frames processados
        "fps": fps,  # Taxa de quadros por segundo do vídeo
        "duracao_segundos": duracao_segundos,  # Duração total do vídeo em segundos
        "frame_width": width,  # Largura do frame do vídeo
        "frame_height": height,  # Altura do frame do vídeo
        "initial_box": initial_box,  # Coordenadas iniciais da caixa delimitadora (ROI)
        "mean_speed_px": mean_speed_px,  # Velocidade média em pixels por frame
        "max_speed_px": max_speed_px,  # Velocidade máxima em pixels por frame
        "mean_speed_px_per_s": mean_speed_px_per_s,  # Velocidade média em pixels por segundo
        "max_speed_px_per_s": max_speed_px_per_s,  # Velocidade máxima em pixels por segundo
        "total_distance_px": total_distance_px,  # Distância total percorrida em pixels
        "straight_distance_px": straight_distance_px,  # Distância em linha reta (início ao fim) em pixels
        "path_efficiency": path_efficiency,  # Eficiência da trajetória (reta / total)
        "success_frames": success_frames,  # Número de frames onde o objeto foi rastreado com sucesso
        "success_rate": success_rate,  # Taxa de sucesso do rastreamento (0.0 a 1.0)
        "mean_speed_m_s": mean_speed_m_s,  # Velocidade média em metros por segundo (se calibrado)
        "max_speed_m_s": max_speed_m_s,  # Velocidade máxima em metros por segundo (se calibrado)
        "mean_speed_km_h": mean_speed_km_h,  # Velocidade média em km/h (se calibrado)
        "max_speed_km_h": max_speed_km_h,  # Velocidade máxima em km/h (se calibrado)
        "trajectory": trajectory,  # Lista contendo os dados de posição frame a frame
        "video_output": video_out_path,  # Caminho do vídeo gerado com as anotações
        "debug_dir": debug_dir,  # Diretório onde as imagens de debug foram salvas
    }

    csv_path = None  # Inicializa caminho do CSV (será preenchido se salvarmos a trajetória)
    if save_csv:  # Se opção de salvar CSV ativa
        csv_filename = f"{base_name}_trajectory_{timestamp}.csv"  # Nome do arquivo de trajetória com timestamp
        csv_path = os.path.join(output_dir, csv_filename)  # Monta o caminho completo para o CSV no diretório de saída
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:  # Abre o arquivo CSV em modo escrita com UTF-8
            writer_csv = csv.writer(f, delimiter=";")  # Cria escritor CSV usando ponto e vírgula como separador
            writer_csv.writerow(["frame", "x", "y", "speed_px_per_frame"])  # Escreve cabeçalho com nomes das colunas
            for p in trajectory:  # Itera sobre cada ponto registrado da trajetória
                writer_csv.writerow(  # Escreve uma linha no CSV contendo dados do frame atual
                    [
                        p["frame"],  # Coluna com o índice do frame
                        f"{p['x']:.3f}",  # Coluna com a coordenada X formatada com 3 casas decimais
                        f"{p['y']:.3f}",  # Coluna com a coordenada Y formatada com 3 casas decimais
                        f"{p['speed_px_per_frame']:.3f}",  # Coluna com a velocidade instantânea em px/frame formatada
                    ]
                )
        stats["csv_output"] = csv_path  # Registra o caminho do CSV gerado dentro do dicionário de estatísticas
    
    report_filename = f"{base_name}_relatorio_{timestamp}.txt"  # Nome do arquivo de relatório textual com timestamp
    report_path = os.path.join(output_dir, report_filename)  # Constroi o caminho completo do relatório no diretório de saída

    with open(report_path, "w", encoding="utf-8") as f:  # Abre o relatório TXT em modo escrita com codificação UTF-8
        f.write("=== Relatório de Tracking de Objeto ===\n\n")  # Registra o título principal do relatório
        f.write(f"Data/Hora da análise : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")  # Registra data e hora da geração
        f.write(f"Vídeo de entrada     : {video_path}\n")  # Registra o caminho do vídeo analisado
        f.write(f"Tracker utilizado    : {tracker_type}\n\n")  # Registra o tipo de tracker usado

        f.write("--- Informações do vídeo ---\n")  # Seção com metadados do vídeo
        f.write(f"Resolução            : {width} x {height}\n")  # Registra largura e altura do vídeo
        f.write(f"FPS (arquivo)        : {fps:.2f}\n")  # Registra FPS reportado pelo arquivo
        f.write(f"Frames processados   : {frame_idx}\n")  # Registra total de frames processados
        f.write(f"Duração aprox. (s)   : {duracao_segundos:.2f}\n\n")  # Registra duração estimada em segundos

        f.write("--- Bounding box inicial ---\n")  # Seção com informações da ROI inicial
        bx, by, bw, bh = initial_box  # Descompacta os valores da caixa inicial (posição e tamanho)
        f.write(f"Posição (x, y)       : ({bx}, {by})\n")  # Registra a posição inicial da ROI
        f.write(f"Tamanho (w, h)       : {bw} x {bh} px\n\n")  # Registra o tamanho da ROI em pixels

        f.write("--- Qualidade do tracking ---\n")  # Seção sobre desempenho do rastreamento
        f.write(f"Frames com sucesso   : {success_frames}\n")  # Registra quantos frames obtiveram tracking válido
        f.write(f"Taxa de sucesso      : {success_rate*100:.2f} %\n\n")  # Registra a taxa de sucesso em porcentagem

        f.write("--- Métricas de movimento (em pixels) ---\n")  # Seção com métricas em unidades de pixels
        f.write(f"Vel. média (px/frame): {mean_speed_px:.4f}\n")  # Registra velocidade média em px/frame
        f.write(f"Vel. máx.  (px/frame): {max_speed_px:.4f}\n")  # Registra velocidade máxima em px/frame
        f.write(f"Vel. média (px/s)    : {mean_speed_px_per_s:.4f}\n")  # Registra velocidade média convertida para px/s
        f.write(f"Vel. máx.  (px/s)    : {max_speed_px_per_s:.4f}\n")  # Registra velocidade máxima convertida para px/s
        f.write(f"Dist. total (px)     : {total_distance_px:.4f}\n")  # Registra distância total percorrida em pixels
        f.write(f"Dist. reta (px)      : {straight_distance_px:.4f}\n")  # Registra distância em linha reta em pixels
        f.write(f"Eficiência trajetória: {path_efficiency*100:.2f} %\n\n")  # Registra eficiência do caminho em porcentagem

        f.write("--- Métricas físicas (se escala for fornecida) ---\n")  # Seção com métricas físicas (depende de calibração)
        if pixels_per_meter and pixels_per_meter > 0 and fps > 0:  # Verifica se há escala válida para converter pixels em metros
            f.write(f"Escala utilizada     : {pixels_per_meter} px ≈ 1 m\n")  # Registra a escala fornecida
            f.write(f"Vel. média (m/s)     : {mean_speed_m_s:.4f}\n")  # Registra velocidade média em metros por segundo
            f.write(f"Vel. máx.  (m/s)     : {max_speed_m_s:.4f}\n")  # Registra velocidade máxima em metros por segundo
            f.write(f"Vel. média (km/h)    : {mean_speed_km_h:.4f}\n")  # Registra velocidade média convertida para km/h
            f.write(f"Vel. máx.  (km/h)    : {max_speed_km_h:.4f}\n")  # Registra velocidade máxima convertida para km/h
        else:  # Caso não haja escala disponível
            f.write("Escala física        : não fornecida (velocidades em px/s)\n")  # Registra ausência de calibração física
            f.write("km/h                 : N/A (é preciso saber quantos px = 1 m)\n")  # Explica a limitação para km/h
        f.write("\n")  # Adiciona linha em branco para separar seções

        f.write("--- Arquivos gerados ---\n")  # Seção listando os arquivos produzidos
        if video_out_path:  # Verifica se um vídeo de saída foi gerado
            f.write(f"Vídeo com tracking   : {video_out_path}\n")  # Registra o caminho do vídeo de saída
        else:  # Caso não tenha sido solicitado salvar vídeo
            f.write("Vídeo com tracking   : (não gerado)\n")  # Registra ausência de vídeo

        if csv_path:  # Verifica se o CSV foi gerado
            f.write(f"Trajetória (CSV)     : {csv_path}\n")  # Registra o caminho do CSV
        else:  # Caso CSV tenha sido desativado
            f.write("Trajetória (CSV)     : (não gerado)\n")  # Registra ausência de CSV
        if debug_dir:  # Verifica se houve imagens de debug
            f.write(f"Imagens de debug     : {debug_dir}\n")  # Registra a pasta com imagens de debug
        else:  # Caso debug não tenha sido solicitado
            f.write("Imagens de debug     : (não geradas)\n")  # Registra ausência de imagens debug

        f.write(f"Relatório (TXT)      : {report_path}\n")  # Registra o caminho do próprio relatório

    stats["report_path"] = report_path  # Adiciona caminho do relatório às estatísticas retornadas

    # Registra no log o sucesso da operação
    logger.info(  # Escreve no log uma mensagem resumindo o tracking feito
        f"Tracking concluído: frames={frame_idx}, "
        f"FPS={fps:.2f}, dist_total_px={total_distance_px:.2f}"
    )
    logger.info(f"Relatório salvo em: {report_path}")  # Informa no log onde o relatório foi armazenado

    return stats  # Retorna o dicionário com todas as estatísticas coletadas
