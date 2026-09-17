import string
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Aqui a gente diz para o matplotlib usar o "TkAgg" como motor de desenho.
#
# Isso é necessário porque o TkAgg é o motor que sabe desenhar dentro de
# uma janela feita com Tkinter (a biblioteca de interface gráfica do Python).
# Sem essa linha, o gráfico do tabuleiro não apareceria corretamente na janela.
matplotlib.use("TkAgg")


def makegraphicalboard():
    """
    Cria um tabuleiro gráfico vazio, já com o tamanho certo, pronto para
    receber os desenhos das peças depois.
    """
    # "Figure" é basicamente uma folha de desenho em branco do matplotlib.
    #
    # figsize=(7, 7) define que a folha vai ter 7 x 7 polegadas.
    # dpi=50 define a resolução (quantos pontos por polegada). Esses dois
    # números juntos controlam o tamanho final, em pixels, da imagem do tabuleiro.
    fig = Figure(figsize=(7, 7), dpi=50)
    return fig


def makearrayboard():
    """
    Cria a matriz que representa o tabuleiro do jogo, começando tudo vazio.
    """
    # Um tabuleiro de Connect 4 (Lig 4) tem 6 linhas e 7 colunas.
    #
    # np.zeros([6, 7]) cria uma matriz desse tamanho preenchida inteiramente
    # com zeros. Cada zero representa uma casa vazia do tabuleiro. Conforme
    # o jogo avança, esses zeros vão sendo substituídos por outros números
    # que representam as peças do jogador e do computador.
    board = np.zeros([6, 7])
    return board


def cointoss(call):
    """
    Faz o "cara ou coroa" que decide quem começa jogando.

    A função recebe o palpite do jogador (0 ou 1, escolhido clicando em um
    botão) e compara com um número sorteado aleatoriamente.
    """
    # Sorteia um número aleatório: ou 0, ou 1.
    coin = np.random.randint(0, 2)

    # Se o número sorteado for igual ao palpite do jogador, o jogador acertou
    # e a função devolve True. Caso contrário, devolve False.
    if coin == call:
        return True
    else:
        return False


def checkifvalid(board, column):
    """
    Verifica se ainda é possível jogar em determinada coluna.

    Recebe o tabuleiro e o número da coluna escolhida. Retorna True se
    houver pelo menos uma casa vazia nessa coluna, e False se a coluna
    já estiver completamente cheia.
    """
    # Começa assumindo que a coluna está cheia (jogada inválida).
    valid = False

    # Percorre as 6 linhas daquela coluna, de cima a baixo.
    # Assim que encontra uma casa com valor 0 (vazia), marca como válida.
    for j in range(6):
        if board[j][column] == 0:
            valid = True

    return valid


def dousermove(board, column):
    """
    Executa a jogada do jogador humano em uma coluna escolhida.
    """
    # Essa variável serve para garantir que a peça seja colocada uma única
    # vez, na primeira casa vazia encontrada, e não em todas as casas vazias.
    placed = False

    # As peças de Connect 4 "caem" por gravidade, então precisamos procurar
    # a partir da linha mais baixa (linha 5) até a mais alta (linha 0).
    # O range(5, -1, -1) faz exatamente isso: 5, 4, 3, 2, 1, 0.
    for i in range(5, -1, -1):
        # Assim que acha a primeira casa vazia (valor 0) de baixo para cima,
        # e ainda não colocou nenhuma peça nesta jogada, coloca a peça ali.
        if ((board[i][column] == 0) and (placed == False)):
            board[i][column] = 1  # O número 1 representa a peça do jogador humano
            placed = True

    return board


