#VINICIUS RODRIGUES DA COSTA ED02

import heapq
from collections import deque
import time
import sys

def analisar_labirinto(conteudo):
    labirinto = []
    inicio = None
    fim = None
    linhas = conteudo.split('\n')
    for i in range(1, len(linhas)-1):  # Ignora bordas
        linha = linhas[i]
        linha_processada = []
        for j, caractere in enumerate(linha.strip()):
            if caractere == 'S':
                inicio = (i-1, j)
                linha_processada.append(False)
            elif caractere == 'E':
                fim = (i-1, j)
                linha_processada.append(False)
            elif caractere in [' ', '.', "'"]:  # Caminhos válidos
                linha_processada.append(False)
            else:
                linha_processada.append(True)  # Parede
        labirinto.append(linha_processada)
    return labirinto, inicio, fim

def busca_em_largura(labirinto, inicio, fim):
    fila = deque([(inicio, [inicio])])
    visitados = set()
    while fila:
        (no, caminho) = fila.popleft()
        if no == fim:
            return caminho
        if no in visitados:
            continue
        visitados.add(no)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x, y = no[0] + dx, no[1] + dy
            if 0 <= x < len(labirinto) and 0 <= y < len(labirinto[0]) and not labirinto[x][y]:
                fila.append(((x, y), caminho + [(x, y)]))
    return None

def busca_em_profundidade(labirinto, inicio, fim):
    pilha = [(inicio, [inicio])]
    visitados = set()
    while pilha:
        (no, caminho) = pilha.pop()
        if no == fim:
            return caminho
        if no in visitados:
            continue
        visitados.add(no)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x, y = no[0] + dx, no[1] + dy
            if 0 <= x < len(labirinto) and 0 <= y < len(labirinto[0]) and not labirinto[x][y]:
                pilha.append(((x, y), caminho + [(x, y)]))
    return None

def heuristica(ponto_a, ponto_b):
    return abs(ponto_a[0] - ponto_b[0]) + abs(ponto_a[1] - ponto_b[1])

def busca_gulosa(labirinto, inicio, fim):
    heap = []
    heapq.heappush(heap, (heuristica(inicio, fim), inicio, [inicio]))
    visitados = set()
    while heap:
        h, no, caminho = heapq.heappop(heap)
        if no == fim:
            return caminho
        if no in visitados:
            continue
        visitados.add(no)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x, y = no[0] + dx, no[1] + dy
            if 0 <= x < len(labirinto) and 0 <= y < len(labirinto[0]) and not labirinto[x][y]:
                heapq.heappush(heap, (heuristica((x,y), fim), (x,y), caminho + [(x,y)]))
    return None

def busca_heuristica(labirinto, inicio, fim):
    heap = []
    heapq.heappush(heap, (0 + heuristica(inicio, fim), 0, inicio, [inicio]))
    visitados = {inicio: 0}
    while heap:
        f, g, no, caminho = heapq.heappop(heap)
        if no == fim:
            return caminho
        if g > visitados.get(no, float('inf')):
            continue
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x, y = no[0] + dx, no[1] + dy
            if 0 <= x < len(labirinto) and 0 <= y < len(labirinto[0]) and not labirinto[x][y]:
                novo_g = g + 1
                if novo_g < visitados.get((x,y), float('inf')):
                    visitados[(x,y)] = novo_g
                    heapq.heappush(heap, (novo_g + heuristica((x,y), fim), novo_g, (x,y), caminho + [(x,y)]))
    return None

# Exemplo de uso:
if __name__ == "__main__":
    arquivos_labirinto = ['ed02/ed02-labirinto/maze1.txt', 'ed02/ed02-labirinto/maze2.txt', 'ed02/ed02-labirinto/maze3.txt', 'ed02/ed02-labirinto/maze4.txt', 'ed02/ed02-labirinto/maze5.txt', 'ed02/ed02-labirinto/maze6.txt']
    for arquivo in arquivos_labirinto:
        with open(arquivo, 'r') as f:
            conteudo = f.read()
        labirinto, inicio, fim = analisar_labirinto(conteudo)
        if not inicio or not fim:
            print(f"{arquivo}: Início/Fim não encontrado.")
            continue
        
        print(f"\nTestando arquivo {arquivo}:")
        for algoritmo in [busca_em_largura, busca_em_profundidade, busca_gulosa, busca_heuristica]:
            tempo_inicio = time.time()
            caminho = algoritmo(labirinto, inicio, fim)
            decorrido = time.time() - tempo_inicio
            uso_memoria = sys.getsizeof(caminho) if caminho else 0
            print(f"{algoritmo.__name__}: Tempo={decorrido:.2f}s, Memória={uso_memoria} bytes, Caminho={len(caminho) if caminho else 'N/A'}")