import os
import random
import math
import copy
from multiprocessing import Pool

# =============================================================================
# CARREGAMENTO DE DADOS E UTILITÁRIOS
# =============================================================================

def ler_instancia(arq_entrada):
  cidades = []
  with open(arq_entrada, 'r') as f:
    linhas = f.readlines()

    if not linhas:
      print("[-] Erro: O arquivo de entrada esta totalmente vazio.")
      return cidades
    
    linhas_limpas = [l.strip() for l in linhas if l.strip()]

    try:
      num_cidades = int(linhas_limpas[0])

    except (ValueError, IndexError):
      print(f"[-] Erro critico: A primeira linha do arquivo não é um numero inteiro valido! Conteudo: '{linhas_limpas[0]}'")
      return cidades
    
    for i, linha in enumerate(linhas_limpas[1:], start=2):
      partes = linha.split()

      if not partes: 
        continue
      try:
        if len(partes) >= 2:
          x = float(partes[0])
          y = float(partes[1])
          cidades.append((x, y))
        else:
          print(f"[-] Aviso: Linha {i} ignorada por não conter X e Y completos: '{linhas}'")

      except ValueError as e:
        print(f"[!] Erro de conversão na linha {i}: Não foi possivel converter para um numero.")
        print(f"    Conteudo real da linha: '{linha}' | Pares detectadas: {partes}")

  return cidades

def calcular_matriz_distancias(cidades):
  num_cidades = len(cidades)
  matriz_distancias = [[0.0] * num_cidades for _ in range(num_cidades)]
  for i in range(num_cidades):
    for j in range(i + 1, num_cidades): #= ????
      if i != j:
        x1, y1 = cidades[i]
        x2, y2 = cidades[j]
        matriz_distancias[i][j] = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
  return matriz_distancias

def calcular_custo_rota(rota, matriz_distancias):
  distancia_total = 0.0
  num_cidades = len(rota)
  for i in range(num_cidades):
    cidade_atual = rota[i]
    proxima_cidade = rota[(i + 1) % num_cidades] # Volta para a cidade inicial
    distancia_total += matriz_distancias[cidade_atual][proxima_cidade]
  return distancia_total

# =============================================================================
# ESTRUTURA DA BACTERIA
# =============================================================================

class Bacteria:
  def __init__(self, rota, custo):
    self.rota = rota
    self.custo = custo
    self.saude = 0.0

# =============================================================================
# FUNÇÕES DE PARALELIZAÇÃO
# =============================================================================

def _avaliar_movimento_quimiotatico(args):
    """
    Função global necessária para o Pool de Multiprocessing.
    Executa a quimiotaxia (passos) para uma única bactéria.
    """
    bacteria, matriz_distancias, Nc, Ns = args
    num_cidades = len(bacteria.rota)
    
    for _ in range(Nc):
        # Passo de Tumble: Gera uma nova rota candidata por mutação de inversão
        nova_rota = copy.deepcopy(bacteria.rota)
        idx1, idx2 = sorted(random.sample(range(num_cidades), 2))
        nova_rota[idx1:idx2] = reversed(nova_rota[idx1:idx2])
        
        novo_custo = calcular_custo_rota(nova_rota, matriz_distancias)
        
        # Passo de Run: Se melhorou, continua movendo-se naquela direção
        passos_dados = 0
        while passos_dados < Ns and novo_custo < bacteria.custo:
            bacteria.rota = nova_rota
            bacteria.custo = novo_custo
            passos_dados += 1
            
            # Tenta estender o movimento na mesma direção (outra pequena mutação)
            idx1, idx2 = sorted(random.sample(range(num_cidades), 2))
            nova_rota = copy.deepcopy(bacteria.rota)
            nova_rota[idx1:idx2] = reversed(nova_rota[idx1:idx2])
            novo_custo = calcular_custo_rota(nova_rota, matriz_distancias)
            
        bacteria.saude += bacteria.custo
        
    return bacteria

# =============================================================================
# ALGORITMO BFOA
# =============================================================================

