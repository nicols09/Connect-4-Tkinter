import platform
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
import connect4module as c4
import os
from PIL import Image, ImageTk, ImageSequence

matplotlib.use("TkAgg")

# ---------------------------------------------------------------------------
# Paleta de cores e fontes do jogo
# ---------------------------------------------------------------------------

BG_COLOR = "#F4F1EA"        # fundo bege claro
PRIMARY_COLOR = "#E63946"   # vermelho (cor do jogador, usada para os botões de ação)
PRIMARY_HOVER = "#C1121F"   # vermelho mais escuro, para quando o botão é clicado
SECONDARY_COLOR = "#457B9D"  # azul (usado em botões secundários/navegação)
SECONDARY_HOVER = "#33607F"
TEXT_COLOR = "#1D3557"      # azul bem escuro, usado no texto principal
MUTED_TEXT_COLOR = "#6C7A89"  # cinza-azulado, para textos secundários

# Cores usadas no modo 1 vs 1 para mostrar de quem é a vez. São versões mais
# escuras do vermelho e do amarelo das peças, para o texto continuar legível
# sobre o fundo bege.
PLAYER1_COLOR = "#C1121F"   # Jogador 1 (peças vermelhas)
PLAYER2_COLOR = "#A67C00"   # Jogador 2 (peças amarelas)

# Fonte de destaque (títulos)
# Fonte de corpo (textos/instruções)
TITLE_FONT = ("Arial", 34, "bold")
SUBTITLE_FONT = ("Arial", 16)
STATEMENT_FONT = ("Arial", 22, "bold")
BODY_FONT = ("Segoe UI", 13)
BUTTON_FONT = ("Segoe UI", 13, "bold")
COLUMN_BUTTON_FONT = ("Segoe UI", 12, "bold")


def setup_styles(root):
    """
    Configura o visual (cores, fontes, espaçamento) de todos os widgets
    ttk usados no jogo. É chamada uma única vez, quando o app abre.

    Usamos o tema "clam" como base porque, diferente do tema padrão do
    Windows, ele permite customizar a cor de fundo dos botões — no tema
    padrão, a cor de fundo do botão é sempre controlada pelo sistema
    operacional e não pode ser alterada por código.
    """
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=BG_COLOR)

    style.configure(
        "TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=BODY_FONT
    )
    style.configure(
        "Title.TLabel",
        background=BG_COLOR,
        foreground=PRIMARY_COLOR,
        font=TITLE_FONT,
    )
    style.configure(
        "Subtitle.TLabel",
        background=BG_COLOR,
        foreground=MUTED_TEXT_COLOR,
        font=SUBTITLE_FONT,
    )
    style.configure(
        "Statement.TLabel",
        background=BG_COLOR,
        foreground=TEXT_COLOR,
        font=STATEMENT_FONT,
    )
    style.configure(
        "Body.TLabel",
        background=BG_COLOR,
        foreground=TEXT_COLOR,
        font=BODY_FONT,
    )

    # Botão principal (ação mais importante da tela, ex: "Jogar")
    style.configure(
        "Primary.TButton",
        background=PRIMARY_COLOR,
        foreground="white",
        font=BUTTON_FONT,
        padding=(18, 10),
        borderwidth=0,
    )
    style.map(
        "Primary.TButton",
        background=[("active", PRIMARY_HOVER), ("pressed", PRIMARY_HOVER)],
    )

    # Botão secundário (ações de navegação, ex: "Voltar")
    style.configure(
        "Secondary.TButton",
        background=SECONDARY_COLOR,
        foreground="white",
        font=BUTTON_FONT,
        padding=(16, 9),
        borderwidth=0,
    )
    style.map(
        "Secondary.TButton",
        background=[("active", SECONDARY_HOVER), ("pressed", SECONDARY_HOVER)],
    )

    # Botões de coluna (a-g), embaixo do tabuleiro
    style.configure(
        "Column.TButton",
        font=COLUMN_BUTTON_FONT,
        padding=(6, 6),
    )

    # Campos de texto (ex: nomes dos jogadores no modo 1 vs 1)
    style.configure("TEntry", padding=(8, 6))


