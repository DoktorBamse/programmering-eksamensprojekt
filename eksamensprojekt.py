import json
import re
import time
import os
import math

class Block:
    def __init__(self, name, tool, type, hardness):
        self.name = name
        self.tool = tool
        self.type = type
        self.hardness = hardness

    def printWithId(self, id):
        print(id + ". " + self.name)

    def toolLevel(self):
        if (self.type[-2:] == " I"):
            level = "Wooden "
        elif (self.type[-3:] == " II"):
            level = "Stone "
        elif (self.type[-4:] == " III"):
            level = "Iron "
        elif (self.type[-3:] == " IV"):
            level = "Diamond "
        else:
            level = ""

        return level

    def printInfo(self):
        print("\033[1;44m- BLOCK INFORMATION -\033[0m")
        print("\033[1mName / Type: \033[0m" + self.name + " (" + self.type +")")
        print("\033[1mRecommended tool: \033[0m" + self.toolLevel() + self.tool)
        print("\033[1mHardness: \033[0m" + self.hardness)
    
    def getSpeedMultiplier(self, chosenTool, chosenToolLevel):
        if (chosenTool == "Hand" or chosenTool == "Any tool" or chosenTool == "Any tool (instant)"): 
            speedMultiplier = 1

        elif (chosenTool == "Shear"):
            if (self.name == "Wool"): speedMultiplier = 5
            else: speedMultiplier = 15

        elif (chosenTool == "Sword"):
            if (self.name == "Cobweb"): speedMultiplier = 15
            else: speedMultiplier = 1.5

        elif(chosenTool == "Bucket"): speedMultiplier = 99999
        elif (chosenToolLevel == "Wooden"): speedMultiplier = 2
        elif (chosenToolLevel == "Stone"): speedMultiplier = 4
        elif (chosenToolLevel == "Iron"): speedMultiplier = 6
        elif (chosenToolLevel == "Gold"): speedMultiplier = 12
        elif (chosenToolLevel == "Diamond"): speedMultiplier = 8
        elif (chosenToolLevel == "Netherite"): speedMultiplier = 9

        return speedMultiplier

    def calculateMiningTime(self, chosenTool, chosenToolLevel, chosenEfficiency, chosenHaste, chosenMiningFatigue, inWater, onGround, blockAmount):
        canHarvest = False
        correctTool = False

        # Checks if correct tool is being used
        if ("Any tool" not in self.tool):
            if (chosenTool == self.tool): correctTool = True
        else: canHarvest = True

        # Checks if correct type of tool is being used, in order to harvest
        if (correctTool == True):
            toolLevelRankings = [" ", "Wooden ", "Stone ", "Iron ", "Gold ", "Diamond ", "Netherite "]
            if (chosenToolLevel == None): chosenToolLevel = ""
            chosenToolRank = toolLevelRankings.index(chosenToolLevel + " ")
            blockToolRank = self.toolLevel()
            if (blockToolRank == ""): blockToolRank = " "
            blockToolRank = toolLevelRankings.index(blockToolRank)

            if (blockToolRank > chosenToolRank):
                if (blockToolRank == 3 and chosenToolRank == 4): canHarvest = True
            else: canHarvest = True

        if (correctTool == True): 
            speedMultiplier = self.getSpeedMultiplier(chosenTool, chosenToolLevel)
            if (chosenEfficiency != 0 and chosenEfficiency != None):
                speedMultiplier += math.pow(chosenEfficiency, 2) + 1
        else: speedMultiplier = 1

        if (chosenHaste != 0):
            speedMultiplier *= 0.2 * chosenHaste + 1
        if (chosenMiningFatigue != 0):
            speedMultiplier *= math.pow(0.3, min(chosenMiningFatigue, 4))
        if (inWater):
            speedMultiplier /= 5
        if (not onGround):
            speedMultiplier /= 5

        damage = speedMultiplier / (float) (self.hardness)

        if (canHarvest):
            damage /= 30
        else:
            damage /= 100

        if (damage > 1):
            ticks = blockAmount
            seconds = ticks / 20
            return seconds

        ticks = math.ceil(1 / damage) * blockAmount + ((blockAmount - 1) * 6)
        seconds = ticks / 20
        return seconds

def versionChecker(string):
    string = string.lower()
    versions = " ("
    if string.find("java") != -1:
        versions += "JE/"
    if string.find("bedrock") != -1:
        versions += "BE/"
    if string.find("education") != -1:
        versions += "edu/"
    versions = versions[:-1] + ")"
    return versions

