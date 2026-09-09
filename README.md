# Connect 4 com interface Tkinter

> Jogo Connect 4 desenvolvido em Python 3 com interface gráfica Tkinter.

O projeto possui uma partida contra o computador, sorteio para definir quem
começa e tabuleiro desenhado com Matplotlib.

## Funcionalidades atuais

- Sorteio de cara ou coroa para definir quem começa.
- Jogadas do jogador e do computador em um tabuleiro de 6 por 7.
- Computador capaz de tentar vencer e bloquear jogadas do jogador.
- Identificação de vitória, derrota e empate.
- Exibição do tabuleiro integrado à janela Tkinter.

## Requisitos

- Python 3.10 ou superior.
- Tkinter instalado no sistema.
- NumPy.
- Matplotlib.

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
python -c "import tkinter, numpy, matplotlib; print('Dependencias instaladas com sucesso')"
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