class Connect4App(tk.Tk):
    """
    Controller class, will control whole application
    """

    def __init__(self):

        # create window that will display all the frames
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, "Connect 4")
        self.configure(background=BG_COLOR)
        setup_styles(self)

        # Nomes dos jogadores do modo 1 vs 1. Ficam guardados aqui, no
        # controlador, porque são compartilhados entre duas telas: a
        # LocalPage (onde os nomes são digitados) e a LocalBoardPage (onde
        # a partida acontece). Os valores abaixo são só os nomes padrão,
        # usados caso nenhum nome seja digitado.
        self.player1_name = "Jogador 1"
        self.player2_name = "Jogador 2"

        container = tk.Frame(self, background=BG_COLOR)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # dictionary with all frames in the app listed
        self.frames = {}

        # creates each page and adds it to container
        for f in (StartPage, RulesPage, PlayMenuPage, LocalPage,
                  TossPage, BoardPageLose, BoardPageWin, LocalBoardPage,
                  CreditsPage):
            frame = f(container, self)
            self.frames[f] = frame   # adds pages to dictionary
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        # Centraliza a janela na tela do usuário, sem travar o tamanho dela.
        #
        # Importante: aqui passamos só a posição ("+x+y") para o geometry(),
        # e NÃO um tamanho fixo ("LARGURAxALTURA+x+y"). Se passássemos um
        # tamanho fixo, a janela pararia de se redimensionar sozinha quando
        # o conteúdo muda — por exemplo, quando os botões "Jogar de Novo" e
        # "Voltar ao Menu" aparecem ao fim de uma partida. Como aqui só a
        # posição é definida, a janela continua se ajustando normalmente,
        # só que já nasce centralizada na tela.
        self.update_idletasks()
        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"+{x}+{y}")

    # raises necessary page to top to see
    def show_frame(self, page):

        frame = self.frames[page]

        # Algumas telas (TossPage, BoardPageWin, BoardPageLose) guardam o
        # estado de uma partida/sorteio anterior. Sem isso, ao voltar pra
        # elas depois de já ter jogado uma vez, ficariam "travadas" no
        # resultado antigo. Se a tela tiver um método on_show, ele é
        # chamado automaticamente aqui, toda vez que o usuário navega até
        # ela, garantindo que sempre comece do zero.
        if hasattr(frame, "on_show"):
            frame.on_show()

        frame.tkraise()


class StartPage(tk.Frame):
    """
    Tela inicial: mensagem de boas-vindas e o menu principal, com as opções
    de ver as regras do jogo ou começar a jogar.
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window, style="TFrame")
        self.grid_columnconfigure(1, weight=1)

        # Carrega a imagem do título e redimensiona com o Pillow, a imagem é quadrada por enquanto, por isso
        # redimensionei ela como 250x250.
        caminho = os.path.join(os.path.dirname(__file__), "titulo.png")
        img = Image.open(caminho).resize((250, 250))
        self.titulo_img = ImageTk.PhotoImage(img)

        title = ttk.Label(self, image=self.titulo_img, background=BG_COLOR)
        title.grid(row=1, column=1, pady=(60, 6))
        title = ttk.Label(self, image=self.titulo_img, background=BG_COLOR)
        title.grid(row=1, column=1, pady=(60, 6))

        subtitle = ttk.Label(
            self,
            text="Conecte 4 peças em linha e vença o adversário!",
            style="Subtitle.TLabel",
        )
        subtitle.grid(row=2, column=1, pady=(0, 40))

        button_rules = ttk.Button(
            self,
            text="Como Jogar",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(RulesPage),
        )
        button_rules.grid(row=3, column=1, pady=8, ipadx=10)

        button_play = ttk.Button(
            self,
            text="Jogar",
            style="Primary.TButton",
            command=lambda: controller.show_frame(PlayMenuPage),
        )
        button_play.grid(row=4, column=1, pady=8, ipadx=10)

        button_credits = ttk.Button(
            self,
            text="Créditos",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(CreditsPage),
        )
        button_credits.grid(row=5, column=1, pady=8, ipadx=10)

class RulesPage(tk.Frame):
    """
    Tela de regras: explica em poucas palavras como o jogo funciona,
    para quem estiver jogando pela primeira vez.
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window, style="TFrame")
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(self, text="Como Jogar", style="Title.TLabel")
        title.configure(font=("Arial", 28, "bold"))
        title.grid(row=1, column=1, pady=(40, 20))

        rules_text = (
            "O objetivo é ser o primeiro a conectar 4 peças da mesma cor "
            "em uma linha, seja na horizontal, na vertical ou na diagonal.\n\n"
            "1. Clique em uma das letras (a-g) embaixo do tabuleiro para "
            "escolher a coluna onde quer soltar sua peça.\n\n"
            "2. A peça cai até o espaço vazio mais baixo daquela coluna.\n\n"
            "3. Você e o adversário/máquina se revezam, jogando uma peça por vez.\n\n"
            "4. Vence quem conseguir alinhar 4 peças da mesma cor primeiro.\n\n"
            "5. Se o tabuleiro encher e ninguém tiver vencido, é empate."
        )

        rules_label = ttk.Label(
            self,
            text=rules_text,
            style="Body.TLabel",
            justify="left",
            wraplength=520,
        )
        rules_label.grid(row=2, column=1, padx=40, pady=(0, 20))

        # --- GIF animado ---
        caminho_gif = os.path.join(os.path.dirname(__file__), "vd.gif")
        gif = Image.open(caminho_gif)

        self.gif_frames = []
        self.gif_delays = []
        for frame in ImageSequence.Iterator(gif):
            frame_img = frame.convert("RGBA")
            frame_img.thumbnail((480, 360))
            self.gif_frames.append(ImageTk.PhotoImage(frame_img))
            self.gif_delays.append(frame.info.get("duration", 100))

        self.gif_label = ttk.Label(
            self, image=self.gif_frames[0], background=BG_COLOR
        )
        self.gif_label.grid(row=3, column=1, pady=(0, 20))

        self.gif_index = 0
        self.animate_gif()

        button_back = ttk.Button(
            self,
            text="Voltar",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(StartPage),
        )
        button_back.grid(row=4, column=1, pady=10, ipadx=10)

    def animate_gif(self):
        """Mostra o quadro atual e agenda o próximo."""
        self.gif_label.configure(image=self.gif_frames[self.gif_index])
        delay = self.gif_delays[self.gif_index]
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.after(delay, self.animate_gif)

