# App Metric 🎯

**App Metric** é uma aplicação desktop desenvolvida em Python para rastreamento de objetos em vídeos (Object Tracking) e análise de métricas de movimento.

O software permite que o usuário selecione um objeto em um vídeo, rastreie sua trajetória automaticamente e gere relatórios detalhados contendo velocidade, distância percorrida e eficiência do movimento.

---

## 🚀 Funcionalidades

- **Interface Gráfica Moderna:** Construída com `customtkinter` para fácil navegação.
- **Rastreamento Robusto:** Utiliza algoritmos do OpenCV (CSRT, KCF) para seguir objetos.
- **Cálculo de Métricas:**
  - Velocidade (pixels/frame, pixels/s).
  - Conversão para unidades reais (m/s, km/h) se a escala for fornecida.
  - Distância total e eficiência da trajetória.
- **Geração de Resultados:**
  - 📹 Vídeo processado com a bounding box e HUD.
  - 📊 Arquivo `.csv` com a trajetória quadro a quadro.
  - 📄 Relatório `.txt` com resumo estatístico.
  - 🖼️ Imagens de Debug (Bordas e detecção de movimento).
- **Logs:** Sistema de logs para monitoramento da execução.

---

## 📂 Estrutura do Projeto

```text
Project/
├── data/
│   ├── raw/          # Coloque seus vídeos originais aqui (.mp4, .avi)
│   └── results/      # Onde os relatórios, vídeos e CSVs são salvos
├── src/
│   ├── core/         # Lógica principal (tracking.py)
│   ├── io/           # Utilitários de entrada/saída (logger, paths)
│   └── ui/           # Interface gráfica (janelas, abas)
├── tests/            # Testes unitários
├── requiriments.txt  # Dependências do projeto
└── Readme.md         # Documentação