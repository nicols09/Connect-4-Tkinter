# Visão consolidada do Connect 4

## Objetivo

Modernizar o jogo Connect 4 desktop sem perder o funcionamento que já existe.
O trabalho deve priorizar a análise do projeto, a organização da interface, a
melhoria da usabilidade, a documentação e a manutenção da lógica atual.

## Estado atual

O projeto é composto por dois módulos principais:

- `connect4module.py`: concentra a representação do tabuleiro, as regras de
  jogada, a verificação de vitória ou empate, a estratégia do computador e a
  geração do gráfico do tabuleiro.
- `gamegui.py`: concentra a janela Tkinter, as telas, os botões, o sorteio
  inicial e a integração do gráfico Matplotlib com a interface.

O jogo utiliza um tabuleiro de 6 linhas por 7 colunas. O jogador escolhe uma
coluna, a peça ocupa a posição livre mais baixa e, em seguida, o computador
realiza sua jogada. A partida termina quando um dos lados conecta quatro peças
ou quando não existem mais movimentos.

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
- Manter a partida individual contra o computador nesta versão.
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

- Preservar a alternância entre jogada do jogador e jogada do computador.
- Impedir novas jogadas depois do encerramento da partida.
- Exibir corretamente o resultado final no tabuleiro.
- Atualizar o gráfico de maneira consistente depois de cada jogada.

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

1. **Análise:** executar o projeto e registrar funcionalidades, problemas e
  pontos de refatoração.
2. **Documentação:** revisar textos e registrar requisitos, instalação,
  execução e uso.
3. **Interface:** mapear telas, definir padrão visual, reorganizar a tela
  principal e melhorar a usabilidade.
4. **Lógica:** organizar o código existente, tratar erros e testar as regras.
5. **Integração:** validar a comunicação entre interface e lógica.

## Critérios de aceite

- As funcionalidades atuais são registradas antes das alterações.
- As telas seguem um padrão visual consistente.
- A navegação e as mensagens ficam mais claras para o jogador.
- A lógica existente continua funcionando após a refatoração.
- A integração entre interface e lógica é validada.
- A documentação descreve dependências, instalação, execução e uso.

## Responsabilidades sugeridas

- **Interface:** telas, navegação, componentes visuais, responsividade e
  integração com o tabuleiro.
- **Lógica:** regras, estratégia do computador, validações, refatoração e
  testes do núcleo.
- **Documentação:** README, instruções de uso, registro das funcionalidades e
  revisão dos textos.

As responsabilidades podem ser compartilhadas, mas cada entrega deve ter uma
pessoa responsável pela verificação final.
