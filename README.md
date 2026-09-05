
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
