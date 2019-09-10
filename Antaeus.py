#!/usr/bin/env python2
import math
import random
import cmath

if __name__ != "__main__":
    from CvPythonExtensions import *
    import CvUtil
    import CvMapGeneratorUtil
    from CvMapGeneratorUtil import FractalWorld
    from CvMapGeneratorUtil import TerrainGenerator
    from CvMapGeneratorUtil import FeatureGenerator

    def getDescription():
        return "Antaeus Map Generator: a combination of various fun and unpredictable generators."

    def isAdvancedMap():
        "This map should show up in simple mode"
        return 0

    def getNumCustomMapOptions():
        return 4

    def getCustomMapOptionName(argsList):
        selection_names = {
                0 : "type of map",
                1 : "type of generator",
                2 : "symmetry",
                3 : "distribution of climate"
                }
        translated_text = unicode(CyTranslator().getText(selection_names[argsList[0]], ()))
        return translated_text

    def getNumCustomMapOptionValues(argsList):
        selection_names = {
                0: 3,
                1: 3,
                2: 10,
                3: 6,
                }
        return selection_names[argsList[0]]

    def getCustomMapOptionDescAt(argsList):
        selection_names = {
            0: ["Flat",
                "Cylindrical",
                "Toroid"],
            1: ["IID",
                "Fractal Land",
                "Riveria"],
            2: ["None",
                "2-Rotational",
                "3-Rotational",
                "4-Rotational",
                "5-Rotational",
                "Bilateral",
                "2-Dihedral",
                "3-Dihedral",
                "4-Dihedral (experimental)",
                "5-Dihedral (experimental)",
                ],
            3: ["Default",
                "Global",
                "North Hemisphere",
                "Fractal",
                "Regional",
                "Regional Fractal"]
            }
        translated_text = unicode(CyTranslator().getText(selection_names[argsList[0]][argsList[1]], ()))
        return translated_text

    def getCustomMapOptionDefault(argsList):
        [iOption] = argsList
        option_defaults = {
            0:      1,
            1:      1,
            2:      0,
            3:      0,
            }
        return option_defaults[iOption]

    def isRandomCustomMapOption(argsList):
        [iOption] = argsList
        option_random = {
            0:      true,
            1:      true,
            2:      true,
            3:      true,
            }
        return option_random[iOption]

    def getMapType ():
        return CyMap().getCustomMapOption(0)

    def getGeneratorType ():
        return CyMap().getCustomMapOption(1)

    def getSymmetryType ():
        SymmetryList = {
            0: 0,
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: -1,
            6: -2,
            7: -3,
            8: -4,
            9: -5,
            }
        return SymmetryList[CyMap().getCustomMapOption(2)]

    def getClimateType ():
        if CyMap().getCustomMapOption(3) == 0:
            if getMapType() == 0:
                return 3
            elif getMapType() == 1:
                return 0
            else:
                return 4
        else:
            return CyMap().getCustomMapOption(3) - 1

    def getWrapX():
        return (getMapType () == 1 or getMapType () == 2)

    def getWrapY():
        return (getMapType () == 2)

    def getGridSize(argsList):
        # Reduce grid sizes by one level.
        grid_sizes = {
            WorldSizeTypes.WORLDSIZE_DUEL:      (6,4),
            WorldSizeTypes.WORLDSIZE_TINY:      (8,5),
            WorldSizeTypes.WORLDSIZE_SMALL:     (10,6),
            WorldSizeTypes.WORLDSIZE_STANDARD:  (13,8),
            WorldSizeTypes.WORLDSIZE_LARGE:     (16,10),
            WorldSizeTypes.WORLDSIZE_HUGE:      (21,13)
        }

        if (argsList[0] == -1): # (-1,) is passed to function on loads
            return []
        [eWorldSize] = argsList
        return grid_sizes[eWorldSize]

    class IIDPlotGenerator(CvMapGeneratorUtil.FractalWorld):
        def __init__(self, fracXExp=CyFractal.FracVals.DEFAULT_FRAC_X_EXP,
                     fracYExp=CyFractal.FracVals.DEFAULT_FRAC_Y_EXP):
            self.gc = CyGlobalContext()
            self.map = self.gc.getMap()
            self.iNumPlotsX = self.map.getGridWidth()
            self.iNumPlotsY = self.map.getGridHeight()
            self.mapRand = self.gc.getGame().getMapRand()
            self.iFlags = self.map.getMapFractalFlags()
            self.plotTypes = [PlotTypes.PLOT_OCEAN] * (self.iNumPlotsX*self.iNumPlotsY)
            self.fracXExp = fracXExp
            self.fracYExp = fracYExp
            # init User Input variances
            self.seaLevelChange = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
            self.seaLevelMax = 100
            self.seaLevelMin = 0
            self.hillGroupOneRange = self.gc.getClimateInfo(self.map.getClimate()).getHillRange()
            self.hillGroupOneBase = 25
            self.hillGroupTwoRange = self.gc.getClimateInfo(self.map.getClimate()).getHillRange()
            self.hillGroupTwoBase = 75
            self.peakPercent = self.gc.getClimateInfo(self.map.getClimate()).getPeakPercent()
            self.stripRadius = 15

        def initFractal(self):
            "For no rifts, use rift_grain = -1"
            return

        def generatePlotTypes(self, water_percent=34, shift_plot_types=True, grain_amount=3):
            # Check for changes to User Input variances.
            self.checkForOverrideDefaultUserInputVariances()

            water_percent += self.seaLevelChange
            water_percent = min(water_percent, self.seaLevelMax)
            water_percent = max(water_percent, self.seaLevelMin)

            for x in range(self.iNumPlotsX):
                for y in range(self.iNumPlotsY):
                    i = y*self.iNumPlotsX + x

                    if self.mapRand.get(100, "Generate Plot Types PYTHON") < water_percent:
                        self.plotTypes[i] = PlotTypes.PLOT_OCEAN
                    elif self.mapRand.get(100, "Generate Plot Types PYTHON") >= self.hillGroupTwoRange * 4:
                        self.plotTypes[i] = PlotTypes.PLOT_LAND
                    elif self.mapRand.get(100, "Generate Plot Types PYTHON") < self.peakPercent:
                        self.plotTypes[i] = PlotTypes.PLOT_PEAK
                    else:
                        self.plotTypes[i] = PlotTypes.PLOT_HILLS

            return self.plotTypes

    class PostprocessPlotGenerator(CvMapGeneratorUtil.FractalWorld):
        def __init__(self, fracXExp=CyFractal.FracVals.DEFAULT_FRAC_X_EXP,
                     fracYExp=CyFractal.FracVals.DEFAULT_FRAC_Y_EXP):
            self.gc = CyGlobalContext()
            self.map = self.gc.getMap()
            self.iNumPlotsX = self.map.getGridWidth()
            self.iNumPlotsY = self.map.getGridHeight()
            self.mapRand = self.gc.getGame().getMapRand()
            self.iFlags = self.map.getMapFractalFlags()
            self.plotTypes = [PlotTypes.PLOT_OCEAN] * (self.iNumPlotsX*self.iNumPlotsY)
            self.fracXExp = fracXExp
            self.fracYExp = fracYExp
            self.continentsFrac = CyFractal()
            self.hillsFrac = CyFractal()
            self.peaksFrac = CyFractal()
            # init User Input variances
            self.seaLevelChange = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
            self.seaLevelMax = 100
            self.seaLevelMin = 0
            self.hillGroupOneRange = self.gc.getClimateInfo(self.map.getClimate()).getHillRange()
            self.hillGroupOneBase = 25
            self.hillGroupTwoRange = self.gc.getClimateInfo(self.map.getClimate()).getHillRange()
            self.hillGroupTwoBase = 75
            self.peakPercent = self.gc.getClimateInfo(self.map.getClimate()).getPeakPercent()
            self.stripRadius = 15

        def generatePlotTypes(self, mapData, water_percent=78, shift_plot_types=True, grain_amount=3):
            # Check for changes to User Input variances.
            self.checkForOverrideDefaultUserInputVariances()

            self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
            self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

            water_percent += self.seaLevelChange
            water_percent = min(water_percent, self.seaLevelMax)
            water_percent = max(water_percent, self.seaLevelMin)

            iWaterThreshold = self.continentsFrac.getHeightFromPercent(water_percent)
            iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
            iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
            iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
            iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
            iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)

            for x in range(self.iNumPlotsX):
                for y in range(self.iNumPlotsY):
                    i = y*self.iNumPlotsX + x
                    val = self.continentsFrac.getHeight(x,y)
                    if (val <= iWaterThreshold or mapData[i] == ' ') and (mapData[i] != '*' and mapData[i] != '.' and mapData[i] != '+' and mapData[i] != '#'):
                        self.plotTypes[i] = PlotTypes.PLOT_OCEAN
                    else:
                        if mapData[i] == '.':
                            self.plotTypes[i] = PlotTypes.PLOT_LAND
                        elif mapData[i] == '+':
                            self.plotTypes[i] = PlotTypes.PLOT_HILLS
                        elif mapData[i] == '#':
                            self.plotTypes[i] = PlotTypes.PLOT_PEAK
                        else:
                            hillVal = self.hillsFrac.getHeight(x,y)
                            if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
                                peakVal = self.peaksFrac.getHeight(x,y)
                                if (peakVal <= iPeakThreshold):
                                    self.plotTypes[i] = PlotTypes.PLOT_PEAK
                                else:
                                    self.plotTypes[i] = PlotTypes.PLOT_HILLS
                            else:
                                self.plotTypes[i] = PlotTypes.PLOT_LAND

            if shift_plot_types:
                    self.shiftPlotTypes()

            return self.plotTypes

    class YYTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
        def __init__(self, iDesertPercent=32, iPlainsPercent=18,
                     fSnowLatitude=0.7, fTundraLatitude=0.6,
                     fGrassLatitude=0.1, fDesertBottomLatitude=0.2,
                     fDesertTopLatitude=0.5, fracXExp=-1,
                     fracYExp=-1, grain_amount=4):

            self.gc = CyGlobalContext()
            self.map = CyMap()

            grain_amount += self.gc.getWorldInfo(self.map.getWorldSize()).getTerrainGrainChange()

            self.grain_amount = grain_amount

            self.iWidth = self.map.getGridWidth()
            self.iHeight = self.map.getGridHeight()

            self.mapRand = self.gc.getGame().getMapRand()

            self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.
            if self.map.isWrapX(): self.iFlags += CyFractal.FracVals.FRAC_WRAP_X
            if self.map.isWrapY(): self.iFlags += CyFractal.FracVals.FRAC_WRAP_Y

            self.deserts=CyFractal()
            self.plains=CyFractal()
            self.variation=CyFractal()
            self.variationx=CyFractal()
            self.variationy=CyFractal()

            iDesertPercent += self.gc.getClimateInfo(self.map.getClimate()).getDesertPercentChange()
            iDesertPercent = min(iDesertPercent, 100)
            iDesertPercent = max(iDesertPercent, 0)

            self.iDesertPercent = iDesertPercent
            self.iPlainsPercent = iPlainsPercent

            self.iDesertTopPercent = 100
            self.iDesertBottomPercent = max(0,int(100-iDesertPercent))
            self.iPlainsTopPercent = 100
            self.iPlainsBottomPercent = max(0,int(100-iDesertPercent-iPlainsPercent))
            self.iMountainTopPercent = 75
            self.iMountainBottomPercent = 60

            fSnowLatitude += self.gc.getClimateInfo(self.map.getClimate()).getSnowLatitudeChange()
            fSnowLatitude = min(fSnowLatitude, 1.0)
            fSnowLatitude = max(fSnowLatitude, 0.0)
            self.fSnowLatitude = fSnowLatitude

            fTundraLatitude += self.gc.getClimateInfo(self.map.getClimate()).getTundraLatitudeChange()
            fTundraLatitude = min(fTundraLatitude, 1.0)
            fTundraLatitude = max(fTundraLatitude, 0.0)
            self.fTundraLatitude = fTundraLatitude

            fGrassLatitude += self.gc.getClimateInfo(self.map.getClimate()).getGrassLatitudeChange()
            fGrassLatitude = min(fGrassLatitude, 1.0)
            fGrassLatitude = max(fGrassLatitude, 0.0)
            self.fGrassLatitude = fGrassLatitude

            fDesertBottomLatitude += self.gc.getClimateInfo(self.map.getClimate()).getDesertBottomLatitudeChange()
            fDesertBottomLatitude = min(fDesertBottomLatitude, 1.0)
            fDesertBottomLatitude = max(fDesertBottomLatitude, 0.0)
            self.fDesertBottomLatitude = fDesertBottomLatitude

            fDesertTopLatitude += self.gc.getClimateInfo(self.map.getClimate()).getDesertTopLatitudeChange()
            fDesertTopLatitude = min(fDesertTopLatitude, 1.0)
            fDesertTopLatitude = max(fDesertTopLatitude, 0.0)
            self.fDesertTopLatitude = fDesertTopLatitude

            self.fracXExp = fracXExp
            self.fracYExp = fracYExp

            self.iNumPlotsX = self.gc.getMap().getGridWidth()
            self.iNumPlotsY = self.gc.getMap().getGridHeight()

            self.initFractals()

        def initFractals(self):
            global yy_latitude

            yy_latitude = [0.0] * (self.iNumPlotsX*self.iNumPlotsY)

            self.deserts.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
            self.iDesertTop = self.deserts.getHeightFromPercent(self.iDesertTopPercent)
            self.iDesertBottom = self.deserts.getHeightFromPercent(self.iDesertBottomPercent)

            self.plains.fracInit(self.iWidth, self.iHeight, self.grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
            self.iPlainsTop = self.plains.getHeightFromPercent(self.iPlainsTopPercent)
            self.iPlainsBottom = self.plains.getHeightFromPercent(self.iPlainsBottomPercent)

            self.variation.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
            self.variationx.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
            self.variationy.fracInit(self.iWidth, self.iHeight, self.grain_amount - 2, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

            self.terrainDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")
            self.terrainPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
            self.terrainIce = self.gc.getInfoTypeForString("TERRAIN_SNOW")
            self.terrainTundra = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
            self.terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")

            low = self.variationx.getHeightFromPercent(5)
            hi = self.variationx.getHeightFromPercent(95)

            lowy = self.variationy.getHeightFromPercent(5)
            hiy = self.variationy.getHeightFromPercent(95)

            fur = self.mapRand.get(20, "Generate Plot Types PYTHON")
            self.range = 0.2 + 0.02 * fur
            self.pos = -0.6 + 0.02 * self.mapRand.get(50 - fur, "Generate Plot Types PYTHON")

            for x in range(self.iNumPlotsX):
                for y in range(self.iNumPlotsY):
                    i = y*self.iNumPlotsX + x
                    if getClimateType() == 0:
                        yy_latitude[i] = abs((self.iHeight / 2) - y)/float(self.iHeight/2)
                    elif getClimateType () == 1:
                        yy_latitude[i] = (y)/float(self.iHeight) * 0.92
                    elif getClimateType () == 2:
                        yy_latitude[i] = (self.variationx.getHeight(x, y) - low) / float(hi - low)
                        if yy_latitude[i] < 0:
                            yy_latitude[i] = 0.0
                        if yy_latitude[i] > 1:
                            yy_latitude[i] = 1.0
                    elif getClimateType () == 3:
                        yy_latitude[i] = abs((y)/float(self.iHeight) * self.range + self.pos)
                    else:
                        yy_latitude[i] = (self.variationy.getHeight(x, y) - lowy) / float(hiy - lowy) * 0.7 + 0.15
                        if yy_latitude[i] < 0:
                            yy_latitude[i] = 0.0
                        if yy_latitude[i] > 1:
                            yy_latitude[i] = 1.0

        def getLatitudeAtPlot(self, iX, iY):
            lat = yy_latitude[iX + iY * self.iNumPlotsX]

            # Adjust latitude using self.variation fractal, to mix things up:
            lat += (128 - self.variation.getHeight(iX, iY))/(255.0 * 5.0)

            # Limit to the range [0, 1]:
            if lat < 0:
                lat = 0.0
            if lat > 1:
                lat = 1.0

            return lat

    class YYFeatureGenerator (CvMapGeneratorUtil.FeatureGenerator):
        def getLatitudeAtPlot(self, iX, iY):
            "returns a value in the range of 0.0 (tropical) to 1.0 (polar)"
            return yy_latitude[iX + iY * CyGlobalContext().getMap().getGridWidth()]

    def generatePlotTypes():
        NiTextOut("Setting Plot Types (Python Fractal) ...")
        if getGeneratorType () == 0:
            # iid
            fractal_world = IIDPlotGenerator()
            fractal_world.initFractal()
            return fractal_world.generatePlotTypes()
        elif getGeneratorType () == 1:
            # Fractal Land

            water_percent = 40
            water_percent = water_percent + CyGlobalContext().getSeaLevelInfo(CyGlobalContext().getMap().getSeaLevel()).getSeaLevelChange()
            water_percent = min(water_percent, 100)
            water_percent = max(water_percent, 0)

            hillRange = CyGlobalContext().getClimateInfo(CyGlobalContext().getMap().getClimate()).getHillRange()
            peakPercent = CyGlobalContext().getClimateInfo(CyGlobalContext().getMap().getClimate()).getPeakPercent()

            map_data = FractalTerrainGenerator(
                    CyGlobalContext().getMap().getGridWidth(),
                    CyGlobalContext().getMap().getGridHeight(),
                    symmetry = getSymmetryType(),
                    wrapH = getWrapX(),
                    wrapV = getWrapY(),
                    waterPercent = water_percent,
                    hillRange = hillRange,
                    peakPercent = peakPercent
                    )

            fractal_world = PostprocessPlotGenerator()
            fractal_world.initFractal()

            res = fractal_world.generatePlotTypes(map_data)

            return res
        else:
            # Riveria

            water_percent = 25
            water_percent = water_percent + CyGlobalContext().getSeaLevelInfo(CyGlobalContext().getMap().getSeaLevel()).getSeaLevelChange()
            water_percent = min(water_percent, 100)
            water_percent = max(water_percent, 0)

            map_data = RiveriaTerrainGenerator(CyGlobalContext().getMap().getGridWidth(), CyGlobalContext().getMap().getGridHeight(), symmetry = getSymmetryType(), wrapH = getWrapX(), wrapV = getWrapY(), waterPercent = water_percent)

            fractal_world = PostprocessPlotGenerator()
            fractal_world.initFractal()

            res = fractal_world.generatePlotTypes(map_data, shift_plot_types = False)

            return res

    def generateTerrainTypes():
        NiTextOut("Generating Terrain (Python Fractal) ...")
        terraingen = YYTerrainGenerator()
        terrainTypes = terraingen.generateTerrain()
        return terrainTypes

    def addFeatures():
        NiTextOut("Adding Features (Python Fractal) ...")
        featuregen = YYFeatureGenerator()
        featuregen.addFeatures()
        return 0

    # End of civ4-specific stuff

def randomPoint ():
    while (True):
        x = complex (random.gauss(0, 1), random.gauss(0, 1))
        if (abs(x) < 10):
            return x

def floodfill (map, w, h, wrapV, wrapH, i, j, visited, separator):
    queue = [(i, j)]
    visited[j * w + i] = True
    re = 1

    while len(queue) > 0:
        head = queue[0]
        queue = queue[1:]
        i = head[0]
        j = head[1]
        c = j * w + i

        for di in range(-1, 2):
            for dj in range(-1, 2):
                i2 = (i + di) % w
                j2 = (j + dj) % w
                c2 = j2 * w + i2
                if (i + di >= 0 or wrapH) and (i + di < w or wrapH) and (j + dj >= 0 or wrapV) and (j + dj < h or wrapV) and map[c2] != separator and not visited[c2]:
                    queue.append ((i2, j2))
                    visited[j2 * w + i2] = True
                    re = re + 1
    return re

def countIslands (map, w, h, wrapV, wrapH):
    visited = [False] * (w * h)
    islands = 0
    for i in range(w):
        for j in range(h):
            c = j * w + i
            if map[c] != ' ' and not visited[c]:
                x = floodfill(map, w, h, wrapV, wrapH, i, j, visited, ' ')
                islands = islands + 1
    return islands

def countContinents (map, w, h, wrapV, wrapH):
    visited = [False] * (w * h)
    islands = 0
    for i in range(w):
        for j in range(h):
            c = j * w + i
            if map[c] != ' ' and not visited[c]:
                x = floodfill(map, w, h, wrapV, wrapH, i, j, visited, ' ')
                if x >= 9:
                    islands = islands + 1
    return islands

def fixConnectivity (map, w, h, wrapV, wrapH):
    finished = False
    while not finished:
        visited = [False] * (w * h)
        for c in range(w * h):
            if map[c] != '#' and not visited[c]:
                x = floodfill(map, w, h, wrapV, wrapH, c % w, c // w, visited, '#')
                break

        queue = []
        previous = {}
        visited2 = list(visited)
        for c in range(w * h):
            if visited[c]:
                queue.append((c % w, c // w))

        finished = True
        while len(queue) > 0:
            head = queue[0]
            queue = queue[1:]
            i = head[0]
            j = head[1]
            c = j * w + i

            if map[c] != '#' and (i,j) in previous:
                while previous[(i,j)] in previous:
                    (i, j) = previous[(i,j)]
                    map[j * w + i] = '+'
                finished = False
                break

            for di in range(-1, 2):
                for dj in range(-1, 2):
                    i2 = (i + di) % w
                    j2 = (j + dj) % w
                    c2 = j2 * w + i2
                    if (i + di >= 0 or wrapH) and (i + di < w or wrapH) and (j + dj >= 0 or wrapV) and (j + dj < h or wrapV) and not visited2[c2]:
                        queue.append ((i2, j2))
                        previous[(i2, j2)] = (i, j)
                        visited2[j2 * w + i2] = True

class transformer:
    def transform(self, coord):
        return coord

    def __str__ (self):
        return "<iden>"

class linearTransformer(transformer):
    def __init__ (self, minExpansionRatio = 0.4, maxExpansionRatio = 0.9, maxAspectRatio = 4.0):
        self.offset = randomPoint()
        scale = random.uniform(minExpansionRatio, maxExpansionRatio)
        stretch = math.exp(random.uniform(-math.log(maxAspectRatio) / 2, math.log(maxAspectRatio) / 2))
        rotate1 = cmath.exp(1j*random.random()*cmath.pi*2)
        rotate2 = cmath.exp(1j*random.random()*cmath.pi*2)

        self.xx = (  rotate1.real * rotate2.real * stretch - rotate1.imag * rotate2.imag / stretch) * scale
        self.xy = (- rotate1.imag * rotate2.real * stretch - rotate1.real * rotate2.imag / stretch) * scale
        self.yx = (  rotate1.real * rotate2.imag * stretch + rotate1.imag * rotate2.real / stretch) * scale
        self.yy = (- rotate1.imag * rotate2.imag * stretch + rotate1.real * rotate2.real / stretch) * scale

    def transform(self, coord):
        return complex(coord.real*self.xx + coord.imag*self.xy, coord.real*self.yx + coord.imag*self.yy) + self.offset

    def __str__ (self):
        return "<linear>"

class diamondTransformer(transformer):
    def transform(self, coord):
        rho = abs(coord)
        theta = math.atan2(coord.imag, coord.real)
        return complex(math.sin(theta)*math.cos(rho), math.sin(rho)*math.cos(theta))
    def __str__ (self):
        return "<diamond>"

class varDiamondTransformer(transformer):
    def transform(self, coord):
        return coord
        rho = abs(coord)
        if rho < 1e-8:
            return None

        theta = math.atan2(coord.imag, coord.real)
        quadrant = math.floor(theta / (math.pi / 2)) * math.pi / 2
        theta = theta - quadrant - math.pi / 4

        rho = math.sqrt(rho + 1./16)
        x = rho * math.sin(theta)
        ya = 2 * (rho**2) * (math.cos(theta)**2)
        y = (ya + 1 / ya)/math.sqrt(8)

        return cmath.exp((quadrant + math.pi / 4) * 1j) * y + cmath.exp((quadrant + 3 * math.pi / 4) * 1j) * x

    def __str__ (self):
        return "<vardiamond>"

class sequenceTransformer(transformer):
    def __init__ (self, transList):
        self.transList = transList
    def transform(self, coord):
        for trans in self.transList:
            coord = trans.transform(coord)
        return coord
    def __str__ (self):
        return "<seq" + "".join(map(lambda x: x.__str__(), self.transList)) + ">"

class symmetryTransformer(transformer):
    def __init__ (self, symmetry):
        self.symmetry = symmetry
    def transform(self, coord):
        if self.symmetry < 0:
            if random.randrange(2):
                coord = -coord.conjugate()
            return coord * cmath.exp(1j*random.randrange(-self.symmetry)*cmath.pi*2/-self.symmetry)
        elif self.symmetry == 0:
            return coord
        else:
            return coord * cmath.exp(1j*random.randrange(self.symmetry)*cmath.pi*2/self.symmetry)
    def __str__ (self):
        return "<sym>"

class classicalDecorator(transformer):
    pass

class pickerTransformer(transformer):
    def __init__ (self, transformerList, symmetry):

        n = len(transformerList)

        weightList = [0.0] * n
        for i in range(n):
            weightList[i] = random.expovariate(1.0)
        tot = sum(weightList)
        for i in range(n):
            weightList[i] /= float(tot)

        self.pairList = list(zip(map(lambda trans: sequenceTransformer((trans, symmetryTransformer(symmetry))), transformerList), weightList))

    def transform (self, coord):

        x = random.random()

        for (a,b) in self.pairList:
            if (b >= x):
                return a.transform(coord)
            else:
                 x = x - b

    def __str__ (self):
        return "<pick" + "".join(map(lambda x: x[0].__str__(), self.pairList)) + ">"

class interpolator:
    def __init__ (self, n):
        self.weightList = [0.0] * n
        for i in range(n):
            self.weightList[i] = random.expovariate(1.0)
        tot = sum(self.weightList)
        for i in range(n):
            self.weightList[i] /= float(tot)
    def interpolate (self, coordList):
        return sum([x*y for (x,y) in zip(coordList, self.weightList)])
    def __str__ (self):
        return "default"

class linearInterpolator(interpolator):
    def __str__ (self):
        return "linear"

class diamondInterpolator(interpolator):
    def interpolate (self, coordList):
        rho = math.sqrt(sum([abs(x)*w for (x,w) in zip(coordList, self.weightList)]))
        psi = sum([math.atan2(x.imag,x.real)*w for (x,w) in zip(coordList, self.weightList)])
        return cmath.exp(1j * psi) * rho
    def __str__ (self):
        return "diamond"

class interpolatorTransformer(transformer):
    def __init__ (self, transformerList, interpolator):
        self.transformerList = transformerList
        self.interpolator = interpolator

    def transform(self, coord):
        return self.interpolator.interpolate([x.transform(coord) for x in self.transformerList])

    def __str__ (self):
        return "<interp(" + self.interpolator.__str__() + ")" + ("".join([trans.__str__() for trans in self.transformerList])) + ">"

class treeTransformer(transformer):
    def __init__ (self, regularity = 1.0, fun = 1.0, depthLimit = 2,
                  minExpansionRatio = 0.2, maxExpansionRatio = 1.1):
        if regularity < 0:
            regularity = 0
        if regularity > 1.5:
            regularity = 1.5
        if fun < 0:
            fun = 0

        if random.random() <= (1.2 - fun) / 2.4:
            # linear transformer
            self.trans = linearTransformer(minExpansionRatio, maxExpansionRatio, 3.03 / (regularity + 0.01))
        elif random.expovariate(2.0) <= 0.8 * fun and depthLimit > 1:
            if random.randrange(4) < 1:
                # sequence transformer

                delta = (maxExpansionRatio - minExpansionRatio) * 0.2
                transA = treeTransformer(regularity + 0.2, fun - 0.5, depthLimit - 1,
                                         minExpansionRatio + delta, maxExpansionRatio - delta)
                transB = treeTransformer(regularity + 0.2, fun - 0.5, depthLimit - 1,
                                         minExpansionRatio + delta, maxExpansionRatio - delta)
                self.trans = sequenceTransformer((transA, transB))
            else:
                # interpolator transformer
                n = 2
                while random.random() <= 1.2 * (0.5 ** n) * fun:
                    n = n + 1
                transList = [None] * n
                for i in range(n):
                    transList[i] = treeTransformer(regularity - 0.2, fun - 0.5, depthLimit - 1,
                                                   minExpansionRatio, maxExpansionRatio)
                r = random.randrange(64)
                if r < 40:
                    self.trans = interpolatorTransformer(transList, linearInterpolator(n))
                else:
                    self.trans = interpolatorTransformer(transList, diamondInterpolator(n))
        else:
            if random.randrange(16) < 12:
                # diamond
                pre_trans = linearTransformer(minExpansionRatio, maxExpansionRatio, 2.525 / (regularity + 0.01))
                diamond_trans = diamondTransformer()
                self.trans = sequenceTransformer((pre_trans, diamond_trans))
            else:
                # varDiamond
                pre_trans = linearTransformer(minExpansionRatio, maxExpansionRatio, 2.525 / (regularity + 0.01))
                varDiamond_trans = varDiamondTransformer()
                self.trans = sequenceTransformer((pre_trans, varDiamond_trans))

    def transform (self, coord):
        return self.trans.transform(coord)

    def __str__ (self):
        return self.trans.__str__()

def drawFractal(width = 20, height = 15, wrapV = False, wrapH = True,
                minEmptyPercent = 30, maxEmptyPercent = 50, symmetry = 0,
                minTransform = 3, maxTransform = 5, minInsideRate = 0.9, quality = 100.0,
                absoluteRadiusLimit = [(0.99, 0, 100.0)], relativeRadiusLimit = [(0.95, 0.25, 1.0, 100.0)],
                scaleMaxTrial = 100):
    success = False

    while not success:
        # Build a transList
        n = random.randint(minTransform, maxTransform)
        transList = [None] * n
        for i in range(n):
            if i == 0:
                transList[i] = treeTransformer(1.0, 1.0, 3, 0.5, 1.0)
            else:
                transList[i] = treeTransformer(random.random(), random.expovariate(0.7), 2, 0.1, 1.0)

        # Make it a picker
        picker = pickerTransformer(transList, symmetry)

        # Test run
        points = []

        for i in range(50 + width * height // 2):
            coord = randomPoint()

            for j in range(100):
                coord = picker.transform(coord)
            for j in range(100):
                coord = picker.transform(coord)
                points.append(coord)

        xs = [p.real for p in points]
        ys = [p.imag for p in points]

        xs.sort()
        ys.sort()

        # decide the offset

        offset = complex(-xs[len(xs) // 2], -ys[len(ys) // 2])

        # check the radius conditions

        rs = [abs(p+offset) for p in points]
        rs.sort()
        success = True
        for (r, lb, ub) in absoluteRadiusLimit:
            if not lb <= rs[int(len(rs) * r)] <= ub:
                success = False
        for (r1, r2, lb, ub) in relativeRadiusLimit:
            if not lb * rs[int(len(rs) * r2)] <= rs[int(len(rs) * r1)] <= ub * rs[int(len(rs) * r2)]:
                success = False

        if success:
            # now we can scale the picture accordingly!

            wellScaled = False
            smallestLargeBadScale = 1e1000
            currentScaleMaxTrial = scaleMaxTrial

            while not wellScaled and currentScaleMaxTrial > 0:
                scale = (width + height) * random.expovariate(2)

                wellScaled = True
                if scale > smallestLargeBadScale:
                    wellScaled = False

                if wellScaled:
                    mapData = [0] * (width * height)
                    for p in points:
                        coord2 = int((p.real + offset.real) * scale + 0.5 * width), int((p.imag + offset.imag) * scale + 0.5 * height)
                        if (wrapH):
                            coord2 = coord2[0] % width, coord2[1]
                        if (wrapV):
                            coord2 = coord2[0], coord2[1] % height
                        pos = coord2[0] * height + coord2[1]
                        if 0 <= coord2[0] < width and 0 <= coord2[1] < height:
                            mapData[pos] = mapData[pos] + 1

                    if not (minEmptyPercent * 0.01 <= sum(map(lambda x: (x==0)*1, mapData)) / float(len(mapData)) <= maxEmptyPercent * 0.01):
                        wellScaled = False

                    nInside = sum(mapData)
                    if nInside / float(len(points)) < minInsideRate:
                        wellScaled = False
                        if scale < smallestLargeBadScale:
                            smallestLargeBadScale = scale

                currentScaleMaxTrial = currentScaleMaxTrial - 1

            if not wellScaled:
                success = False
            else:
                nIteration = int(width * height * quality * (len(points) / float(nInside)) / 100)

                mapData = [0] * (width * height)
                for i in range(nIteration):

                    coord = randomPoint()

                    for j in range(100):
                        coord = picker.transform(coord)
                    for j in range(100):
                        coord = picker.transform(coord)
                        x = coord.real
                        y = coord.imag
                        x = int((x + offset.real) * scale + 0.5 * width)
                        y = int((y + offset.imag) * scale + 0.5 * height)
                        if (wrapH):
                            x = x % width
                        if (wrapV):
                            y = y % height
                        pos = x * height + y
                        if 0 <= x < width and 0 <= y < height:
                            mapData[pos] = mapData[pos] + 1

                success = True

    return mapData

def FractalTerrainGenerator(width = 20, height = 15, wrapV = False, wrapH = True,
                           waterPercent = 40, symmetry = 0,
                           hillRange = 5, peakPercent = 25):

    if symmetry == 0 or symmetry == 1:
        minTransform = 2
        maxTransform = 4
    elif symmetry == 2 or symmetry == -1:
        minTransform = 2
        maxTransform = 3
    elif symmetry == -2 or symmetry == 3 or symmetry == 4:
        minTransform = 1
        maxTransform = 3
    elif symmetry == -3 or symmetry == -4 or 5 <= symmetry <= 8:
        minTransform = 1
        maxTransform = 2
    else:
        minTransform = 1
        maxTransform = 1

    mapData = drawFractal(width = width, height = height, wrapV = wrapV, wrapH = wrapH,
                          minEmptyPercent = 0, maxEmptyPercent = waterPercent + 10,
                          symmetry = symmetry, minTransform = minTransform, maxTransform = maxTransform,
                          minInsideRate = 0.10)

    vals = list(mapData)
    vals.sort()

    realWaterPercent = waterPercent + random.random() * 20 - 10
    if realWaterPercent < 0:
        realWaterPercent = 0
    if realWaterPercent > 100:
        realWaterPercent = 100
        realWaterPercent = 99.999
    if hillRange <= 0:
        hillRange = 0.001
    if peakPercent <= 0:
        peakPercent = 0.001

    waterLine = vals[int(len(vals) * (realWaterPercent * 0.01))]
    hillLine = vals[int(len(vals) * (1 - hillRange * 4 * 0.01))]
    peakLine = vals[int(len(vals) * (1 - hillRange * 4 * peakPercent * 0.0001))]
    res = [' '] * (width * height)

    for x in range(width):
        for y in range(height):
            newCoord = y * width + x
            oldCoord = x * height + y
            if mapData[oldCoord] > 0:
                if mapData[oldCoord] >= waterLine:
                    res[newCoord] = '.';
                if mapData[oldCoord] >= hillLine:
                    res[newCoord] = '+';
                if mapData[oldCoord] > peakLine:
                    res[newCoord] = '#';

    fixConnectivity (res, width, height, wrapV, wrapH)

    return res

def intCoord (coord, scale, w, h, wrapV, wrapH):
    coord2 = int(coord.real * scale + 0.5 * w), int(coord.imag * scale + 0.5 * h)
    if (wrapH):
        coord2 = coord2[0] % w, coord2[1]
    if (wrapV):
        coord2 = coord2[0], coord2[1] % h

    return coord2

def isNear (c1, c2):
    if (c1[0] == c2[0] and c1[1] - 1 <= c2[1] <= c1[1] + 1):
        return True
    if (c1[1] == c2[1] and c1[0] - 1 <= c2[0] <= c1[0] + 1):
        return True
    return False

def symmetryList (coord, symmetry):
    re = []

    if symmetry < 0:
        for i in range(-symmetry):
            re.append(coord * cmath.exp(1j * i * math.pi * 2 / -symmetry))
            re.append(-coord.conjugate() * cmath.exp(1j * i * math.pi * 2 / -symmetry))
    elif symmetry == 0:
        re.append(coord)
    else:
        for i in range(symmetry):
            re.append(coord * cmath.exp(1j * i * math.pi * 2 / symmetry))

    return re

def drawLine (res, t, scale, w, h, coord, direc, l1, l2, wrapV, wrapH, symmetry, depthLimit = 25):

    c1i = symmetryList (t.transform(coord + direc * l1), symmetry)
    c2i = symmetryList (t.transform(coord + direc * l2), symmetry)

    withinBoundry = False
    for x in c1i + c2i:
        c = intCoord(x, scale, w, h, wrapV, wrapH)
        if 0 <= c[0] < w and 0 <= c[1] < h:
            res[c[0] + c[1] * w] = ' '
        if 0 <= c[0] < w and 0 <= c[1] < h:
            withinBoundry = True

    isAllNear = True
    for coordPair in zip(c1i, c2i):
        if not isNear(intCoord(coordPair[0], scale, w, h, wrapV, wrapH), intCoord(coordPair[1], scale, w, h, wrapV, wrapH)):
            isAllNear = False

    if depthLimit > 1 and (l2 - l1 >= 0.02 or (withinBoundry and not isAllNear)):
        drawLine(res, t, scale, w, h, coord, direc, l1, (l1+l2) / 2.0, wrapV, wrapH, symmetry, depthLimit - 1)
        drawLine(res, t, scale, w, h, coord, direc, (l1+l2) / 2.0, l2, wrapV, wrapH, symmetry, depthLimit - 1)

def RiveriaTerrainGenerator(width = 20, height = 15, wrapV = False, wrapH = True,
                            waterPercent = 25, symmetry = 0, maxContinents = 1):

    finished = False

    while not finished:
        t = treeTransformer(0.5, 1.5, 3, 0.3, 1.2)

        res = ['*'] * (width * height)
        scale = math.sqrt(width ** 2 + height ** 2) * 0.375
        retry = 32

        while res.count(' ') < (waterPercent - 5) * 0.01 * len(res) and retry > 0:
            coord = randomPoint()
            direc = complex(cmath.exp(random.random() * math.pi * 2j))

            length = random.random()
            c1 = coord - direc * length
            c2 = coord + direc * length

            c1i = intCoord(t.transform(c1), scale, width, height, wrapV, wrapH)
            c2i = intCoord(t.transform(c2), scale, width, height, wrapV, wrapH)

            while length <= 32.0 and (0 <= c1i[0] < width and 0 <= c1i[1] < height or 0 <= c2i[0] < width and 0 <= c2i[1] < height):
                length = length + random.random()

                c1 = coord - direc * length
                c2 = coord + direc * length

                c1i = intCoord(t.transform(c1), scale, width, height, wrapV, wrapH)
                c2i = intCoord(t.transform(c2), scale, width, height, wrapV, wrapH)

            drawLine (res, t, scale, width, height, coord, direc, -length, length, wrapV, wrapH, symmetry)

            retry = retry - 1

        finished = (waterPercent - 5) * 0.01 * len(res) < res.count(' ') < (waterPercent + 5) * 0.01 * len(res)

    return res

def ShadeTerrainGenerator(width = 20, height = 15, wrapV = False, wrapH = True,
                            waterPercent = 40, symmetry = 0,
                            hillRange = 5, peakPercent = 25):

    finished = False

    while not finished:
        t = treeTransformer(0.5, 1.5, 7, 0.2, 1.5)
        t2 = linearTransformer()

        mapData = [0] * (width * height)
        scale = math.sqrt(width ** 2 + height ** 2) * 0.25

        for x in range(width):
            for y in range(height):
                i = x * height + y
                mapData[i] = t2.transform(t.transform(complex (x - (width - 1) / 2.0, y - (height - 1) / 2.0) / scale)).real

        vals = list(mapData)
        vals.sort()

        realWaterPercent = waterPercent + random.random() * 20 - 10
        if realWaterPercent < 0:
            realWaterPercent = 0
        if realWaterPercent > 100:
            realWaterPercent = 100
            realWaterPercent = 99.999
        if hillRange <= 0:
            hillRange = 0.001
        if peakPercent <= 0:
            peakPercent = 0.001

        waterLine = vals[int(len(vals) * (realWaterPercent * 0.01))]
        hillLine = vals[int(len(vals) * (1 - hillRange * 4 * 0.01))]
        peakLine = vals[int(len(vals) * (1 - hillRange * 4 * peakPercent * 0.0001))]
        res = [' '] * (width * height)

        for x in range(width):
            for y in range(height):
                newCoord = y * width + x
                oldCoord = x * height + y
                if mapData[oldCoord] > 0:
                    if mapData[oldCoord] >= waterLine:
                        res[newCoord] = '.';
                    if mapData[oldCoord] >= hillLine:
                        res[newCoord] = '+';
                    if mapData[oldCoord] > peakLine:
                        res[newCoord] = '#';
        finished = True

    return res

def printMap(w, h, m):
    for i in range(h):
        print("".join(m[i*w:(i+1)*w]))

if __name__ == "__main__":
    H = 34
    W = 55
    m = FractalTerrainGenerator(W, H, symmetry = -1)
    printMap(W, H, m)
    print(countIslands(m, W, H, False, True))
    print(countContinents(m, W, H, False, True))

    printMap(W, H, RiveriaTerrainGenerator(W, H, symmetry = -1))
