# Library for Map Generation Classes
import math
import random
from PIL import Image, ImageDraw

class Dist_Function:   # die Distribution beschreibt, auf welche Koordinaten brushpunkte verteilt werden
    def __init__(self, size, spray):
        self.size = size
        self.spray = spray
        self.dist = []

    def calcdist(self): # berechne die Distributionsverteilung
        for x in range(0, self.size):
            y = self.size / 3 * math.sin(x * 12.0 / self.size) + x
            y = random.randrange(int(-self.size * self.spray), int(self.size * self.spray)) + y
            y = int(round(y, 0))
            self.dist.append(y)

    def clean(self, border, density):   # definiere die Grenze und nehme einige Punkte raus
        for x in range(0, self.size):
            if random.randint(0, density + 10) < 10:
                self.dist[x] = -10
            elif self.dist[x] < border:
                self.dist[x] = -10
            elif self.dist[x] > self.size - border:
                self.dist[x] = -10
            elif x < border:
                self.dist[x] = -10
            elif x > self.size - border:
                self.dist[x] = -10

class Brush:
    def __init__(self, size, height):
        self.size = size
        self.height = height
        self.brush = []
        self.mid = int(self.size / 2)

        for y in range(0,self.size):
            row =[]
            for x in range(0,self.size):
                row.append(0)
            self.brush.append(row)

        for y in range(0,self.size):
            for x in range(0, self.size):
                if y <= self.mid :
                    if x >= (self.mid - y)  and x <= (self.mid + y):
                        self.brush[y][x] = 1
                        self.brush[self.size-y-1][x] = 1
                    if x >= (self.mid - y+2) and x <= (self.mid + y-2):
                        self.brush[y][x] = 2
                        self.brush[self.size - y - 1][x] = 2
                    if x >= (self.mid - y + 4) and x <= (self.mid + y - 4):
                        self.brush[y][x] = 3
                        self.brush[self.size - y - 1][x] = 3
                    if x >= (self.mid - y + 5) and x <= (self.mid + y - 5):
                        self.brush[y][x] = 4
                        self.brush[self.size - y - 1][x] = 4

class Seedmap:
    def __init__(self, size):
        self.size = size
        self.map = []

        for y in range(0,self.size):
            row =[]
            for x in range(0,self.size):
                row.append(0)
            self.map.append(row)

    def drawfromdist(self,dist):
        for x in range(0, self.size):
            y = dist.dist[x]
            if y > 0:   self.map[x][y] = 1