def checkgamestate(board):
    """
    Verifica se alguém já venceu o jogo, olhando o tabuleiro inteiro.

    A ideia usada aqui é simples: cada peça do jogador vale 1 e cada peça
    do computador vale 5. Então, se somarmos 4 peças em sequência (na
    horizontal, vertical ou diagonal):

    - se a soma der 4, é porque as 4 peças são do jogador (1+1+1+1 = 4)
      então o jogador venceu.
    - se a soma der 20, é porque as 4 peças são do computador (5+5+5+5 = 20)
      então o computador venceu.

    Quando alguém vence, a função troca o valor das 4 peças vencedoras por
    um número bem maior (100 para o jogador, 200 para o computador). Isso é
    só um "marcador": mais tarde, na hora de desenhar o tabuleiro, o código
    usa esses números para saber quais peças precisam ser destacadas com
    uma linha.

    No final, a função devolve um número que representa o estado do jogo:
        0 -> o jogo ainda está rolando, ninguém venceu ainda
        1 -> o jogador venceu
        2 -> o computador venceu
        3 -> deu empate (o tabuleiro encheu e ninguém venceu)
    """
    # Começa supondo que o jogo ainda não terminou.
    gamestate = 0

    # ------------------------------------------------------------------
    # A partir daqui, checamos se o JOGADOR venceu (soma das peças == 4).
    # São 4 direções possíveis: horizontal, vertical, diagonal para a
    # direita e diagonal para a esquerda. A lógica se repete em cada uma,
    # só muda a direção em que somamos as 4 casas vizinhas.
    # ------------------------------------------------------------------

    # Checa vitória do jogador na HORIZONTAL.
    # Para cada linha (j), olha grupos de 4 colunas seguidas (i, i+1, i+2, i+3).
    for j in range(6):
        for i in range(4):
            if (board[j][i] + board[j][i+1]
                    + board[j][i+2] + board[j][i+3] == 4):

                # Encontrou uma vitória! Marca essas 4 casas com o valor 100,
                # para que depois elas sejam desenhadas de forma destacada.
                board[j][i] = 100
                board[j][i+1] = 100
                board[j][i+2] = 100
                board[j][i+3] = 100

                gamestate = 1

    # Checa vitória do jogador na VERTICAL.
    # Para cada coluna (i), olha grupos de 4 linhas seguidas, de baixo para cima.
    for i in range(7):
        for j in range(5, 2, -1):
            if (board[j][i] + board[j-1][i]
                    + board[j-2][i] + board[j-3][i] == 4):

                board[j][i] = 100
                board[j-1][i] = 100
                board[j-2][i] = 100
                board[j-3][i] = 100

                gamestate = 1

    # Checa vitória do jogador na DIAGONAL que sobe para a direita.
    for j in range(5, 2, -1):
        for i in range(4):
            if (board[j][i] + board[j-1][i+1]
                    + board[j-2][i+2] + board[j-3][i+3] == 4):

                board[j][i] = 100
                board[j-1][i+1] = 100
                board[j-2][i+2] = 100
                board[j-3][i+3] = 100

                gamestate = 1

    # Checa vitória do jogador na DIAGONAL que sobe para a esquerda.
    for j in range(5, 2, -1):
        for i in range(6, 2, -1):
            if (board[j][i] + board[j-1][i-1]
                    + board[j-2][i-2] + board[j-3][i-3] == 4):

                board[j][i] = 100
                board[j-1][i-1] = 100
                board[j-2][i-2] = 100
                board[j-3][i-3] = 100

                gamestate = 1

    # ------------------------------------------------------------------
    # Agora fazemos exatamente as mesmas 4 checagens acima, mas procurando
    # a soma 20 em vez de 4, já que 20 só é possível com 4 peças do
    # computador (5+5+5+5 = 20).
    # ------------------------------------------------------------------

    # Checa vitória do computador na HORIZONTAL.
    for j in range(6):
        for i in range(4):
            if (board[j][i] + board[j][i+1]
                    + board[j][i+2] + board[j][i+3] == 20):

                board[j][i] = 200
                board[j][i+1] = 200
                board[j][i+2] = 200
                board[j][i+3] = 200

                gamestate = 2

    # Checa vitória do computador na VERTICAL.
    for i in range(7):
        for j in range(5, 2, -1):
            if (board[j][i] + board[j-1][i]
                    + board[j-2][i] + board[j-3][i] == 20):

                board[j][i] = 200
                board[j-1][i] = 200
                board[j-2][i] = 200
                board[j-3][i] = 200

                gamestate = 2

    # Checa vitória do computador na DIAGONAL que sobe para a direita.
    for j in range(5, 2, -1):
        for i in range(4):
            if (board[j][i] + board[j-1][i+1]
                    + board[j-2][i+2] + board[j-3][i+3] == 20):

                board[j][i] = 200
                board[j-1][i+1] = 200
                board[j-2][i+2] = 200
                board[j-3][i+3] = 200

                gamestate = 2

    # Checa vitória do computador na DIAGONAL que sobe para a esquerda.
    for j in range(5, 2, -1):
        for i in range(6, 2, -1):
            if (board[j][i] + board[j-1][i-1]
                    + board[j-2][i-2] + board[j-3][i-3] == 20):

                board[j][i] = 200
                board[j-1][i-1] = 200
                board[j-2][i-2] = 200
                board[j-3][i-3] = 200

                gamestate = 2

    # ------------------------------------------------------------------
    # Por fim, checamos se deu empate.
    #
    # Um empate só acontece quando o tabuleiro está completamente cheio
    # e ninguém venceu. Para saber se ainda tem espaço livre, basta olhar
    # a linha do topo (linha 0): se qualquer casa dessa linha ainda tiver
    # valor 0, quer dizer que ainda dá pra jogar em alguma coluna.
    # ------------------------------------------------------------------
    possiblemoves = False
    for i in range(0, 7, 1):
        if (board[0][i] == 0):
            possiblemoves = True

    # Se não sobrou nenhuma jogada possível E ninguém venceu até agora,
    # então o resultado do jogo é empate.
    if ((possiblemoves == False) and (gamestate == 0)):
        gamestate = 3

    return gamestate


