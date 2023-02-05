"""
This file handles all of the data related to the text files.
    This includes controling the:
        HighScores.txt
        Upgrades.txt
        Currency.txt
"""

# from https://www.diderot.one/course/34/chapters/2808/#anchor-segment-214904
from cmu_112_graphics import * #ModalApp, App, Mode

#from built-in functions into Python 3.85
import copy
import math
import random

#from @B0-8-115 www.diderot.one/course/34/chapters/2604/#anchor-atom-189700
def readFile(path):  
    with open(path, "rt") as f:  
        return f.read()  

#from @B0-8-115 www.diderot.one/course/34/chapters/2604/#anchor-atom-189700
def writeFile(path, contents):  
    with open(path, "wt") as f:  
        f.write(contents)



def changeCurrency(change):
    content = readFile('Currency.txt')
    if content == "":
        currentCoins = str(0 + int(change))
        if change < 0:
            currentCoins = str(0)
            writeFile('Currency.txt', currentCoins)
            return False
        writeFile('Currency.txt', currentCoins)
    else:
        currentCoins = int(int(content) + change)
        print(currentCoins)
        if currentCoins < 0:
            currentCoins = str(int(int(currentCoins) - change))
            print(currentCoins)
            print('less than 0, switch back to:',currentCoins)
            writeFile('Currency.txt', currentCoins)
            return False
        writeFile('Currency.txt', str(currentCoins))
    return True

def getCurrency():
    content = readFile('Currency.txt')
    if content == "":
        writeFile('Currency.txt', str(0))
        return 0
    else:
        return int(content)

def getUpgrade(upgrade):
    contents = readFile('Upgrades.txt')
    if contents == "":
        uploadFormat = "SPEEDY BOOTS-12000|MAGNET-12000|DOUBLE POINTS-12000|AI-12000|"
        writeFile('Upgrades.txt', uploadFormat)
    contents = readFile('Upgrades.txt')
    for content in contents.split("|"):
        if content.startswith(upgrade):
            return int(content[content.find("-")+1:])
    return 0

def setUpgrade(upgrade, newValue):
    contents = readFile('Upgrades.txt')
    newContents = ""
    if contents == "":
        uploadFormat = "SPEEDY BOOTS-12000|MAGNET-12000|DOUBLE POINTS-12000|AI-12000|"
        writeFile('Upgrades.txt', uploadFormat)    
    for content in contents.split("|"):
        if content.startswith(upgrade):
            mark = content.find("-")
            newContents += f"{content[:mark]}-{newValue}|"
        else:
            newContents += f"{content}|"
    while newContents.endswith('||'):
        newContents = newContents[:-1]
    writeFile('Upgrades.txt', newContents)    


def upgradePowerUp(upgrade):
    currentValue = getUpgrade(upgrade)
    increment = 2000
    if currentValue + increment <= 22000: #max upgrade
        cost = int(currentValue/75)
        print("BEFORE",getCurrency())
        if changeCurrency(-cost):
            setUpgrade(upgrade, currentValue + increment)
            print("processed:", readFile('Upgrades.txt'))
            print(getCurrency())
        else:
            print(f'insufficent funds.. cost is {cost} and you have {getCurrency()}')


def newScore(score):
    newContent = f"{readFile('HighScores.txt')}You-{score}\n"
    writeFile('HighScores.txt', newContent)

def getBestScore(who):
    allScores = readFile('HighScores.txt')
    scores = set()
    for content in allScores.splitlines():
        if content.startswith(who):
            scores.add(int(content[content.index('-')+1:]))

    highScore = 0
    for score in scores:
        if score > highScore:
            highScore = score

    return highScore

def listTopNScores(N):
    contents = ""
    allScores = readFile('HighScores.txt')
    scoreDict = dict()
    onlyScores = []

    for content in allScores.splitlines():
        player = content[:content.index('-')]
        score = int(content[content.index('-')+1:])

        scoreDict[score] = scoreDict.get(score, set())
        scoreDict[score].add(player)
        onlyScores += [score]

    onlyScores.sort(reverse = True)

    topN = 0
    for score in onlyScores:
        for player in scoreDict[score]:
            if topN < N and score > 0:
                topN += 1
                contents += f"{topN}. {player} - {score}\n"

    return contents
            