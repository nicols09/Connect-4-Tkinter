import platform
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
import connect4module as c4
import os
from PIL import Image, ImageTk

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

        container = tk.Frame(self, background=BG_COLOR)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # dictionary with all frames in the app listed
        self.frames = {}

        # creates each page and adds it to container
        for f in (StartPage, RulesPage, PlayMenuPage, LocalPage,
                  TossPage, BoardPageLose, BoardPageWin, CreditsPage):
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
        rules_label.grid(row=2, column=1, padx=40, pady=(0, 30))

        button_back = ttk.Button(
            self,
            text="Voltar",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(StartPage),
        )
        button_back.grid(row=3, column=1, pady=10, ipadx=10)


class PlayMenuPage(tk.Frame):
    """
    Tela de escolha do modo de jogo: contra a máquina (já funcional) ou
    1 vs 1 local (ainda não implementado, só o botão de acesso).
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
    Tela reservada para o modo 1 vs 1 local. A funcionalidade ainda não foi
    desenvolvida — por enquanto só existe a navegação até aqui, avisando
    que o modo está a caminho.
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window, style="TFrame")
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(self, text="1 vs 1 Local", style="Title.TLabel")
        title.configure(font=("Georgia", 28, "bold"))
        title.grid(row=1, column=1, pady=(80, 20))

        message = ttk.Label(
            self,
            text="Em breve! Este modo de jogo ainda está em desenvolvimento.",
            style="Subtitle.TLabel",
            wraplength=420,
            justify="center",
        )
        message.grid(row=2, column=1, pady=(0, 40))

        button_back = ttk.Button(
            self,
            text="Voltar",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(PlayMenuPage),
        )
        button_back.grid(row=3, column=1, pady=10, ipadx=10)

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
        title.grid(row=1, column=1, pady=(80, 20))

    # Elaborar um texto bem feito para colocar nos créditos.

        message = ttk.Label(
            self,
            text="Área em desenvolvimento, aguarde novos releases",
            style="Subtitle.TLabel",
            wraplength=420,
            justify="center",
        )
        message.grid(row=2, column=1, pady=(0, 40))

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

        # Hidden buttons that becomes visible after user makes selection
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