def getTools(blockData):
    tools = []

    while True:
        startIndex = blockData.find("{{ItemLink|") + 11
        if startIndex == -1 + 11:
            break
        endIndex = blockData[startIndex:].find("}}") + startIndex
        item = blockData[startIndex:endIndex]

        if "=" in item:
            blockData = blockData[0:startIndex-11] + "{{BlockLink|" + blockData[startIndex:]
        else:
            blockData = blockData[0:startIndex-11] + "{{FoundItem|" + blockData[startIndex:]
            tools.append(item)

    startIndex = blockData.find("\\'\\'Any\\'\\' (all") + 4
    blockData = blockData[0:startIndex] + "FoundItem|Any tool" + blockData[startIndex+3:]
    tools.append("Any tool")

    startIndex = blockData.find("\\'\\'Any\\'\\' (instantly") + 4
    blockData = blockData[0:startIndex] + "FoundItem|Any tool (instant)" + blockData[startIndex+3:]
    tools.append("Any tool (instant)")

    startIndex = blockData.find("\\'\\'None\\'\\' (unbreakable") + 4
    blockData = blockData[0:startIndex] + "FoundItem|None" + blockData[startIndex+3:]
    tools.append("None")

    return tools, blockData

def getTypes(blockData):
    types = []

    endIndex = blockData.find("\\n|\\n<div")

    while endIndex != -1:
        blockData = blockData[0:endIndex] + ":TypeEnd" + blockData[endIndex+9:]
        type = blockData[0:endIndex+8]

        startIndex = type.rfind("\\n|")
        blockData = blockData[0:startIndex] + "TypeStart:" + blockData[startIndex+3:]

        type = blockData[startIndex+10:]
        type = type[0:type.find(":TypeEnd")]

        if "|\"" in type: type = type[type.find("|\""):]
        if "\"|" in type: type = type[:type.find("\"|")]
        type = type.strip()
        type = type.strip("[")
        type = type.strip("]")
        type = type.strip("|\"")
        type = type.strip("\"")
        type = type.strip("\\n")

        onlyIndex = type.find("{{only|")
        if onlyIndex != -1:
            versions = versionChecker(type)
            type = type[0:onlyIndex-1] + versions

        types.append(type)

        blockData = blockData[0:startIndex] + "TypeStart:" + type + blockData[blockData.rfind(":TypeEnd"):]

        endIndex = blockData.find("\\n|\\n<div")

    return types, blockData

def getToolTypesIndex(tools, types, blockData):
    toolTypes = []
    typeNumber = 0

    for tool in tools:
        toolIndex = blockData.find("FoundItem|" + tool)
        nextToolIndex = blockData.find("FoundItem|",toolIndex + 1)

        while True:
            type = types[typeNumber]
            typeIndex = blockData[toolIndex:nextToolIndex].find("TypeStart:" + type + ":TypeEnd")

            if (len(toolTypes) != 0):
                lastIndex = toolTypes[-1][2]
            else: lastIndex = 0

            if (typeIndex + toolIndex < lastIndex):
                break
            else:
                toolType = [tool, type, typeIndex + toolIndex]
                toolTypes.append(toolType)
                typeNumber += 1
                if (typeNumber == len(types)):
                    break
    return toolTypes

def getBlockIndex(blockData):
    blocks = []

    while True:
        startIndex = blockData.find("{{BlockLink|") + 12
        if startIndex == -1 + 12:
            break

        endIndex = blockData[startIndex:-1].find("\\n") + startIndex
        blockData = blockData[0:startIndex - 12] + "{{FoundLink|" + blockData[startIndex:]

        block = blockData[startIndex:endIndex] 

        idIndex = block.find("id=")
        if idIndex != -1:
            if idIndex == 0:
                block = block[block.find("|") + 1:]
            else: 
                block = block[0:block.find("|")] + block[block.find("}}"):]

        onlyIndex = block.find("{{only|")
        if onlyIndex != -1:
            versions = versionChecker(block)
            block = block[0:block.find("}}")] + versions + "}}"

        if "link=" in block:
            block = block[block.find("|")+1:]
            if "link=" in block:
                block = block[5:]

        splitIndex = block.find("|")
        if splitIndex != -1:
            block = block[splitIndex+1:]

        block = block[0:block.find("}}")]

        newBlock = [block, startIndex]
        blocks.append(newBlock)
    
    return blocks

