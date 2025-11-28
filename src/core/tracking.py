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


import os
import csv
import math
import cv2
import numpy as np
from src.io.logger import get_app_logger
from datetime import datetime
from typing import List, Tuple, Dict, Optional

logger = get_app_logger("tracking")

def _create_tracker(tracker_type: str = "CSRT"):

    t = tracker_type.upper()

    if t == "CSRT":
        if hasattr(cv2, "TrackerCSRT_create"):
            return cv2.TrackerCSRT_create()
        if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
            return cv2.legacy.TrackerCSRT_create()
    elif t == "KCF":
        if hasattr(cv2, "TrackerKCF_create"):
            return cv2.TrackerKCF_create()
        if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerKCF_create"):
            return cv2.legacy.TrackerKCF_create()

    raise RuntimeError(
        f"Não foi possível criar o tracker '{tracker_type}'. "
        "Instale 'opencv-contrib-python'."
    )

def track_single_object(
    video_path: str,
    output_dir: str,
    tracker_type: str = "CSRT",
    save_video: bool = True,
    save_csv: bool = False,
    pixels_per_meter: Optional[float] = None,
    save_debug_images: bool = True,

) -> Dict:

    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Não foi possível abrir o vídeo: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    max_disp_w = 960
    max_disp_h = 540
    scale = min(max_disp_w / width, max_disp_h / height, 1.0)  

    disp_w = int(width * scale)
    disp_h = int(height * scale)

    ret, frame = cap.read()
    if not ret or frame is None:
        cap.release()
        raise RuntimeError("Não foi possível ler o primeiro frame do vídeo.")

    if scale < 1.0:
        frame_disp = cv2.resize(frame, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
    else:
        frame_disp = frame.copy()

    roi_scaled = cv2.selectROI(
        "Selecione o objeto (ENTER/ESP para confirmar)",
        frame_disp,
        fromCenter=False,
        showCrosshair=True,
    )
    cv2.destroyWindow("Selecione o objeto (ENTER/ESP para confirmar)")

    if roi_scaled == (0, 0, 0, 0):
        cap.release()
        raise RuntimeError("ROI inválida (talvez o usuário cancelou).")

    x_s, y_s, w_s, h_s = roi_scaled
    x = int(x_s / scale)
    y = int(y_s / scale)
    w = int(w_s / scale)
    h = int(h_s / scale)
    roi = (x, y, w, h)
    initial_box = roi  

    tracker = _create_tracker(tracker_type)
    tracker.init(frame, roi)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    debug_dir = None
    if save_debug_images:
        debug_dir = os.path.join(output_dir, f"{base_name}_debug_{timestamp}")
        os.makedirs(debug_dir, exist_ok=True)
    
    logger.info(f"Iniciando tracking: vídeo={video_path}, tracker={tracker_type}")

    video_out_path: Optional[str] = None
    writer = None
    if save_video:
        video_filename = f"{base_name}_tracking_{timestamp}.mp4"
        video_out_path = os.path.join(output_dir, video_filename)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            video_out_path,
            fourcc,
            fps if fps > 0 else 30.0,
            (width, height),
        )

    trajectory: List[Dict] = []
    prev_center: Optional[Tuple[float, float]] = None
    speeds_px: List[float] = []
    total_distance_px = 0.0
    frame_idx = 0
    success_frames = 0

    prev_gray: Optional[np.ndarray] = None
    debug_indices = set()
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if save_debug_images and total_frames > 0:
        debug_indices.update(
            {
                0,
                max(0, total_frames // 4),
                max(0, total_frames // 2),
                max(0, 3 * total_frames // 4),
                max(0, total_frames - 1),
            }
        )

    cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Tracking", disp_w, disp_h)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        success, box = tracker.update(frame)

        if success:
            success_frames += 1
            x, y, w, h = [int(v) for v in box]
            cx = x + w / 2.0
            cy = y + h / 2.0

            speed_px = 0.0
            if prev_center is not None:
                dx = cx - prev_center[0]
                dy = cy - prev_center[1]
                speed_px = float(math.hypot(dx, dy))
                speeds_px.append(speed_px)
                total_distance_px += speed_px

            prev_center = (cx, cy)

            trajectory.append(
                {
                    "frame": frame_idx,
                    "x": cx,
                    "y": cy,
                    "speed_px_per_frame": speed_px,
                }
            )

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (int(cx), int(cy)), 4, (0, 0, 255), -1)

            speed_px_s = speed_px * fps if fps > 0 else 0.0
            hud_lines = [
                f"Frame: {frame_idx}",
                f"Vel: {speed_px:.2f} px/frame  ({speed_px_s:.2f} px/s)",
            ]
            y0 = 25
            for i, text in enumerate(hud_lines):
                cv2.putText(
                    frame,
                    text,
                    (10, y0 + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )
        else:
            cv2.putText(
                frame,
                "Tracking perdido",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
        if save_debug_images and debug_dir is not None and (frame_idx in debug_indices):
            edges = cv2.Canny(gray, 100, 200)
            edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                diff_norm = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
            else:
                diff_norm = np.zeros_like(gray)
            diff_bgr = cv2.cvtColor(diff_norm, cv2.COLOR_GRAY2BGR)

            panel = np.hstack([frame, edges_bgr, diff_bgr])
            
            txt = f"frame={frame_idx} | vel={speed_px:.2f}"
            cv2.putText(panel, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            debug_name = os.path.join(debug_dir, f"debug_frame_{frame_idx:05d}.png")
            cv2.imwrite(debug_name, panel)
        
        prev_gray = gray

        if writer is not None:
            writer.write(frame)

        if scale < 1.0:
            frame_disp = cv2.resize(frame, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
        else:
            frame_disp = frame

        cv2.imshow("Tracking", frame_disp)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

        if cv2.getWindowProperty("Tracking", cv2.WND_PROP_VISIBLE) < 1:
            break

        frame_idx += 1

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()

    mean_speed_px = float(np.mean(speeds_px)) if speeds_px else 0.0
    max_speed_px = float(np.max(speeds_px)) if speeds_px else 0.0

    if fps > 0:
        mean_speed_px_per_s = mean_speed_px * fps
        max_speed_px_per_s = max_speed_px * fps
        duracao_segundos = frame_idx / fps
    else:
        mean_speed_px_per_s = 0.0
        max_speed_px_per_s = 0.0
        duracao_segundos = 0.0

    straight_distance_px = 0.0
    path_efficiency = 0.0
    if len(trajectory) >= 2:
        x0, y0 = trajectory[0]["x"], trajectory[0]["y"]
        x1, y1 = trajectory[-1]["x"], trajectory[-1]["y"]
        straight_distance_px = float(math.hypot(x1 - x0, y1 - y0))
        if total_distance_px > 0:
            path_efficiency = straight_distance_px / total_distance_px

    success_rate = (success_frames / frame_idx) if frame_idx > 0 else 0.0

    mean_speed_m_s = None
    max_speed_m_s = None
    mean_speed_km_h = None
    max_speed_km_h = None

    if pixels_per_meter and pixels_per_meter > 0 and fps > 0:
        mean_speed_m_s = mean_speed_px_per_s / pixels_per_meter
        max_speed_m_s = max_speed_px_per_s / pixels_per_meter
        mean_speed_km_h = mean_speed_m_s * 3.6
        max_speed_km_h = max_speed_m_s * 3.6

    stats = {
        "video_input": video_path,
        "tracker_type": tracker_type,
        "num_frames": frame_idx,
        "fps": fps,
        "duracao_segundos": duracao_segundos,
        "frame_width": width,
        "frame_height": height,
        "initial_box": initial_box,
        "mean_speed_px": mean_speed_px,
        "max_speed_px": max_speed_px,
        "mean_speed_px_per_s": mean_speed_px_per_s,
        "max_speed_px_per_s": max_speed_px_per_s,
        "total_distance_px": total_distance_px,
        "straight_distance_px": straight_distance_px,
        "path_efficiency": path_efficiency,
        "success_frames": success_frames,
        "success_rate": success_rate,
        "mean_speed_m_s": mean_speed_m_s,
        "max_speed_m_s": max_speed_m_s,
        "mean_speed_km_h": mean_speed_km_h,
        "max_speed_km_h": max_speed_km_h,
        "trajectory": trajectory,
        "video_output": video_out_path,
        "debug_dir": debug_dir,
    }

    csv_path = None
    if save_csv:
        csv_filename = f"{base_name}_trajectory_{timestamp}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer_csv = csv.writer(f, delimiter=";")
            writer_csv.writerow(["frame", "x", "y", "speed_px_per_frame"])
            for p in trajectory:
                writer_csv.writerow(
                    [
                        p["frame"],
                        f"{p['x']:.3f}",
                        f"{p['y']:.3f}",
                        f"{p['speed_px_per_frame']:.3f}",
                    ]
                )
        stats["csv_output"] = csv_path
    
    report_filename = f"{base_name}_relatorio_{timestamp}.txt"
    report_path = os.path.join(output_dir, report_filename)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== Relatório de Tracking de Objeto ===\n\n")
        f.write(f"Data/Hora da análise : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Vídeo de entrada     : {video_path}\n")
        f.write(f"Tracker utilizado    : {tracker_type}\n\n")

        f.write("--- Informações do vídeo ---\n")
        f.write(f"Resolução            : {width} x {height}\n")
        f.write(f"FPS (arquivo)        : {fps:.2f}\n")
        f.write(f"Frames processados   : {frame_idx}\n")
        f.write(f"Duração aprox. (s)   : {duracao_segundos:.2f}\n\n")

        f.write("--- Bounding box inicial ---\n")
        bx, by, bw, bh = initial_box
        f.write(f"Posição (x, y)       : ({bx}, {by})\n")
        f.write(f"Tamanho (w, h)       : {bw} x {bh} px\n\n")

        f.write("--- Qualidade do tracking ---\n")
        f.write(f"Frames com sucesso   : {success_frames}\n")
        f.write(f"Taxa de sucesso      : {success_rate*100:.2f} %\n\n")

        f.write("--- Métricas de movimento (em pixels) ---\n")
        f.write(f"Vel. média (px/frame): {mean_speed_px:.4f}\n")
        f.write(f"Vel. máx.  (px/frame): {max_speed_px:.4f}\n")
        f.write(f"Vel. média (px/s)    : {mean_speed_px_per_s:.4f}\n")
        f.write(f"Vel. máx.  (px/s)    : {max_speed_px_per_s:.4f}\n")
        f.write(f"Dist. total (px)     : {total_distance_px:.4f}\n")
        f.write(f"Dist. reta (px)      : {straight_distance_px:.4f}\n")
        f.write(f"Eficiência trajetória: {path_efficiency*100:.2f} %\n\n")

        f.write("--- Métricas físicas (se escala for fornecida) ---\n")
        if pixels_per_meter and pixels_per_meter > 0 and fps > 0:
            f.write(f"Escala utilizada     : {pixels_per_meter} px ≈ 1 m\n")
            f.write(f"Vel. média (m/s)     : {mean_speed_m_s:.4f}\n")
            f.write(f"Vel. máx.  (m/s)     : {max_speed_m_s:.4f}\n")
            f.write(f"Vel. média (km/h)    : {mean_speed_km_h:.4f}\n")
            f.write(f"Vel. máx.  (km/h)    : {max_speed_km_h:.4f}\n")
        else:
            f.write("Escala física        : não fornecida (velocidades em px/s)\n")
            f.write("km/h                 : N/A (é preciso saber quantos px = 1 m)\n")
        f.write("\n")

        f.write("--- Arquivos gerados ---\n")
        if video_out_path:
            f.write(f"Vídeo com tracking   : {video_out_path}\n")
        else:
            f.write("Vídeo com tracking   : (não gerado)\n")

        if csv_path:
            f.write(f"Trajetória (CSV)     : {csv_path}\n")
        else:
            f.write("Trajetória (CSV)     : (não gerado)\n")
        if debug_dir:
            f.write(f"Imagens de debug     : {debug_dir}\n")
        else:
            f.write("Imagens de debug     : (não geradas)\n")

        f.write(f"Relatório (TXT)      : {report_path}\n")

    stats["report_path"] = report_path

    logger.info(
    f"Tracking concluído: frames={frame_idx}, "
    f"FPS={fps:.2f}, dist_total_px={total_distance_px:.2f}"
    )
    logger.info(f"Relatório salvo em: {report_path}")

    return stats
