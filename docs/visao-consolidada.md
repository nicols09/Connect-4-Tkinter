# Visão consolidada do Connect 4

## Objetivo

Evoluir o jogo Connect 4 desktop para permitir partidas multiplayer local 1x1,
sem perder as regras fundamentais que já existem. O trabalho deve priorizar a
análise do projeto, o desenvolvimento da lógica necessária, a adaptação da
interface, a melhoria da usabilidade e a documentação.

## Estado atual

O projeto é composto por dois módulos principais:

- `connect4module.py`: concentra a representação do tabuleiro, as regras de
  jogada, a verificação de vitória ou empate, a estratégia atual do computador
  e a geração do gráfico do tabuleiro.
- `gamegui.py`: concentra a janela Tkinter, as telas, os botões, o sorteio
  inicial e a integração do gráfico Matplotlib com a interface.

O jogo utiliza um tabuleiro de 6 linhas por 7 colunas. Atualmente, um jogador
escolhe uma coluna, a peça ocupa a posição livre mais baixa e, em seguida, o
computador realiza sua jogada. A partida termina quando um dos lados conecta
quatro peças ou quando não existem mais movimentos.

O fluxo atual possui as seguintes telas e estados:

1. Tela inicial para iniciar a partida.
2. Sorteio de cara ou coroa para decidir quem começa.
3. Tabuleiro para a partida quando o jogador começa.
4. Tabuleiro para a partida quando o computador começa.
5. Mensagem de vitória, derrota ou empate ao final.

## Diretrizes técnicas

- Preservar a matriz de 6 por 7 e as regras existentes enquanto a modernização
  visual estiver sendo desenvolvida.
- Manter a separação entre regras e interface: mudanças de layout devem ficar
  principalmente em `gamegui.py`, e mudanças de regra devem ser isoladas em
  `connect4module.py`.
- Manter Tkinter como framework da interface e Matplotlib como representação
  inicial do tabuleiro.
- Desenvolver no `connect4module.py` o suporte às partidas entre dois jogadores
  humanos no mesmo dispositivo.
- Preservar a matriz de 6 por 7, a queda das peças, a validação de jogadas, a
  detecção de vitória e o empate.
- Manter a lógica do computador funcionando enquanto o modo 1x1 é desenvolvido.
- Não alterar as regras existentes sem registrar e testar o impacto.

## Escopo de modernização

### Interface e navegação

- Criar uma tela inicial mais clara, com ação principal de início.
- Organizar o sorteio inicial com instruções, resultado e continuação visível.
- Padronizar títulos, textos, botões, espaçamentos e dimensões da janela.
- Melhorar o posicionamento dos botões das colunas para diferentes sistemas e
  resoluções.
- Traduzir e revisar os textos exibidos na interface, mantendo uma linguagem
  consistente.
- Melhorar as mensagens e o feedback das ações do jogador.

### Fluxo de partida

- Permitir selecionar o modo de partida multiplayer local 1x1.
- Alternar corretamente os turnos entre os dois jogadores.
- Associar cada jogada ao jogador da vez e impedir jogadas fora do turno.
- Impedir novas jogadas depois do encerramento da partida.
- Exibir corretamente o resultado final no tabuleiro.
- Atualizar o gráfico de maneira consistente depois de cada jogada.

### Lógica do jogo

- Separar a operação de realizar uma jogada da decisão específica do
  computador.
- Representar os dois jogadores sem depender da lógica de decisão da IA.
- Retornar para a interface informações suficientes sobre jogada inválida,
  turno atual, vitória, derrota ou empate.
- Cobrir a nova lógica com testes antes de integrá-la à interface.

### Identidade visual

- Definir uma paleta, tipografia e componentes reutilizáveis para as telas.
- Melhorar a leitura do tabuleiro e diferenciar visualmente jogador,
  computador e peças vencedoras.

### Qualidade e manutenção

- Remover duplicação de comportamento na interface quando isso puder ser feito
  sem alterar o fluxo.
- Tornar nomes, responsabilidades e mensagens mais claros.
- Registrar dependências, instalação, execução e uso no README.
- Criar verificações para as regras principais antes de refatorar o núcleo.
- Executar uma partida completa após cada mudança relevante na interface.

## Ordem de entrega

1. **Análise:** registrar o fluxo atual e os pontos que impedem o multiplayer
   local 1x1.
2. **Lógica:** desenvolver e testar o suporte a dois jogadores em
   `connect4module.py`.
3. **Interface:** adaptar telas, botões, mensagens e fluxo de turnos em
   `gamegui.py`.
4. **Integração:** validar a comunicação entre interface e lógica.
5. **Documentação:** registrar requisitos, instalação, execução e uso.

## Critérios de aceite

- O modo multiplayer local 1x1 pode ser iniciado pela interface.
- Os dois jogadores realizam jogadas alternadas no mesmo dispositivo.
- Uma jogada inválida não altera o tabuleiro nem troca o turno.
- A vitória e o empate são identificados corretamente para os dois jogadores.
- As telas seguem um padrão visual consistente.
- A lógica atual do computador continua funcionando, quando aplicável.
- A integração entre interface e lógica é validada.
- A documentação descreve dependências, instalação, execução e uso.

## Responsabilidades sugeridas

- **Interface:** telas, navegação, componentes visuais, responsividade e
  integração com o tabuleiro.
- **Lógica:** regras, suporte ao multiplayer 1x1, estratégia do computador,
  validações, refatoração e testes do núcleo.
- **Documentação:** README, instruções de uso, registro das funcionalidades e
  revisão dos textos.

As responsabilidades podem ser compartilhadas, mas cada entrega deve ter uma
pessoa responsável pela verificação final.
