from keys import api_token
import requests, json
egb = {76482434: 'admiralbulldog', 193673646: 'Lyrical', 196482746: 'ainkrad', 93526520: 'bb3px', 116249155: 'nefrit', 363739653: 'alberkaaa', 115651292: 'copy', 196878136: 'Kataomi', 208181197: 'adzantick', 105045291: 'thiolicor', 106305042: 'Larl', 106755427: 'Mo13ei', 203351055: 'malik', 27178898: 'SkyLark', 187824320: 'kitrak', 324277900: 'yopaj', 412413765: 'stonebank', 50580004: 'xibbe', 130991304: 'Riddys', 152168157: 'omar', 54580962: 'insania', 131303632: '4nalog', 94155156: 'fly', 103910993: 'lil pleb', 123787715: 'respect', 383867949: 'SLATEM$', 91730177: 'Seleri', 104334048: 'kidaro', 117015167: 'pablo', 191066225: '4IVAN', 177411785: 'daxak', 164685175: 'K1', 193564777: 'otaker', 165110440: 'retsu', 177203952: 'yuma', 18689006: 'pma', 835864135: 'pma', 100594231: 'skem', 163458082: 'ряф^^', 117514269: 'laise', 165564598: 'MieRo`', 919735867: 'daze', 168126336: 'cloud', 113331514: 'miposhka', 111030315: 'zayac', 292921272: 'wisper', 114619230: 'crystallize', 957204049: 'gotthejuice', 100058342: 'skiter', 164962869: 'Shad', 93817671: 'malady', 138880576: 'Davai Lama', 140288368: 'tobi', 346412363: 'ari', 125445069: 'v1olent', 262838756: 'kordan', 194979527: 'shigetsu', 40805086: 'mellojul', 294135421: 'Nicky`Cool', 107803494: 'Ori', 86698277: '33', 241519559: 'dream', 171097887: 'Nande', 418942836: 'rincyq', 161839895: 'antares', 320219866: 'kaori', 879017980: 'darklord', 48823667: 'Bengan', 392169957: 'Sanctity-', 175311897: 'swedenstrong', 96803083: 'Stormstormer', 210053851: 'Lorenof', 16497807: 'tofu', 898754153: 'ame', 312436974: 'CHIRA_JUNIOR', 904131336: 'Munkushi~', 56351509: 'dm', 181267255: 'onejey', 302214028: 'collapse', 106573901: 'noone', 140297552: 'no!ob', 58513047: 'supream^', 183719386: 'atf', 93618577: 'bzm', 152455523: 'v-tune', 127617979: 'crystallis', 116934015: 'dyrachyo', 109757023: 'ulnit', 118134220: 'fath_bian', 98885811: 'lowskill', 126238768: 'gunnar', 217472313: 'xakoda', 25907144: 'cr1t', 108958769: 'phantomem', 221666230: 'quinn', 178692606: 'antoha', 175463659: 'cooman', 114585639: 'lil_nickdota', 86725175: 'resolut1on', 117421467: 'sonneiko', 369342470: 'sonneiko', 86811043: 'monkeys-forever', 245373129: 'xcalibur', 56939869: 'gorgc', 150748346: 'krylat', 115464954: 'desire', 165671428: 'sclkoma', 35504297: 'leBron', 401792574: 'taiga', 89117038: 'yapzor', 167976729: 'yuragi', 94049589: 'fng', 92847434: 'ghostik', 132851371: 'ramzes', 154715080: 'abed', 195108598: 'noticed', 393024955: 'stariy_bog', 1060164724: 'speedmanq', 113995822: 'iltw', 171262902: 'watson', 164199202: '9class', 315657960: 'mason', 73401082: 'dukalis', 170834508: 'player1', 92706637: 'iannihilate', 9403474: 'yamich', 126212866: 'saberlight', 375507918: '23savage', 355168766: 'natsumi', 10366616: 'sneyking', 86738694: 'qojqva', 88271237: 'ceb', 172099728: 'kiritych', 190100004: 'shiishak', 124801257: 'nightfall', 1675023758: 'limitlessqt', 361688848: 'dnm', 999961232: 'baxadoto', 132309493: 'raven', 404150207: 'y0nd', 317880638: 'save', 431770905: 'torontotokyo', 145550466: 'dubu', 123023873: 'squad1x', 368917218: 'layme', 208407289: 'reira', 480412663: 'gpk', 26316691: 'illidan', 241884166: 'hellscream', 103735745: 'saksa', 439345730: 're1bl', 105178768: 'bsj', 133558180: 'zitraks', 84429681: 'moo', 898455820: 'malr1ne', 372801387: 'shergarat', 97658618: 'timado', 96169991: 'ar1se', 165390194: 'dinozavrik', 173480718: 'sketcher_8', 321580662: 'yatoro', 86700461: 'w33haa', 1044002267: 'satanic', 70388657: 'dendi', 858106446: 'kiyotaka', 250114507: 'iceberg', 293731272: '7jesu', 1171243748: 'parker', 141690233: 'cancel', 295697470: 'immersion', 331855530: 'pure', 159020918: 'rodjer', 148612029: 'poshliy_vladik', 100471531: 'jabz', 87063175: 'lelis', 117311875: 'lukiluki', 94054712: 'topson', 1159912962: 'azimovdota', 95145869: '420jenkins', 155162307: 'smilling knight', 77490514: 'boxi', 256156323: 'mira', 858200619: 'afganistan_doto', 84772440: 'iceiceice', 102099826: 'dj', 1150772339: 'Timadofun', 335437141: 'yamichc', 195415954: 'inhuman', 121870008: 'roflmao', 218231587: 'not me', 92487440: 'Fraser', 130123201: 'mitrofanushka', 320017600: 'daylight', 309345956: 'volshebnik', 47977302: 'dr.bum', 72393079: 'mannik', 185059559: 'hduo', 86785083: 'afterlife', 889201734: 'malady(smurf)', 145065875: 'sayuw', 139822354: 'setsu', 101695162: 'fy', 262476000: 'stojkov', 220154695: 'mks', 150961567: 'planet', 126842529: 'Ws', 196493853: 'Aq', 205226309: '1D3E', 173978074: 'NothingToSay', 202217968: 'Emo', 301750126: 'Mikoto', 145957968: 'b a b', 392565237: 'JaCkky', 206642367: 'Ghost', 137129583: 'Xm', 185908355: 'lou', 126064542: 'Pangpang', 147767183: 'Zeal', 170896543: 'YSR-04E', 145358275: '五年两年多少年', 140411011: 'TraVins', 152859296: 'jhocam', 282359850: 'BEEBIE', 134711350: 'dstones', 168028715: 'flyfly', 196931374: '458', 458287006: 'x123', 315272623: 'blood', 139937922: 'yang', 219755398: 'jing', 191597529: 'undyne_', 156029808: 'bdz', 148880949: 'player3', 171874354: 'player4', 372105535: 'htz', 116837520: 'gan', 287966898: 'player5', 206379758: 'cdr', 137092505: 'Allen', 156195808: '', 293904640: 'wayne', 371876003: '', 152545459: 'gabbi', 138543123: 'pyw', 199953095: '哦？', 129958758: '狠', 80929738: '千雪ちゆき', 150960169: '大葡萄dy95087', 320252024: 'iroha', 162126721: 'Flyicu', 286279456: '绝世高手', 470392491: '无相', 373667079: 'Arc Drive', 489696354: '雨季不再来', 396462897: '构式', 398896331: 'Myut', 122586792: '灰原 哀', 219950601: 'LeMao', 353498499: 'Griffith', 193815691: 'Q', 349495318: 'Krish`-', 94281932: ':)', 277835316: '))))))))))))))))))', 153727297: '匿名的', 135656964: '。', 100598959: '4', 394071544: 'BLESSED CHINA LOW RANK', 118305301: 'Guts', 158847773: 'ni', 128398556: '哥白尼', 193884241: 'Kaiju No.16', 164948665: 'Manic', 201826550: 'Yellow', 181145703: 'Steins Gate', 1114778241: 'pos 1 ty', 139268745: '君とONE LOVE永遠に2 hearts', 252551173: 'Ignite me', 100616105: 'cml', 141398569: '心碎小子', 158401119: 'LYcHee', 155447692: 'bwiset', 99983413: '86 pancakes ^-^', 108717482: 'Obsession', 241107899: '☁️1/22yearsold', 113435203: 'ChYuaN', 139031324: 'Xiang', 285319482: '.-.', 1066782497: '134882858(Bnlvdn)', 134357466: 'Twitch.tv/micedoto', 199222238: '谢谢', 207945924: 'mid', 195072449: 'NOOB', 286985748: 'Jigi Prime', 167488455: '-', 135673679: 'Like a child waiting for X`mas', 311360822: 'winkwell', 100406744: '45', 257694165: '影', 285770518: 'KNP♥', 101460882: 'RAYUM', 173378701: 'king bob', 199833749: '< blank >', 446737104: '.', 142991995: 'core player', 134665319: 'Bagnaia^', 130416036: '正', 184138153: 'Murasaki-', 174081158: '混', 252716815: '蛊心', 363029497: '偷感大王', 76904792: 'ahchin', 228517469: 'Sky Striker Mobilize - Engage!', 130040732: 'WAITING FOR HUMAN TEAM (EN/CN)', 1029352973: '隔壁老王', 135607261: '#NotLikeThis MODE: Oli~ Comeback', 162274034: 'dream on', 836325393: 'Stuck in reverse LFT', 336937491: 'dx', 126397214: 'enjoy', 363724571: ':)', 356343152: 'ZZZ', 149259389: '0.0', 902424411: 'Cliché', 399862798: 'Peter Griefing', 430337036: '-.-', 318286721: '龙', 215121858: 'Bot (2)', 89423756: '1974', 147267417: 'nice', 484759837: '烛影斧声', 1129118044: 'B-RABBIT', 106863163: '问剑', 230487729: 'Reverie for Another Sphere', 140251702: '-O-O-', 185590374: 'Dendi 2009', 405351356: 'Rerise', 847565596: 'rue', 343084576: 'NARMAN', 972243573: 'Matson', 333700720: 'blackpink', 146711951: 'Force', 152285172: 'arcane fantasy', 1202267677: 'aik~', 101356886: 'Miracle---', 122817493: 'patient zero', 184620877: '2ls', 1062148399: 'диф', 93845249: 'Wuiter', 450454900: 'Kiseki', 256444993: "these percs' they heaven sent", 326327879: 'xsvamp1re', 392006194: 'what if i fall?', 1286226756: "teydo;tlikewinnin'", 113112046: 'nn_', 917319178: 'Stewie2K', 84385735: 'Kyzko', 345509021: 'tv/lukas_doto', 223382342: 'b0t', 351836036: 'Pensils', 234119750: '=/', 191362875: 'Speeed', 995397364: 'CLOWNFIESTA', 383788462: 'мистер мораль', 84853828: 'Aquariano nato', 135403353: 'MC HAMMSTER', 107023378: 'so bad', 1677766292: 'rostislav999', 349569834: 'lantana', 851178649: 'LESHA-KILLER_52', 92601861: 'I will be the best', 872008996: 'onlywinmatter', 860414909: 'Actor', 190826739: '90210', 168291251: "what's ok", 136829091: 'NongMon', 199666759: 'К о т', 1048617659: 'крeкep', 296702734: 'so close but so far', 917164766: '神', 1001714951: 'ботик', 1673586483: 'Sae', 127530803: 'y:<', 860264647: 'p~love.心の平和', 123213918: 'lucker', 175350492: '536', 147408273: 'Ruling Days', 1224667851: 'losing every lane', 364698744: 'Мамонтенок', 402583877: 'Лузаю с кайфом))', 126127817: 'Gamer', 170809075: 'marmelad bear', 164090265: 'Megoway-', 232281409: 'LLF', 1031547092: 'Mistake', 123717676: 'dininizi sikiyim', 457637739: 'Limbo🔴', 1172719712: 'Midnight', 133682196: 'Blaze', 151669649: 'NLineは', 285282252: 'JANTER', 127565532: 'Fishman', 891521610: 'Mr. Luck', 383361785: "raison d'etre", 891566317: 'johnnupro', 257921351: 'swaga', 215308703: '@SaintsMike', 158072796: 'maybe win maybe no', 352545711: 'Seishiro Nagi', 312051473: '3 pos dif', 1675517497: 'Ankou ♡', 185202677: 'goomoonryong', 401902808: 'Makunouchi', 1004229172: 'Brutal-', 899495504: 'fiend', 90423751: 'Double jump', 847783992: 'any?', 175891708: '-/', 108928414: 'CHAD', 112426916: 'MTD)', 179266369: ',', 911977148: '< blank >', 114162163: 'tg3', 857788254: 'Abo Prime', 1150028510: '>^)#--', 388905349: '.', 405499625: 'hardmode gameplay enj', 250199344: 'Mny', 1010173059: 'Nagato', 1016676974: 'catching up', 196490133: 'Focus', 192981126: 'hAze._.', 196481318: 'Hitogami 裏切りの神', 124286163: 'Котакбас', 118370366: 'single down', 135513713: 'あちこち', 117483894: 'no bs', 398747760: '≠)≠', 902207238: '-.,.,.-', 179684293: 'Stormy', 221532774: 'all good', 333351042: '-', 146383297: 'mm warrior', 195516068: 'DRT', 1052101649: 'Suiiiiiiiiiiiiii', 325697153: '9m', 147130490: 'player1', 113926403: 'OuiSaki (LFT)', 123561201: 'Solo que enjoyer (Fun)', 242072548: '当当GOD', 417235485: 'LAY DOWN MY LIFE', 165040324: 'Marceline'}
game_changer_list = [
    'Leshrac'
    'Faceless Void',
    'Enigma',
    'Elder Titan',
    'Phoenix',
    'Disruptor',
    'Bane',
    'Doom',
    'Magnus',
    'Bristleback',
    'Winter Wyvern'
    'Doom',
    'Tidehunter'
    'Tusk',
    'Ancient Apparition'
    'Phantom Lancer',
    'Axe',
    'Storm Spirit']

