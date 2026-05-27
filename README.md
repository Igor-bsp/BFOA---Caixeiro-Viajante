# Caixeiro viajante utilizando Busca de Alimento Bacteriana (BFOA)

Este repositório contém a implementação prática do $1^{\circ}$ Trabalho Prático de Inteligência Artificial do Departamento de Ciência da Computação (Dcomp) da UFSJ. O objetivo principal é resolver o clássico Problema do Caixeiro Viajante (TSP) utilizando e comparando duas abordagens meta-heurísticas distintas:

* **BFOA (Bacteria Foraging Optimization Algorithm):** Algoritmo de Inteligência de Enxame baseado no comportamento de busca de alimento da bactéria E. coli, implementado com otimização e paralelização multi-core para alto desempenho.
  
* **GA (Genetic Algorithm):** Algoritmo Genético clássico baseado na Computação Evolutiva, utilizando operadores de Seleção por Torneio, Cruzamento Ordenado (OX) e Mutação por Troca (Swap) para fins de comparação científica.

## Visão Geral do Projeto

* ```bfoa_tsp.py:``` Código-fonte principal do algoritmo de busca de alimento bacteriana paralelizado.
* ```algoritmo_genetico.py:``` Código-fonte do algoritmo genético adaptado para representação por caminho (permutação).  
* **Instâncias de Teste:** Arquivos de dados (como entrada.txt e entrada_grande.txt) contendo as coordenadas cartesianas das cidades a serem visitadas.  
* **Artigo Científico:** Relatório técnico detalhado contendo a fundamentação teórica, hiperparâmetros, gráficos de convergência e análise comparativa dos resultados.

## Estrutura do Projeto

A estrutura de pastas do projeto foi organizada para facilitar a manutenção e escalabilidade:
```
.
└── TP1/                          # Pasta raiz
    ├── bfoa.py                   # Aplicação busca de alimento bacteriana
    ├── algoritmo_genetico.py     # Aplicação algoritmo genético
    ├── Documentacao/             # Pasta com o Artigo
    │   └── artigo.pdf/           # Artigo científico
    ├── LICENSE                   # Licença de uso
    ├── README.md                 # Este arquivo de orientação
    └── requirements.txt          # Dependências do projeto

```
## Configuração e Execução (Localmente)

Para executar o projeto localmente, siga os passos abaixo:

### Pré-requisitos
* Python 3.8+
* pip (gerenciador de pacotes do Python)

### 1. Clonar o Repositório
```bash
git clone git@github.com:matheuznsilva/BFOA---Caixeiro-Viajante
cd BFOA---Caixeiro-Viajante/ # Ou o nome da pasta do seu projeto
```
### 2. Criar e Ativar o Ambiente Virtual
É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto:

```Bash
python3 -m venv venv
# No Linux/macOS:
source venv/bin/activate
# No Windows:
.\venv\Scripts\activate
```
### 3. Instalar as Dependências
Com o ambiente virtual ativado, instale as dependências listadas no requirements.txt:

```Bash
pip install -r requirements.txt
```

### 4. Executar a Aplicação
Certifique-se de que seu ambiente virtual está ativado e que você está na raiz do projeto e execute o seguinte comando:

```Bash
# No Linux/macOS:
python bfoa_tps.py
python algoritmo_genetico.py 

# No Windows (CMD/PowerShell):
python bfoa_tps.py
python algoritmo_genetico.py 
```

## Tecnologias Utilizadas

<div> 
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&amp;logo=python&amp;logoColor=white" alt="python">  
</div>

## Licença
MIT License

## ✍️ Autores

| [![Breno E. dos Santos](https://avatars.githubusercontent.com/u/)](https://github.com/) | [![Gabriel de P. Lara](https://avatars.githubusercontent.com/u/)](https://github.com/) | [![Igor B. S. Pinto](https://avatars.githubusercontent.com/u/)](https://github.com/) | [![Matheus N. Silva](https://avatars.githubusercontent.com/u/23366884?v=4)](https://github.com/matheuznsilva) |
|:-:|:-:|:-:|:-:|
| [Breno E. dos Santos](https://github.com/) | [Gabriel de P. Lara](https://github.com/) | [Igor B. S. Pinto](https://github.com/) | [Matheus N. Silva](https://github.com/matheuznsilva) |