def getHardness(name, bigData):
    if "(" in name:
        name = name[0:name.find("(") - 1]
    
    index = bigData.find(">" + name + "</span></span></a>\\n</th>\\n<td>")

    if (index == -1):
        return
    
    startIndex = index + 32 + len(name)
    endIndex = bigData.find("\\", startIndex)
    hardness = bigData[startIndex:endIndex]

    if (hardness == "?" or hardness == "∞"):
        return
    else:
        return hardness

def instantiateBlocks(toolTypes, blocks, bigData): 
    blockList = []
    blockNumber = 0 

    for i in range(len(toolTypes)):
        tool = toolTypes[i][0]
        type = toolTypes[i][1]
        if (i == len(toolTypes) - 1):
            nextTypeIndex = -1
        else:
            nextTypeIndex = toolTypes[i+1][2]

        while True:
            name = blocks[blockNumber][0]
            blockIndex = blocks[blockNumber][1]

            if (blockIndex == -1):
                break
            elif (blockIndex > nextTypeIndex and nextTypeIndex != -1):
                break
            else:
                hardness = getHardness(name, bigData)
                if (hardness != None and tool != "None" and "instant" not in tool):
                    block = Block(name, tool, type, hardness)
                    blockList.append(block)
                blockNumber += 1
                if (blockNumber == len(blocks)):
                    break

    return blockList

with open("blockData.json", "r", encoding="utf-8") as file:
    blockData = json.load(file) 
blockData = str(blockData)

with open("bigData.json", "r", encoding="utf-8") as file:
    bigData = json.load(file) 
bigData = str(bigData)

tools, blockData = getTools(blockData)
types, blockData = getTypes(blockData)
toolTypes = getToolTypesIndex(tools, types, blockData)
blocks = getBlockIndex(blockData)
blockList = instantiateBlocks(toolTypes, blocks, bigData)

def numberCheck(userInput, minValue, maxValue):
    try:
        userInput = int(userInput)
        if (minValue <= userInput and userInput <= maxValue):
            return True
        else:
            print("\n\033[1;41mHas to be between " + (str) (minValue) + " and " + (str) (maxValue) + "\033[0m")
            time.sleep(2)
            return False
    except ValueError:
        print("\n\033[1;41mHas to be a whole number\033[0m")
        time.sleep(2)
        return False

def printBlocks():
    while True:
        oldTool = ""
        blockIndex = 0
        tools = []

        for block in blockList:
            if (block.tool != oldTool):
                print("\n\033[1;44m- " + block.tool + " \033[0m")
                if "Any tool" in block.tool: tools.append("Hand")
                else: tools.append(block.tool)

            blockIndex += 1
            id = (str) (blockIndex)
            block.printWithId(id)
            oldTool = block.tool


        userInput = input("\n\033[1mType block number: \033[0m")
        if (numberCheck(userInput, 1, len(blockList)) == True): break
        else: continue
    
    return blockList[(int) (userInput) - 1], tools

def pickTool():
    print("\n\033[1;43m- SETTINGS -\033[0m")

    count = 0
    for tool in relevantTools:
        count += 1
        if "Any tool" in tool: tool = "Hand"
        print((str) (count) + ". " + tool)

    userInput = input("\n\033[1mPick a tool: \033[0m")
    if (numberCheck(userInput, 1, len(relevantTools)) == True): 
        return relevantTools[(int) (userInput) - 1]
    else: return None

def pickToolLevel():
    print("\n\033[1;43m- SETTINGS -\033[0m")

    count = 0
    levels = ["Wooden", "Stone", "Iron", "Gold", "Diamond", "Netherite"]
    for level in levels:
        count += 1
        print((str) (count) + ". " + level)

    userInput = input("\n\033[1mPick tool level: \033[0m")
    if (numberCheck(userInput ,1 , len(levels)) == True): 
        return levels[(int) (userInput) - 1]
    else: return None

def pickEffect(effect):
    print("\n\033[1;43m- SETTINGS -\033[0m")

    userInput = input("\033[1mPick " + effect + " level: \033[0m")
    if (numberCheck(userInput, 0 , 255) == True): 
        return (int) (userInput)
    else: return None

