import os
import random
import math
import copy
import time
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Pool

# =============================================================================
# UTILITÁRIOS COMUNS
# =============================================================================

def ler_instancia(arquivo):
    """Lê coordenadas das cidades. Formato: primeira linha = número de cidades,
    depois cada linha: x y"""
    with open(arquivo, 'r') as f:
        linhas = [l.strip() for l in f if l.strip()]
    if not linhas:
        return []
    try:
        num_cidades = int(linhas[0])
    except:
        num_cidades = len(linhas) - 1
    cidades = []
    for linha in linhas[1:]:
        partes = linha.split()
        if len(partes) >= 2:
            x, y = float(partes[0]), float(partes[1])
            cidades.append((x, y))
    return cidades[:num_cidades]

def calcular_matriz_distancias(cidades):
    n = len(cidades)
    matriz = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = cidades[i]
        for j in range(n):
            if i == j:
                continue
            xj, yj = cidades[j]
            matriz[i][j] = math.hypot(xi - xj, yi - yj)
    return matriz

def calcular_custo_rota(rota, matriz):
    custo = 0.0
    n = len(rota)
    for i in range(n):
        custo += matriz[rota[i]][rota[(i+1) % n]]
    return custo

# =============================================================================
# BFOA CORRIGIDO
# =============================================================================

class Bacteria:
    def __init__(self, rota, custo):
        self.rota = rota
        self.custo = custo
        self.saude = 0.0

def _avaliar_quimiotaxia(args):
    bacteria, matriz, Nc, Ns = args
    n = len(bacteria.rota)
    for _ in range(Nc):
        i1, i2 = sorted(random.sample(range(n), 2))
        nova_rota = bacteria.rota[:]
        nova_rota[i1:i2+1] = reversed(nova_rota[i1:i2+1])
        novo_custo = calcular_custo_rota(nova_rota, matriz)

        if novo_custo < bacteria.custo:
            bacteria.rota = nova_rota
            bacteria.custo = novo_custo
            bacteria.saude += bacteria.custo

            passos = 1
            while passos < Ns:
                prox_rota = bacteria.rota[:]
                prox_rota[i1:i2+1] = reversed(prox_rota[i1:i2+1])
                prox_custo = calcular_custo_rota(prox_rota, matriz)
                if prox_custo < bacteria.custo:
                    bacteria.rota = prox_rota
                    bacteria.custo = prox_custo
                    bacteria.saude += bacteria.custo
                    passos += 1
                else:
                    break
        else:
            bacteria.saude += bacteria.custo
    return bacteria

