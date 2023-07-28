import cv2
import pytesseract
import aircv
import os
from skimage.metrics import structural_similarity as ssim
import json
import copy


def find_Equipment(path, dir):
    global id
    imgobj = aircv.imread(path)
    imgsrc = aircv.imread('Resources/recognizer.png')
    match_result = aircv.find_all_template(imgobj, imgsrc, 0.6)
    for i in range(0, len(match_result)):
        y = match_result[i]['rectangle'][0][0]
        x = match_result[i]['rectangle'][0][1]
        img_temp = imgobj[x - 39:x + 60, y - 108:y + 138]
        cv2.imwrite(dir + str(id) + '.png', img_temp)
        id = id + 1
    return 0


def blackWhite(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    for i in range(0, 21):
        for j in range(0, 21):
            if gray[i][j] < 30:
                gray[i][j] = 0
            else:
                gray[i][j] = 255
    return gray


def diff(a, b):
    c = a - b
    for i in range(0, 21):
        for j in range(0, 21):
            c[i][j] = c[i][j] ** 2
    return c


def diff3D(a, b):
    c = a - b
    for i in range(0, 21):
        for j in range(0, 21):
            for k in range(0, 3):
                c[i][j][k] = c[i][j][k] ** 2
    return c


def getScore(a, b):
    score = sum(sum(diff(blackWhite(a), blackWhite(b))))
    return score


def getStatTypeSimple(a, b):
    score = 6000
    stat_index = 0
    for i in range(0, len(b)):
        tempScore = getScore(a, b[i])
        if tempScore < score:
            score = tempScore
            stat_index = i
    statType = stat_name[stat_index]
    return statType


def getStatType(a, b):
    score = 0
    stat_index = 0
    for i in range(0, len(b)):
        tempScore = ssim(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.cvtColor(b[i], cv2.COLOR_BGR2GRAY))
        if tempScore > score:
            score = tempScore
            stat_index = i
    statType = stat_name[stat_index]
    return statType


def getSetType(a, b):
    score = 0
    set_index = 0
    for i in range(0, len(b)):
        tempScore = ssim(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.cvtColor(b[i], cv2.COLOR_BGR2GRAY))
        if tempScore > score:
            score = tempScore
            set_index = i
    setType = set_name[set_index]
    return setType


def isPercent(value):
    for i in value:
        if i == ',' or i == ' ':
            value = value.replace(i, '')
    for i in range(0, len(value)):
        if value[i] == '%':
            return [True, value[0:i]]
    return [False, value]


def reformat(value):
    for i in value:
        if not i.isdigit():
            value = value.replace(i, '')
    return value


set_name = ['Attack', 'Counter', 'Crit', 'Defense', 'Destruction', 'Health', 'Hit', 'Immunity', 'Injury', 'Lifesteal',
            'Penetration', 'Protection', 'Rage', 'Resist', 'Revenge', 'Speed', 'Torrent', 'Unity']

setimg_buffer = []
for file_name in os.listdir('Resources/SET'):
    setimg_buffer = setimg_buffer + [cv2.imread('Resources/SET/' + file_name)]

stat_name = ['Attack', 'CriticalHitChance', 'CriticalHitDamage', 'Defense', 'Effectiveness', 'EffectResistance',
             'Health', 'Speed']

statimg_buffer = []
mstatimg_buffer = []
for file_name in os.listdir('Resources/STAT'):
    statimg_buffer = statimg_buffer + [cv2.imread('Resources/STAT/' + file_name)]
for file_name in os.listdir('Resources/MSTAT'):
    mstatimg_buffer = mstatimg_buffer + [cv2.imread('Resources/MSTAT/' + file_name)]

with open("Resources/template.json", "r", encoding="utf-8") as f:
    template = json.load(f)

exporter = []


def exportGear(path, name):
    global id
    for file_name in os.listdir(path):
        if file_name[-4:] == '.png':
            find_Equipment(path + '/' + file_name, path + '/Temp/')

    for file_name in os.listdir(path + '/Temp'):
        print(file_name)
        image = cv2.imread(path + '/Temp/' + file_name)
        main_stat_type = image[13:39, 110:136]
        mainStat = getStatType(main_stat_type, mstatimg_buffer)

        sub_stat1_type = image[50:71, 112:133]
        subStat1 = getStatType(sub_stat1_type, statimg_buffer)
        sub_stat2_type = image[75:96, 112:133]
        subStat2 = getStatType(sub_stat2_type, statimg_buffer)
        sub_stat3_type = image[50:71, 177:198]
        subStat3 = getStatType(sub_stat3_type, statimg_buffer)
        sub_stat4_type = image[75:96, 177:198]
        subStat4 = getStatType(sub_stat4_type, statimg_buffer)
        main_stat_value = image[13:39, 135:190]
        mainStatValue = pytesseract.image_to_string(main_stat_value, config='--psm 8')
        sub_stat1_value = image[50:71, 135:175]
        subStat1Value = pytesseract.image_to_string(sub_stat1_value, config='--psm 8')
        sub_stat2_value = image[75:96, 135:175]
        subStat2Value = pytesseract.image_to_string(sub_stat2_value, config='--psm 8')
        sub_stat3_value = image[50:71, 200:240]
        subStat3Value = pytesseract.image_to_string(sub_stat3_value, config='--psm 8')
        sub_stat4_value = image[75:96, 200:240]
        subStat4Value = pytesseract.image_to_string(sub_stat4_value, config='--psm 8')
        set = image[63:109, 72:107]
        setName = getSetType(set, setimg_buffer)
        item_lv = image[14:29, 18:39]
        itemLv = pytesseract.image_to_string(item_lv, config='--psm 8')
        enhance_lv = image[1:18, 71:102]
        enhanceLv = pytesseract.image_to_string(enhance_lv, config='--psm 8')

        subStatsType = [subStat1, subStat2, subStat3, subStat4]
        subStatsValue = [subStat1Value[0:-1][0:3], subStat2Value[0:-1][0:3], subStat3Value[0:-1][0:3],
                         subStat4Value[0:-1][0:3]]
        gear = copy.deepcopy(template)
        gear["gear"] = name
        gear["set"] = setName + 'Set'
        if reformat(enhanceLv) == '':
            continue
        if int(reformat(enhanceLv)) != 15:
            continue
        else:
            gear["enhance"] = 15

        gear["level"] = reformat(itemLv)
        print(gear["enhance"])
        print(gear["level"])
        if isPercent(mainStatValue[0:-1])[0]:
            gear["main"]["type"] = mainStat + 'Percent'
            gear["augmentedStats"]["mainType"] = mainStat + 'Percent'
            gear["main"]["value"] = isPercent(mainStatValue[0:-1])[1]
            gear["augmentedStats"]["mainValue"] = isPercent(mainStatValue[0:-1])[1]
        else:
            gear["main"]["type"] = mainStat
            gear["augmentedStats"]["mainType"] = mainStat
            gear["main"]["value"] = isPercent(mainStatValue[0:-1])[1]
            gear["augmentedStats"]["mainValue"] = isPercent(mainStatValue[0:-1])[1]

        for i in range(0, 4):
            if isPercent(subStatsValue[i])[0]:
                gear["substats"][i]["type"] = subStatsType[i] + 'Percent'
                gear["substats"][i]["value"] = isPercent(subStatsValue[i])[1]
            else:
                gear["substats"][i]["type"] = subStatsType[i]
                gear["substats"][i]["value"] = isPercent(subStatsValue[i])[1]
        gear["id"] = file_name[:-4]
        gear["ingameId"] = file_name[:-4]
        gear["ingameEquippedId"] = file_name[:-4]
        global exporter
        exporter = exporter + [gear]


id = 0
exportGear('Screenshots/1-Weapon', 'Weapon')
exportGear('Screenshots/2-Helmet', 'Helmet')
exportGear('Screenshots/3-Armor', 'Armor')
exportGear('Screenshots/4-Necklace', 'Necklace')
exportGear('Screenshots/5-Ring', 'Ring')
exportGear('Screenshots/6-Boots', 'Boots')
finalExporter = {"heroes": [], "items": []}
finalExporter["items"] = exporter
with open("export.json", "w", encoding="utf-8") as f:
    json.dump(finalExporter, f, indent=4, ensure_ascii=False)
