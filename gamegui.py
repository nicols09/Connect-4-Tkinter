import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import connect4module as c4
import os
import math
import winsound  # <--- Módulo nativo do Windows para reproduzir áudio .wav
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

# Placar da disputa "melhor de N" (ScoreBoard) e ritmo entre as partidas
CARD_COLOR = "#FFFFFF"            # fundo do cartão do placar
CARD_BORDER_COLOR = "#D8D3C7"     # borda e divisórias do cartão
SCORE_COLUMN_WIDTH = 210          # espaço (px) reservado ao placar, nos dois lados do tabuleiro
SCORE_NAME_WRAP = 110             # largura (px) em que nomes grandes quebram de linha
NEXT_GAME_DELAY_MS = 2200         # pausa entre o fim de uma partida e o início da próxima (ms)
SCORE_TITLE_FONT = ("Arial", 15, "bold")
SCORE_SMALL_FONT = ("Segoe UI", 11)
SCORE_NAME_FONT = ("Segoe UI", 13, "bold")
SCORE_NUMBER_FONT = ("Arial", 28, "bold")

# Fonte de destaque (títulos)
# Fonte de corpo (textos/instruções)
TITLE_FONT = ("Arial", 34, "bold")
SUBTITLE_FONT = ("Arial", 16)
STATEMENT_FONT = ("Arial", 22, "bold")
BODY_FONT = ("Segoe UI", 13)
BUTTON_FONT = ("Segoe UI", 13, "bold")
COLUMN_BUTTON_FONT = ("Segoe UI", 12, "bold")

# Animação da moeda do cara ou coroa
COIN_SIZE = 170      # tamanho da moeda em repouso (px, quadrada)
COIN_LIFT = 60       # quanto a moeda sobe durante o arremesso (px)
COIN_TURNS = 3       # voltas completas que a moeda dá antes de parar
COIN_FRAMES = 45     # quantidade de quadros da animação
COIN_FRAME_MS = 30   # tempo entre os quadros (ms): 45 x 30 ms = ~1,35 s


def setup_styles(root):
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

    style.configure(
        "Column.TButton",
        font=COLUMN_BUTTON_FONT,
        padding=(6, 6),
    )

    style.configure("TEntry", padding=(8, 6))


class Connect4App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, "Connect 4")
        self.configure(background=BG_COLOR)
        setup_styles(self)

        self.player1_name = "Jogador 1"
        self.player2_name = "Jogador 2"
        self.local_first_player = 1

        self.game_mode = "computer"
        self.series_best_of = 3

        self.current_page = None
        self.previous_page = None

        container = tk.Frame(self, background=BG_COLOR)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for f in (StartPage, RulesPage, PlayMenuPage, LocalPage, SeriesPage,
                  TossPage, LocalTossPage, BoardPageLose, BoardPageWin,
                  LocalBoardPage, CreditsPage):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        self.update_idletasks()
        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"+{x}+{y}")

    def show_frame(self, page):
        frame = self.frames[page]
        self.previous_page = self.current_page
        self.current_page = page

        if hasattr(frame, "on_show"):
            frame.on_show()

        frame.tkraise()

    def open_series_page(self, mode):
        self.game_mode = mode
        self.show_frame(SeriesPage)


class StartPage(tk.Frame):
    def __init__(self, window, controller):
        ttk.Frame.__init__(self, window, style="TFrame")
        self.grid_columnconfigure(1, weight=1)

        caminho = os.path.join(os.path.dirname(__file__), "titulo.png")
        if os.path.exists(caminho):
            img = Image.open(caminho).resize((250, 250))
            self.titulo_img = ImageTk.PhotoImage(img)
            title = ttk.Label(self, image=self.titulo_img, background=BG_COLOR)
        else:
            title = ttk.Label(self, text="Connect 4", style="Title.TLabel")

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

        caminho_gif = os.path.join(os.path.dirname(__file__), "vd.gif")
        if os.path.exists(caminho_gif):
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
        if hasattr(self, "gif_frames") and self.gif_frames:
            self.gif_label.configure(image=self.gif_frames[self.gif_index])
            delay = self.gif_delays[self.gif_index]
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.after(delay, self.animate_gif)