class BFOA_TSP:
    def __init__(self, cidades, s=60, Nc=20, Ns=5, Nre=6, Ned=5, Ped=0.25):
        self.cidades = cidades
        self.num_cidades = len(cidades)
        self.matriz = calcular_matriz_distancias(cidades)
        self.s = s
        self.Nc = Nc
        self.Ns = Ns
        self.Nre = Nre
        self.Ned = Ned
        self.Ped = Ped
        self.populacao = []
        self.melhor_bacteria = None
        self.historico_melhores = []

    def inicializar(self):
        self.populacao = []
        for _ in range(self.s):
            rota = list(range(self.num_cidades))
            random.shuffle(rota)
            custo = calcular_custo_rota(rota, self.matriz)
            b = Bacteria(rota, custo)
            self.populacao.append(b)
        self.melhor_bacteria = copy.deepcopy(min(self.populacao, key=lambda b: b.custo))

    def executar(self):
        self.inicializar()
        print("[BFOA] Iniciando...")
        for l in range(self.Ned):
            for _ in range(self.Nre):
                for b in self.populacao:
                    b.saude = 0.0
                args = [(b, self.matriz, self.Nc, self.Ns) for b in self.populacao]
                with Pool(os.cpu_count()) as pool:
                    self.populacao = pool.map(_avaliar_quimiotaxia, args)
                for b in self.populacao:
                    if b.custo < self.melhor_bacteria.custo:
                        self.melhor_bacteria = copy.deepcopy(b)
                self.populacao.sort(key=lambda b: b.saude)
                sobreviventes = self.populacao[:self.s // 2]
                self.populacao = sobreviventes + copy.deepcopy(sobreviventes)

            for i in range(len(self.populacao)):
                if random.random() < self.Ped:
                    nova_rota = list(range(self.num_cidades))
                    random.shuffle(nova_rota)
                    self.populacao[i].rota = nova_rota
                    self.populacao[i].custo = calcular_custo_rota(nova_rota, self.matriz)
                    self.populacao[i].saude = 0.0
                    if self.populacao[i].custo < self.melhor_bacteria.custo:
                        self.melhor_bacteria = copy.deepcopy(self.populacao[i])

            self.historico_melhores.append(self.melhor_bacteria.custo)
            print(f"  Ciclo Ned {l+1}/{self.Ned} -> Melhor custo: {self.melhor_bacteria.custo:.4f}")

        return self.melhor_bacteria, self.historico_melhores

# =============================================================================
# ALGORITMO GENÉTICO (GA)
# =============================================================================

class AlgoritmoGenetico_TSP:
    def __init__(self, cidades, tam_pop=100, geracoes=300, tx_cruz=0.85, tx_mut=0.15, tam_torneio=5):
        self.cidades = cidades
        self.num_cidades = len(cidades)
        self.matriz = calcular_matriz_distancias(cidades)
        self.tam_pop = tam_pop
        self.geracoes = geracoes
        self.tx_cruz = tx_cruz
        self.tx_mut = tx_mut
        self.tam_torneio = tam_torneio
        self.populacao = []
        self.melhor_rota = None
        self.melhor_custo = float('inf')
        self.historico_melhores = []

    def inicializar(self):
        self.populacao = [list(range(self.num_cidades)) for _ in range(self.tam_pop)]
        for cromo in self.populacao:
            random.shuffle(cromo)
        self.melhor_custo = float('inf')
        self.melhor_rota = None

    def avaliar(self, rota):
        return calcular_custo_rota(rota, self.matriz)

    def selecao_torneio(self):
        competidores = random.sample(self.populacao, self.tam_torneio)
        return min(competidores, key=self.avaliar)

    def cruzamento_ox(self, pai1, pai2):
        if random.random() > self.tx_cruz:
            return pai1[:], pai2[:]
        n = self.num_cidades
        p1, p2 = sorted(random.sample(range(n), 2))
        filho1 = [None]*n
        filho2 = [None]*n
        filho1[p1:p2+1] = pai1[p1:p2+1]
        filho2[p1:p2+1] = pai2[p1:p2+1]

        def completar(filho, doador, p1, p2):
            pos = (p2+1) % n
            for i in range(n):
                gene = doador[(p2+1+i) % n]
                if gene not in filho:
                    filho[pos] = gene
                    pos = (pos+1) % n
        completar(filho1, pai2, p1, p2)
        completar(filho2, pai1, p1, p2)
        return filho1, filho2

    def mutacao_swap(self, cromo):
        if random.random() < self.tx_mut:
            i, j = random.sample(range(self.num_cidades), 2)
            cromo[i], cromo[j] = cromo[j], cromo[i]
        return cromo

    def executar(self):
        self.inicializar()
        print("[GA] Iniciando...")
        for g in range(self.geracoes):
            avaliados = [(self.avaliar(c), c) for c in self.populacao]
            avaliados.sort(key=lambda x: x[0])
            melhor_atual = avaliados[0][0]
            if melhor_atual < self.melhor_custo:
                self.melhor_custo = melhor_atual
                self.melhor_rota = copy.deepcopy(avaliados[0][1])
            self.historico_melhores.append(self.melhor_custo)

            nova_pop = [copy.deepcopy(avaliados[0][1]), copy.deepcopy(avaliados[1][1])]
            while len(nova_pop) < self.tam_pop:
                pai1 = self.selecao_torneio()
                pai2 = self.selecao_torneio()
                f1, f2 = self.cruzamento_ox(pai1, pai2)
                f1 = self.mutacao_swap(f1)
                f2 = self.mutacao_swap(f2)
                nova_pop.append(f1)
                if len(nova_pop) < self.tam_pop:
                    nova_pop.append(f2)
            self.populacao = nova_pop

            if (g+1) % 50 == 0 or g == 0:
                print(f"  Geração {g+1}/{self.geracoes} -> Melhor custo: {self.melhor_custo:.4f}")

        return self.melhor_rota, self.melhor_custo, self.historico_melhores

# =============================================================================
# EXECUÇÃO COMPARATIVA E GRÁFICOS SEPARADOS
# =============================================================================

def executar_comparacao(arquivo_instancia="entrada_maior.txt", num_execucoes=10):
    """Roda ambos os algoritmos, coleta dados e gera gráficos separados."""
    if not os.path.exists(arquivo_instancia):
        print(f"Erro: arquivo {arquivo_instancia} não encontrado!")
        return

    cidades = ler_instancia(arquivo_instancia)
    print(f"Instância carregada: {len(cidades)} cidades.")
    print(f"Executando {num_execucoes} execuções de cada algoritmo. Isso pode levar alguns minutos...\n")

    melhores_ga = []
    melhores_bfoa = []
    historico_ga = []
    historico_bfoa = []
    tempos_ga = []
    tempos_bfoa = []

    for execucao in range(num_execucoes):
        print(f"\n*** Execução {execucao+1}/{num_execucoes} ***")
        # GA
        random.seed(execucao)
        ga = AlgoritmoGenetico_TSP(cidades, tam_pop=100, geracoes=300)
        inicio = time.time()
        _, custo_ga, hist_ga = ga.executar()
        tempo_ga = time.time() - inicio
        melhores_ga.append(custo_ga)
        historico_ga.append(hist_ga)
        tempos_ga.append(tempo_ga)

        # BFOA
        random.seed(execucao)
        bfoa = BFOA_TSP(cidades, s=60, Nc=20, Ns=5, Nre=6, Ned=5, Ped=0.25)
        inicio = time.time()
        _, hist_bfoa = bfoa.executar()
        tempo_bfoa = time.time() - inicio
        melhores_bfoa.append(bfoa.melhor_bacteria.custo)
        historico_bfoa.append(hist_bfoa)
        tempos_bfoa.append(tempo_bfoa)

        print(f"Resultados execução {execucao+1}:")
        print(f"  GA   -> custo: {custo_ga:.4f}  tempo: {tempo_ga:.2f}s")
        print(f"  BFOA -> custo: {bfoa.melhor_bacteria.custo:.4f}  tempo: {tempo_bfoa:.2f}s")

    # Estatísticas finais
    print("\n" + "="*60)
    print("COMPARAÇÃO FINAL (baseado em {} execuções)".format(num_execucoes))
    print(f"GA   : melhor={min(melhores_ga):.4f}  médio={np.mean(melhores_ga):.4f} ± {np.std(melhores_ga):.4f}  tempo médio={np.mean(tempos_ga):.2f}s")
    print(f"BFOA : melhor={min(melhores_bfoa):.4f}  médio={np.mean(melhores_bfoa):.4f} ± {np.std(melhores_bfoa):.4f}  tempo médio={np.mean(tempos_bfoa):.2f}s")
    print("="*60)

    # Salvar dados em CSV
    with open("resultados_comparacao.csv", "w") as f:
        f.write("execucao,GA_custo,BFOA_custo,GA_tempo,BFOA_tempo\n")
        for i in range(num_execucoes):
            f.write(f"{i+1},{melhores_ga[i]:.4f},{melhores_bfoa[i]:.4f},{tempos_ga[i]:.2f},{tempos_bfoa[i]:.2f}\n")
    print("\nDados salvos em 'resultados_comparacao.csv'")

    # Gráfico 1: Curvas de convergência (última execução)
    plt.figure(figsize=(10,6))
    plt.plot(historico_ga[-1], label="GA", color="blue", linewidth=2)
    plt.plot(historico_bfoa[-1], label="BFOA", color="red", linewidth=2)
    plt.xlabel("Iterações (Geração para GA / Ciclo Ned para BFOA)", fontsize=12)
    plt.ylabel("Melhor distância encontrada", fontsize=12)
    plt.title("Curva de Convergência - Melhor Execução", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("convergencia.png", dpi=150)
    print("Gráfico de convergência salvo como 'convergencia.png'")
    plt.close()

    # Gráfico 2: Boxplot comparativo
    plt.figure(figsize=(8,6))
    dados = [melhores_ga, melhores_bfoa]
    bp = plt.boxplot(dados, labels=["GA", "BFOA"], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    plt.ylabel("Melhor distância", fontsize=12)
    plt.title(f"Distribuição dos Melhores Custos ({num_execucoes} execuções)", fontsize=14)
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig("boxplot.png", dpi=150)
    print("Boxplot salvo como 'boxplot.png'")
    plt.close()

    print("\nTodos os gráficos e dados foram gerados com sucesso!")

if __name__ == "__main__":
    # Ajuste o número de execuções conforme necessário (10 é um bom compromisso)
    executar_comparacao("entrada_maior.txt", num_execucoes=90)