import pygame
import random
from pygame.locals import *
from levels import *

def checkpos(x,y,array):
    freeTiles = []
    for i in [(0,1),(0,-1),(0,0),(1,0),(-1,0)]:
        if  array[(x+i[0])%len(array)][(y+i[1])%len(array[x])][0] in ["b","v","p"]:
            freeTiles.append(i)

    #ici

    return freeTiles

def enemyCanMove(e):
    if e[2] == "0" and moveCounter % 3 == 0:
        return True
    if e[2] == "1" and moveCounter %2 == 0:
        return True
    if e[2] == "2":
        return True
    return False


#fonction qui gère les mouvements du joueur + enimies
def move(speed):
    points = 0
    playerpos = (-1,-1)
    entitiesDone = []
    x1,y1 = speed #direction du mouvement
    irange = range(len(levelMap))
    if x1 < 0:
        irange = range(len(levelMap)-1,-1,-1)

    for i in irange: #on parcour le niveau

        jrange = range(len(levelMap[i]))
        if y1 < 0:
            jrange = range(len(levelMap[i])-1,-1,-1)
        for j in jrange:
            if levelMap[i][j][0] == "p" and levelMap[i][j] not in entitiesDone:
                entitiesDone.append(levelMap[i][j])
                playerpos = (i,j)
                #la case est une bille on peut y aller et on renvoi 1
                if  levelMap[(i+x1)%len(levelMap)][(j+y1)%len(levelMap[i])][0] == "b":
                    levelMap[(i+x1)%len(levelMap)][(j+y1)%len(levelMap[i])] = levelMap[i][j]
                    levelMap[i][j] = "v"
                    points = 1

                #la case est vide on peut y aller
                if  levelMap[(i+x1)%len(levelMap)][(j+y1)%len(levelMap[i])][0] == "v":
                    levelMap[(i+x1)%len(levelMap)][(j+y1)%len(levelMap[i])] = levelMap[i][j]
                    levelMap[i][j] = "v"

                if  levelMap[(i+x1)%len(levelMap)][(j+y1)%len(levelMap[i])][0] == "e":
                    levelMap[i][j] = "v"

            if levelMap[i][j][0] == "e" and levelMap[i][j] not in entitiesDone and speed != (0,0):
                if enemyCanMove(levelMap[i][j]):
                    entitiesDone.append(levelMap[i][j])
                    possibleSpeeds = checkpos(i,j,levelMap)
                    try:
                        x2,y2 = random.choice(possibleSpeeds)
                    except:
                        x2,y2 = 0,0
                    levelMap[(i+x2)%len(levelMap)][(j+y2)%len(levelMap[i])] = levelMap[i][j]
                    levelMap[i][j] = "v"

    if playerpos == (-1,-1):
        return -1

    #on ne peut pas aller sur la case
    return points

#affiche a l'ecran l'image contenue dans path, au coordonées (x,y) et de taille (w,h)
def renderSprite(window,path, x, y, w, h):
    try:
        sprite = pygame.image.load("assets/"+str(path)+".png").convert_alpha()
        sprite = pygame.transform.scale(sprite, (w, h))
        window.blit(sprite,(x,y))
    except:
        print("error loading texture of " + str(path) + ".png")
        exit()


#initialisation de la fenetre de jeu, et des drapeaux
pygame.init()
pygame.font.init()
scoreFont = pygame.font.SysFont('PrStart.ttf', 30)
running = True
levelSelect = True

while running:

    #au debut on selectionne un niveau
    if levelSelect:
        level = 0
        starting = True
        playing = True
        levelSelect = False
        window = pygame.display.set_mode((500,500))


    #quand on commence un niveau, initialisation des variables + redimention de la fenetre
    if starting:
        frameTime = 100
        countdown = 1000
        pygame.time.set_timer(USEREVENT+1,frameTime)
        GAMEOVER, FLOOR, levelMap = levelsMap[level]
        levelMap = list(levelMap)
        ROWS, COLUMNS,WIDTH,HEIGHT = (len(levelMap),len(levelMap[0]),round(900/len(levelMap)),round(900/len(levelMap[0])))
        window = pygame.display.set_mode((ROWS*WIDTH,COLUMNS*HEIGHT))
        points = 0
        maxWaitTime = 2
        pointsLeft = 1
        moveCounter = 0
        cooldown = 0
        speed = (0,0)
        starting = False
        playing = True

    #si le timer arrive a 0 on affiche l'ecran de fin
    if playing and (countdown <= 0 or pointsLeft == 0) :
        playing = False
        if countdown <= 0:
            renderSprite(window, GAMEOVER, 0, 0, 100, 100)

    # gestion des evenements
    for event in pygame.event.get():
        if event.type == QUIT: #bouton fermer
            running = False
        if event.type == MOUSEBUTTONDOWN: #clic kde souris
            x,y = event.pos
            levelSelect = False
            pass
        if event.type == KEYDOWN and event.key == K_a: #"a"
            level=(level+1)%len(levelsMap)
            starting = True
        if event.type == KEYDOWN and event.key == K_UP: #"up"
            speed = (0,-1)
        if event.type == KEYDOWN and event.key == K_DOWN: #"down"
            speed = (0,1)
        if event.type == KEYDOWN and event.key == K_RIGHT: #"right"
            speed = (1,0)
        if event.type == KEYDOWN and event.key == K_LEFT: #"left"
            speed = (-1,0)
        if event.type == USEREVENT+1 and playing:

            #le joueur et l'enemi se deplacent
            value = move(speed)
            if value != -1:
                points += value
            else :
                running = False
            if speed != (0,0):
                moveCounter += 1

            #on affiche les elements du niveau
            renderSprite(window, FLOOR, 0, 0, WIDTH * ROWS, HEIGHT * COLUMNS)

            pointsLeft = 0
            for x in range(len(levelMap)):
                for y in range(len(levelMap[x])):
                    if levelMap[x][y][0] != "v":
                        renderSprite(window, levelMap[x][y][3:], x*WIDTH, y*HEIGHT, WIDTH, HEIGHT)
                    if levelMap[x][y][0] == "b":
                        pointsLeft += 1

            #affichage du texte
            score = scoreFont.render("Points:"+str(points), False, (255, 255, 255))
            time = scoreFont.render("Time left:"+str(int(countdown)), False, (255, 255, 255))
            window.blit(score,(10,5))
            window.blit(time,(WIDTH * COLUMNS - 200,5))

            #reinitialisation du veteur vitesse
            speed = (0,0)

            #update de la fenetre
            pygame.display.update()
#on ferme la fenetre
pygame.quit()