class BFOA_TSP:
  def __init__(self, cidades, s, nc, ns, nre, ned, ped):
      
      self.cidades = cidades
      self.num_cidades = len(cidades)
      self.matriz_distancias = calcular_matriz_distancias(cidades)

      self.s = s      # Tamanho da População (Número de Bactérias)
      self.nc = nc    # Passos quimiotáticos
      self.ns = ns    # Comprimento da corrida (número de passos que a bactéria continua se movendo na mesma direção)
      self.nre = nre  # Passos de reprodução
      self.ned = ned  # Passos de eliminação/dispersão
      self.ped = ped  # Probabilidade de eliminação

      self.populacao = []
      self.melhor_bacteria = None
      self.inicializar_populacao()

  def inicializar_populacao(self):
    for _ in range(self.s):
      rota_inicial = list(range(self.num_cidades))
      random.shuffle(rota_inicial)
      custo_inicial = calcular_custo_rota(rota_inicial, self.matriz_distancias)
      bacteria = Bacteria(rota_inicial, custo_inicial)
      self.populacao.append(bacteria)

      if self.melhor_bacteria is None or custo_inicial < self.melhor_bacteria.custo:
        self.melhor_bacteria = copy.deepcopy(bacteria)
    
  def executar(self):
    num_cores = os.cpu_count() or 1
    pool = Pool(processes=num_cores)

    print(f"[*] Inicializando BFOA paralelizado utilizando {num_cores} cores...")

    for l in range(self.ned):
      for k in range(self.nre):
        for bac in self.populacao:
          bac.saude = 0.0
          
        args = [(bac, self.matriz_distancias, self.nc, self.ns) for bac in self.populacao]
          
        self.populacao = pool.map(_avaliar_movimento_quimiotatico, args)

        for bac in self.populacao:
          if bac.custo < self.melhor_bacteria.custo:
            self.melhor_bacteria = copy.deepcopy(bac)

        self.populacao.sort(key=lambda b: b.custo)

        metade_sobrevivente = self.populacao[:self.s // 2]
        self.populacao = metade_sobrevivente + copy.deepcopy(metade_sobrevivente)

        for bac in self.populacao:
          if random.random() < self.ped:
            nova_rota = list(range(self.num_cidades))
            random.shuffle(nova_rota)
            bac.rota = nova_rota
            bac.custo = calcular_custo_rota(nova_rota, self.matriz_distancias)

            if bac.custo < self.melhor_bacteria.custo:
              self.melhor_bacteria = copy.deepcopy(bac)

        print(f" > Ciclo de Dispersão {l+1}/{self.ned} concluído. Melhor Distancia até agora: {self.melhor_bacteria.custo:.4f}")

    pool.close()
    pool.join()
    return self.melhor_bacteria

# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == '__main__':
    caminho_instancia = "entrada_maior.txt" 
    
    if not os.path.exists(caminho_instancia):
        print(f"Erro: Arquivo '{caminho_instancia}' não encontrado. Por favor, crie o arquivo.")
    else:
        cidades = ler_instancia(caminho_instancia)
        
        # Configuração do Algoritmo
        #bfoa = BFOA_TSP(
        #    cidades=cidades, 
        #    s=40,    # Tamanho da População
        #    nc=15,   # Passos quimiotáticos
        #    ns=4,    # Comprimento da corrida
        #    nre=5,   # Passos de reprodução
        #    ned=4,   # Passos de eliminação/dispersão
        #    ped=0.25  # Probabilidade de eliminação
        #)
        
        bfoa = BFOA_TSP(
            cidades=cidades, 
            s=60,    # Tamanho da População
            nc=20,   # Passos quimiotáticos
            ns=5,    # Comprimento da corrida
            nre=6,   # Passos de reprodução
            ned=5,   # Passos de eliminação/dispersão
            ped=0.25  # Probabilidade de eliminação
        )

        melhor_solucao = bfoa.executar()
        
        print("\n================ RESULTADO FINAL ================")
        print(f"Melhor Rota Encontrada: {melhor_solucao.rota}")
        print(f"Distância Total Calculada: {melhor_solucao.custo:.4f}")