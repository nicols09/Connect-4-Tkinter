import platform
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
import connect4module as c4

# Define o motor de desenho do matplotlib como "TkAgg", que é o que sabe
# desenhar gráficos dentro de uma janela feita com Tkinter.
matplotlib.use("TkAgg")

# Aqui a gente define 3 tamanhos de fonte que serão reaproveitados em
# várias telas do jogo, para manter um visual parecido em todo o app.
# "large" é usado nos títulos, "med" nos textos normais e "small" em
# espaços que servem só para dar um respiro visual entre elementos.
large = ("ComicSansMS", 40)
med = ("ComicSansMS", 30)
small = ("ComicSansMS", 20)


class Connect4App(tk.Tk):
    """
    Classe controladora. É ela quem comanda o aplicativo inteiro.

    A ideia geral aqui é a seguinte: em vez de abrir uma janela nova
    toda vez que o jogo muda de tela, criamos todas as telas (frames)
    de uma vez só, empilhadas umas sobre as outras, dentro da mesma
    janela. Depois, só "levantamos" a tela que queremos mostrar para
    o usuário, escondendo as outras por trás.
    """

    def __init__(self):

        # Cria a janela principal do aplicativo, que vai conter todas as telas.
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, "Connect 4 Game")

        # "container" é uma caixa que vai servir de base para empilhar
        # todas as telas do jogo, uma em cima da outra.
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Esse dicionário vai guardar cada tela do jogo, para que a gente
        # consiga encontrá-la rapidamente pelo nome da classe depois.
        self.frames = {}

        # Aqui a gente cria cada uma das 4 telas do jogo (StartPage,
        # TossPage, BoardPageLose e BoardPageWin), uma por uma, e vai
        # empilhando todas dentro do container, na mesma posição
        # (linha 0, coluna 0). Como todas ficam exatamente no mesmo
        # lugar, dá pra "trocar de tela" simplesmente trazendo a tela
        # certa para frente das outras.
        for f in (StartPage, TossPage, BoardPageLose, BoardPageWin):
            frame = f(container, self)
            self.frames[f] = frame   # guarda a tela no dicionário, usando a classe como chave
            frame.grid(row=0, column=0, sticky="nsew")
            self.show_frame(StartPage)

    def show_frame(self, page):
        """
        Traz a tela pedida para a frente, escondendo as outras atrás dela.
        """
        # Busca a tela certa dentro do dicionário e a levanta para o topo,
        # tornando-a visível para o usuário.
        frame = self.frames[page]
        frame.tkraise()


