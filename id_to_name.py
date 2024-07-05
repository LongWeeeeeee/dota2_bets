from keys import api_token
import requests, json
import certifi
top_1000_europe_top_1000_asia = {}
egb = {76482434: 'admiralbulldog', 193673646: 'Lyrical', 196482746: 'ainkrad', 93526520: 'bb3px', 116249155: 'nefrit', 363739653: 'alberkaaa', 115651292: 'copy', 196878136: 'Kataomi', 208181197: 'adzantick', 105045291: 'thiolicor', 106305042: 'Larl', 106755427: 'Mo13ei', 203351055: 'malik', 27178898: 'SkyLark', 187824320: 'kitrak', 324277900: 'yopaj', 412413765: 'stonebank', 50580004: 'xibbe', 130991304: 'Riddys', 152168157: 'omar', 54580962: 'insania', 131303632: '4nalog', 94155156: 'fly', 103910993: 'lil pleb', 123787715: 'respect', 383867949: 'SLATEM$', 91730177: 'Seleri', 104334048: 'kidaro', 117015167: 'pablo', 191066225: '4IVAN', 177411785: 'daxak', 164685175: 'K1', 193564777: 'otaker', 165110440: 'retsu', 177203952: 'yuma', 18689006: 'pma', 835864135: 'pma', 100594231: 'skem', 163458082: 'ряф^^', 117514269: 'laise', 165564598: 'MieRo`', 919735867: 'daze', 168126336: 'cloud', 113331514: 'miposhka', 111030315: 'zayac', 292921272: 'wisper', 114619230: 'crystallize', 957204049: 'gotthejuice', 100058342: 'skiter', 164962869: 'Shad', 93817671: 'malady', 138880576: 'Davai Lama', 140288368: 'tobi', 346412363: 'ari', 125445069: 'v1olent', 262838756: 'kordan', 194979527: 'shigetsu', 40805086: 'mellojul', 294135421: 'Nicky`Cool', 107803494: 'Ori', 86698277: '33', 241519559: 'dream', 171097887: 'Nande', 418942836: 'rincyq', 161839895: 'antares', 320219866: 'kaori', 879017980: 'darklord', 48823667: 'Bengan', 392169957: 'Sanctity-', 175311897: 'swedenstrong', 96803083: 'Stormstormer', 210053851: 'Lorenof', 16497807: 'tofu', 898754153: 'ame', 312436974: 'CHIRA_JUNIOR', 904131336: 'Munkushi~', 56351509: 'dm', 181267255: 'onejey', 302214028: 'collapse', 106573901: 'noone', 140297552: 'no!ob', 58513047: 'supream^', 183719386: 'atf', 93618577: 'bzm', 152455523: 'v-tune', 127617979: 'crystallis', 116934015: 'dyrachyo', 109757023: 'ulnit', 118134220: 'fath_bian', 98885811: 'lowskill', 126238768: 'gunnar', 217472313: 'xakoda', 25907144: 'cr1t', 108958769: 'phantomem', 221666230: 'quinn', 178692606: 'antoha', 175463659: 'cooman', 114585639: 'lil_nickdota', 86725175: 'resolut1on', 117421467: 'sonneiko', 369342470: 'sonneiko', 86811043: 'monkeys-forever', 245373129: 'xcalibur', 56939869: 'gorgc', 150748346: 'krylat', 115464954: 'desire', 165671428: 'sclkoma', 35504297: 'leBron', 401792574: 'taiga', 89117038: 'yapzor', 167976729: 'yuragi', 94049589: 'fng', 92847434: 'ghostik', 132851371: 'ramzes', 154715080: 'abed', 195108598: 'noticed', 393024955: 'stariy_bog', 1060164724: 'speedmanq', 113995822: 'iltw', 171262902: 'watson', 164199202: '9class', 315657960: 'mason', 73401082: 'dukalis', 170834508: 'player1', 92706637: 'iannihilate', 9403474: 'yamich', 126212866: 'saberlight', 375507918: '23savage', 355168766: 'natsumi', 10366616: 'sneyking', 86738694: 'qojqva', 88271237: 'ceb', 172099728: 'kiritych', 190100004: 'shiishak', 124801257: 'nightfall', 1675023758: 'limitlessqt', 361688848: 'dnm', 999961232: 'baxadoto', 132309493: 'raven', 404150207: 'y0nd', 317880638: 'save', 431770905: 'torontotokyo', 145550466: 'dubu', 123023873: 'squad1x', 368917218: 'layme', 208407289: 'reira', 480412663: 'gpk', 26316691: 'illidan', 241884166: 'hellscream', 103735745: 'saksa', 439345730: 're1bl', 105178768: 'bsj', 133558180: 'zitraks', 84429681: 'moo', 898455820: 'malr1ne', 372801387: 'shergarat', 97658618: 'timado', 96169991: 'ar1se', 165390194: 'dinozavrik', 173480718: 'sketcher_8', 321580662: 'yatoro', 86700461: 'w33haa', 1044002267: 'satanic', 70388657: 'dendi', 858106446: 'kiyotaka', 250114507: 'iceberg', 293731272: '7jesu', 1171243748: 'parker', 141690233: 'cancel', 295697470: 'immersion', 331855530: 'pure', 159020918: 'rodjer', 148612029: 'poshliy_vladik', 100471531: 'jabz', 87063175: 'lelis', 117311875: 'lukiluki', 94054712: 'topson', 1159912962: 'azimovdota', 95145869: '420jenkins', 155162307: 'smilling knight', 77490514: 'boxi', 256156323: 'mira', 858200619: 'afganistan_doto', 84772440: 'iceiceice', 102099826: 'dj', 1150772339: 'Timadofun', 335437141: 'yamichc', 195415954: 'inhuman', 121870008: 'roflmao', 218231587: 'not me', 92487440: 'Fraser', 130123201: 'mitrofanushka', 320017600: 'daylight', 309345956: 'volshebnik', 47977302: 'dr.bum', 72393079: 'mannik', 185059559: 'hduo', 86785083: 'afterlife', 889201734: 'malady(smurf)', 145065875: 'sayuw', 139822354: 'setsu', 101695162: 'fy', 262476000: 'stojkov', 220154695: 'mks', 150961567: 'planet', 126842529: 'Ws', 196493853: 'Aq', 205226309: '1D3E', 173978074: 'NothingToSay', 202217968: 'Emo', 301750126: 'Mikoto', 145957968: 'b a b', 392565237: 'JaCkky', 206642367: 'Ghost', 137129583: 'Xm', 185908355: 'lou', 126064542: 'Pangpang', 147767183: 'Zeal', 170896543: 'YSR-04E', 145358275: '五年两年多少年', 140411011: 'TraVins', 152859296: 'jhocam', 282359850: 'BEEBIE', 134711350: 'dstones', 168028715: 'flyfly', 196931374: '458', 458287006: 'x123', 315272623: 'blood', 139937922: 'yang', 219755398: 'jing', 191597529: 'undyne_', 156029808: 'bdz', 148880949: 'player3', 171874354: 'player4', 372105535: 'htz', 116837520: 'gan', 287966898: 'player5', 206379758: 'cdr', 137092505: 'Allen', 156195808: '', 293904640: 'wayne', 371876003: '', 152545459: 'gabbi', 138543123: 'pyw', 199953095: '哦？', 129958758: '狠', 80929738: '千雪ちゆき', 150960169: '大葡萄dy95087', 320252024: 'iroha', 162126721: 'Flyicu', 286279456: '绝世高手', 470392491: '无相', 373667079: 'Arc Drive', 489696354: '雨季不再来', 396462897: '构式', 398896331: 'Myut', 122586792: '灰原 哀', 219950601: 'LeMao', 353498499: 'Griffith', 193815691: 'Q', 349495318: 'Krish`-', 94281932: ':)', 277835316: '))))))))))))))))))', 153727297: '匿名的', 135656964: '。', 100598959: '4', 394071544: 'BLESSED CHINA LOW RANK', 118305301: 'Guts', 158847773: 'ni', 128398556: '哥白尼', 193884241: 'Kaiju No.16', 164948665: 'Manic', 201826550: 'Yellow', 181145703: 'Steins Gate', 1114778241: 'pos 1 ty', 139268745: '君とONE LOVE永遠に2 hearts', 252551173: 'Ignite me', 100616105: 'cml', 141398569: '心碎小子', 158401119: 'LYcHee', 155447692: 'bwiset', 99983413: '86 pancakes ^-^', 108717482: 'Obsession', 241107899: '☁️1/22yearsold', 113435203: 'ChYuaN', 139031324: 'Xiang', 285319482: '.-.', 1066782497: '134882858(Bnlvdn)', 134357466: 'Twitch.tv/micedoto', 199222238: '谢谢', 207945924: 'mid', 195072449: 'NOOB', 286985748: 'Jigi Prime', 167488455: '-', 135673679: 'Like a child waiting for X`mas', 311360822: 'winkwell', 100406744: '45', 257694165: '影', 285770518: 'KNP♥', 101460882: 'RAYUM', 173378701: 'king bob', 199833749: '< blank >', 446737104: '.', 142991995: 'core player', 134665319: 'Bagnaia^', 130416036: '正', 184138153: 'Murasaki-', 174081158: '混', 252716815: '蛊心', 363029497: '偷感大王', 76904792: 'ahchin', 228517469: 'Sky Striker Mobilize - Engage!', 130040732: 'WAITING FOR HUMAN TEAM (EN/CN)', 1029352973: '隔壁老王', 135607261: '#NotLikeThis MODE: Oli~ Comeback', 162274034: 'dream on', 836325393: 'Stuck in reverse LFT', 336937491: 'dx', 126397214: 'enjoy', 363724571: ':)', 356343152: 'ZZZ', 149259389: '0.0', 902424411: 'Cliché', 399862798: 'Peter Griefing', 430337036: '-.-', 318286721: '龙', 215121858: 'Bot (2)', 89423756: '1974', 147267417: 'nice', 484759837: '烛影斧声', 1129118044: 'B-RABBIT', 106863163: '问剑', 230487729: 'Reverie for Another Sphere', 140251702: '-O-O-', 185590374: 'Dendi 2009', 405351356: 'Rerise', 847565596: 'rue', 343084576: 'NARMAN', 972243573: 'Matson', 333700720: 'blackpink', 146711951: 'Force', 152285172: 'arcane fantasy', 1202267677: 'aik~', 101356886: 'Miracle---', 122817493: 'patient zero', 184620877: '2ls', 1062148399: 'диф', 93845249: 'Wuiter', 450454900: 'Kiseki', 256444993: "these percs' they heaven sent", 326327879: 'xsvamp1re', 392006194: 'what if i fall?', 1286226756: "teydo;tlikewinnin'", 113112046: 'nn_', 917319178: 'Stewie2K', 84385735: 'Kyzko', 345509021: 'tv/lukas_doto', 223382342: 'b0t', 351836036: 'Pensils', 234119750: '=/', 191362875: 'Speeed', 995397364: 'CLOWNFIESTA', 383788462: 'мистер мораль', 84853828: 'Aquariano nato', 135403353: 'MC HAMMSTER', 107023378: 'so bad', 1677766292: 'rostislav999', 349569834: 'lantana', 851178649: 'LESHA-KILLER_52', 92601861: 'I will be the best', 872008996: 'onlywinmatter', 860414909: 'Actor', 190826739: '90210', 168291251: "what's ok", 136829091: 'NongMon', 199666759: 'К о т', 1048617659: 'крeкep', 296702734: 'so close but so far', 917164766: '神', 1001714951: 'ботик', 1673586483: 'Sae', 127530803: 'y:<', 860264647: 'p~love.心の平和', 123213918: 'lucker', 175350492: '536', 147408273: 'Ruling Days', 1224667851: 'losing every lane', 364698744: 'Мамонтенок', 402583877: 'Лузаю с кайфом))', 126127817: 'Gamer', 170809075: 'marmelad bear', 164090265: 'Megoway-', 232281409: 'LLF', 1031547092: 'Mistake', 123717676: 'dininizi sikiyim', 457637739: 'Limbo🔴', 1172719712: 'Midnight', 133682196: 'Blaze', 151669649: 'NLineは', 285282252: 'JANTER', 127565532: 'Fishman', 891521610: 'Mr. Luck', 383361785: "raison d'etre", 891566317: 'johnnupro', 257921351: 'swaga', 215308703: '@SaintsMike', 158072796: 'maybe win maybe no', 352545711: 'Seishiro Nagi', 312051473: '3 pos dif', 1675517497: 'Ankou ♡', 185202677: 'goomoonryong', 401902808: 'Makunouchi', 1004229172: 'Brutal-', 899495504: 'fiend', 90423751: 'Double jump', 847783992: 'any?', 175891708: '-/', 108928414: 'CHAD', 112426916: 'MTD)', 179266369: ',', 911977148: '< blank >', 114162163: 'tg3', 857788254: 'Abo Prime', 1150028510: '>^)#--', 388905349: '.', 405499625: 'hardmode gameplay enj', 250199344: 'Mny', 1010173059: 'Nagato', 1016676974: 'catching up', 196490133: 'Focus', 192981126: 'hAze._.', 196481318: 'Hitogami 裏切りの神', 124286163: 'Котакбас', 118370366: 'single down', 135513713: 'あちこち', 117483894: 'no bs', 398747760: '≠)≠', 902207238: '-.,.,.-', 179684293: 'Stormy', 221532774: 'all good', 333351042: '-', 146383297: 'mm warrior', 195516068: 'DRT', 1052101649: 'Suiiiiiiiiiiiiii', 325697153: '9m', 147130490: 'player1', 113926403: 'OuiSaki (LFT)', 123561201: 'Solo que enjoyer (Fun)', 242072548: '当当GOD', 417235485: 'LAY DOWN MY LIFE', 165040324: 'Marceline'}
top_600_asia_europe = {355168766: 'Aug A3 )', 126842529: 'Shenorita', 196493853: 'wither', 375507918: 'Dior Dior', 72312627: 'kimchi', 202217968: 'Bilguun', 851183451: '58', 173978074: 'NothingToSay', 100594231: 'debil_2OOO^_-', 217540519: 'halimaw mag dota', 205226309: '1D3E-', 145957968: 'win lane', 104512126: 'Jaehaera', 137193239: 'kikyo', 210053851: '精神', 137129583: '^', 392565237: '?', 185908355: '问心', 220154695: '陪玩+tianxinpwd', 100670407: 'v', 155494381: 'MIKE', 206642367: 'Enchanted', 126064542: 'Pangpang', 242835570: 'Yoki', 301750126: 'Katana', 262838756: '섬찟', 170896543: 'YSR-04E', 150862738: '<>', 147767183: 'milet', 140411011: 'Bu Gatti', 88119245: 'Clutch Factor ~ Musky', 330534326: 'Mireska', 101695162: '其疾如风', 199953095: '哦？', 458287006: '=)', 145358275: '五年两年多少年', 898754153: '^^', 152859296: 'YOUtopia', 164532005: 'ljcute', 150960169: '大葡萄dy95087', 168028715: '999', 156029808: 'barlo', 129958758: '狠', 162126721: 'Flyicu', 80929738: '千雪ちゆき', 154715080: '>.<', 328554617: 'Fin', 389022189: 'jihyo', 134711350: '开摆', 282359850: 'The nightmare is over!', 360648679: 'lowskill', 107803494: '...', 196931374: '?', 139937922: '..', 148215639: '李火旺', 184950344: 'PEACEMAKER', 191597529: '逝', 320252024: 'iroha', 248388120: 'Duruk MMR (Inner Peace)', 116837520: 'IDC', 163497368: 'ladybug', 315272623: 'Hououin Kyoma', 169327015: 'Billie Jeans', 196400041: 'xiao xiao ba', 219755398: 'recovery', 148880949: 'pos1', 171874354: 'yatoro涛', 110460425: '番茄队长', 287966898: 'Moncleur', 119898344: 'PHI.AÑEDEZ', 286279456: '绝世高手', 324277900: 'Rasmus?', 401653350: 'PROCRASTINATION', 162539779: 'Awaken', 353498499: 'Griffith', 1125296112: '我', 372105535: 'B M K', 1123117748: 'lunatic lit it', 137092505: 'Allen', 122586792: '灰原 哀', 140613225: '+', 118134220: 'Bach', 94296097: 'lilas', 293904640: 'papage', 1201927095: 'หัวเรือ', 470392491: '无相', 373667079: 'Arc Drive', 87693259: 'Thomas Shelbai', 138543123: 'Neil', 371876003: 'China = banana eater', 219950601: 'LeMao', 133505373: '丫γF歪γf 点 康姆', 349495318: 'Zzzz', 158847773: 'ni', 396462897: '构式', 341678201: 'sen', 201826550: 'Yellow', 150961567: '镜', 203557151: '四百后面大十七万', 152545459: 'kick.com/gabbidoto', 138857296: 'rosesarerosie', 94281932: ':)', 100471531: 'J', 255219872: '猪打滚儿', 277835316: '))))))))))))))))))', 394071544: 'gg,wp', 193815691: 'Q', 489696354: 'mimic tears', 135656964: '。', 167488455: '-', 153727297: 'Welcome to dota 10', 193884241: 'O', 241107899: '☁️lft1', 407558440: 'hurt', 108717482: 'Obsession', 128398556: '哥白尼', 212560917: '321cursedzxc', 398896331: 'Myut', 163907952: 'PPPPPPPPPPPP', 207829314: '李长歌', 141398569: '打1或2谢谢', 139031324: 'Xiang', 164948665: 'Manic', 1114778241: 'pos 1 ty', 100598959: '4', 161016689: '1', 135673679: 'Like a child waiting for X`mas', 100616105: 'cml', 188821350: 'gbd', 893182924: '...', 181145703: 'Steins Gate', 1066782497: '134882858(Bnlvdn)', 136737280: 'J Clown', 252551173: 'Ignite me', 322925642: 'H20', 237201026: 'Solas sa dorchadas', 122255316: 'whatishappines?', 446737104: '.', 132309493: 'win lane', 155447692: 'bwiset', 156195808: '老蔡分和我差不多了家', 113435203: 'ChYuaN', 199222238: '谢谢', 101460882: 'RAYUM', 114645455: 'Лошадь', 366166639: 'SayonaraEri', 99983413: '86 pancakes ^-^', 106476169: '×', 345803031: 'unLucK-PH', 207945924: 'POS3', 195072449: 'NOOB', 285319482: '.-.', 311360822: 'winkwell', 861414087: 'lewis', 286985748: 'new player', 356343152: 'ZZZ', 257694165: '影', 173378701: 'king bob', 199833749: '< blank >', 142991995: 'core player', 348722410: 'Madara', 134357466: 'Twitch.tv/micedoto', 188551857: '< blank >', 184138153: 'Murasaki-', 180011187: 'THEFASTLIFE', 135607261: '#NotLikeThis MODE: Oli~ Comeback', 145550466: 'DuBu', 76904792: 'ahchin', 162274034: 'recalib suxx', 149486894: '烈烈风中丶', 252716815: '蛊心', 430337036: '-.-', 228517469: 'Sky Striker Mobilize - Engage!', 100406744: '45', 285770518: 'KNP♥', 336937491: 'dx', 176616331: 'Kendrick Lamar', 363724571: 'Loser', 102099826: 'dj', 356124184: 'goingstraightaheadwiththescar', 130040732: 'Goal Disallowed by VAR - Offside', 969542873: 'cy`', 149259389: '0.0', 902424411: 'Cliché', 105920571: 'wtd', 103045129: 'OldMoney', 111114687: 'May thy knife chip and shatter', 215121858: 'Bot (2)', 411804252: 'xc', 318286721: '龙', 837609249: 'C28', 130416036: '正', 836325393: 'PHI.ALPUERTO', 118559150: 'xd', 158401119: 'LYcHee', 106863163: '问剑', 301339401: 'Amani_', 145331311: 'sdasdsd', 876794068: 'level 1 creep', 399862798: 'Peter Griefing', 141544241: 'elation', 124801257: 'pma+tryhard', 1267986232: 'Sherlock', 183719386: 'Suma1L-', 480412663: 'yuuuuuuuuuuuuuuuuuuuuuuuuuuuu', 872625732: '^ ^', 114040350: 'CHIPI CHIPI CHAPA CHAPA', 172099728: 'xigua', 171262902: 'freedom', 302214028: 'Frames Janco', 1116768636: 'Yasuharu Takanashi fan', 93618577: 'garbago', 181267255: 'LLM', 361192969: 'amor fati', 292921272: 'Madshka', 898455820: 'Буська', 221666230: 'Insulation', 195415954: 'noise', 165564598: 'positivity on top of the world', 162610516: 'Aidil-', 140288368: 'Dark', 1044002267: 'Moon', 838436660: 'this mms )', 85696663: 'Calm', 123023873: '살얼음신경단독', 16497807: 'tOfu', 1724073565: 'ポロノイ 1', 164199202: 'Tom Riddle', 241519559: 'wanna be better', 431770905: '想像力상상력想像力—', 339195074: '世间多不公 以血引雷霆!', 957204049: 'Another level', 412076227: 'cutesy', 73401082: 'Dukalis', 1150772339: 'THE PAIN', 317880638: 'sipping juice in a better wrld', 121870008: 'roflmao', 103735745: 'washed up(and toxic)', 230487729: 'Reverie for Another Sphere', 294135421: 'don`t even try to pick me', 140251702: '-O-O-', 72393079: 'Professional', 331855530: 'Fukk Sleep', 374875067: 'Gift of Perseverance', 106573901: 'N1-', 312436974: 'CHIRA_JUNIOR', 56351509: 'mode: Ace', 904131336: '检察官', 86745912: 'MULTICAST', 1630337523: '귀신', 145372258: 'СУПЕРМЕН', 105248644: '((Gh))', 226135101: 'idcidcidc', 320219866: ':(', 47977302: 'tv/doctorbum', 293731272: 'Kracava', 309345956: 'One Chance', 405351356: 'Rerise', 852137897: 'bor3d', 321580662: 'arima kishou', 100058342: 'skiter', 114619230: 'Crystallize', 177203952: 'Yuma', 10366616: 'Sneyking', 157989498: '671', 152455523: 'maden from broken part of star', 98885811: 'Girei', 185590374: 'Dendi 2009', 93817671: 'meta_abuser', 117421467: 'Nikul(not lukin)', 126212866: 'sabeRight', 156328257: '333', 164962869: 'melt', 40805086: 'legacy', 333700720: 'Somnus丶', 140297552: 'No!ob™', 847565596: 'rue', 195108598: 'мусор', 196878136: 'captivity', 326378153: 'wraith pact', 1165281456: '彡✿Ｍｕｋｅ✿彡', 92487440: '$$$ϬΘГȺӴ$$$', 86700461: '33(w)', 86698277: 'not human (животное)', 185059559: '-', 343084576: 'NARMAN', 191066225: '4IVAN', 392169957: 'ㄷㄷ', 346412363: 'worst pub demon', 175311897: 'SuperZombie2', 919735867: 'razraz', 972243573: 'MaTson', 153609394: '\U000e0021', 96803083: 'Stormstormer', 1171243748: 'Jason Statham', 116249155: 'nefrit', 101356886: 'Miracle---', 155162307: 'knight', 138880576: 'Fake gg expert', 241884166: 'Hellscream', 113331514: 'lmao', 204217293: '111', 115464954: 'dEsire', 128959139: 'JosMeOri', 116934015: 'Psycho mode', 1202267677: 'aik~', 167976729: 'scarlet;,.`', 152285172: 'arcane fantasy', 146711951: 'Force', 262476000: 'stojkov', 97658618: 'freak', 218231587: 'vibe', 96183976: 'kq', 910028605: 'dfaijklnosz', 479933304: 'ンＮＯＲＩＣＫ', 117514269: 'destroyed', 120416283: 'ocean eyes', 872008996: 'onlywinmatter', 196482746: 'munkushi~', 122107762: "Darling won't you break my hearT", 130123201: 'wannabee', 58513047: 'spm', 418942836: 'ride or die', 369342470: 'Rainy...', 108958769: 'sustain', 450454900: 'Kiseki', 127617979: 'Crystallis', 1675023758: 'Обнулил время', 295697470: 'evolution error', 168126336: '.', 1003786231: '<3', 184620877: '2ls', 999066307: 'asd', 308504257: 'byebye', 217472313: 'Xakoda', 113112046: 'nn_', 54580962: 'Kaladin Stormblessed', 145065875: '(=', 88271237: 'radiobouffon', 177411785: 'f5', 1062148399: 'диф', 439345730: 'npc', 390015464: 'lovecats_anddogs', 999961232: 'SayitAGAIN', 190826739: 'uuugly', 317814449: 't', 160119017: 'помойка', 93845249: 'Wuiter', 1153798101: 'Ethereal', 193564777: 'Otaker', 87063175: 'bot', 203351055: 'Royalty', 196142865: '7s', 1286226756: "teydo;tlikewinnin'", 138177198: '規律', 191362875: 'Speeed', 879017980: 'practice session', 364698744: 'Lord Farquaad', 161839895: 'babe', 99552197: 'Tundra Nine Fan', 351836036: 'Pensils', 363739653: 'bossed up', 165110440: '1', 332342615: 'bark bark', 1092267175: 'strong', 203903442: 'rqweytreeqwqqq', 392006194: 'what if i fall?', 25907144: 'kom kom', 228516683: 'Dao', 163061132: 'Stoic', 86738694: 'DDX', 893135754: 'vibes', 93526520: 'Liquid`ixmike88', 345509021: 'tv/lukas_doto', 135403353: 'MC HAMMSTER', 107855479: 'tell me a tale', 84385735: 'Kyzko', 417604379: 'lft3)', 48823667: '.', 152962063: 'naaaa', 1079923091: 'tv/maloydotos (md)', 98482878: 'Jacque Fresco', 1040820193: '闇と怒り', 917319178: 'ути пути', 193879048: '1533', 118948666: 'WOKEUPLIKETHIS', 383788462: 'мистер мораль', 256444993: "these percs' they heaven sent", 195001460: '--', 925407683: 'гламур', 175350492: '536', 220394209: 'Accel Matta 98', 150748346: 'stupid', 111620041: '...', 860414909: 'proletariy', 94007628: 'trump fan', 917164766: '五条', 94054712: 'Topson', 1710474385: '[[ ]]', 1677766292: 'rostislav999', 1048617659: 'крeкep', 147408273: 'last dance', 168291251: "what's ok", 194979527: 'classic 200 rank carry', 127565532: 'Fishman', 183324260: 'ChioRlz♥ ҉҈҉҈҈҉', 92601861: 'I will be the best', 122817493: 'patient zero', 181532808: 'fozzy^^', 84853828: 'Aquariano nato', 234119750: '=/', 164685175: 'k1', 109757023: "Cie'th", 241501414: 'great disillusionment', 165390194: 'Обыкновенный бобр', 1694254651: 'thots', 114023044: 'sadvetements', 125915245: 'x', 175891708: '-/', 1631918157: 'こんにちは、友達', 111030315: 'ATA', 201695405: 'xdd', 437643262: 'χaηaχ\u2067\u2067❤', 860264647: 'p~love.心の平和', 159020918: 'Icaros', 163458082: 'ряф^^', 457637739: 'Limbo🔴', 326327879: 'xsvamp1re', 113995822: 'dota expert', 115651292: 'Broken Angel Hospital', 27178898: 'БЕЗУМ', 136829091: 'NongMon', 1157907397: 'h8h8l', 220621418: 'Simon', 161595677: 'certified player', 140835095: 'its not a girl its trouble', 851178649: 'ab', 285282252: 'JANTER', 1031547092: 'Mistake', 312082610: 'dota 2 enjoyer =)', 1001714951: 'ботик', 256156323: 'adjust the sails', 223382342: 'b0t', 123787715: '☢ПøзϋŦΰ฿чÛķ®☢', 154974246: '))', 368917218: 'sonio', 127530803: 'y:<', 349569834: 'lantana', 170834508: 'принцесса сибилла 🐘', 105045291: 'Rita', 123213918: 'lucker', 170809075: '!', 117960359: 'mad scientist', 835864135: 'xd', 243565888: 'letters numbers', 858106446: 'classic 100 rank mid', 995397364: 'Be safe, play safe', 216034047: '))', 399949991: 'paid actor', 296702734: 'so close but so far', 1224667851: 'Безнадёжный игрок', 1673586483: 'Bullshit', 107023378: 'so bad', 1172719712: 'Midnight', 847851833: 'mode alohadance', 857788254: 'Abo Prime', 123717676: 'dininizi sikiyim', 282535874: 'kUBAJIDA', 187824320: 'braindead', 199666759: 'К о т', 250114507: 'new me', 77490514: 'boxi', 130991304: 'delusional thomas', 190100004: 'Шишак', 132851371: 'PREMIUM DOLBAEB', 94155156: 'aint no way', 148612029: 'VladikTheHtiviy', 178692606: 'ijust need to push myself harder', 158072796: 'maybe win maybe no', 126238768: 'New leaf', 184427590: 'B e s a t t ツ', 134556694: 'pos5 boosting service', 91730177: 'Scuffed Chair', 50580004: 'OK', 232281409: 'bet', 175463659: 'Cooman', 412413765: 'Worst mm ever', 424661031: 'Shtark-', 79648574: 'potemkin', 312051473: '3 pos dif', 238239590: 'taichou uebishe', 1305619263: 'shesad', 131303632: '4nalog', 891521610: 'Mr. Luck', 104334048: 'kidaro', 35504297: '@LeBorn', 163173919: '200g f w ?', 129204173: 'fukumean', 383361785: "raison d'etre", 387624608: 'NiMoooSh', 91663166: 'iLOVEOKAYGGWP', 913612002: '.tw.tv/ark_dota', 108928414: 'CHAD', 402583877: 'Лузаю с кайфом))', 151669649: 'NLineは', 351234297: 'ketamine', 173539244: 'haku', 389276156: 'Difference', 106755427: 'elodin', 257921351: 'swaga', 352545711: 'Seishiro Nagi', 1674270943: '冰淇淋', 858200619: 'AFGANISTAN', 316971553: 'zxc слоник', 164090265: 'Megoway-', 1730958870: 'Rnd', 137396710: 'average', 320017600: 'bad idea', 94049589: 'NF', 1144214248: 'tv/waneda21', 171097887: 'ГЕРАКАКЛ', 322186211: 'one way or another', 176446673: 'Björnes Magasin', 911977148: '< blank >', 319292743: 'selfharm', 899495504: 'fiend', 250199344: 'Mny', 847783992: 'any?', 90423751: 'Double jump', 402429299: 'Bitch', 185202677: 'goomoonryong', 120840516: 'звёзд特維爾 VaniLLl', 116865891: 'm1rele', 114585639: 'JUST LIFE ON THE CUT', 124286163: 'Котакбас', 874542740: 'Yellow Flash', 196715811: 'blessings', 179266369: ',', 1675517497: 'Ankou ♡', 169307887: 'kill your weakness', 1150028510: '>^)#--', 1016676974: 'catching up', 169808301: 'мистер совесть', 133682196: 'Blaze', 197547532: 'Astral', 1081078145: '.', 221532774: 'all good', 393024955: 'Копатыща', 425588742: 'weh', 935495351: 'I believe in miracles', 162812365: 'Seikai nai sekai', 81475303: 'fun fun fun having fun', 836056780: 'Shooty!', 1139937786: 'ao', 152168157: 'so sad wrab el 3ebad', 968545762: 'y', 42194754: 'xd', 397063804: 'tony who', 289887816: 'tv/Octarinn', 1026694469: '..', 117015167: 'GREAT patch', 1159912962: 'p.u.s.s.-e', 196490133: 'Grinding in the shadows~', 401902808: 'Makunouchi', 135513713: 'あちこち', 126127817: 'Gamer', 1004229172: 'Brutal-', 185181822: 'Yuuichi', 115331673: 'hi', 118370366: 'single down', 950127743: 'うずまきナルト', 196481318: 'Hitogami 裏切りの神', 206097366: '🆕', 21270361: 'NO CARE', 844400266: 'bark russian = mute', 118305301: 'Guts', 9403474: 'Сhief', 117483894: 'no bs', 201839427: 'Грубый стиль', 165671428: '社会科马', 229311481: '♓', 1641327670: 'Vendetta', 133558180: 'rtc', 277255518: 'IMPROVE', 344861218: 'pencilboxer', 192981126: 'hAze._.', 334481624: 'Alternate', 97590558: 'K1ng GizZard', 56939869: 'O', 1115553566: '污垢', 325697153: '9m', 113926403: 'OuiSaki (LFT)', 372801387: 'tv/ShergaratVladimir', 123561201: 'Solo que enjoyer (Fun)', 906439403: 'Deez', 242072548: '当当GOD', 195516068: 'DRT', 333351042: '-', 122049498: 'be water my friend', 323562138: 'world behind us'}
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
pro_teams = ['team falcons', 'entity', 'cuyes e-sports', 'noping esports', 'level up', 'dms', 'v1dar gaming', 'thunder awaken', 'infamous gaming', 'outcast', 'salvation gaming', 'winter bear', 'manta esports', 'virtus.pro', 'fantasy gaming', 'monte ', 'kalmychata', 'g2 x ig', 'justbetter', 'estar backs!', 'midas club', 'talon esports', 'xtreme gaming', 'wbg.xg', 'entity gaming', 'team spirit', 'betboom team', 'psg quest', 'beastcoast', 'dark horse', 'gaimin gladiators', 'team liquid', 'g2.invictus gaming', 'azure ray', 'g2.ig', 'tundra esports', 'aurora gaming', 'hydra', 'matreshka', 'og', 'lgd gaming', 'team  kev', 'talon', 'lgd gaiming', 'heroic', 'virtus pro', 'shopify rebelion', 'shopify rebellion', 'execration', 'hardbass team', 'south team', 'acatsuki', 'infamous', 'qhali', 'havu', 'blacklist rivalry ', 'tnc predator', 'team tough', 'team kev', 'bleed', 'apex genesis', 'cuyes e-sport', 'monte', 'leviatan', 'neon esports', 'team secret', 'nouns', 'l1ga team', 'natus vincere', 'navi junior', 'mouz', 'yellow submarine', 'team turtle', 'dandelions', 'psg.quest', 'grin esports', 'levelup.marsbahis', 'prism esports', 'dragon esports club', 'team hryvnia', 'team bald reborn', 'blacklist rivalry', 'lava esports', 'yangon galacticos', 'nextup', 'asakura', 'aurora.1xbet', 'team tea', 'ihc', 'b8', 'ihc esports', 'spiky gaming', 'bleed esports', 'night pulse', '1win', 'twisted minds', 'team bright', 'lava esports ', 'one move', 'hokori', 'infinity', 'justbetter', 'nemiga gaming', 'sibe team', '9pandas', 'boom esports', 'nigma galaxy', 'team zero']
pass
# count = 0
# skip = 0
# while skip != 1000:
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
#         if player['steamAccount']['id'] not in top_1000_europe_top_1000_asia:
#             top_1000_europe_top_1000_asia[player['steamAccount']['id']] = player['steamAccount']['name']
#     skip += 100
# pass