translate = {
 1: "Anti-Mage",
 2: "Axe",
 3: "Bane",
 4: "Bloodseeker",
 5: "Crystal Maiden",
 6: "Drow Ranger",
 7: "Earthshaker",
 8: "Juggernaut",
 9: "Mirana",
 11: "Shadow Fiend",
 10: "Morphling",
 12: "Phantom Lancer",
 13: "Puck",
 14: "Pudge",
 15: "Razor",
 16: "Sand King",
 17: "Storm Spirit",
 18: "Sven",
 19: "Tiny",
 20: "Vengeful Spirit",
 21: "Windranger",
 22: "Zeus",
 23: "Kunkka",
 25: "Lina",
 31: "Lich",
 26: "Lion",
 27: "Shadow Shaman",
 28: "Slardar",
 29: "Tidehunter",
 30: "Witch Doctor",
 32: "Riki",
 33: "Enigma",
 34: "Tinker",
 35: "Sniper",
 36: "Necrophos",
 37: "Warlock",
 38: "Beastmaster",
 39: "Queen of Pain",
 40: "Venomancer",
 41: "Faceless Void",
 42: "Wraith King",
 43: "Death Prophet",
 44: "Phantom Assassin",
 45: "Pugna",
 46: "Templar Assassin",
 47: "Viper",
 48: "Luna",
 49: "Dragon Knight",
 50: "Dazzle",
 51: "Clockwerk",
 52: "Leshrac",
 53: "Nature's Prophet",
 54: "Lifestealer",
 55: "Dark Seer",
 56: "Clinkz",
 57: "Omniknight",
 58: "Enchantress",
 59: "Huskar",
 60: "Night Stalker",
 61: "Broodmother",
 62: "Bounty Hunter",
 63: "Weaver",
 64: "Jakiro",
 65: "Batrider",
 66: "Chen",
 67: "Spectre",
 69: "Doom",
 68: "Ancient Apparition",
 70: "Ursa",
 71: "Spirit Breaker",
 72: "Gyrocopter",
 73: "Alchemist",
 74: "Invoker",
 75: "Silencer",
 76: "Outworld Destroyer",
 77: "Lycan",
 78: "Brewmaster",
 79: "Shadow Demon",
 80: "Lone Druid",
 81: "Chaos Knight",
 82: "Meepo",
 83: "Treant Protector",
 84: "Ogre Magi",
 85: "Undying",
 86: "Rubick",
 87: "Disruptor",
 88: "Nyx Assassin",
 89: "Naga Siren",
 90: "Keeper of the Light",
 91: "Io",
 92: "Visage",
 93: "Slark",
 94: "Medusa",
 95: "Troll Warlord",
 96: "Centaur Warrunner",
 97: "Magnus",
 98: "Timbersaw",
 99: "Bristleback",
 100: "Tusk",
 101: "Skywrath Mage",
 102: "Abaddon",
 103: "Elder Titan",
 104: "Legion Commander",
 105: "Techies",
 106: "Ember Spirit",
 107: "Earth Spirit",
 108: "Underlord",
 109: "Terrorblade",
 110: "Phoenix",
 111: "Oracle",
 112: "Winter Wyvern",
 113: "Arc Warden",
 114: 'Monkey King',
 119: 'Dark Willow',
 120: "Pangolier",
 121: 'Grimstroke',
 123: "Hoodwink",
 126: 'Void Spirit',
 128: 'Snapfire',
 129: 'Mars',
 135: 'Dawnbreaker',
 136: 'Marci',
 137: "Primal Beast",
 138: "Muerta",
}

