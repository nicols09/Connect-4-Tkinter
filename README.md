# Connect 4 com interface Tkinter

> Jogo Connect 4 desenvolvido em Python 3 com interface gráfica Tkinter.

O projeto permite jogar contra o computador ou no modo multiplayer local (1 vs 1 no mesmo dispositivo), conta com sorteio de cara ou coroa para definir quem começa, tela de regras com demonstração animada e tabuleiro desenhado com Matplotlib.

## Funcionalidades atuais

- **Menu inicial modernizado** com logo personalizada e acesso rápido a Como Jogar, Jogar e Créditos.
- **Dois modos de partida**:
  - **Contra a Máquina:** partida contra o computador, que tenta vencer e bloquear sequências do jogador.
  - **Multiplayer local (1 vs 1):** dois jogadores humanos no mesmo dispositivo, com personalização de nomes, turnos alternados e indicação visual de quem é a vez.
- **Sorteio de cara ou coroa** antes da partida em ambos os modos para definir quem joga primeiro.
- **Tela "Como Jogar"** com explicação das regras em português e demonstração em GIF animado.
- **Fim de partida completo:** identificação de vitória, derrota e empate, destaque das 4 peças vencedoras no tabuleiro e opções de **Jogar de Novo** ou **Voltar ao Menu**.
- **Tela de Créditos** com informações sobre o projeto original, a equipe do Projeto Integrador e as melhorias realizadas.

## Como jogar

1. Na tela inicial, clique em **Como Jogar** para ver as regras ou em **Jogar** para escolher o modo de partida.
2. Em **Escolha o Modo de Jogo**, selecione:
   - **Jogar contra a Máquina:** realiza o cara ou coroa e inicia a partida contra o computador.
   - **1 vs 1:** informe o nome do Jogador 1 (peças vermelhas) e do Jogador 2 (peças amarelas) — ou deixe em branco para usar os nomes padrão —, realize o sorteio de cara ou coroa e jogue alternadamente.
3. Durante a partida, clique nos botões de **a** a **g** abaixo do tabuleiro para soltar uma peça na coluna desejada.
4. Ao término da partida, clique em **Jogar de Novo** para reiniciar ou **Voltar ao Menu** para trocar o modo de jogo.

## Requisitos

- Python 3.10 ou superior.
- Tkinter instalado no sistema.
- NumPy.
- Matplotlib.
- Pillow.

No Linux baseado em Debian ou Ubuntu, instale o Python, o suporte ao Tkinter,
o ambiente virtual e o pip com:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk
```

No Windows ou macOS, instale o Python pelo site oficial e confirme que o
Tkinter foi incluído na instalação.

## Instalação

Dentro da pasta do projeto, crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell, use:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Com o ambiente virtual ativo, instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Para confirmar a instalação:

```bash
python -c "import tkinter, numpy, matplotlib, PIL; print('Dependencias instaladas com sucesso')"
```

## Execução

Com o ambiente virtual ativo, execute:

```bash
python gamegui.py
```

Para sair do ambiente virtual depois de fechar o jogo:

```bash
deactivate
```

## Solução de problemas

### `No module named pip`

Instale o pacote do pip pelo gerenciador do sistema. Em Debian ou Ubuntu:

```bash
sudo apt install python3-pip python3-venv
```

### `No module named tkinter`

Instale o suporte gráfico do Python:

```bash
sudo apt install python3-tk
```

### A janela não abre

O jogo precisa ser executado em um ambiente com interface gráfica. Em uma
conexão SSH sem encaminhamento gráfico ou em um terminal sem display, o
Tkinter não conseguirá abrir a janela.

## Sobre o projeto

Este projeto foi desenvolvido originalmente para aprender a criar interfaces
gráficas em Python. A lógica do jogo foi escrita inicialmente em Python 2 e
depois adaptada para Python 3, com a interface gráfica adicionada posteriormente.

O projeto também serviu para praticar a criação de aplicações Python com
múltiplas telas usando Tkinter e a integração de gráficos do Matplotlib em uma
janela Tkinter.

## Captura de tela

<img width="300" alt="game_screenshot" src="https://user-images.githubusercontent.com/40459599/53034902-2ac24d80-346c-11e9-94d3-85b3db84ad71.png">

## Licença

Este projeto está licenciado nos termos da licença MIT. Consulte
[LICENSE.txt](LICENSE.txt) para mais informações.

## Agradecimentos

- [Tutorial de Tkinter utilizado como referência](https://www.youtube.com/playlist?list=PLQVvvaa0QuDclKx-QpC9wntnURXVJqLyk)