class PlayMenuPage(tk.Frame):
    """
    Tela de escolha do modo de jogo: contra a máquina ou 1 vs 1 local
    (dois jogadores no mesmo computador).
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window, style="TFrame")
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(
            self, text="Escolha o Modo de Jogo", style="Title.TLabel"
        )
        title.configure(font=("Arial", 28, "bold"))
        title.grid(row=1, column=1, pady=(60, 40))

        button_machine = ttk.Button(
            self,
            text="Jogar contra a Máquina",
            style="Primary.TButton",
            command=lambda: controller.show_frame(TossPage),
        )
        button_machine.grid(row=2, column=1, pady=10, ipadx=10)

        button_local = ttk.Button(
            self,
            text="1 vs 1",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(LocalPage),
        )
        button_local.grid(row=3, column=1, pady=10, ipadx=10)

        button_back = ttk.Button(
            self,
            text="Voltar",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(StartPage),
        )
        button_back.grid(row=4, column=1, pady=(40, 10))


class LocalPage(tk.Frame):
    """
    Tela do modo 1 vs 1 local: antes de começar a partida, cada jogador
    digita o próprio nome. Se um campo ficar em branco, é usado o nome
    padrão ("Jogador 1" ou "Jogador 2").
    """

    # Limite de caracteres por nome, para o texto não ficar grande demais
    # na tela do tabuleiro.
    MAX_NAME_LENGTH = 20

    HINT_TEXT = ("Deixe em branco para usar os nomes padrão "
                 "(Jogador 1 e Jogador 2).")

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window, style="TFrame")
        self.controller = controller
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(self, text="1 vs 1", style="Title.TLabel")
        title.configure(font=("Arial", 28, "bold"))
        title.grid(row=1, column=1, pady=(50, 6))

        subtitle = ttk.Label(
            self, text="Digite o nome de cada jogador", style="Subtitle.TLabel"
        )
        subtitle.grid(row=2, column=1, pady=(0, 24))

        # Regra que impede digitar mais do que MAX_NAME_LENGTH caracteres:
        # o Tkinter chama is_valid_length a cada tecla (o "%P" é o texto
        # que o campo teria depois da tecla) e só aceita a digitação se a
        # função devolver True.
        validate_length = (self.register(self.is_valid_length), "%P")

        label_p1 = ttk.Label(
            self, text="Jogador 1 (peças vermelhas)", style="Body.TLabel"
        )
        label_p1.grid(row=3, column=1, pady=(0, 4))
        self.entry_p1 = ttk.Entry(
            self, width=26, justify="center", font=BODY_FONT,
            validate="key", validatecommand=validate_length,
        )
        self.entry_p1.grid(row=4, column=1, pady=(0, 16))

        label_p2 = ttk.Label(
            self, text="Jogador 2 (peças amarelas)", style="Body.TLabel"
        )
        label_p2.grid(row=5, column=1, pady=(0, 4))
        self.entry_p2 = ttk.Entry(
            self, width=26, justify="center", font=BODY_FONT,
            validate="key", validatecommand=validate_length,
        )
        self.entry_p2.grid(row=6, column=1, pady=(0, 12))

        # Mensagem de apoio: normalmente mostra a dica sobre os nomes
        # padrão, e vira um aviso em vermelho quando há algum problema.
        self.message = ttk.Label(
            self, text=self.HINT_TEXT, style="Body.TLabel",
            foreground=MUTED_TEXT_COLOR, wraplength=420, justify="center",
        )
        self.message.grid(row=7, column=1, padx=20)

        button_start = ttk.Button(
            self, text="Iniciar Partida", style="Primary.TButton",
            command=self.start_game,
        )
        button_start.grid(row=8, column=1, pady=(20, 8), ipadx=10)

        button_back = ttk.Button(
            self, text="Voltar", style="Secondary.TButton",
            command=lambda: controller.show_frame(PlayMenuPage),
        )
        button_back.grid(row=9, column=1, pady=10, ipadx=10)

        # Enter no primeiro campo pula para o segundo; Enter no segundo
        # inicia a partida.
        self.entry_p1.bind("<Return>", lambda event: self.entry_p2.focus_set())
        self.entry_p2.bind("<Return>", lambda event: self.start_game())

    def on_show(self):
        """Chamado automaticamente pelo show_frame() sempre que o usuário
        chega a esta tela: limpa os campos e a mensagem, para cada nova
        partida começar com a tela de nomes vazia."""
        self.entry_p1.delete(0, tk.END)
        self.entry_p2.delete(0, tk.END)
        self.set_message(self.HINT_TEXT, MUTED_TEXT_COLOR)
        # after_idle espera a tela terminar de aparecer antes de colocar o
        # cursor no primeiro campo.
        self.after_idle(self.entry_p1.focus_set)

    def is_valid_length(self, new_text):
        return len(new_text) <= self.MAX_NAME_LENGTH

    def set_message(self, text, color):
        self.message.configure(text=text, foreground=color)

    def start_game(self):
        """Lê os nomes digitados, valida e abre a tela do tabuleiro."""
        name1 = self.entry_p1.get().strip() or "Jogador 1"
        name2 = self.entry_p2.get().strip() or "Jogador 2"

        # Com nomes iguais, a mensagem "Vez de ..." não diria quem é quem.
        if name1.lower() == name2.lower():
            self.set_message(
                "Os dois jogadores não podem ter o mesmo nome.",
                PRIMARY_COLOR,
            )
            return

        self.controller.player1_name = name1
        self.controller.player2_name = name2
        self.controller.show_frame(LocalBoardPage)


class CreditsPage(tk.Frame):
    """
    Tela de créditos: por enquanto só exibe um aviso de que a área
    ainda está em desenvolvimento.
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window, style="TFrame")
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(self, text="Créditos", style="Title.TLabel")
        title.configure(font=("Arial", 28, "bold"))
        title.grid(row=1, column=1, pady=(40, 20))

        credits_text = (
            "Essa é uma branch do repositório:\n"
            "https://github.com/saiduc/Connect-4-Tkinter, pertencente ao "
            "Sai Pandian.\n\n"
            "O repositório foi escolhido para receber melhorias em um "
            "Projeto Integrador da Fatec de Ribeirão Preto - SP. Os "
            "participantes foram os alunos do 2° semestre do curso de "
            "Análise e Desenvolvimento de Sistemas: Antonio Pires, Hugo "
            "Oliveira, Luiz Felipe, Mateus dos Santos, Nícolas dos Anjos "
            "e Paulo Otávio.\n\n"
            "As melhorias até o momento foram:\n\n"
            "• Tradução para português\n"
            "• Criação de um botão de restart das partidas\n"
            "• Melhorias na parte visual (front-end), adicionando "
            "botões, títulos e cores\n"
            "• Menu na tela inicial, que conta com a explicação das "
            "regras do jogo e um vídeo de demonstração de partida\n"
            "• Botão de regressar ao menu após o fim de uma partida\n"
            "• Centralização do tabuleiro\n"
            "• Criação de uma logo do Connect4 na tela inicial do "
            "programa\n"
            "• Criação do modo 1v1 local"
        )

        # Mantemos a mesma fonte (style="Subtitle.TLabel") que já estava
        # no texto provisório ("Área em desenvolvimento..."). Como agora
        # o texto é bem mais longo, só ajustamos o alinhamento para a
        # esquerda (mais fácil de ler em parágrafos/listas do que
        # centralizado) e aumentamos o "wraplength" para caber melhor.
        message = ttk.Label(
            self,
            text=credits_text,
            style="Subtitle.TLabel",
            wraplength=560,
            justify="left",
        )
        message.grid(row=2, column=1, padx=30, pady=(0, 30))

        button_back = ttk.Button(
            self,
            text="Voltar",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(StartPage),
        )
        button_back.grid(row=3, column=1, pady=10, ipadx=10)


