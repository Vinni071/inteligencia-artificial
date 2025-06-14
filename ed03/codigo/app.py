import csv
import math
import random
import time
import os

# --- 1. Funções de Apoio e Leitura de Dados ---

def ler_coordenadas(caminho_arquivo):
    """Lê as coordenadas do arquivo CSV usando a biblioteca padrão 'csv'."""
    coordenadas = []
    with open(caminho_arquivo, 'r', newline='') as f:
        leitor = csv.reader(f)
        next(leitor)  # Pula o cabeçalho (ex: 'x,y')
        for linha in leitor:
            coordenadas.append([float(linha[0]), float(linha[1])])
    return coordenadas

def calcular_matriz_distancias(coordenadas):
    """Calcula e retorna a matriz de distâncias euclidianas usando a biblioteca 'math'."""
    n_cidades = len(coordenadas)
    # Cria uma matriz como uma lista de listas
    matriz = [[0.0] * n_cidades for _ in range(n_cidades)]
    for i in range(n_cidades):
        for j in range(i + 1, n_cidades):
            coord_i = coordenadas[i]
            coord_j = coordenadas[j]
            # Cálculo da distância euclidiana
            dist = math.sqrt((coord_i[0] - coord_j[0])**2 + (coord_i[1] - coord_j[1])**2)
            matriz[i][j] = matriz[j][i] = dist
    return matriz

def calcular_distancia_total(rota, matriz_distancias):
    """Calcula o custo (distância total) de uma rota."""
    distancia = 0
    for i in range(len(rota) - 1):
        distancia += matriz_distancias[rota[i]][rota[i+1]]
    # Adiciona a distância de volta à cidade inicial
    distancia += matriz_distancias[rota[-1]][rota[0]]
    return distancia

# --- 2. Métodos de Inicialização da População ---

def inicializacao_aleatoria(n_individuos, n_cidades):
    """Cria uma população inicial de rotas aleatórias."""
    populacao = []
    cidades = list(range(n_cidades))
    for _ in range(n_individuos):
        rota = random.sample(cidades, n_cidades)
        populacao.append(rota)
    return populacao

def heuristica_vizinho_mais_proximo(matriz_distancias):
    """Gera uma rota usando a heurística do vizinho mais próximo."""
    n_cidades = len(matriz_distancias)
    cidade_inicial = random.randrange(n_cidades)
    rota = [cidade_inicial]
    nao_visitadas = set(range(n_cidades))
    nao_visitadas.remove(cidade_inicial)
    
    cidade_atual = cidade_inicial
    while nao_visitadas:
        # Encontra o vizinho mais próximo da cidade atual
        vizinho_mais_proximo = min(nao_visitadas, key=lambda cidade: matriz_distancias[cidade_atual][cidade])
        nao_visitadas.remove(vizinho_mais_proximo)
        rota.append(vizinho_mais_proximo)
        cidade_atual = vizinho_mais_proximo
    return rota

def inicializacao_heuristica(n_individuos, n_cidades, matriz_distancias):
    """Cria uma população inicial usando a heurística do vizinho mais próximo."""
    populacao = []
    # Metade da população é gerada com a heurística para garantir boas soluções iniciais
    n_heuristicos = n_individuos // 2
    for _ in range(n_heuristicos):
        populacao.append(heuristica_vizinho_mais_proximo(matriz_distancias))
    
    # A outra metade é aleatória para manter a diversidade
    cidades = list(range(n_cidades))
    for _ in range(n_individuos - n_heuristicos):
        rota = random.sample(cidades, n_cidades)
        populacao.append(rota)
        
    return populacao

# --- 3. Operadores Genéticos ---

def selecao_torneio(populacao, fitness, k=3):
    """Seleciona um indivíduo da população usando seleção por torneio."""
    selecionados = random.sample(list(zip(populacao, fitness)), k)
    selecionados.sort(key=lambda x: x[1])
    return selecionados[0][0]

def crossover_ordenado(pai1, pai2):
    """Crossover Ordenado (OX1)."""
    tamanho = len(pai1)
    filho = [None] * tamanho
    inicio, fim = sorted(random.sample(range(tamanho), 2))
    
    filho[inicio:fim] = pai1[inicio:fim]
    genes_pai1 = set(pai1[inicio:fim])
    
    ponteiro_pai2 = 0
    ponteiro_filho = 0
    while None in filho:
        if ponteiro_filho == inicio:
            ponteiro_filho = fim
        if pai2[ponteiro_pai2] not in genes_pai1:
            filho[ponteiro_filho] = pai2[ponteiro_pai2]
            ponteiro_filho += 1
        ponteiro_pai2 += 1
    return filho

