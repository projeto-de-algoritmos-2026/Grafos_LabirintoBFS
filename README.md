
# GRAFOS - G45
Repositório referente ao trabalho 1 da disciplina de Projeto de Algorítmos 2026.2

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 211062698  |  Marcos Vinícius Lima Bezerra |
| 241031852  | Matheus Lemes Amaral |

## Objetivo
A ideia é construir uma pequena simulação onde um personagem explora um labirinto representado como grafo. O personagem começa buscando a saída usando DFS (busca em profundidade), e ao encontrá-la, usa BFS (busca em largura) para determinar o menor caminho de volta.

O objetivo é usar essa exploração como forma de visualizar, na prática, o funcionamento dos dois algoritmos — como cada um percorre o grafo, quais estruturas de dados usa (pilha vs. fila) e as diferenças de comportamento entre eles.

## Instalação e execução

Requisitos:

- Python 3.9 ou superior;
- ambiente gráfico capaz de abrir uma janela Pygame.

No Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

No Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

A aplicação abre uma janela com o labirinto à esquerda e o painel de métricas
à direita. Para validar apenas a lógica sem abrir a janela, execute a suíte
unitária descrita na seção [Testes](#testes).

Após o DFS encontrar a saída, o BFS percorre o grafo explorado para calcular o menor caminho de volta ao início. Em seguida, o personagem refaz esse caminho até a saída.

## Fluxo da simulação

1. O DFS explora o labirinto usando uma pilha e backtracking.
2. O BFS usa uma fila para encontrar o menor caminho entre a saída e o início.
3. O personagem volta ao início e segue o caminho mínimo até a saída.

## Cenários reproduzíveis

Cada rodada exibe a seed usada no painel lateral. A tecla `R` cria um novo
labirinto com uma seed aleatória; a tecla `S` repete o cenário atual usando a
mesma seed. Para iniciar sempre com uma seed conhecida, defina
`DEFAULT_SEED` em `config.py` ou chame `App.new_maze(seed=123)`.

Quando nenhuma seed é informada, uma seed aleatória é gerada automaticamente.
A mesma seed controla tanto a geração do labirinto quanto a ordem aleatória da
exploração DFS, permitindo repetir o fluxo completo DFS → BFS.

## Controles

| Tecla | Ação |
| --- | --- |
| `ESPAÇO` | Pausa ou continua a animação |
| `R` | Gera um novo labirinto com seed aleatória |
| `S` | Reinicia o mesmo cenário usando a seed exibida |
| `+` / `-` | Aumenta ou diminui a velocidade |
| `ESC` | Encerra a aplicação |

## Interface e estados

O painel lateral exibe a seed, a fase atual, velocidade, passos do DFS,
células visitadas, tamanhos e resumos da pilha DFS e da fila BFS, além do
comprimento do menor caminho. As estruturas longas são truncadas no painel,
mas suas quantidades permanecem visíveis.

As fases aparecem no painel com estes nomes:

- `DFS explorando`: o personagem segue a pilha e faz backtracking;
- `BFS calculando`: a fila se expande a partir da saída;
- `Voltando ao início`: o personagem percorre o caminho mínimo em direção à entrada;
- `Indo para a saída`: o mesmo caminho é percorrido no sentido inverso;
- `Concluído`: a rodada terminou ou não havia caminho disponível.

As cores da legenda identificam início, saída, área do DFS, célula atual,
visitas e fronteira do BFS e caminho mínimo.

## DFS versus BFS

As duas buscas têm papéis diferentes na simulação:

| Algoritmo | Estrutura | Estratégia | Objetivo na aplicação |
| --- | --- | --- | --- |
| DFS | Pilha (LIFO) | Aprofunda por um caminho e faz backtracking nos becos sem saída | Explorar o labirinto até encontrar a saída |
| BFS | Fila (FIFO) | Visita os vértices por camadas, expandindo a fronteira | Encontrar o menor caminho entre a saída e o início |

As cores da animação acompanham essas fases: azul escuro representa a área
explorada pelo DFS, azul claro representa células já visitadas pelo BFS, roxo
representa a fronteira atual da fila BFS e verde representa o caminho mínimo
encontrado. A célula amarela indica a posição atual durante o DFS; o
personagem é desenhado em branco durante o BFS e o retorno pelo caminho.

O BFS opera sobre o `graph_explorado`, isto é, o subgrafo construído pelo DFS
até a saída. Como o labirinto gerado é uma árvore perfeita, esse caminho é o
caminho mínimo do labirinto.

## API do BFS

`bfs_shortest_path(grafo, origem, destino)` retorna uma lista de vértices na
ordem origem → destino. Se origem e destino forem iguais, retorna uma lista
com esse único vértice; se o destino não for alcançável, retorna `None`.

## Testes

Execute a suíte unitária com:

```bash
python -m unittest discover -s tests -v
```

## Solução de problemas

- `ModuleNotFoundError: No module named 'pygame'`: ative o ambiente virtual e
  execute `python -m pip install -r requirements.txt`.
- Em Python 3.14 com Pygame 2.6.1, a aplicação usa automaticamente o backend
  `freetype` para contornar a importação circular do módulo de fontes. O aviso
  sobre AVX2 na inicialização é apenas informativo e não impede a execução.
- A janela não abre em um servidor ou terminal remoto sem display: execute em
  uma sessão com ambiente gráfico; a suíte unitária continua disponível para
  validar a lógica sem interface.
- Para repetir uma demonstração, defina `DEFAULT_SEED` em `config.py` antes de
  iniciar ou use `S` durante a execução.