blacklist_players = {
    'qsonya',
    'fritterus',
    'febby',
    'jubei',
    'invokergirl',
     'vovapain',
     'lenagol0vach',
     'gusar',
     'vikared',
     'rostislav_999',
    'ephey',
}
teams_to_bet = ['Team Falcons', 'Xtreme gaming', 'WBG.XG', 'Entity Gaming', 'Team Spirit', 'Betboom team', 'PSG Quest', 'Beastcoast', 'Gaimin Gladiators', 'Team Liquid', 'G2.Invictus Gaming', 'Azure Ray', 'G2.IG', 'Tundra Esports', 'Aurora Gaming', 'Og', 'LGD Gaiming', 'Heroic', 'Virtus Pro', 'Shopify Rebelion', 'Team Secret', 'Nouns', 'L1ga team', 'Natus Vincere', 'Navi Junior', 'Mouz', 'Yellow Submarine', 'Team Turtle', 'Night Pulse', '1win', 'Twisted minds', 'One move', 'Nemiga gaming', 'Sibe team', '9pandas', 'Boom', 'Nigma Galaxy', 'Team Zero']
# count = 0
# skip = 0
# while skip != 400:
#     query = '''{
#       leaderboard{
#         season(request:{leaderBoardDivision:EUROPE}){
#           players(take:100, skip:%s){
#             steamAccount{
#               isAnonymous
#                         id
#               name
#           }
#           }}
#       }
#     }''' % skip
#     headers = {"Authorization": f"Bearer {api_token}"}
#     response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
#     data = json.loads(response.text)
#     for player in data['data']['leaderboard']['season']['players']:
#         if not player['steamAccount']['isAnonymous']:
#             if player['steamAccount']['id'] not in egb:
#                 egb[player['steamAccount']['id']] = player['steamAccount']['name']
#     skip += 100
# pass