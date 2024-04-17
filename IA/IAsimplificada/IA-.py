import pygame
import math
import random
import neat
import pickle

geracao = -1

pygame.init()
fontePontos = pygame.font.SysFont("Comic Sans", 25)

telaLargura = pygame.display.Info().current_w
telaAltura = pygame.display.Info().current_h - 220
tela = pygame.display.set_mode((telaLargura, telaAltura))

sizeVoce = 60
sizeCoisoide = 32


class Voce:
  def __init__(self):
    self.x = telaLargura/2
    self.mover = 0
    self.y = telaAltura - sizeVoce + 2


class Coisoide:
  def __init__(self):
    self.x = random.randint(0, telaLargura - 32)
    self.y = 0
    self.altura = 0


def Principal(genomas, config):

  def adicionar():
    if tempo > dificuldade*5 and len(bolas) < 5:
      bolas.append(Coisoide())
      return 0.0001
    elif tempo > dificuldade*4 and len(bolas) < 4:
      bolas.append(Coisoide())
      return 0.0001
    elif tempo > dificuldade*3 and len(bolas) < 3:
      bolas.append(Coisoide())
      return 0.0001
    elif tempo > dificuldade*2 and len(bolas) < 2:
      bolas.append(Coisoide())
      return 0.0001
    elif tempo < dificuldade and len(bolas) < 1:
      bolas.append(Coisoide())
      return 0
    return 0

  def colisao(indexVoce):
    x1 = voce.x + sizeVoce/2
    x2 = bola.x + sizeCoisoide/2
    y1 = voce.y + sizeVoce/2
    y2 = bola.y + sizeCoisoide/2

    r, g, b = 255 - (255/24) * indexVoce, (255/24) * \
        indexVoce if indexVoce % 2 == 0 else 0, (255/24) * indexVoce
    voceCor = (r, g, b)

    #pygame.draw.line(tela, (0, 255, 0), (x1, y1), (x2, y2))

    pygame.draw.circle(tela, voceCor, (x1, y1), sizeVoce / 2)
    pygame.draw.circle(tela, (255, 0, 0), (x2, y2), sizeCoisoide / 2)

    if math.sqrt(math.pow(x1 - x2, 2)+math.pow(y1 - y2, 2)) < sizeCoisoide/2+sizeVoce/2:
      return True

  global geracao
  geracao += 1
  
  if geracao == 50:
    pickle.dump(listaGenomas, open('genomas.p', 'wb'))

  redes = []
  listaGenomas = []
  voces = []
  for _, genoma in genomas:
    rede = neat.nn.FeedForwardNetwork.create(genoma, config)
    redes.append(rede)
    genoma.fitness = 0
    listaGenomas.append(genoma)
    voces.append(Voce())

  tempo = 0  # adicionado a cada frame
  velocidade = 10  # do jogador

  dificuldade = 250  # tempo para mais uma bola ser adicionada
  rapidez = 0.002  # rapidez com que bolas caem

  bolas = []

  posicao = 0

  rodando = True
  while rodando:
    tempo += 1
    tela.fill((0, 0, 0))

    texto = fontePontos.render(
        f'Pontos: {round(tempo / 100)}', True, (250, 250, 250))
    tela.blit(texto, (0, 0))
    ger = fontePontos.render(f'Geração: {geracao}', True, (250, 250, 250))
    tela.blit(ger, (telaLargura - ger.get_width(), 0))

    # mover bolas
    for bola in bolas:
      bola.altura += rapidez
      bola.y += bola.altura
      if bola.y > telaAltura + 1:
        bola.altura = 0
        bola.y = 0
        bola.x = random.randint(0, telaLargura - sizeCoisoide)

    # rapidez com que bolas caem

    if rapidez < .006:
      rapidez += adicionar()

    # IA
    for i, voce in enumerate(voces):
      listaGenomas[i].fitness += 0
      for bola in bolas:
        output = redes[i].activate((voce.x, bola.x, voce.y, bola.y))
        if output[0] > 0:
          listaGenomas[i].fitness += 1
          voce.x += 0.2*velocidade
          if voce.x > telaLargura - sizeVoce*2:
            listaGenomas[i].fitness -= 15
            voce.x -= 0.2*velocidade
            listaGenomas[i].fitness -= 21
        elif output[0] < 0:
          listaGenomas[i].fitness += 1
          voce.x -= 0.2*velocidade
          if voce.x < sizeVoce:
            listaGenomas[i].fitness -= 15
            voce.x += 0.2*velocidade
            listaGenomas[i].fitness -= 21

    # verificar colisão
    for bola in bolas:
      for i, voce in enumerate(voces):
        if colisao(i):
          posicao += 1
          voces.pop(i)
          listaGenomas[i].fitness -= 25
          listaGenomas.pop(i)
          redes.pop(i)
          print(posicao, '°\nTempo:', tempo)
          print('_____________________')

    pygame.display.update()

    if len(voces) == 0:
      rodando = False


def IA(caminhoConfig):
  config = neat.Config(neat.DefaultGenome,
                       neat.DefaultReproduction,
                       neat.DefaultSpeciesSet,
                       neat.DefaultStagnation,
                       caminhoConfig)
  populacao = neat.Population(config)
  populacao.add_reporter(neat.StdOutReporter(True))
  populacao.add_reporter(neat.StatisticsReporter())

  populacao.run(Principal, 20)


if __name__ == '__main__':
  caminhoConfig = r'C:\Users\MatRod\Downloads\Arquivos\ArquivosDeProgramas\Prog\Python\PythonProjectz\Projectz\Pou2 e IA\ConfigIA.txt'
  IA(caminhoConfig)