def plotgraphicalboard(board):
    """
    Desenha o tabuleiro na tela, com base nos números guardados na matriz.

    Primeiro a função separa as peças em grupos, de acordo com o valor
    de cada casa da matriz:

    - peças normais do jogador (valor 1)
    - peças normais do computador (valor 5)
    - peças vencedoras do jogador (valor 100)
    - peças vencedoras do computador (valor 200)

    Depois, desenha cada grupo de peças no gráfico, com cores diferentes,
    e liga as peças vencedoras com uma linha grossa.
    """

    # Cada uma dessas listas vai guardar as coordenadas (x = coluna, y = linha)
    # de um tipo de peça específico.
    userx = []
    usery = []
    userwonx = []
    userwony = []
    computerx = []
    computery = []
    computerwonx = []
    computerwony = []

    # Percorre todas as casas do tabuleiro (todas as linhas e colunas) e,
    # dependendo do número guardado em cada casa, guarda a posição (i, j)
    # na lista correspondente.
    for j in range(6):
        for i in range(7):
            if board[j][i] == 1:
                userx.append(i)
                usery.append(j)

            elif board[j][i] == 5:
                computerx.append(i)
                computery.append(j)

            elif board[j][i] == 100:
                userwonx.append(i)
                userwony.append(j)

            elif board[j][i] == 200:
                computerwonx.append(i)
                computerwony.append(j)

    # Transforma as listas em arrays do numpy. Isso é feito porque arrays
    # permitem fazer contas (como somar ou multiplicar) em todos os
    # elementos de uma vez, sem precisar de um laço "for".
    userx = np.array(userx) + 1
    usery = np.array(usery) - 1

    # No gráfico, o eixo Y cresce de baixo para cima. Mas na nossa matriz,
    # o índice das linhas cresce de cima para baixo (a linha 0 é a de cima).
    # Essa conta (multiplicar por -1 e somar 5) serve justamente para
    # "inverter" essa contagem, colocando a peça na altura certa do desenho.
    usery = ((usery * -1) + 5)

    userwonx = np.array(userwonx) + 1
    userwony = np.array(userwony) - 1
    userwony = ((userwony * -1) + 5)

    # Faz o mesmo ajuste de posição para as peças do computador.
    # Somamos 1 no x para a peça ficar centralizada na coluna certa do desenho.
    computerx = np.array(computerx) + 1

    # Subtraímos 1 no y, e depois invertemos, pelo mesmo motivo explicado acima.
    computery = np.array(computery) - 1
    computery = ((computery * -1) + 5)

    computerwonx = np.array(computerwonx) + 1
    computerwony = np.array(computerwony) - 1
    computerwony = ((computerwony * -1) + 5)

    # Cria a folha de desenho (figura) e um único gráfico (subplot) dentro dela.
    f = makegraphicalboard()
    a = f.add_subplot(111)

    # Ajusta as margens da figura para que o tabuleiro ocupe quase toda a área,
    # deixando bem pouca borda em branco ao redor.
    f.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.99)

    # Define os limites dos eixos: x vai de 0 a 8, y vai de 0 a 7.
    a.axis([0, 8, 0, 7])
    a.plot()

    # Desenha as peças normais do jogador como bolinhas vermelhas...
    a.plot(userx, usery, marker='o', markersize=50,
           linestyle=' ', color='red')

    # ...e as peças normais do computador como bolinhas amarelas.
    a.plot(computerx, computery, marker='o',
           markersize=50, linestyle=' ', color='yellow')

    # Desenha as peças vencedoras do computador ligadas por uma linha grossa,
    # para destacar visualmente qual foi a sequência que ganhou o jogo.
    a.plot(computerwonx, computerwony, marker='o', markersize=50,
           linestyle='-', linewidth=20, color='yellow')

    # Faz o mesmo destaque para as peças vencedoras do jogador.
    a.plot(userwonx, userwony, marker='o', markersize=50,
           linestyle='-', linewidth=20, color='red')