class PlayMenuPage(tk.Frame):
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
            command=lambda: controller.open_series_page("computer"),
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

        self.entry_p1.bind("<Return>", lambda event: self.entry_p2.focus_set())
        self.entry_p2.bind("<Return>", lambda event: self.start_game())

    def on_show(self):
        if self.controller.previous_page is SeriesPage:
            return

        self.entry_p1.delete(0, tk.END)
        self.entry_p2.delete(0, tk.END)
        self.set_message(self.HINT_TEXT, MUTED_TEXT_COLOR)
        self.after_idle(self.entry_p1.focus_set)

    def is_valid_length(self, new_text):
        return len(new_text) <= self.MAX_NAME_LENGTH

    def set_message(self, text, color):
        self.message.configure(text=text, foreground=color)

    def start_game(self):
        name1 = self.entry_p1.get().strip() or "Jogador 1"
        name2 = self.entry_p2.get().strip() or "Jogador 2"

        if name1.lower() == name2.lower():
            self.set_message(
                "Os dois jogadores não podem ter o mesmo nome.",
                PRIMARY_COLOR,
            )
            return

        self.controller.player1_name = name1
        self.controller.player2_name = name2
        self.controller.open_series_page("local")


class SeriesPage(tk.Frame):
    def __init__(self, window, controller):
        ttk.Frame.__init__(self, window, style="TFrame")
        self.controller = controller
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(self, text="Quantas Partidas?", style="Title.TLabel")
        title.configure(font=("Arial", 28, "bold"))
        title.grid(row=1, column=1, pady=(60, 6))

        subtitle = ttk.Label(
            self, text="Escolha o formato da disputa", style="Subtitle.TLabel"
        )
        subtitle.grid(row=2, column=1, pady=(0, 24))

        row = 3
        for best_of in c4.SERIES_OPTIONS:
            button = ttk.Button(
                self, text=f"Melhor de {best_of}", style="Primary.TButton",
                command=lambda n=best_of: self.choose(n),
            )
            button.grid(row=row, column=1, pady=(8, 0), ipadx=10)

            hint = ttk.Label(
                self, text=f"Vence quem fizer {best_of // 2 + 1} vitórias",
                style="Body.TLabel", foreground=MUTED_TEXT_COLOR,
            )
            hint.grid(row=row + 1, column=1, pady=(2, 8))
            row += 2

        button_back = ttk.Button(
            self, text="Voltar", style="Secondary.TButton",
            command=self.go_back,
        )
        button_back.grid(row=row, column=1, pady=(24, 10), ipadx=10)

    def choose(self, best_of):
        self.controller.series_best_of = best_of

        if self.controller.game_mode == "local":
            self.controller.show_frame(LocalTossPage)
        else:
            self.controller.show_frame(TossPage)

    def go_back(self):
        if self.controller.game_mode == "local":
            self.controller.show_frame(LocalPage)
        else:
            self.controller.show_frame(PlayMenuPage)


class CreditsPage(tk.Frame):
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
            "As melhorias efetuadas foram:\n\n"
            "• Tradução para português\n"
            "• Melhorias na parte visual (front-end), adicionando "
            "botões, títulos e cores\n"
            "• Menu na tela inicial, que conta com a explicação das "
            "regras do jogo e um vídeo de demonstração de partida\n"
            "• Botão de regressar ao menu após o fim de uma partida\n"
            "• Centralização do tabuleiro\n"
            "• Criação de uma logo do Connect4 na tela inicial do "
            "programa\n"
            "• Criação do modo 1v1 local\n"
            "• Adição de uma moeda para ser mostrada no sorteio do "
            "cara ou coroa\n"
            "• Efeito sonoro ao jogar o cara ou coroa\n"
            "• Adição dos modos melhor de 3, melhor de 5 e melhor de 7"
        )

        text_area = ttk.Frame(self)
        text_area.grid(row=2, column=1, padx=30, pady=(0, 30), sticky="ns")
        text_area.grid_rowconfigure(0, weight=1)
        text_area.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(2, weight=1)

        self.text = tk.Text(
            text_area,
            width=48,
            height=16,
            wrap="word",
            font=SUBTITLE_FONT,
            foreground=MUTED_TEXT_COLOR,
            background=BG_COLOR,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#D8D3C7",
            highlightcolor="#D8D3C7",
            padx=12,
            pady=10,
            cursor="arrow",
        )
        self.text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            text_area, orient="vertical", command=self.text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.insert("1.0", credits_text)
        self.text.configure(state="disabled")

        button_back = ttk.Button(
            self,
            text="Voltar",
            style="Secondary.TButton",
            command=lambda: controller.show_frame(StartPage),
        )
        button_back.grid(row=3, column=1, pady=10, ipadx=10)

    def on_show(self):
        self.text.yview_moveto(0)