class TossPage(tk.Frame):
    """
    Toss Page, contains coin toss function
    """

    def __init__(self, window, controller):
        ttk.Frame.__init__(self, window, style="TFrame")
        self.controller = controller
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(self, text="Cara ou Coroa", style="Title.TLabel")
        title.configure(font=("Arial", 28, "bold"))
        title.grid(row=1, column=1, pady=(50, 10))

        toss = ttk.Label(
            self, text="Escolha cara ou coroa", style="Subtitle.TLabel"
        )
        toss.grid(row=2, column=1, pady=(0, 20))

        # "outcome", "nextstep" e os botões agora são guardados como
        # atributos (self.xxx) em vez de variáveis locais do __init__.
        # Isso é necessário para que on_show() consiga encontrá-los e
        # resetá-los sempre que o usuário voltar a esta tela, mesmo esse
        # __init__ só rodando uma única vez durante toda a vida do app.
        self.button_heads = ttk.Button(
            self, text="Cara", style="Primary.TButton",
            command=self.heads, width=8,
        )
        self.button_tails = ttk.Button(
            self, text="Coroa", style="Secondary.TButton",
            command=self.tails, width=8,
        )
        self.button_heads.grid(row=3, column=1, pady=6)
        self.button_tails.grid(row=4, column=1, pady=6)

        # empty labels that will be updated with outcome after user selects
        self.outcome = ttk.Label(self, text="", style="Statement.TLabel")
        self.outcome.grid(row=6, column=1, pady=(20, 0))
        self.nextstep = ttk.Label(self, text="", style="Body.TLabel")
        self.nextstep.grid(row=7, column=1)

        # Botões ocultos que ficam visíveis depois que o usuário faz uma seleção
        self.button_win = ttk.Button(
            self, text="Continuar", style="Primary.TButton",
            command=lambda: controller.show_frame(BoardPageWin),
        )
        self.button_lose = ttk.Button(
            self, text="Continuar", style="Primary.TButton",
            command=lambda: controller.show_frame(BoardPageLose),
        )

        self.reset()

    def on_show(self):
        """Chamado automaticamente pelo show_frame() sempre que o
        usuário navega até esta tela — garante que o sorteio comece
        do zero."""
        self.reset()

    def reset(self):
        """Deixa a tela pronta para um novo sorteio: textos vazios, os
        botões "Cara"/"Coroa" reativados, e o botão "Continuar"
        escondido até que o usuário escolha um lado da moeda de novo."""
        self.outcome.configure(text="")
        self.nextstep.configure(text="")
        self.button_heads.configure(text="Cara", command=self.heads)
        self.button_tails.configure(text="Coroa", command=self.tails)
        self.button_win.grid_remove()
        self.button_lose.grid_remove()

    def heads(self):
        """
        Runs cointoss function in connect4module with chosen call = 1
        Updates buttons to have no function, so user cannot reselect
        Updates labels to show outcome of coin toss
        Makes relevant continue button visible
        """
        call = 1
        result = c4.cointoss(call)
        self.button_tails.configure(text="", command=donothing)
        self.button_heads.configure(command=donothing)
        if result == True:
            self.outcome.configure(text="Você ganhou o sorteio!")
            self.nextstep.configure(text="Você jogará primeiro")
            self.button_win.grid(row=8, column=1, pady=20, ipadx=10)
        else:
            self.outcome.configure(text="Você perdeu o sorteio!")
            self.nextstep.configure(text="O computador jogará primeiro")
            self.button_lose.grid(row=8, column=1, pady=20, ipadx=10)
        self.outcome.update()
        self.nextstep.update()
        self.button_heads.update()
        self.button_tails.update()

    def tails(self):
        """
        Runs cointoss function in connect4module with chosen call = 0
        Updates buttons to have no function, so user cannot reselect
        Updates labels to show outcome of coin toss
        Makes relevant continue button visible
        """
        call = 0
        result = c4.cointoss(call)
        self.button_heads.configure(text="", command=donothing)
        self.button_tails.configure(command=donothing)
        if result == True:
            self.outcome.configure(text="Você ganhou o sorteio!")
            self.nextstep.configure(text="Você jogará primeiro")
            self.button_win.grid(row=8, column=1, pady=20, ipadx=10)
        else:
            self.outcome.configure(text="Você perdeu o sorteio!")
            self.nextstep.configure(text="O computador jogará primeiro")
            self.button_lose.grid(row=8, column=1, pady=20, ipadx=10)
        self.outcome.update()
        self.nextstep.update()
        self.button_heads.update()
        self.button_tails.update()