def crossover_pmx(parent1, parent2):
    """Partially Mapped Crossover (PMX) - Versão Corrigida."""
    size = len(parent1)
    p1, p2 = list(parent1), list(parent2)
    child = [None] * size

    # 1. Escolher pontos de corte
    start, end = sorted(random.sample(range(size), 2))
    
    # 2. Copiar o segmento de p1 para o filho
    child[start:end] = p1[start:end]
    
    # 3. Lidar com genes do segmento de p2
    for i in range(start, end):
        gene_from_p2 = p2[i]
        
        # Se este gene de p2 não estiver já no segmento do filho
        if gene_from_p2 not in child[start:end]:
            # Encontrar uma posição para ele
            current_pos = i
            gene_to_place = p1[current_pos]
            
            # Seguir a cadeia de mapeamento até que um local vazio seja encontrado
            while True:
                # Encontrar onde o gene_to_place está em p2
                try:
                    temp_pos = p2.index(gene_to_place)
                except ValueError:
                    break

                # Se o local no filho estiver vazio, colocar o gene lá
                if child[temp_pos] is None:
                    child[temp_pos] = gene_from_p2
                    break
                # Se não, esse local faz parte do segmento original, então temos um novo gene para colocar
                else:
                    gene_to_place = p1[temp_pos]

    # 4. Preencher o resto do filho a partir de p2
    for i in range(size):
        if child[i] is None:
            child[i] = p2[i]
            
    return child

def mutacao_troca(rota):
    """Mutação por troca (swap)."""
    idx1, idx2 = random.sample(range(len(rota)), 2)
    rota[idx1], rota[idx2] = rota[idx2], rota[idx1]
    return rota

def mutacao_inversao(rota):
    """Mutação por inversão."""
    inicio, fim = sorted(random.sample(range(len(rota)), 2))
    segmento = rota[inicio:fim]
    segmento.reverse()
    rota[inicio:fim] = segmento
    return rota

# --- 4. Motor Principal do Algoritmo Genético ---

class AlgoritmoGeneticoTSP:
    def __init__(self, matriz_distancias, config):
        self.matriz_distancias = matriz_distancias
        self.n_cidades = len(matriz_distancias)
        self.config = config
        self.metodo_inicializacao = self._selecionar_operador('inicializacao', {'aleatoria': lambda: inicializacao_aleatoria(self.config['n_individuos'], self.n_cidades), 'heuristica': lambda: inicializacao_heuristica(self.config['n_individuos'], self.n_cidades, self.matriz_distancias)})
        self.metodo_crossover = self._selecionar_operador('crossover', {'ordenado': crossover_ordenado, 'pmx': crossover_pmx})
        self.metodo_mutacao = self._selecionar_operador('mutacao', {'troca': mutacao_troca, 'inversao': mutacao_inversao})

    def _selecionar_operador(self, tipo, mapa_operadores):
        nome = self.config[tipo]
        if nome in mapa_operadores:
            return mapa_operadores[nome]
        raise ValueError(f"Método de '{tipo}' desconhecido: {nome}")

    def rodar(self):
        inicio_tempo = time.time()
        populacao = self.metodo_inicializacao()
        melhor_rota_global, melhor_distancia_global = None, float('inf')
        geracoes_sem_melhora, geracao_final = 0, 0
        
        for geracao in range(self.config['max_geracoes']):
            geracao_final = geracao + 1
            fitness_populacao = [calcular_distancia_total(ind, self.matriz_distancias) for ind in populacao]
            
            melhor_distancia_geracao = min(fitness_populacao)
            if melhor_distancia_geracao < melhor_distancia_global:
                melhor_distancia_global = melhor_distancia_geracao
                melhor_rota_global = populacao[fitness_populacao.index(melhor_distancia_geracao)]
                geracoes_sem_melhora = 0
            else:
                geracoes_sem_melhora += 1

            if self.config['criterio_parada'] == 'convergencia' and geracoes_sem_melhora >= self.config['paciencia_convergencia']:
                break
            
            nova_populacao = [melhor_rota_global]  # Elitismo
            while len(nova_populacao) < self.config['n_individuos']:
                pai1 = selecao_torneio(populacao, fitness_populacao)
                pai2 = selecao_torneio(populacao, fitness_populacao)
                filho = self.metodo_crossover(pai1, pai2)
                if random.random() < self.config['taxa_mutacao']:
                    filho = self.metodo_mutacao(filho)
                nova_populacao.append(filho)
            populacao = nova_populacao

        tempo_execucao = time.time() - inicio_tempo
        return melhor_distancia_global, tempo_execucao, geracao_final

# --- 5. Execução dos Experimentos ---