_coin_faces_cache = {}


def load_coin_faces():
    if "faces" not in _coin_faces_cache:
        pasta = os.path.dirname(__file__)
        faces = []
        for nome in ("Cara.png", "Coroa.png"):
            caminho = os.path.join(pasta, nome)
            if os.path.exists(caminho):
                imagem = Image.open(caminho).convert("RGBA")
                faces.append(imagem.resize((COIN_SIZE, COIN_SIZE), Image.LANCZOS))
        if len(faces) == 2:
            _coin_faces_cache["faces"] = tuple(faces)
    return _coin_faces_cache.get("faces")


class CoinWidget(ttk.Label):
    def __init__(self, master):
        ttk.Label.__init__(self, master, style="TLabel")
        self._after_id = None
        self._on_done = None
        self._photo = None
        self._frame = 0
        self._total_angle = 0

        faces = load_coin_faces()
        if faces:
            self.cara, self.coroa = faces
            self.available = True
            self.show_rest()
        else:
            self.available = False

    def render(self, face_is_cara, scale_x, lift):
        face = self.cara if face_is_cara else self.coroa
        width = max(2, round(COIN_SIZE * scale_x))
        coin = face.resize((width, COIN_SIZE), Image.BILINEAR)

        frame = Image.new("RGBA", (COIN_SIZE, COIN_SIZE + COIN_LIFT), (0, 0, 0, 0))
        frame.paste(coin, ((COIN_SIZE - width) // 2, COIN_LIFT - round(lift)))

        self._photo = ImageTk.PhotoImage(frame)
        self.configure(image=self._photo)

    def show_rest(self):
        self.stop()
        if self.available:
            self.render(True, 1.0, 0)

    def stop(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self._on_done = None

    def spin(self, lands_on_cara, on_done):
        if not self.available:
            on_done()
            return

        self.stop()
        self._on_done = on_done

        self._total_angle = 2 * math.pi * COIN_TURNS
        if not lands_on_cara:
            self._total_angle += math.pi

        self._frame = 0
        self._tick()

    def _tick(self):
        t = self._frame / COIN_FRAMES
        eased = 1 - (1 - t) ** 2
        angle = self._total_angle * eased
        lift = COIN_LIFT * 4 * t * (1 - t)

        self.render(math.cos(angle) >= 0, abs(math.cos(angle)), lift)

        if self._frame >= COIN_FRAMES:
            self._after_id = None
            on_done, self._on_done = self._on_done, None
            if on_done:
                on_done()
            return

        self._frame += 1
        self._after_id = self.after(COIN_FRAME_MS, self._tick)


class TossPage(tk.Frame):
    def __init__(self, window, controller):
        ttk.Frame.__init__(self, window, style="TFrame")
        self.controller = controller
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(self, text="Cara ou Coroa", style="Title.TLabel")
        title.configure(font=("Arial", 28, "bold"))
        title.grid(row=1, column=1, pady=(50, 10))

        self.prompt = ttk.Label(
            self, text="Escolha cara ou coroa", style="Subtitle.TLabel"
        )
        self.prompt.grid(row=2, column=1, pady=(0, 20))

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

        self.coin = CoinWidget(self)
        self.coin.grid(row=5, column=1, pady=(10, 0))

        self.outcome = ttk.Label(self, text="", style="Statement.TLabel")
        self.outcome.grid(row=6, column=1, pady=(20, 0))
        self.nextstep = ttk.Label(self, text="", style="Body.TLabel")
        self.nextstep.grid(row=7, column=1)

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
        self.reset()

    def reset(self):
        self.outcome.configure(text="")
        self.nextstep.configure(text="")
        self.button_heads.configure(text="Cara", command=self.heads)
        self.button_tails.configure(text="Coroa", command=self.tails)
        self.button_win.grid_remove()
        self.button_lose.grid_remove()
        self.coin.show_rest()

    def heads(self):
        self.start_toss(1)

    def tails(self):
        self.start_toss(0)

    def start_toss(self, call):
        # --- TOCAR EFEITO SONORO DA MOEDA CAINDO ---
        sound_path = os.path.join(os.path.dirname(__file__), "som-moeda.wav")
        if os.path.exists(sound_path):
            # SND_FILENAME reproduz o arquivo .wav; SND_ASYNC toca sem travar a interface/animação
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

        won = c4.cointoss(call)

        if call == 1:
            self.button_tails.configure(text="")
        else:
            self.button_heads.configure(text="")
        self.button_heads.configure(command=donothing)
        self.button_tails.configure(command=donothing)

        landed = call if won else 1 - call
        self.coin.spin(landed == 1, lambda: self.show_result(won))

    def show_result(self, won):
        if won:
            self.outcome.configure(text="Você ganhou o sorteio!")
            self.nextstep.configure(text="Você jogará primeiro")
            self.button_win.grid(row=8, column=1, pady=20, ipadx=10)
        else:
            self.outcome.configure(text="Você perdeu o sorteio!")
            self.nextstep.configure(text="O computador jogará primeiro")
            self.button_lose.grid(row=8, column=1, pady=20, ipadx=10)


class LocalTossPage(TossPage):
    def __init__(self, window, controller):
        TossPage.__init__(self, window, controller)

        self.button_win.configure(
            command=lambda: controller.show_frame(LocalBoardPage)
        )

        self.prompt.configure(wraplength=480, justify="center")
        self.outcome.configure(wraplength=520, justify="center")
        self.nextstep.configure(wraplength=520, justify="center")

    def reset(self):
        TossPage.reset(self)
        self.prompt.configure(
            text=f"{self.controller.player1_name}, escolha cara ou coroa"
        )

    def show_result(self, won):
        name1 = self.controller.player1_name
        name2 = self.controller.player2_name

        if won:
            first_player = 1
            self.outcome.configure(text=f"{name1} ganhou o sorteio!")
            first_name = name1
        else:
            first_player = 2
            self.outcome.configure(text=f"{name1} perdeu o sorteio!")
            first_name = name2

        self.controller.local_first_player = first_player
        self.nextstep.configure(text=f"{first_name} jogará primeiro")
        self.button_win.grid(row=8, column=1, pady=20, ipadx=10)


class ScoreBoard(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(
            self, master, background=CARD_COLOR,
            highlightthickness=1, highlightbackground=CARD_BORDER_COLOR,
        )
        self.grid_columnconfigure(0, weight=1)

        title = tk.Label(
            self, text="PLACAR", font=SCORE_TITLE_FONT,
            background=CARD_COLOR, foreground=TEXT_COLOR,
        )
        title.grid(row=0, column=0, columnspan=2, pady=(12, 0))

        self.format_label = tk.Label(
            self, text="", font=SCORE_SMALL_FONT,
            background=CARD_COLOR, foreground=MUTED_TEXT_COLOR,
        )
        self.format_label.grid(row=1, column=0, columnspan=2)

        self.add_divider(row=2)

        self.name_labels = {}
        self.score_labels = {}
        for player in (1, 2):
            name = tk.Label(
                self, text="", font=SCORE_NAME_FONT, background=CARD_COLOR,
                wraplength=SCORE_NAME_WRAP, justify="left", anchor="w",
            )
            name.grid(row=2 + player, column=0, sticky="w",
                      padx=(14, 6), pady=4)

            score = tk.Label(
                self, text="0", font=SCORE_NUMBER_FONT, background=CARD_COLOR,
                width=2, anchor="e",
            )
            score.grid(row=2 + player, column=1, sticky="e",
                       padx=(0, 14), pady=4)

            self.name_labels[player] = name
            self.score_labels[player] = score

        self.add_divider(row=5)

        self.footer_label = tk.Label(
            self, text="", font=SCORE_SMALL_FONT,
            background=CARD_COLOR, foreground=MUTED_TEXT_COLOR,
        )
        self.footer_label.grid(row=6, column=0, columnspan=2, pady=(0, 12))

    def add_divider(self, row):
        divider = tk.Frame(self, height=1, background=CARD_BORDER_COLOR)
        divider.grid(row=row, column=0, columnspan=2, sticky="ew",
                     padx=12, pady=8)

    def setup(self, name1, name2, color1, color2, series):
        names = {1: name1, 2: name2}
        colors = {1: color1, 2: color2}
        for player in (1, 2):
            self.name_labels[player].configure(
                text=names[player], foreground=colors[player]
            )
            self.score_labels[player].configure(foreground=colors[player])

        self.format_label.configure(text=f"Melhor de {series.best_of}")
        self.refresh(series)

    def refresh(self, series):
        for player in (1, 2):
            self.score_labels[player].configure(text=str(series.wins[player]))

        if series.finished:
            footer = "Disputa encerrada"
        else:
            footer = f"Partida {series.current_game}"
            if series.draws:
                plural = "s" if series.draws > 1 else ""
                footer += f" · {series.draws} empate{plural}"
        self.footer_label.configure(text=footer)


class BaseBoardPage(tk.Frame):
    def __init__(self, window, controller):
        ttk.Frame.__init__(self, window, style="TFrame")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1, minsize=SCORE_COLUMN_WIDTH)
        self.grid_columnconfigure(2, weight=1, minsize=SCORE_COLUMN_WIDTH)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(11, weight=1)

        title = ttk.Label(self, text="Connect4", style="Title.TLabel")
        title.configure(font=("Arial", 26, "bold"))
        title.grid(row=1, column=1, pady=(20, 0))

        self.statement = ttk.Label(
            self, text="Escolha uma coluna", style="Statement.TLabel",
            wraplength=420, justify="center",
        )
        self.statement.grid(row=4, column=1, pady=(60, 0))

        self.detail = ttk.Label(
            self, text="", style="Body.TLabel",
            wraplength=420, justify="center",
        )
        self.detail.grid(row=5, column=1, pady=(6, 0))

        self.button_row = ttk.Frame(self, width=350, height=40)
        self.button_row.grid(row=3, column=1, pady=(4, 0))

        self.buttons = []
        for i, letra in enumerate("abcdefg"):
            btn = ttk.Button(
                self.button_row,
                text=letra,
                style="Column.TButton",
                width=2,
                command=lambda col=i: self.choose_column(col)
            )
            btn.place(
                relx=0.01 + 0.98 * (i + 1) / 8,
                rely=0,
                anchor="n"
            )
            self.buttons.append(btn)

        self.menu_button = ttk.Button(
            self, text="Voltar ao Menu", style="Secondary.TButton",
            command=lambda: controller.show_frame(PlayMenuPage),
        )

        self.scoreboard = ScoreBoard(self)
        self.scoreboard.grid(row=2, column=2, sticky="nw", padx=(20, 0))

        self.canvas = None
        self.series = None
        self.next_game_job = None

        self.start_series()

    def on_show(self):
        self.start_series()

    def player_name(self, player):
        raise NotImplementedError

    def first_starter(self):
        raise NotImplementedError

    def new_game(self):
        raise NotImplementedError

    def choose_column(self, column):
        raise NotImplementedError

    def player_color(self, player):
        if player == 1:
            return PLAYER1_COLOR
        return PLAYER2_COLOR

    def start_series(self):
        self.cancel_next_game()

        self.series = c4.BestOfSeries(
            self.controller.series_best_of, self.first_starter()
        )
        self.scoreboard.setup(
            self.player_name(1), self.player_name(2),
            self.player_color(1), self.player_color(2), self.series,
        )
        self.new_game()

    def game_finished(self, state):
        self.disable_columns()

        series_over = self.series.record_game(state)
        self.scoreboard.refresh(self.series)

        if series_over:
            self.show_series_result()
            return

        if state == c4.DRAW:
            self.statement.configure(
                text="Empate! Ninguém pontua.", foreground=TEXT_COLOR
            )
        else:
            winner = 1 if state == c4.PLAYER1_WINS else 2
            self.statement.configure(
                text=f"{self.player_name(winner)} venceu a partida!",
                foreground=self.player_color(winner),
            )
        self.detail.configure(text="Próxima partida em instantes...")

        self.next_game_job = self.after(NEXT_GAME_DELAY_MS, self.begin_next_game)

    def begin_next_game(self):
        self.next_game_job = None
        self.new_game()

    def cancel_next_game(self):
        if self.next_game_job is not None:
            self.after_cancel(self.next_game_job)
            self.next_game_job = None

    def show_series_result(self):
        winner = self.series.winner
        name1 = self.player_name(1)
        name2 = self.player_name(2)
        wins1 = self.series.wins[1]
        wins2 = self.series.wins[2]

        self.statement.configure(
            text=f"{self.player_name(winner)} venceu a melhor de "
                 f"{self.series.best_of}!",
            foreground=self.player_color(winner),
        )
        self.detail.configure(
            text=f"Placar final: {name1} {wins1} x {wins2} {name2}"
        )
        self.show_menu_button()

    def redraw_board(self):
        graph = c4.plotgraphicalboard(self.board)
        old_canvas = self.canvas

        self.canvas = FigureCanvasTkAgg(graph, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=1)

        if old_canvas is not None:
            old_canvas.get_tk_widget().destroy()

    def enable_columns(self):
        for i, button in enumerate(self.buttons):
            button.configure(command=lambda col=i: self.choose_column(col))

    def disable_columns(self):
        for button in self.buttons:
            button.configure(command=donothing)

    def show_menu_button(self):
        self.menu_button.grid(row=10, column=1, pady=(16, 10))

    def hide_menu_button(self):
        self.menu_button.grid_remove()


class ComputerBoardPage(BaseBoardPage):
    computer_starts = False

    def player_name(self, player):
        if player == 1:
            return "Você"
        return "Máquina"

    def first_starter(self):
        return 2 if self.computer_starts else 1

    def new_game(self):
        self.board = c4.makearrayboard()

        if self.series.starter == 2:
            self.computer_move()

        self.redraw_board()
        self.enable_columns()
        self.statement.configure(text="Escolha uma coluna", foreground=TEXT_COLOR)
        self.detail.configure(text="")
        self.hide_menu_button()

    def computer_move(self):
        computercolumn = c4.decidecomputermove(self.board)
        while not c4.checkifvalid(self.board, computercolumn):
            computercolumn = c4.decidecomputermove(self.board)
        c4.docomputermove(self.board, computercolumn)

    def choose_column(self, column):
        if c4.checkifvalid(self.board, column):
            c4.dousermove(self.board, column)
            self.continuegame()

    def continuegame(self):
        gamestate = c4.checkgamestate(self.board)

        if gamestate == c4.GAME_ONGOING:
            self.computer_move()
            gamestate = c4.checkgamestate(self.board)

        self.redraw_board()

        if gamestate != c4.GAME_ONGOING:
            self.game_finished(gamestate)


class BoardPageWin(ComputerBoardPage):
    computer_starts = False


class BoardPageLose(ComputerBoardPage):
    computer_starts = True


class LocalBoardPage(BaseBoardPage):
    def player_name(self, player):
        if player == 1:
            return self.controller.player1_name
        return self.controller.player2_name

    def first_starter(self):
        return self.controller.local_first_player

    def new_game(self):
        self.match = c4.LocalMatch(self.series.starter)
        self.board = self.match.board

        self.redraw_board()
        self.enable_columns()
        self.show_turn()
        self.detail.configure(text="")
        self.hide_menu_button()

    def show_turn(self):
        self.statement.configure(
            text=f"Vez de {self.player_name(self.match.current_player)}",
            foreground=self.player_color(self.match.current_player),
        )

    def choose_column(self, column):
        if self.match.play(column) != c4.MOVE_OK:
            return

        self.redraw_board()

        if not self.match.finished:
            self.show_turn()
        else:
            self.game_finished(self.match.state)


def donothing():
    pass


def runapp(app):
    try:
        app.mainloop()
    except UnicodeDecodeError:
        runapp(app)


app = Connect4App()
runapp(app)
