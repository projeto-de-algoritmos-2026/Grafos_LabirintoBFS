# DFS explora, BFS resolve — demonstração visual em labirinto

Projeto didático que mostra, visualmente, um personagem explorando um
labirinto com **DFS** (busca em profundidade, com pilha e backtracking) até
achar a saída, e depois usando **BFS** (busca em largura) para calcular o
menor caminho de volta ao início — e, na sequência, andar até a saída pelo
mesmo caminho.

Nenhuma biblioteca de grafos/algoritmos prontos é usada (`networkx`, etc). DFS
e BFS são implementados manualmente em `algorithms.py`, com pilha e fila
(`deque`) puras.

## Os dois grafos

- **Grafo completo** (`graph_completo`, em `maze.py`): representa todo o
  labirinto de verdade — todas as células e passagens possíveis. É uma
  lista de adjacências de verdade (`graph.py`), montada a partir das paredes
  derrubadas na geração do labirinto. O personagem não "vê" esse grafo
  inteiro de uma vez — só consulta os vizinhos da célula onde está.

- **Grafo explorado** (`graph_explorado`, em `main.py`): começa vazio. Cada
  vez que o personagem avança para uma célula nova durante o DFS, uma
  aresta é adicionada aqui. No fim da exploração, é uma **árvore** (subgrafo
  do grafo completo) — e é sobre essa árvore que o BFS roda para achar o
  caminho de volta.

Como o labirinto gerado é "perfeito" (sem loops — o `graph_completo` já é,
ele mesmo, uma árvore), o caminho encontrado pelo BFS no grafo explorado
acaba sendo também o caminho ótimo do labirinto real, só que "podado" dos
becos sem saída que o DFS visitou por engano.

## Como rodar

Requer Python 3.9+ e uma tela (é uma aplicação gráfica, roda numa janela —
não funciona em terminal puro nem em ambientes sem display).

```bash
pip install -r requirements.txt
python main.py
```

## Controles

| Tecla     | Ação                              |
|-----------|------------------------------------|
| `ESPAÇO`  | Pausar / continuar a animação      |
| `R`       | Gerar novo labirinto e reiniciar   |
| `+` / `-` | Aumentar / diminuir velocidade     |
| `ESC`     | Sair                               |

## Estrutura do projeto

```
maze_dfs_bfs/
├── main.py          # loop principal + máquina de estados
├── maze.py          # geração do labirinto (recursive backtracker) e grafo completo
├── graph.py          # estrutura de grafo genérica (lista de adjacências)
├── algorithms.py     # DFS exploratório e BFS de menor caminho, como generators
├── visualizer.py      # desenho (Pygame): labirinto, células, HUD
├── config.py          # cores, tamanhos, velocidades
└── requirements.txt
```

## Fases da animação

1. **Gerar labirinto** — instantâneo, ao iniciar ou apertar `R`.
2. **DFS explorando** — personagem anda célula a célula pelo grafo completo,
   com pilha explícita; quando trava num beco sem saída, faz backtrack. Cada
   avanço vira uma aresta nova no grafo explorado. O painel lateral mostra a
   pilha em tempo real.
3. **BFS calculando** — ao achar a saída, roda BFS no grafo explorado
   (saída → início) para achar o único caminho na árvore.
4. **Voltando ao início** — anima o personagem por esse caminho.
5. **Indo para a saída** — anima o personagem pelo caminho invertido.
6. **Concluído** — resumo: passos do DFS (com backtrack) vs. tamanho do
   caminho ótimo encontrado pelo BFS.

## Personalização rápida

Em `config.py`: mude `COLS`/`ROWS` para labirintos maiores/menores,
`CELL_SIZE` para ajustar zoom, e `DEFAULT_STEPS_PER_SEC` para a velocidade
inicial da animação.
