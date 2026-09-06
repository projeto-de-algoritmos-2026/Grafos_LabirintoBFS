
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
