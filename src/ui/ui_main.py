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
Este projeto desenvolve um programa capaz de detectar movimento em vídeos utilizando um filtro espacial Sobel. 
O sistema permite que o usuário selecione um vídeo, extrai seus quadros e aplica o filtro para realçar bordas e variações de intensidade. 
A partir dessas informações, o programa identifica regiões em movimento e extrai dados relevantes, como tempo decorrido, 
intensidade do movimento e limites aproximados do objeto detectado. 
O trabalho demonstra a aplicação prática do processamento digital de imagens para análise de movimento utilizando filtros espaciais.
'''
# ################


from ui_init import AppMetricApp

if __name__ == "__main__":
    app = AppMetricApp()