class BoardPageLose(tk.Frame):
    """
    Board Page, contains main game
    If player lost toss
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window, style="TFrame")
        self.controller = controller

        # Deixa as colunas das laterais ocuparem o espaço que sobrar
        # para manter o conteúdo no meio da tela

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Faz a mesma coisa com as linhas de cima e de baixo

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(11, weight=1)

        title = ttk.Label(self, text="Connect4", style="Title.TLabel")
        title.configure(font=("Arial", 26, "bold"))
        title.grid(row=1, column=1, pady=(20, 0))

        # "statement" e os botões de coluna agora são guardados como
        # atributos (self.xxx), e não mais variáveis locais do __init__.
        # Isso é necessário para que o botão de "Reiniciar" consiga
        # encontrá-los e reconfigurá-los depois, mesmo esse __init__ só
        # rodando uma única vez durante toda a vida do aplicativo.

        self.statement = ttk.Label(
            self, text="Escolha uma coluna", style="Statement.TLabel"
        )
        self.statement.grid(row=4, column=1, pady=(60, 0))

        # Cria uma área para colocar os botões embaixo do tabuleiro

        self.button_row = ttk.Frame(self, width=350, height=40)
        self.button_row.grid(row=3, column=1, pady=(4, 0))

        # Lista para guardar os botões

        self.buttons = []

        # Cria um botão para cada coluna do jogo

        for i, letra in enumerate("abcdefg"):
            btn = ttk.Button(
                self.button_row,
                text=letra,
                style="Column.TButton",
                width=2,
                command=lambda col=i: self.choose_column(col)
            )

            # Coloca os botões em suas posições

            btn.place(
                relx=0.01 + 0.98 * (i + 1) / 8,
                rely=0,
                anchor="n"
            )

            # Adiciona o botão na lista

            self.buttons.append(btn)

        # Botão de reiniciar a partida. Criado aqui junto com o resto da
        # tela, mas só fica visível (via .grid) depois que a partida atual
        # termina — veja end_game() e new_game() mais abaixo.
        
        self.restart_button = ttk.Button(
            self, text="Jogar de Novo", style="Primary.TButton",
            command=self.new_game,
        )
        self.menu_button = ttk.Button(
            self, text="Voltar ao Menu", style="Secondary.TButton",
            command=lambda: controller.show_frame(PlayMenuPage),
        )

        # Começa a primeira partida desta tela assim que ela é criada.
        self.new_game()

    def on_show(self):
        """Chamado automaticamente pelo show_frame() sempre que o
        usuário navega até esta tela — garante uma partida nova, mesmo
        se a tela já tiver sido usada antes (ex: jogou, voltou ao menu
        e ganhou/perdeu o mesmo sorteio de novo).
        """
        self.new_game()

    def new_game(self):
        """
        (Re)inicia a partida do zero, nesta mesma tela.

        É chamada tanto na primeira vez que a tela aparece quanto toda
        vez que o jogador clica no botão "Jogar de Novo" depois do fim
        de uma partida anterior.
        """
        self.board = c4.makearrayboard()

        # Como o jogador perdeu o sorteio nesta tela, o computador sempre
        # joga primeiro.
        computercolumn = c4.decidecomputermove(self.board)
        while c4.checkifvalid(self.board, computercolumn) != True:
            computercolumn = c4.decidecomputermove(self.board)
        c4.docomputermove(self.board, computercolumn)

        self.redraw_board()

        for i, button in enumerate(self.buttons):
            button.configure(command=lambda col=i: self.choose_column(col))
            button.update()

        self.statement.configure(text="Escolha uma coluna")
        self.statement.update()

        self.restart_button.grid_remove()
        self.menu_button.grid_remove()

    def redraw_board(self):
        """Desenha (ou redesenha) o tabuleiro atual na tela."""
        graph = c4.plotgraphicalboard(self.board)
        canvas = FigureCanvasTkAgg(graph, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1)

    def choose_column(self, column):
        if c4.checkifvalid(self.board, column) == True:
            c4.dousermove(self.board, column)
            self.continuegame()

    def continuegame(self):
        """
        Função principal que toca o jogo para frente. Confere o estado
        atual (checkgamestate), faz o computador jogar se a partida
        continuar, e atualiza a tela conforme o resultado final.
        """

        gamestate = c4.checkgamestate(self.board)

        if gamestate == 0:
            computercolumn = c4.decidecomputermove(self.board)
            while c4.checkifvalid(self.board, computercolumn) != True:
                computercolumn = c4.decidecomputermove(self.board)
            c4.docomputermove(self.board, computercolumn)
            gamestate = c4.checkgamestate(self.board)
            self.redraw_board()

        if gamestate == 1:
            self.redraw_board()
            self.end_game("Você Venceu!")
            print("You win")

        if gamestate == 2:
            self.end_game("Você Perdeu!")
            print("You lose")

        if gamestate == 3:
            self.redraw_board()
            self.statement.configure(text="Empate!")
            self.statement.update()
            self.show_end_buttons()
            print("You draw")

    def end_game(self, message):
        """
        Reaproveitada tanto para vitória quanto para derrota: desativa
        os botões de coluna, mostra a mensagem final e exibe os botões
        de reiniciar/voltar ao menu.
        """
        for button in self.buttons:
            button.configure(command=donothing)
            button.update()
        self.statement.configure(text=message)
        self.statement.update()
        self.show_end_buttons()

    def show_end_buttons(self):
        self.restart_button.grid(row=9, column=1, pady=(24, 4), ipadx=6)
        self.menu_button.grid(row=10, column=1, pady=(0, 10))


class BoardPageWin(tk.Frame):
    """
    Board Page, contains main game
    If player won toss
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window, style="TFrame")
        self.controller = controller

    # Deixa as colunas das laterais ocuparem o espaço que sobrar
    # para manter o conteúdo no meio da tela

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

    # Faz a mesma coisa com as linhas de cima e de baixo

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(11, weight=1)

        title = ttk.Label(self, text="Connect4", style="Title.TLabel")
        title.configure(font=("Arial", 26, "bold"))
        title.grid(row=1, column=1, pady=(20, 0))


        self.statement = ttk.Label(
            self, text="Escolha uma coluna", style="Statement.TLabel"
        )
        self.statement.grid(row=4, column=1, pady=(60, 0))

     # Cria uma área para colocar os botões embaixo do tabuleiro

        self.button_row = ttk.Frame(self, width=350, height=40)
        self.button_row.grid(row=3, column=1, pady=(4, 0))

        # Lista para guardar os botões
        
        self.buttons = []

        # Cria um botão para cada coluna do jogo

        for i, letra in enumerate("abcdefg"):
            btn = ttk.Button(
                self.button_row,
                text=letra,
                style="Column.TButton",
                width=2,
                command=lambda col=i: self.choose_column(col)
            )

            # Coloca os botões em suas posições

            btn.place(
                relx=0.01 + 0.98 * (i + 1) / 8,
                rely=0,
                anchor="n"
            )

            # Adiciona o botão na lista

            self.buttons.append(btn)

        self.restart_button = ttk.Button(
            self, text="Jogar de Novo", style="Primary.TButton",
            command=self.new_game,
        )
        self.menu_button = ttk.Button(
            self, text="Voltar ao Menu", style="Secondary.TButton",
            command=lambda: controller.show_frame(PlayMenuPage),
        )

        # Começa a primeira partida desta tela assim que ela é criada.
        self.new_game()

    def on_show(self):
        """Chamado automaticamente pelo show_frame() sempre que o
        usuário navega até esta tela — garante uma partida nova, mesmo
        se a tela já tiver sido usada antes (ex: jogou, voltou ao menu
        e ganhou/perdeu o mesmo sorteio de novo).
        """
        self.new_game()

    def new_game(self):
        """
        (Re)inicia a partida do zero, nesta mesma tela.

        Igual à versão de BoardPageLose, mas aqui o tabuleiro começa
        totalmente vazio (sem jogada do computador), já que o jogador
        ganhou o sorteio e joga primeiro.
        """
        self.board = c4.makearrayboard()
        self.redraw_board()

        for i, button in enumerate(self.buttons):
            button.configure(command=lambda col=i: self.choose_column(col))
            button.update()

        self.statement.configure(text="Escolha uma coluna")
        self.statement.update()

        self.restart_button.grid_remove()
        self.menu_button.grid_remove()

    def redraw_board(self):
        """Desenha (ou redesenha) o tabuleiro atual na tela."""
        graph = c4.plotgraphicalboard(self.board)
        canvas = FigureCanvasTkAgg(graph, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1)

    def choose_column(self, column):
        if c4.checkifvalid(self.board, column) == True:
            c4.dousermove(self.board, column)
            self.continuegame()

    def continuegame(self):
        """
        Função principal do jogo nesta tela. Funciona exatamente da
        mesma forma explicada em BoardPageLose.continuegame.
        """

        gamestate = c4.checkgamestate(self.board)

        if gamestate == 0:
            computercolumn = c4.decidecomputermove(self.board)
            while c4.checkifvalid(self.board, computercolumn) != True:
                computercolumn = c4.decidecomputermove(self.board)
            c4.docomputermove(self.board, computercolumn)
            gamestate = c4.checkgamestate(self.board)
            self.redraw_board()

        if gamestate == 1:
            self.redraw_board()
            self.end_game("Você Venceu!")
            print("You win")

        if gamestate == 2:
            self.end_game("Você Perdeu!")
            print("You lose")

        if gamestate == 3:
            self.redraw_board()
            self.statement.configure(text="Empate!")
            self.statement.update()
            self.show_end_buttons()
            print("You draw")

    def end_game(self, message):
        """
        Reaproveitada tanto para vitória quanto para derrota: desativa
        os botões de coluna, mostra a mensagem final e exibe os botões
        de reiniciar/voltar ao menu.
        """
        for button in self.buttons:
            button.configure(command=donothing)
            button.update()
        self.statement.configure(text=message)
        self.statement.update()
        self.show_end_buttons()

    def show_end_buttons(self):
        self.restart_button.grid(row=9, column=1, pady=(24, 4), ipadx=6)
        self.menu_button.grid(row=10, column=1, pady=(0, 10))