<<<<<<< HEAD

    # Desenha as linhas de grade preta, para ficar parecido com um tabuleiro de verdade.
    #
    # Observação: em versões antigas do matplotlib esse parâmetro se chamava
    # "b=True". Em versões mais novas (a partir da 3.5), esse nome foi
    # removido e substituído por "visible=True", por isso usamos o nome novo aqui.
=======
>>>>>>> 001939829ad2e8fcce1909a01922410a2b5d835b
    a.grid(visible=True, which='major', color='black', linestyle='-')

    return f


def decidecomputermove(board):
    """
    Decide em qual coluna o computador vai jogar.

    A estratégia do computador segue esta ordem de prioridade (a última
    regra que "bater" é a que vale, então as regras mais importantes
    ficam no final da função):

    1. Se possível, joga bem no meio do tabuleiro (essa é uma estratégia
       clássica do Connect 4, porque a coluna do meio participa de mais
       combinações de vitória).
    2. Bloqueia o jogador quando ele está a uma peça de vencer.
    3. Completa sua própria sequência quando está a uma peça de vencer.

    Um detalhe importante: antes de bloquear ou completar uma jogada, o
    computador confere se a casa logo ABAIXO da casa vazia já está ocupada.
    Ele só joga ali se a casa de baixo estiver cheia. Isso evita um erro
    bobo: tentar bloquear uma casa mais alta, mas acabar colocando a peça
    na casa vazia logo abaixo dela (porque as peças caem por gravidade).
    """
    # Começa com uma coluna totalmente aleatória. As regras abaixo vão
    # sobrescrever esse valor sempre que encontrarem uma jogada melhor.
    column = np.random.randint(0, 7)

    if board[5][3] == 0:  # se a coluna do meio (coluna 3) ainda tem espaço, joga nela
        column = 3

    elif board[5][2] == 0:
        column = 2  # evita que o jogador consiga montar um tipo específico de vitória

    # ------------------------------------------------------------------
    # A partir daqui, o computador procura por sequências de 3 peças do
    # jogador (soma == 3, ou seja, 1+1+1) com uma casa vazia ao lado.
    # Encontrando isso, ele deve bloquear jogando nessa casa vazia.
    # ------------------------------------------------------------------

    # Bloqueia o jogador na HORIZONTAL.
    for j in range(6):
        for i in range(4):
            if (board[j][i] + board[j][i+1]
                    + board[j][i+2] + board[j][i+3] == 3):

                if j == 5:
                    # Na linha mais baixa do tabuleiro não existe "casa de baixo"
                    # para checar, então o bloqueio pode ser feito direto.
                    if (board[j][i] == 0):
                        column = i

                    if (board[j][i+1] == 0):
                        column = i + 1

                    if (board[j][i+2] == 0):
                        column = i + 2

                    if (board[j][i+3] == 0):
                        column = i + 3

                else:
                    # Aqui sim conferimos a casa de baixo: só bloqueia se
                    # a casa vazia tiver uma peça logo abaixo dela.
                    if ((board[j][i] == 0) and (board[j+1][i] != 0)):
                        column = i

                    if ((board[j][i+1] == 0) and (board[j+1][i+1] != 0)):
                        column = i + 1

                    if ((board[j][i+2] == 0) and (board[j+1][i+2] != 0)):
                        column = i + 2

                    if ((board[j][i+3] == 0) and (board[j+1][i+3] != 0)):
                        column = i + 3

    # Bloqueia o jogador na VERTICAL.
    # Aqui não é preciso checar a casa de baixo, porque numa coluna a
    # única casa vazia possível é sempre a mais alta ocupada por cima
    # das peças já empilhadas.
    for i in range(7):
        for j in range(5, 2, -1):
            if (board[j][i] + board[j-1][i]
                    + board[j-2][i] + board[j-3][i] == 3):
                column = i

    # Bloqueia o jogador na DIAGONAL que sobe para a direita.
    for j in range(5, 2, -1):
        for i in range(4):
            if (board[j][i] + board[j-1][i+1]
                    + board[j-2][i+2] + board[j-3][i+3] == 3):

                if j == 5:
                    if(board[j][i] == 0):
                        column = i

                    if ((board[j-1][i+1] == 0) and (board[j][i+1] != 0)):
                        column = i + 1

                    if ((board[j-2][i+2] == 0) and (board[j-1][i+2] != 0)):
                        column = i + 2

                    if ((board[j-3][i+3] == 0) and (board[j-2][i+3] != 0)):
                        column = i + 3

                else:
                    if ((board[j][i] == 0) and board[j+1][i] != 0):
                        column = i

                    if ((board[j-1][i+1] == 0) and (board[j][i+1] != 0)):
                        column = i + 1

                    if ((board[j-2][i+2] == 0) and (board[j-1][i+2] != 0)):
                        column = i + 2

                    if ((board[j-3][i+3] == 0) and (board[j-2][i+3] != 0)):
                        column = i + 3

    # Bloqueia o jogador na DIAGONAL que sobe para a esquerda.
    for j in range(5, 2, -1):
        for i in range(6, 2, -1):
            if (board[j][i] + board[j-1][i-1]
                    + board[j-2][i-2] + board[j-3][i-3] == 3):

                if j == 5:
                    if(board[j][i] == 0):
                        column = i

                    if ((board[j-1][i-1] == 0) and (board[j][i-1] != 0)):
                        column = i - 1

                    if ((board[j-2][i-2] == 0) and (board[j-1][i-2] != 0)):
                        column = i - 2

                    if ((board[j-3][i-3] == 0) and (board[j-2][i-3] != 0)):
                        column = i - 3

                else:
                    if ((board[j][i] == 0) and board[j+1][i] != 0):
                        column = i

                    if ((board[j-1][i-1] == 0) and (board[j][i-1] != 0)):
                        column = i - 1

                    if ((board[j-2][i-2] == 0) and (board[j-1][i-2] != 0)):
                        column = i - 2

                    if ((board[j-3][i-3] == 0) and (board[j-2][i-3] != 0)):
                        column = i - 3

    # ------------------------------------------------------------------
    # Agora repetimos exatamente a mesma ideia acima, mas procurando por
    # sequências de 3 peças DO COMPUTADOR (soma == 15, ou seja, 5+5+5).
    # Encontrando isso, o computador deve completar a jogada e vencer.
    #
    # Como isso é verificado DEPOIS dos bloqueios acima, se houver as duas
    # situações ao mesmo tempo (o computador pode vencer E o jogador
    # também pode vencer), o computador vai preferir vencer o jogo em vez
    # de bloquear, porque essa checagem sobrescreve a coluna escolhida antes.
    # ------------------------------------------------------------------

    # Completa a vitória do computador na HORIZONTAL.
    for j in range(6):
        for i in range(4):
            if (board[j][i] + board[j][i+1]
                    + board[j][i+2] + board[j][i+3] == 15):

                if j == 5:
                    if (board[j][i] == 0):
                        column = i

                    if (board[j][i+1] == 0):
                        column = i + 1

                    if (board[j][i+2] == 0):
                        column = i + 2

                    if (board[j][i+3] == 0):
                        column = i + 3

                else:
                    if ((board[j][i] == 0) and (board[j+1][i] != 0)):
                        column = i

                    if ((board[j][i+1] == 0) and (board[j+1][i+1] != 0)):
                        column = i + 1

                    if ((board[j][i+2] == 0) and (board[j+1][i+2] != 0)):
                        column = i + 2

                    if ((board[j][i+3] == 0) and (board[j+1][i+3] != 0)):
                        column = i + 3

    # Completa a vitória do computador na VERTICAL.
    for i in range(7):
        for j in range(5, 2, -1):
            if (board[j][i] + board[j-1][i]
                    + board[j-2][i] + board[j-3][i] == 15):

                column = i

    # Completa a vitória do computador na DIAGONAL que sobe para a direita.
    for j in range(5, 2, -1):
        for i in range(4):
            if (board[j][i] + board[j-1][i+1]
                    + board[j-2][i+2] + board[j-3][i+3] == 15):

                if j == 5:
                    if(board[j][i] == 0):
                        column = i

                    if ((board[j-1][i+1] == 0) and (board[j][i+1] != 0)):
                        column = i + 1

                    if ((board[j-2][i+2] == 0) and (board[j-1][i+2] != 0)):
                        column = i + 2

                    if ((board[j-3][i+3] == 0) and (board[j-2][i+3] != 0)):
                        column = i + 3

                else:
                    if ((board[j][i] == 0) and board[j+1][i] != 0):
                        column = i

                    if ((board[j-1][i+1] == 0) and (board[j][i+1] != 0)):
                        column = i + 1

                    if ((board[j-2][i+2] == 0) and (board[j-1][i+2] != 0)):
                        column = i + 2

                    if ((board[j-3][i+3] == 0) and (board[j-2][i+3] != 0)):
                        column = i + 3

    # Completa a vitória do computador na DIAGONAL que sobe para a esquerda.
    for j in range(5, 2, -1):
        for i in range(6, 2, -1):
            if (board[j][i] + board[j-1][i-1]
                    + board[j-2][i-2] + board[j-3][i-3] == 15):

                if j == 5:
                    if(board[j][i] == 0):
                        column = i

                    if ((board[j-1][i-1] == 0) and (board[j][i-1] != 0)):
                        column = i - 1

                    if ((board[j-2][i-2] == 0) and (board[j-1][i-2] != 0)):
                        column = i - 2

                    if ((board[j-3][i-3] == 0) and (board[j-2][i-3] != 0)):
                        column = i - 3

                else:
                    if ((board[j][i] == 0) and board[j+1][i] != 0):
                        column = i

                    if ((board[j-1][i-1] == 0) and (board[j][i-1] != 0)):
                        column = i - 1

                    if ((board[j-2][i-2] == 0) and (board[j-1][i-2] != 0)):
                        column = i - 2

                    if ((board[j-3][i-3] == 0) and (board[j-2][i-3] != 0)):
                        column = i - 3

    return column


def docomputermove(board, column):
    """
    Executa a jogada do computador em uma coluna escolhida.

    Essa função funciona de forma quase idêntica à dousermove: ela também
    procura a primeira casa vazia de baixo para cima e coloca a peça ali.
    A única diferença é o número usado para representar a peça.
    """
    placed = False

    # Mesma lógica de "gravidade" usada na jogada do jogador: procura de
    # baixo para cima até achar a primeira casa vazia.
    for i in range(5, -1, -1):
        if ((board[i][column] == 0) and (placed == False)):
            board[i][column] = 5  # O número 5 representa a peça do computador
            placed = True

    return board
