import json
import re
import math

path = "C:/Users/Philipp/AppData/Roaming/.minecraft/versions/1.13-pre6/minecraft/"
allBlocks = json.loads(open("../../Python/113/blocks.json").read()) #grass, blocks

outData = []

def parseStr(inStr):
    d = re.findall(r'[a-zA-Z_-]+=[A-Za-z0-9_-]+', inStr)
    out = {}
    for entry in d:
        s = entry.split('=')
        out[s[0]] = s[1]
    return out

def handleSpecialBlocks(model):
    if model == "grass_block":
        return ("top", 0)
    if model.endswith("_slab"): #slab bottom
        return ("top", 9)
    if model.endswith("_slab_top"): #slab top
        return ("top", 10)
    if model.endswith("_slab_double"): #slab double/full block
        return ("end", 0)
    if "fence" in model:
        return ("texture", 4)
    if model.endswith("_carpet"):
        return ("wool", 1)
    if "height" in model:
        return ("texture", 1)
    if "trapdoor" in model:
        return ("texture", 1)
    if model.startswith("block/fire") and "coral" not in model:
        return ("fire", 8)
        
    return None

def getTextureFromModel(model):
    modelData = json.loads(open("{}models/{}.json".format(path, model)).read())
    textures = modelData["textures"]
    texture = ""
    blockType = 0 #0 = SOLID, 1 = FLAT (Snow/Trapdor/Carpet), 2 = TORCH, 3 = FLOWER/PLANT, 4 = FENCE, 5 = WIRE, 6 = RAIL, 8= FIRE, 9 = SLAP bottom, 10 = SLAP top
    special = handleSpecialBlocks(model)

    if special is not None:
        texture = textures[special[0]]
        blockType = special[1]
    else:
        if 'all' in textures:
            texture = textures['all']
        elif 'top' in textures:
            texture = textures['top']
        elif 'side' in textures:
            texture = textures['side']
        elif 'cross' in textures:
            texture = textures['cross']
            blockType = 3
        elif 'rail' in textures:
            texture = textures['rail']
            blockType = 6
        elif 'texture' in textures:
            texture = textures['texture']
        elif 'crop' in textures:
            texture = textures['crop']
            blockType = 3
        elif 'plant' in texture:
            texture = textures['plant']
            blockType = 3
        elif 'line' in texture:
            texture = textures['line']
            blockType = 5
        elif 'torch' in texture:
            texture = textures['torch']
            blockType = 2
        elif 'particle' in textures:
            texture = textures['particle']
        else:
            texture = textures[list(textures.keys())[0]] #simply take first texture
            #print("Take first texture for {}".format(model))

    return (texture, blockType)

def getTextureFromState(textures, propOfState): #returns texture tuple for given state
    if len(textures) == 1:
        return textures[list(textures.keys())[0]] #only one texture

    for textureConds, texture in textures.items():
        found = True
        texCondDic = parseStr(textureConds)
        for texCondKey, texCondVal in texCondDic.items():
            if texCondKey in propOfState:
                if propOfState[texCondKey] != texCondVal: #wrong texture
                    found = False
                    
        if found:
            return texture

    print("Texture not found")
    return None
                
 
def getTextures(block):
    blockStatesData = None
    try:
        blockStatesData = json.loads(open("{}blockstates/{}.json".format(path, block)).read())
    except:
        print("Could not load:{}".format(block))
        return {}

    if 'variants' not in blockStatesData:
        #print("no variants in {}".format(block))
        if 'multipart' not in blockStatesData:
            return {}
        else:
            #print("multipart in: {}".format(block))
            apply = list(blockStatesData["multipart"])[0]["apply"] #take first mdoel in multipart
            model = ""
            if type(apply) is list:
                model = apply[0]["model"]
            else:
                model = apply["model"]
            return {"": getTextureFromModel(model)}
                

    variants = blockStatesData["variants"]

    buffer = {}
    
    for varName, varModel in variants.items():
        model = ""
        if type(varModel) is list:
            model = varModel[0]['model'] #list of diffrent models, simply take first. They should have all the same texture
        else:
            model = varModel['model'] #only one model, take it
        modelData = getTextureFromModel(model)
        buffer[varName] = modelData

    return buffer
    

for blockNameL, blockData in allBlocks.items():
    if blockNameL == "minecraft:air" or blockNameL == "minecraft:void_air" or blockNameL == "minecraft:cave_air":
        continue

    blockOutData = {} #Data of Block that gets written to disc

    #remove "minecraft:" from name
    blockName = blockNameL
    if blockNameL.startswith("minecraft:"):
        blockName = blockNameL[10:]

    textures = getTextures(blockName)
    
    if len(textures) == 0:
        print("No texures for {}".format(blockName))
        continue

    if 'properties' not in blockData:
        if len(textures) > 1:
            print("{} has multiple textures but only one state".format(blockName))
            break
        state = list(blockData["states"])[0]
        texture = textures[list(textures.keys())[0]]
        d = {"texture": texture[0], "from": state["id"], "to": state["id"], "blockType": texture[1]}
        outData.append(d)

    else: #multiple states
        for state in blockData["states"]:
            propOfState = state["properties"]
            texture = getTextureFromState(textures, propOfState)
            d = {"texture": texture[0], "from": state["id"], "to": state["id"], "blockType": texture[1]}
            outData.append(d)

#remove duplicates     
pos = 0
while pos < len(outData)-1:
    if outData[pos]["texture"] == outData[pos+1]["texture"] and outData[pos]["blockType"] == outData[pos+1]["blockType"]:
        if outData[pos]["to"]+1 == outData[pos+1]["from"]:
            outData[pos]["to"] = outData[pos+1]["to"]
            del outData[pos+1]
            pos = max(0, pos-2)
        else:
            print("{}\n{}".format(outData[pos], outData[pos+1]))
    pos += 1
            
with open('colors.json', 'w') as outfile:
    json.dump(outData, outfile)
    