if __name__ == '__main__':
    config_base = {'n_individuos': 100, 'max_geracoes': 500, 'taxa_mutacao': 0.05, 'paciencia_convergencia': 50, 'inicializacao': 'aleatoria', 'crossover': 'ordenado', 'mutacao': 'inversao', 'criterio_parada': 'geracoes'}
    experimentos = []
    for taxa in [0.01, 0.05, 0.15]: experimentos.append(('taxa_mutacao', {**config_base, 'taxa_mutacao': taxa}))
    for init in ['aleatoria', 'heuristica']: experimentos.append(('inicializacao', {**config_base, 'inicializacao': init}))
    for cross in ['ordenado', 'pmx']: experimentos.append(('crossover', {**config_base, 'crossover': cross}))
    for mut in ['troca', 'inversao']: experimentos.append(('mutacao', {**config_base, 'mutacao': mut}))
    for parada in ['geracoes', 'convergencia']: experimentos.append(('criterio_parada', {**config_base, 'criterio_parada': parada}))

    # Define a pasta onde os arquivos CSV devem estar.
    caminho_pasta = 'ed03/codigo'

    # Adiciona diagnósticos para verificar o ambiente de execução.
    print("--- Verificando o ambiente de execução ---")
    print(f"Diretório de trabalho atual: {os.getcwd()}")
    print(f"A verificar a existência da pasta de dados: '{caminho_pasta}'")

    if not os.path.isdir(caminho_pasta):
        print(f"--> ERRO: A pasta '{caminho_pasta}' não foi encontrada.")
        print("--> Por favor, certifique-se de que o script está no diretório correto e que a pasta com os ficheiros .csv existe.")
    else:
        print(f"--> SUCESSO: Pasta '{caminho_pasta}' encontrada.")

    # ATUALIZADO: Lista explícita de arquivos a serem processados.
    arquivos_tsp = [
        os.path.join(caminho_pasta, 'tsp_1.csv'),
        os.path.join(caminho_pasta, 'tsp_2.csv'),
        os.path.join(caminho_pasta, 'tsp_3.csv'),
        os.path.join(caminho_pasta, 'tsp_4.csv'),
        os.path.join(caminho_pasta, 'tsp_5.csv'),
        os.path.join(caminho_pasta, 'tsp_6.csv'),
        os.path.join(caminho_pasta, 'tsp_7.csv'),
        os.path.join(caminho_pasta, 'tsp_8.csv'),
        os.path.join(caminho_pasta, 'tsp_9.csv'),
        os.path.join(caminho_pasta, 'tsp_10.csv')
    ]
    resultados_finais = []
    total_runs = len(arquivos_tsp) * len(experimentos)
    run_count = 0

    print(f"\nIniciando a execução de {total_runs} experimentos...")
    for arquivo in arquivos_tsp:
        # Adiciona prints de diagnóstico dentro do loop
        print(f"\n--- A processar: {arquivo}")
        if not os.path.exists(arquivo):
            print(f"--> AVISO: Ficheiro não encontrado. Verifique se o ficheiro '{os.path.basename(arquivo)}' está dentro da pasta '{caminho_pasta}'.")
            run_count += len(experimentos)
            continue
        
        print("--> Ficheiro encontrado. A iniciar experimentos...")
        coordenadas = ler_coordenadas(arquivo)
        matriz_distancias = calcular_matriz_distancias(coordenadas)
        for nome_experimento, config in experimentos:
            run_count += 1
            ag = AlgoritmoGeneticoTSP(matriz_distancias, config)
            dist, tempo, geracoes = ag.rodar()
            
            nome_base_arquivo = os.path.basename(arquivo)
            resultado = {'experimento': nome_experimento, 'arquivo_tsp': nome_base_arquivo, 'melhor_distancia': dist, 'tempo_execucao_s': tempo, 'geracoes_executadas': geracoes, **config}
            resultados_finais.append(resultado)
            print(f"  ({run_count}/{total_runs}) Concluído: {nome_base_arquivo} / {nome_experimento} / {config[nome_experimento]} -> Dist: {dist:.2f}")

    # --- Salvar Resultados em CSV ---
    if resultados_finais:
        cabecalho = resultados_finais[0].keys()
        with open('resultados_finais.csv', 'w', newline='', encoding='utf-8') as f:
            escritor = csv.DictWriter(f, fieldnames=cabecalho)
            escritor.writeheader()
            escritor.writerows(resultados_finais)
        print("\n--- EXPERIMENTOS CONCLUÍDOS ---")
        print("Resultados salvos em 'resultados_finais.csv'")
    else:
        print("\nNenhum experimento foi executado. Verifique os caminhos dos ficheiros e a configuração.")