class StartPage(tk.Frame):
    """
    Tela inicial do jogo.

    É a primeira coisa que o usuário vê: uma mensagem de boas-vindas e
    um botão para começar a partida.
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window)
        self.grid_columnconfigure(1, weight=1)

        # Título de boas-vindas, exibido bem grande no topo da tela.
        title = ttk.Label(self, text="Bem-vindo ao Connect 4!", font=large)
        title.grid(row=1, column=1)

        # Botão "Begin": quando clicado, chama show_frame para mostrar a
        # próxima tela (TossPage), onde o cara-ou-coroa vai acontecer.
        button_continue = ttk.Button(self, text="Entrar", command=lambda:
                                     controller.show_frame(TossPage))
        button_continue.grid(row=2, column=1)


class TossPage(tk.Frame):
    """
    Tela do cara-ou-coroa.

    Nesta tela, o jogador escolhe "cara" ou "coroa" para decidir quem
    vai jogar primeiro: ele ou o computador.
    """

    def __init__(self, window, controller):
        ttk.Frame.__init__(self, window)
        self.grid_columnconfigure(1, weight=1)

        title = ttk.Label(self, text="Faça sua escolha", font=large)
        title.grid(row=1, column=1)

        toss = ttk.Label(self, text="Escolha Cara ou Coroa", font=med)
        toss.grid(row=2, column=1)

        # Cria os botões de "Heads" (cara) e "Tails" (coroa).
        #
        # Repare que cada botão, além de rodar a função heads/tails, também
        # já recebe de presente as referências dos labels e dos outros
        # botões da tela (outcome, nextstep, button_win, button_lose).
        # Isso é feito porque as funções heads() e tails() precisam mudar
        # o texto desses elementos depois que o usuário decide sua jogada.
        button_heads = ttk.Button(self, text="Cara", command=lambda:
                                  self.heads(outcome,
                                             nextstep,
                                             button_heads,
                                             button_tails,
                                             button_win,
                                             button_lose), width=6)
        button_tails = ttk.Button(self, text="Coroa", command=lambda:
                                  self.tails(outcome,
                                             nextstep,
                                             button_heads,
                                             button_tails,
                                             button_win,
                                             button_lose), width=6)
        button_heads.grid(row=3, column=1)
        button_tails.grid(row=4, column=1)

        # Esses dois textos (labels) começam vazios. Eles só vão ganhar
        # conteúdo depois que o usuário clicar em "Heads" ou "Tails",
        # mostrando se ele ganhou ou perdeu o sorteio, e quem vai começar.
        outcome = ttk.Label(self, text="", font=med)
        outcome.grid(row=6, column=1)
        nextstep = ttk.Label(self, text="", font=med)
        nextstep.grid(row=7, column=1)

        # Esses botões de "Continue" são criados aqui, mas ainda não são
        # posicionados na tela (por isso o usuário não os vê ainda).
        # Eles só vão aparecer (usando .grid) depois que o resultado do
        # sorteio for conhecido, dentro das funções heads() e tails().
        button_win = ttk.Button(self, text="Continue", command=lambda:
                                controller.show_frame(BoardPageWin))
        button_lose = ttk.Button(self, text="Continue", command=lambda:
                                 controller.show_frame(BoardPageLose))

    def heads(self, outcome, nextstep, button_heads, button_tails, button_win, button_lose):
        """
        Executada quando o jogador escolhe "Heads" (cara).

        Roda o sorteio (cointoss) do módulo connect4module com call = 1.
        Desativa os botões de escolha, para o usuário não poder escolher
        de novo. Atualiza os textos com o resultado do sorteio. E, por
        fim, mostra o botão de "Continue" que leva para a tela certa,
        dependendo se o jogador ganhou ou perdeu o sorteio.
        """
        # call = 1 representa a escolha "cara" dentro da função cointoss.
        call = 1
        result = c4.cointoss(call)

        # Desliga os dois botões, trocando seu comando por "donothing"
        # (uma função que não faz nada). Isso impede que o jogador clique
        # de novo depois de já ter escolhido.
        button_tails.configure(text="", command=donothing)
        button_heads.configure(command=donothing)

        if result == True:
            # O jogador acertou o sorteio, então ele começa jogando.
            outcome.configure(text="Você venceu!")
            nextstep.configure(text="Você começará jogando")
            # Mostra o botão que leva para a tela em que o jogador começa (BoardPageWin).
            button_win.grid(row=8, column=1)
        else:
            # O jogador errou o sorteio, então o computador começa jogando.
            outcome.configure(text="Você perdeu!")
            nextstep.configure(text="O computador começará jogando")
            # Mostra o botão que leva para a tela em que o computador começa (BoardPageLose).
            button_lose.grid(row=8, column=1)

        # Força a atualização visual imediata desses elementos na tela.
        outcome.update()
        nextstep.update()
        button_heads.update()
        button_tails.update()
        return

    def tails(self, outcome, nextstep, button_heads, button_tails, button_win, button_lose):
        """
        Executada quando o jogador escolhe "Tails" (coroa).

        Funciona de forma idêntica à função heads(), só muda o valor de
        "call" (agora é 0, representando a escolha "coroa").
        """
        call = 0
        result = c4.cointoss(call)
        button_heads.configure(text="", command=donothing)
        button_tails.configure(command=donothing)
        if result == True:
            outcome.configure(text="Você venceu!")
            nextstep.configure(text="Você começará jogando")
            button_win.grid(row=8, column=1)
        else:
            outcome.configure(text="Você perdeu!")
            nextstep.configure(text="O computador começará jogando")
            button_lose.grid(row=8, column=1)
        outcome.update()
        nextstep.update()
        button_heads.update()
        button_tails.update()
        return


class BoardPageLose(tk.Frame):
    """
    Tela principal do jogo, usada quando o jogador PERDEU o sorteio.

    Como o jogador perdeu o cara-ou-coroa, o computador precisa jogar
    primeiro, antes mesmo do tabuleiro ser mostrado ao usuário pela
    primeira vez.
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window)

        title = ttk.Label(
            self, text="Connect 4 Game", font=large)
        title.grid(row=1, column=1)

        # Um espaço em branco só para dar um respiro visual entre o
        # tabuleiro e o texto de instrução logo abaixo.
        separator = ttk.Label(self, text=" ", font=small)
        separator.grid(row=3, column=1)

        # "statement" e os botões de coluna agora são guardados como
        # atributos (self.xxx), e não mais variáveis locais do __init__.
        # Isso é necessário para que o botão de "Restart" consiga
        # encontrá-los e reconfigurá-los depois, mesmo esse __init__ só
        # rodando uma única vez durante toda a vida do aplicativo.
        self.statement = ttk.Label(self, text="Escolha uma coluna", font=med)
        self.statement.grid(row=4, column=1)

        # Cria um botão para cada uma das 7 colunas do tabuleiro (de "a" a
        # "g"). Agora todos chamam a mesma função "choose_column",
        # passando apenas o número da coluna (0 a 6) — isso evita repetir
        # 7 funções quase idênticas (choose_a, choose_b, ...).
        button_a = ttk.Button(self, text="a", command=lambda:
                              self.choose_column(0), width=1)
        button_b = ttk.Button(self, text="b", command=lambda:
                              self.choose_column(1), width=1)
        button_c = ttk.Button(self, text="c", command=lambda:
                              self.choose_column(2), width=1)
        button_d = ttk.Button(self, text="d", command=lambda:
                              self.choose_column(3), width=1)
        button_e = ttk.Button(self, text="e", command=lambda:
                              self.choose_column(4), width=1)
        button_f = ttk.Button(self, text="f", command=lambda:
                              self.choose_column(5), width=1)
        button_g = ttk.Button(self, text="g", command=lambda:
                              self.choose_column(6), width=1)

        # O Tkinter posiciona os botões em coordenadas fixas de pixel (x, y)
        # para ficarem alinhados certinho embaixo de cada coluna do
        # tabuleiro desenhado. Só que essas coordenadas variam um pouco
        # dependendo do sistema operacional (Windows desenha com uma
        # pequena diferença de espaçamento em relação a Mac/Linux), por
        # isso existe essa checagem de plataforma.
        if platform.system() == "Windows":
            button_a.place(x=68, y=410)
            button_b.place(x=111, y=410)
            button_c.place(x=154, y=410)
            button_d.place(x=197, y=410)
            button_e.place(x=240, y=410)
            button_f.place(x=283, y=410)
            button_g.place(x=327, y=410)
        else:
            button_a.place(x=25, y=410)
            button_b.place(x=68, y=410)
            button_c.place(x=111, y=410)
            button_d.place(x=154, y=410)
            button_e.place(x=197, y=410)
            button_f.place(x=240, y=410)
            button_g.place(x=283, y=410)

        # Guarda todos os botões numa lista. Isso facilita mexer em todos
        # eles de uma vez (por exemplo, desativar todos quando o jogo acabar).
        self.buttons = [button_a, button_b, button_c,
                         button_d, button_e, button_f, button_g]

        # Botão de reiniciar a partida. É criado aqui junto com o resto da
        # tela, mas só fica visível (via .grid) depois que a partida atual
        # termina — veja end_game() e new_game() mais abaixo.
        self.restart_button = ttk.Button(
            self, text="Restart", command=self.new_game)

        # Começa a primeira partida desta tela assim que ela é criada.
        self.new_game()

    def new_game(self):
        """
        (Re)inicia a partida do zero, nesta mesma tela.

        É chamada tanto na primeira vez que a tela aparece quanto toda
        vez que o jogador clica no botão "Restart" depois do fim de uma
        partida anterior.
        """
        # Cria um tabuleiro novo e vazio.
        self.board = c4.makearrayboard()

        # Como o jogador perdeu o sorteio nesta tela, o computador sempre
        # joga primeiro. O laço "while" é uma segurança: a função
        # decidecomputermove pode, em teoria, sugerir uma coluna já cheia,
        # então repetimos a escolha até cair numa coluna válida.
        computercolumn = c4.decidecomputermove(self.board)
        while c4.checkifvalid(self.board, computercolumn) != True:
            computercolumn = c4.decidecomputermove(self.board)
        c4.docomputermove(self.board, computercolumn)

        self.redraw_board()

        # Reativa todos os botões de coluna, garantindo que voltem a
        # chamar choose_column normalmente (e não mais "donothing", que é
        # o que fica configurado quando a partida anterior termina).
        for i, button in enumerate(self.buttons):
            button.configure(command=lambda col=i: self.choose_column(col))
            button.update()

        self.statement.configure(text="Escolha uma coluna")
        self.statement.update()

        # Esconde o botão de reiniciar até a partida atual terminar de novo.
        self.restart_button.grid_remove()

    def redraw_board(self):
        """Desenha (ou redesenha) o tabuleiro atual na tela."""
        graph = c4.plotgraphicalboard(self.board)
        canvas = FigureCanvasTkAgg(graph, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1)

    def choose_column(self, column):
        # Antes de jogar, sempre confere se a coluna ainda tem espaço
        # livre (checkifvalid). Só faz a jogada e chama continuegame se a
        # coluna realmente estiver disponível.
        if c4.checkifvalid(self.board, column) == True:
            c4.dousermove(self.board, column)
            self.continuegame()

    def continuegame(self):
        """
        Essa é a função principal que toca o jogo para frente.

        Ela é chamada toda vez que o jogador termina sua jogada. O
        funcionamento é assim:

        1. Confere o estado atual do jogo (checkgamestate).
        2. Se o jogo ainda não acabou (gamestate == 0), faz o computador
           jogar também, e confere de novo o estado do jogo (pois a
           jogada do computador pode ter terminado a partida).
        3. Dependendo do resultado final (jogador venceu, computador
           venceu ou empate), atualiza o texto na tela, desativa os
           botões (quando aplicável) e mostra o botão de reiniciar.
        """

        gamestate = c4.checkgamestate(self.board)

        if gamestate == 0:
            # O jogo ainda não acabou depois da jogada do usuário, então
            # é a vez do computador jogar.
            computercolumn = c4.decidecomputermove(self.board)
            while c4.checkifvalid(self.board, computercolumn) != True:
                computercolumn = c4.decidecomputermove(self.board)
            c4.docomputermove(self.board, computercolumn)

            # Depois da jogada do computador, checamos o estado do jogo
            # de novo, porque essa jogada pode ter feito o computador vencer.
            gamestate = c4.checkgamestate(self.board)

            # Redesenha o tabuleiro, agora já com a nova peça do computador.
            self.redraw_board()

        if gamestate == 1:
            # O jogador venceu o jogo. Redesenha o tabuleiro (agora com a
            # sequência vencedora destacada, feita pela própria
            # checkgamestate) e encerra a partida.
            self.redraw_board()
            self.end_game("You Won!")
            print("You win")

        if gamestate == 2:
            # O computador venceu o jogo.
            self.end_game("You Lost!")
            print("You lose")

        if gamestate == 3:
            # Deu empate: o tabuleiro encheu e ninguém venceu. Diferente
            # dos outros dois casos, aqui os botões de coluna não fazem
            # mais sentido de qualquer forma (não há espaço livre), mas o
            # botão de reiniciar aparece do mesmo jeito.
            self.redraw_board()
            self.statement.configure(text="It's a draw!")
            self.statement.update()
            self.restart_button.grid(row=9, column=1)
            print("You draw")

    def end_game(self, message):
        """
        Reaproveitada tanto para vitória quanto para derrota: desativa
        todos os botões de coluna (já que a partida acabou e não faz mais
        sentido permitir novas jogadas), mostra a mensagem final e exibe
        o botão de reiniciar.
        """
        for button in self.buttons:
            button.configure(command=donothing)
            button.update()
        self.statement.configure(text=message)
        self.statement.update()
        self.restart_button.grid(row=9, column=1)


