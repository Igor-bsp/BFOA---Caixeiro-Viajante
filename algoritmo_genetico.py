import os
import random
import math
import copy

# =============================================================================
# 1. CARREGAMENTO DE DADOS E UTILITÁRIOS (Idêntico ao BFOA)
# =============================================================================

def ler_instancia(caminho_arquivo):
    """Lê o arquivo de entrada contendo as coordenadas das cidades."""
    cidades = []
    with open(caminho_arquivo, 'r') as f:
        linhas = [linha.strip() for list_l in [f.readlines()] for linha in list_l if linha.strip()]
    if not linhas:
        return cidades
    
    for i, linha in enumerate(linhas[1:], start=2):
        partes = linha.split()
        if not partes:
            continue
        try:
            if len(partes) >= 2:
                x = float(partes[0])
                y = float(partes[1])
                cidades.append((x, y))
        except ValueError:
            continue
    return cidades

def calcular_matriz_distancias(cidades):
    n = len(cidades)
    matriz = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                x1, y1 = cidades[i]
                x2, y2 = cidades[j]
                matriz[i][j] = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return matriz

def calcular_custo_rota(rota, matriz_distancias):
    distancia_total = 0.0
    num_cidades = len(rota)
    for i in range(num_cidades):
        cidade_atual = rota[i]
        proxima_cidade = rota[(i + 1) % num_cidades]
        distancia_total += matriz_distancias[cidade_atual][proxima_cidade]
    return distancia_total

# =============================================================================
# 2. IMPLEMENTAÇÃO DO ALGORITMO GENÉTICO (GA)
# =============================================================================

class AlgoritmoGenetico_TSP:
    def __init__(self, cidades, tam_populacao=100, geracoes=300, tx_cruzamento=0.8, tx_mutacao=0.1, tam_torneio=5):
        self.cidades = cidades
        self.num_cidades = len(cidades)
        self.matriz_distancias = calcular_matriz_distancias(cidades)
        
        self.tam_populacao = tam_populacao
        self.geracoes = geracoes
        self.tx_cruzamento = tx_cruzamento
        self.tx_mutacao = tx_mutacao
        self.tam_torneio = tam_torneio
        
        self.populacao = []
        self.melhor_rota = None
        self.melhor_custo = float('inf')

    def inicializar_populacao(self):
        """Gera cromossomos (rotas) aleatórios."""
        self.populacao = []
        for _ in range(self.tam_populacao):
            cromossomo = list(range(self.num_cidades))
            random.shuffle(cromossomo)
            self.populacao.append(cromossomo)

    def selecao_torneio(self):
        """Seleciona um indivíduo usando o método do torneio."""
        competidores = random.sample(self.populacao, self.tam_torneio)
        melhor_competidor = min(competidores, key=lambda rota: calcular_custo_rota(rota, self.matriz_distancias))
        return melhor_competidor

    def cruzamento_ox(self, pai1, pai2):
        """Operador de Cruzamento Ordenado (Ordered Crossover - OX)."""
        if random.random() > self.tx_cruzamento:
            return copy.deepcopy(pai1), copy.deepcopy(pai2)

        ponto1, ponto2 = sorted(random.sample(range(self.num_cidades), 2))
        
        def gerar_filho(p1, p2):
            filho = [None] * self.num_cidades
            # Copia o segmento do primeiro pai
            filho[ponto1:ponto2+1] = p1[ponto1:ponto2+1]
            
            # Preenche o restante com os genes do pai 2 na ordem correta
            pos_filho = (ponto2 + 1) % self.num_cidades
            pos_pai2 = (ponto2 + 1) % self.num_cidades
            
            while None in filho:
                gene_candidato = p2[pos_pai2]
                if gene_candidato not in filho:
                    filho[pos_filho] = gene_candidato
                    pos_filho = (pos_filho + 1) % self.num_cidades
                pos_pai2 = (pos_pai2 + 1) % self.num_cidades
            return filho

        filho1 = gerar_filho(pai1, pai2)
        filho2 = gerar_filho(pai2, pai1)
        return filho1, filho2

    def mutacao_swap(self, cromossomo):
        """Operador de Mutação por Troca (Swap Mutation)."""
        if random.random() < self.tx_mutacao:
            idx1, idx2 = random.sample(range(self.num_cidades), 2)
            cromossomo[idx1], cromossomo[idx2] = cromossomo[idx2], cromossomo[idx1]
        return cromossomo

    def executar(self):
        self.inicializar_populacao()
        print(f"[*] Iniciando Algoritmo Genético ({self.geracoes} gerações)...")
        
        for g in range(self.geracoes):
            nova_populacao = []
            
            # Elitismo: Mantém os 2 melhores da geração anterior intactos
            self.populacao.sort(key=lambda rota: calcular_custo_rota(rota, self.matriz_distancias))
            nova_populacao.append(copy.deepcopy(self.populacao[0]))
            nova_populacao.append(copy.deepcopy(self.populacao[1]))
            
            # Avalia se encontramos o melhor global
            custo_atual_melhor = calcular_custo_rota(self.populacao[0], self.matriz_distancias)
            if custo_atual_melhor < self.melhor_custo:
                self.melhor_custo = custo_atual_melhor
                self.melhor_rota = copy.deepcopy(self.populacao[0])

            # Preenche o resto da população
            while len(nova_populacao) < self.tam_populacao:
                pai1 = self.selecao_torneio()
                pai2 = self.selecao_torneio()
                
                filho1, filho2 = self.cruzamento_ox(pai1, pai2)
                
                filho1 = self.mutacao_swap(filho1)
                filho2 = self.mutacao_swap(filho2)
                
                nova_populacao.append(filho1)
                if len(nova_populacao) < self.tam_populacao:
                    nova_populacao.append(filho2)
            
            self.populacao = nova_populacao
            
            if (g + 1) % 50 == 0 or g == 0:
                print(f" > Geração {g+1}/{self.geracoes} concluída. Melhor Distância: {self.melhor_custo:.4f}")
                
        return self.melhor_rota, self.melhor_custo

# =============================================================================
# 3. EXECUÇÃO PRINCIPAL
# =============================================================================

if __name__ == '__main__':
    caminho_instancia = "entrada.txt" # Pode alterar para "entrada_grande.txt"
    
    if not os.path.exists(caminho_instancia):
        print(f"Erro: Arquivo '{caminho_instancia}' não encontrado.")
    else:
        cidades = ler_instancia(caminho_instancia)
        
        # Configuração do GA
        ga = AlgoritmoGenetico_TSP(
            cidades=cidades,
            tam_populacao=100,
            geracoes=300,
            tx_cruzamento=0.85,
            tx_mutacao=0.15,
            tam_torneio=5
        )
        
        melhor_rota, melhor_custo = ga.executar()
        
        print("\n================ RESULTADO FINAL (GA) ================")
        print(f"Melhor Rota Encontrada: {melhor_rota}")
        print(f"Distância Total Calculada: {melhor_custo:.4f}")