class Heightmap:
    def __init__(self, size, border):
        self.size = size
        self.border = border
        self.map = []
        self.forest = []
        self.rivers = []

        for y in range(0,size):
            row = []
            forestrow = []
            riverrow = []
            for x in range(0,size):
                row.append(-20)
                forestrow.append(0)
                riverrow.append(0)
            self.map.append(row)
            self.forest.append(forestrow)
            self.rivers.append(riverrow)


    def generate(self,seedmap,brush):
        for y in range(0, self.size):
            for x in range(0, self.size):
                if seedmap.map[x][y] == 1:
                    for j in range(-brush.mid, brush.mid):
                        for i in range(-brush.mid, brush.mid):
                            self.map[x + i][y + j] += brush.brush[brush.mid + i][brush.mid + j]

    def gen2_prep(self,seedmap):
        print("start generating mountaintops")
        for y in range(0, self.size):
            for x in range(0, self.size):
                if seedmap.map[x][y] == 1:
                    self.map[x][y] = random.randrange(10,80,5)

    def slopedown(self):
        print("starting slopedown")
        for y in range(1,self.size-1):                                                  #spaltenschleife
            for x in range(1,self.size-1):                                              #zeilenscleife
                activecell = self.map[x][y]                                             # definiere aktive Zelle
                for n in range(-1,2):                                                   # suchbereich spalte
                    for m in range (-1,2):                                              # suchbereich zeile
                        if m != 0 or n != 0:                                            # schließe aktive zelle als vergleich aus
                            compcell = self.map[x + m][y + n]                           # definiere vergleichszelle
                            if compcell > activecell:                                   # der vergleich macht nur für niedrigere zellen sinn
                                if compcell > 40 :                                      # Berge: schaue auf höher 40
                                    if m == 0 and random.randint(0,1) == 0:             # für Nord Süd
                                        activecell = compcell                           # erweitere etwas den Bergverlauf
                                    elif compcell  % 10 == 0:                           # ansonsten wenn plateau, dann kante
                                        activecell = compcell - 5
                                    else:                                               # ansonsten
                                        if random.randint(0,10) < 3 :                   # mache meistens kante, manchmal plateau
                                            activecell = compcell - 5
                                        else:
                                            activecell = compcell - 10
                                elif random.randint(0,10) < 3 and compcell % 10 == 0:   # für gebiete unter 40
                                    activecell = compcell                               # für eine gewisse wahrscheinlichkeit erweitere plateaus
                                else:
                                    activecell = compcell - 5                           # sonst normaler slopedown
                self.map[x][y] = activecell

        #nun alles nochmal rückwärts
        print("reversing slopedownroute")
        for y in range(self.size-2,1,-1):                                                  #spaltenschleife
            for x in range(self.size-2,1,-1):                                              #zeilenscleife
                activecell = self.map[x][y]                                             # definiere aktive Zelle
                for n in range(-1,2):                                                   # suchbereich spalte
                    for m in range (-1,2):                                              # suchbereich zeile
                        if m != 0 or n != 0:                                            # schließe aktive zelle als vergleich aus
                            compcell = self.map[x + m][y + n]                           # definiere vergleichszelle
                            if compcell > activecell:                                   # der vergleich macht nur für niedrigere zellen sinn
                                if compcell > 40 :                                      # Berge: schaue auf höher 40
                                    if m == 0 and random.randint(0,1) == 0:             # für Nord Süd
                                        activecell = compcell                           # erweitere etwas den Bergverlauf
                                    elif compcell  % 10 == 0:                           # ansonsten wenn plateau, dann kante
                                        activecell = compcell - 5
                                    else:                                               # ansonsten
                                        if random.randint(0,10) < 3 :                   # mache meistens kante, manchmal plateau
                                            activecell = compcell - 5
                                        else:
                                            activecell = compcell - 10
                                elif random.randint(0,10) < 3 and compcell % 10 == 0:   # für gebiete unter 40
                                    activecell = compcell                               # für eine gewisse wahrscheinlichkeit erweitere plateaus
                                else:
                                    activecell = compcell - 5                           # sonst normaler slopedown
                self.map[x][y] = activecell

    def cleanup(self):
        print("Starting Cleanup")
        for y in range(1, self.size - 1):                                                # spaltenschleife
            for x in range(1, self.size - 1):                                           # zeilenscleife
                activecell = self.map[x][y]                                             # definiere aktive Zelle
                for n in range(-1, 2):                                                  # suchbereich spalte
                    for m in range(-1, 2):                                              # suchbereich Zeile
                        if m != 0 or n != 0 :
                            compcell = self.map[x+m][y+n]
                            if activecell < compcell + 5 :
                                compcell -= 5
                self.map[x][y] = compcell
        print("reversed cleanup")
        for y in range(self.size -2, 1, -1):                                                # spaltenschleife
            for x in range(self.size -2, 1, - 1):                                           # zeilenscleife
                activecell = self.map[x][y]                                             # definiere aktive Zelle
                for n in range(-1, 2):                                                  # suchbereich spalte
                    for m in range(-1, 2):                                              # suchbereich Zeile
                        if m != 0 or n != 0 :
                            compcell = self.map[x+m][y+n]
                            if compcell > activecell + 5 :
                                self.map[x][y] = compcell - 5

    def genforest(self, debug = False):
        if debug : print("Generating Forestmap")
        scanarea = int (self.size/50)
        minarea = int(self.size/50 - self.size/300)
        maxarea = int(self.size / 50 + self.size / 300)
        count = 0
        if debug: print(scanarea, minarea,maxarea)
        for y in range(self.border, self.size - self.border):         # spaltenschleife
            for x in range(self.border, self.size - self.border):     # zeilenscleife
                if random.randint(0,10000) < 2:
                    count += 1
                    for n in range(-scanarea, scanarea):              # suchbereich spalte
                        for m in range(-scanarea, scanarea):                            # suchbereich Zeile
                            activecell = self.map[x+m][y+n]  # definiere aktive Zelle
                            distance = math.sqrt((m)*(m) + (n)*(n))
                            if distance < random.randrange(minarea,maxarea) and 5 < activecell < 40:
                                self.forest[x+m][y+n] = 1
        print("Forests generated:",count)

    def seedrivers(self,debug = False):
        if debug: print("Generating Rivermap")
        count = 0
        for y in range(self.border, self.size - self.border):         # spaltenschleife
            for x in range(self.border, self.size - self.border):     # zeilenscleife
                activecell = self.map[x][y]
                if 40 < activecell < 70 and random.randint(0,10000) < 100:
                    count += 1
                    self.rivers[x][y] = 1
        if debug: print("Rivers seeded:", count)

    def genrivers(self,debug = False):
        if debug: print("Generating Rivermap")
        for y in range(self.border, self.size - self.border):         # spaltenschleife
            for x in range(self.border, self.size - self.border):     # zeilenscleife
                if self.rivers[x][y] == 1 and not isnext(self.rivers,x,y):
                    print("new seed found")# seed found , flow down
                    done = False
                    found = False
                    wd = 0
                    while self.map[x][y] > 0 and not done and wd < 1000:
                        done = True
                        if random.randint(0,0) == 0:
                            start = -1
                            stop = 2
                            step = 1
                        else:
                            start = 1
                            stop = -2
                            step = -1
                        for n in range(start, stop, step):              # suchbereich spalte
                            for m in range(start, stop, step):                            # suchbereich Zeile
                                found = False
                                if abs(m) != abs(n) :
                                    activecell = self.map[x][y]
                                    compcell = self.map[x+m][y+n]
                                    print(x, y, m, n, activecell,compcell)
                                    if self.rivers[x+m][y+n] == 0:
                                        #print("no water here yet")
                                        if compcell <= activecell :
                                            print("field is lower or same height")
                                            if activecell % 10 == 0:
                                                x = x+m
                                                y = y+n
                                                self.rivers[x][y] = 1
                                                done = False
                                                print(x, y,compcell, "added after plateau")
                                                found = True
                                                break
                                            elif activecell % 10 == 5:# and compcell % 10 == 0:
                                                x = x + m
                                                y = y + n
                                                self.rivers[x][y] = 1
                                                done = False
                                                print(x, y,compcell, "added after slope")
                                                found = True
                                                break
                            if found == True :
                                break
                                found = False
                        wd += 1
                        if wd > 500: print("Watchdog high")
        if debug : print("Rivermap generated completed")


    def newgrayscale(self,filename):
        image = Image.new("RGB", (self.size, self.size), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        progress = 0
        oldprogress = 0
        for y in range(0, self.size):
            for x in range(0, self.size):
                level = self.map[x][y]
                level = level + 20
                draw.point((x, y), (level * 3, level * 3, level * 3))
            progress = int (y / self.size * 10)
            if progress != oldprogress:
                print(progress * 10," ",end="")
            oldprogress = progress
        print("")
        del draw

        image.save(filename)

    def newtreemap(self,filename):
        image = Image.new("RGB", (self.size, self.size), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        progress = 0
        oldprogress = 0

        for y in range(0, self.size):
            for x in range(0, self.size):
                if self.forest[x][y] == 1:
                    draw.point((x, y), (255, 255, 255))

            progress = int (y / self.size * 10)
            if progress != oldprogress:
                print(progress * 10," ",end="")
                oldprogress = progress
        print("")
        del draw

        image.save(filename)

    def newrivermap(self, filename):
        image = Image.new("RGB", (self.size, self.size), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        progress = 0
        oldprogress = 0
        print("Rivermap",end=" ")
        for y in range(0, self.size):
            for x in range(0, self.size):
                if self.rivers[x][y] == 1:
                    draw.point((x, y), (255, 255, 255))

            progress = int(y / self.size * 10)
            if progress != oldprogress:
                print(progress * 10, " ", end="")
                oldprogress = progress
        print("")
        del draw

        image.save(filename)


    def newimage(self,filename):
        image = Image.new("RGB", (self.size, self.size), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        progress = 0
        oldprogress = 0
        for y in range(0, self.size):
            for x in range(0, self.size):
                level = self.map[x][y]

                if level < - 10 : draw.point((x, y), (  0,  16,  80))
                elif level < -5 : draw.point((x, y), (  0,  16, 128))
                elif level <  0 : draw.point((x, y), (  0 , 16, 255))
                elif level <  5 : draw.point((x, y), (255, 200, 132))
                elif level < 10 : draw.point((x, y), (  0, 120,   0))
                elif level < 15 : draw.point((x, y), (  0, 130,   0))
                elif level < 20 : draw.point((x, y), (  0, 140,   0))
                elif level < 25 : draw.point((x, y), (  0, 150,   0))
                elif level < 30 : draw.point((x, y), (  0, 160,   0))
                elif level < 35 : draw.point((x, y), (  0, 170,   0))
                elif level < 40 : draw.point((x, y), (  0, 180,   0))
                elif level < 45 : draw.point((x, y), (100, 100, 100))
                elif level < 50 : draw.point((x, y), (110, 110, 110))
                elif level < 55 : draw.point((x, y), (120, 120, 120))
                elif level < 60 : draw.point((x, y), (130, 130, 130))
                elif level < 65 : draw.point((x, y), (140, 140, 140))
                elif level < 70 : draw.point((x, y), (150, 150, 150))
                elif level < 75 : draw.point((x, y), (160, 160, 160))
                elif level < 80 : draw.point((x, y), (200, 200, 200))
                else:             draw.point((x, y), (255, 255, 255))

                if self.forest[x][y] == 1 : draw.point((x, y), ( 0, 80, 0))
                if self.rivers[x][y] == 1 : draw.point((x, y), ( 0, 50, 128))
            progress = int (y / self.size * 10)
            if progress != oldprogress: print(progress * 10," ",end="")
            oldprogress = progress
        print("")
        del draw

        image.save(filename)
    def print(self):

        for row in range(0,self.size):
            print(self.map[row])


def isnext(tocheck,x,y,fourway = True):
    if tocheck[x-1][y] == 1 or tocheck[x+1][y] == 1 or tocheck[x][y-1] == 1 or tocheck[x][y+1] == 1 or not fourway and\
                (tocheck[x-1][y-1] == 1  or tocheck[x+1][y+1] == 1 or tocheck[x-1][y+1] == 1 or tocheck[x+1][y-1]) == 1:
        return True
    else:
        return False