class LocalBoardPage(BoardPageWin):
    """
    Tabuleiro do modo 1 vs 1 local.

    Reaproveita toda a interface da BoardPageWin (título, tabuleiro,
    botões de coluna, "Jogar de Novo" e "Voltar ao Menu") e só troca a
    lógica de turno: em vez de o computador responder depois da jogada,
    os dois jogadores humanos se alternam.

    A lógica do jogo continua a mesma do modo contra a máquina:
        - o Jogador 1 usa as peças vermelhas (valor 1 no tabuleiro), jogadas
          com c4.dousermove;
        - o Jogador 2 usa as peças amarelas (valor 5 no tabuleiro), jogadas
          com c4.docomputermove (apesar do nome, essa função só coloca a
          peça de valor 5 na coluna, então serve para qualquer segundo
          jogador);
        - c4.checkgamestate continua dizendo o resultado: 1 = vermelhas
          venceram, 2 = amarelas venceram, 3 = empate, 0 = segue o jogo.
    """

    def __init__(self, window, controller):
        BoardPageWin.__init__(self, window, controller)

        # Nomes grandes quebram em duas linhas em vez de alargar a janela.
        self.statement.configure(wraplength=380, justify="center")

    def player_name(self, player):
        if player == 1:
            return self.controller.player1_name
        return self.controller.player2_name

    def player_color(self, player):
        if player == 1:
            return PLAYER1_COLOR
        return PLAYER2_COLOR

    def new_game(self):
        """
        (Re)inicia a partida: tabuleiro vazio e vez do Jogador 1. É chamada
        quando a tela aparece (via on_show) e no botão "Jogar de Novo".
        Os nomes são lidos do controlador a cada partida, então sempre
        refletem o que foi digitado na LocalPage.
        """
        self.board = c4.makearrayboard()
        self.current_player = 1
        self.redraw_board()

        for i, button in enumerate(self.buttons):
            button.configure(command=lambda col=i: self.choose_column(col))

        self.show_turn()

        self.restart_button.grid_remove()
        self.menu_button.grid_remove()

    def show_turn(self):
        """Mostra de quem é a vez, na cor das peças desse jogador."""
        self.statement.configure(
            text=f"Vez de {self.player_name(self.current_player)}",
            foreground=self.player_color(self.current_player),
        )

    def choose_column(self, column):
        if c4.checkifvalid(self.board, column) != True:
            return

        if self.current_player == 1:
            c4.dousermove(self.board, column)
        else:
            c4.docomputermove(self.board, column)

        self.continuegame()

    def continuegame(self):
        """
        Chamada depois de cada jogada: confere o resultado e, se a partida
        continua, passa a vez para o outro jogador.
        """
        gamestate = c4.checkgamestate(self.board)

        # O desenho vem depois da checagem de propósito: quando alguém
        # vence, checkgamestate marca as 4 peças vencedoras no tabuleiro, e
        # é essa marcação que faz o desenho destacá-las com a linha grossa.
        self.redraw_board()

        if gamestate == 0:
            if self.current_player == 1:
                self.current_player = 2
            else:
                self.current_player = 1
            self.show_turn()

        elif gamestate == 3:
            self.end_game("Empate!")
            self.statement.configure(foreground=TEXT_COLOR)

        else:
            winner = 1 if gamestate == 1 else 2
            self.end_game(f"{self.player_name(winner)} venceu!")
            self.statement.configure(foreground=self.player_color(winner))


def donothing():
    """
    Function that does nothing.
    Makes a button useless if assigned to it
    """
    pass


# Stops program crashing on mac due to UnicodeDecodeError
def runapp(app):
    try:
        app.mainloop()
    except UnicodeDecodeError:
        runapp(app)


app = Connect4App()
runapp(app)