def pickTrueFalse(statement):
    print("\n\033[1;43m- SETTINGS -\033[0m")

    print("1. True")
    print("2. False")

    userInput = input("\n\033[1m" + statement + ": \033[0m")
    if (numberCheck(userInput, 1 , 2) == True): 
        if ((int) (userInput) == 1): return True
        else: return False
    else: return None

def pickBlockAmount():
    print("\n\033[1;43m- SETTINGS -\033[0m")

    userInput = input("\033[1mPick amount of blocks: \033[0m")
    if (numberCheck(userInput, 1 , 1000000) == True): 
        return (int) (userInput)
    else: return None

block, relevantTools = printBlocks()
chosenTool = None
chosenToolLevel = None
chosenEfficiency = None
chosenHaste = None
chosenMiningFatigue = None
inWater = None
onGround = None
blockAmount = None

while True:
    os.system("cls")
    block.printInfo()

    if (blockAmount != None): print("\n\033[1;42m- SETTINGS -\033[0m", end="")

    if (chosenTool == None):
        chosenTool = pickTool()
        continue
    else: 
        if ("Any tool" not in chosenTool and chosenTool != "Shears" and chosenTool != "Bucket" and chosenTool != "Hand"):
            if (chosenToolLevel == None):
                chosenToolLevel = pickToolLevel()
                continue
            else: print("\033[1m\nTool: \033[0m" + (str) (chosenToolLevel) + " " + (str) (chosenTool))
        else: print("\033[1m\nTool: \033[0m" + (str) (chosenTool))

    if ("Any tool" not in chosenTool and chosenTool != "Sword" and chosenTool != "Bucket" and chosenTool != "Hand"):
        if (chosenEfficiency == None):
            chosenEfficiency = pickEffect("efficiency")
            continue
        else: print("\033[1mEffeciency level: \033[0m" + (str) (chosenEfficiency))

    if (chosenHaste == None):
        chosenHaste = pickEffect("haste")
        continue
    else: print("\033[1mHaste level: \033[0m" + (str) (chosenHaste))

    if (chosenMiningFatigue == None):
        chosenMiningFatigue = pickEffect("mining fatigue")
        continue
    else: print("\033[1mMining fatigue level: \033[0m" + (str) (chosenMiningFatigue))   

    if (inWater == None):
        inWater = pickTrueFalse("In water (without aqua affinity)")
        continue
    else: print("\033[1mIn water (without aqua affinity): \033[0m" + (str) (inWater))   

    if (onGround == None):
        onGround = pickTrueFalse("Standing on ground")
        continue
    else: print("\033[1mOn ground: \033[0m" + (str) (onGround))  

    if (blockAmount == None):
        blockAmount = pickBlockAmount()
        continue
    else: print("\033[1mBlock amount: \033[0m" + (str) (blockAmount)) 

    break

def convertTime(time):
    years = (str) ((int) (time // 31556926))
    if (years != "1"): 
        years = years + " years"
    else: years = years + " year"
    time = time % 31556926

    days = (str) ((int) (time // 86400))
    if (days != "1"): 
        days = days + " days"
    else: days = days + " day"
    time = time % 86400

    hours = (str) ((int) (time // 3600))
    if (hours != "1"): 
        hours = hours + " hours"
    else: hours = hours + " hour"
    time = time % 3600

    minutes = (str) ((int) (time // 60))
    if (minutes != "1"): 
        minutes = minutes + " minutes"
    else: minutes = minutes + " minute"
    time = time % 60

    seconds = (str) (round(time, 2))
    if (seconds != "1"): 
        seconds = seconds + " seconds"
    else: seconds = seconds + " second"

    totalTime = years + ", " + days + ", " + hours + ", " + minutes + " and " + seconds

    # Bugged, prints out it anyways, if it's "0.0"
    if (years == "0 years"):
        totalTime = totalTime[totalTime.find(years) + 9:]
        if (days == "0 days"): 
            totalTime = totalTime[totalTime.find(days) + 8:]
            if (hours == "0 hours"): 
                totalTime = totalTime[totalTime.find(hours) + 9:]
                if (minutes == "0 minutes"):
                    totalTime = totalTime[totalTime.find(minutes) + 14:]

    return totalTime

timeToMine = block.calculateMiningTime(chosenTool, chosenToolLevel, chosenEfficiency, chosenHaste, chosenMiningFatigue, inWater, onGround, blockAmount)

convertedTime = convertTime(timeToMine)

print("\n\033[45;1m- Time it will take to mine -\033[0m\n" + convertedTime)