class BoardPageWin(tk.Frame):
    """
    Tela principal do jogo, usada quando o jogador GANHOU o sorteio.

    É praticamente idêntica à BoardPageLose, com uma diferença
    importante: como o jogador ganhou o cara-ou-coroa, é ele quem começa
    jogando. Por isso, o tabuleiro é criado e mostrado ainda totalmente
    vazio, sem nenhuma jogada do computador antes.
    """

    def __init__(self, window, controller):

        ttk.Frame.__init__(self, window)

        title = ttk.Label(self, text="Connect 4 Game", font=large)
        title.grid(row=1, column=1)

        separator = ttk.Label(self, text=" ", font=small)
        separator.grid(row=3, column=1)
        self.statement = ttk.Label(self, text="Escolha uma coluna", font=med)
        self.statement.grid(row=4, column=1)

        # Os botões de coluna (a até g) e o posicionamento deles na tela
        # funcionam exatamente da mesma forma explicada em BoardPageLose.
        button_a = ttk.Button(self, text="a", command=lambda:
                              self.choose_column(0), width=1)
        button_b = ttk.Button(self, text="b", command=lambda:
                              self.choose_column(1), width=1)
        button_c = ttk.Button(self, text="c", command=lambda:
                              self.choose_column(2), width=1)
        button_d = ttk.Button(self, text="d", command=lambda:
                              self.choose_column(3), width=1)
        button_e = ttk.Button(self, text="e", command=lambda:
                              self.choose_column(4), width=1)
        button_f = ttk.Button(self, text="f", command=lambda:
                              self.choose_column(5), width=1)
        button_g = ttk.Button(self, text="g", command=lambda:
                              self.choose_column(6), width=1)

        if platform.system() == "Windows":
            button_a.place(x=68, y=410)
            button_b.place(x=111, y=410)
            button_c.place(x=154, y=410)
            button_d.place(x=197, y=410)
            button_e.place(x=240, y=410)
            button_f.place(x=283, y=410)
            button_g.place(x=327, y=410)
        else:
            button_a.place(x=25, y=410)
            button_b.place(x=68, y=410)
            button_c.place(x=111, y=410)
            button_d.place(x=154, y=410)
            button_e.place(x=197, y=410)
            button_f.place(x=240, y=410)
            button_g.place(x=283, y=410)

        self.buttons = [button_a, button_b, button_c,
                         button_d, button_e, button_f, button_g]

        self.restart_button = ttk.Button(
            self, text="Restart", command=self.new_game)

        # Começa a primeira partida desta tela assim que ela é criada.
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
        mesma forma explicada em BoardPageLose.continuegame: checa o
        estado do jogo, faz o computador jogar se a partida continuar,
        e atualiza a tela conforme o resultado final (vitória, derrota
        ou empate).
        """

        gamestate = c4.checkgamestate(self.board)

        if gamestate == 0:
            # Ainda não acabou: é a vez do computador jogar.
            computercolumn = c4.decidecomputermove(self.board)
            while c4.checkifvalid(self.board, computercolumn) != True:
                computercolumn = c4.decidecomputermove(self.board)
            c4.docomputermove(self.board, computercolumn)
            gamestate = c4.checkgamestate(self.board)
            self.redraw_board()

        if gamestate == 1:
            # O jogador venceu: redesenha o tabuleiro e encerra a partida.
            self.redraw_board()
            self.end_game("Você Venceu!")

        if gamestate == 2:
            # O computador venceu.
            self.end_game("Você Perdeu!")

        if gamestate == 3:
            # Deu empate: redesenha o tabuleiro, mostra a mensagem e
            # exibe o botão de reiniciar.
            self.redraw_board()
            self.statement.configure(text="O jogo empatou!")
            self.statement.update()
            self.restart_button.grid(row=9, column=1)

    def end_game(self, message):
        """
        Reaproveitada tanto para vitória quanto para derrota: desativa
        os botões de coluna, mostra a mensagem final e exibe o botão de
        reiniciar.
        """
        for button in self.buttons:
            button.configure(command=donothing)
            button.update()
        self.statement.configure(text=message)
        self.statement.update()
        self.restart_button.grid(row=9, column=1)


def donothing():
    """
    Função vazia, que literalmente não faz nada.

    Ela é usada como "comando substituto" de um botão quando queremos
    que ele pareça desativado (o botão continua visível e clicável na
    tela, mas nada acontece ao clicar nele).
    """
    pass


def runapp(app):
    """
    Roda o loop principal do aplicativo (mainloop).

    Existe um problema conhecido no Mac, em que o loop principal do
    Tkinter às vezes lança um erro chamado UnicodeDecodeError sem
    motivo real, o que derrubaria o programa. Para evitar isso, essa
    função "pega" esse erro específico e simplesmente reinicia o
    mainloop, como se nada tivesse acontecido.
    """
    try:
        app.mainloop()
    except UnicodeDecodeError:
        runapp(app)


# Cria a aplicação e a coloca para rodar. Essas duas linhas são o ponto
# de entrada do programa: é a partir daqui que a janela do jogo aparece
# na tela e o usuário pode começar a jogar.
app = Connect4App()
runapp(app)
