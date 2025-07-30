class consts:
    def __init__(self):
        self.path_chinese = ['巡猎', '毁灭', '智识', '同谐', '虚无', '存护', '丰饶']
        self.path_english = ['TheHunt', 'Destruction', 'Erudition', 'Harmony', 'Nihility', 'Preservation', 'Abundance']
        self.combat_type = ['Physical', 'Wind', 'Ice', 'Fire', 'Lightning', 'Quantum', 'Imaginary']
        self.character_name_chinese = [
            "镜流", "罗刹", "希儿", "符玄", "银狼", "景元", "丹恒·饮月", "彦卿", "瓦尔特",
            "卡芙卡", "开拓者·存护", "布洛妮娅", "杰帕德", "托帕&账账", "开拓者·毁灭", "白露",
            "姬子", "克拉拉", "刃", "三月七", "阿兰", "佩拉", "艾丝妲", "桂乃芬", "青雀",
            "希露瓦", "桑博", "驭空", "卢卡", "素裳", "丹恒", "停云", "虎克", "玲可",
            "娜塔莎", "黑塔", "藿藿", "银枝", "寒鸦", "阮•梅", "雪衣", "真理医生", "黑天鹅",
            "黄泉", "花火", '知更鸟', '米沙', "加拉赫", "开拓者·同谐",
            "流萤", "波提欧", "砂金"
        ]
        self.character_name_english = [
            "JingLiu", "LuoCha", "Seele", "FuXuan", "SilverWolf", "Jingyuan",
            "DanHengImbibitorLunae", "YanQing", "Welt", "Kafka",
            "TrailblazerPreservation", "Bronya", "Gepard", "TopazNumby",
            "TrailblazerDestruction", "BaiLu", "Himeko", "Clara", "Blade",
            "March7th", "Arlan", "Pela", "Asta", "GuiNaiFen", "QingQue",
            "Serval", "Sampo", "YuKong", "Luka", "SuShang", "DanHeng",
            "TingYun", "Hook", "Lynx", "Natasha", "Herta", "HuoHuo",
            "Argenti", "HanYa", "RuanMei", "XueYi", "DrRatio", "BlackSwan",
            "Acheron", "Sparkle", 'Robin', 'Misha', 'Gallagher', 'TrailblazerHarmony',
            "Firefly", "Boothill", "Aventurine"
        ]
        self.relic_set_name = {
            'Genius': ['Ultraremote Sensing Visor', 'Frequency Catcher', 'Metafield Suit', 'Gravity Walker'],
            'Eagle': ['Beaked Helmet', 'Soaring Ring', 'Winged Suit Harness', 'Quilted Puttees'],
            'Salsotto': ['Moving City', 'Terminator Line'],
            'Guard': ['Cast Iron Helmet', 'Shining Gauntlets', 'Uniform of Old', 'Silver Greaves'],
            'Champion': ['headgear', 'Heavy Gloves', 'Chest Guard', 'Fleetfoot Boots'],
            'Band': ['Polarized Sunglasses', 'Touring Bracelet', 'Leather Jacket With Studs',
                     'Ankle Boots With Rivets'],
            'Vonwacq': ['Island of Birth', 'Islandic Coast'],
            'Thief': ['Myriad-Faced Mask', 'Gloves With Prints', 'Steel Grappling Hook', 'Meteor Boots'],
            'Musketeer': ['Wild Wheat Felt Hat', 'Coarse Leather Gloves', 'Wind-Hunting Shawl', 'Rivets Riding Boots'],
            'Passerby': ['Rejuvenated Wooden Hairstick', 'Roaming Dragon Bracer', 'Ragged Embroided Coat',
                         'Stygian Hiking Boots'],
            'Hunter': ['Artaius Hood', 'Lizard Gloves', 'Ice Dragon Cloak', 'Soft Elkskin Boots'],
            'Knight': ['Forgiving Casque', 'Silent Oath Ring', 'Solemn Breastplate', 'Iron Boots of Order'],
            'Talia': ['Nailscrap Town', 'Exposed Electric Wire'],
            'TheXianzhouLuofu': ['Celestial Ark', 'Ambrosial Arbor Vines'],
            'TheIPC': ['Mega HQ', 'Trade Route'],
            'Herta': ['Space Station', 'Wandering Trek'],
            'Wastelander': ['Breathing Mask', 'Desert Terminal', 'Friar Robe', 'Powered Greaves'],
            'PlanetScrewllum': ['Mechanical Sun', 'Ring System'],
            'Firesmith': ['Obsidian Goggles', 'Ring of Flame-Mastery', 'Fireproof Apron', 'Alloy Leg'],
            'Belobog': ['Fortress of Preservation', 'Iron Defense'],
            'Disciple': ['Prosthetic Eye', 'Ingenium Hand', 'Dewy Feather Garb', 'Celestial Silk Sandals'],
            'Taikiyan': ['Laser Stadium', 'Arclight Race Track'],
            'Insumousu': ['Whalefall Ship', 'Frayed Hawser'],
            'Messenger': ['Holovisor', 'Transformative Arm', 'Secret Satchel', 'Par-kool Sneakers'],
            'Rutilant': ['Laser Stadium', 'Arclight Race Track'],
            'Pioneer': ["Heatproof Shell", "Lacuna Compass", "Sealed Lead Apron",
                        "Starfaring Anchor"],
            'Izumo': ["Magatsu no Morokami", "Blades of Origin and End"],
            'Watchmaker': ["Telescoping Lens", "Fortuitous Wristwatch",
                           "Illusory Formal Suit", "Dream-Concealing Dress Shoes"],
            'Prisoner': ["Sealed Muzzle", "Leadstone Shackles", "Repressive Straitjacket",
                         "Restrictive Fetters"],
            'GrandDuke': ["Crown of Netherflame", "Gloves of Fieryfur", "Robe of Grace",
                          "Ceremonial Boots"],
            'Sigonia': ["Gaiathra Berth", "Knot of Cyclicality"],
            'Glamoth': ["Iron Cavalry Regiment", "Silent Tombstone"],
            'Penacony': ["Grand Hotel", "Dream-Seeking Tracks"],
            'IronCavalry': ["Homing Helm", "Crushing Wristguard", "Silvery Armor", "Skywalk Greaves"],
            'Duran': ["Tent of Golden Sky", "Mechabeast Bridle"],
            'Forge': ['Lotus Lantern Wick', 'Heavenly Flamewheel Silk'],
            'Valorous': ['Mask of Northern Skies', 'Bracelet of Grappling Hooks', 'Plate of Soaring Flight',
                         'Greaves of Pursuing Hunt'],
        }
        self.break_damage_constant = [
            54.0000, 58.0000, 62.0000, 67.5264, 70.5094, 73.5228, 76.5660, 79.6385, 82.7395, 85.8684,
            91.4944, 97.0680, 102.5892, 108.0579, 113.4743, 118.8383, 124.1499, 129.4091, 134.6159,
            139.7703, 149.3323, 158.8011, 168.1768, 177.4594, 186.6489, 195.7452, 204.7484, 213.6585,
            222.4754, 231.1992, 246.4276, 261.1810, 275.4733, 289.3179, 302.7275, 315.7144, 328.2905,
            340.4671, 352.2554, 363.6658, 408.1240, 451.7883, 494.6798, 536.8188, 578.2249, 618.9172,
            658.9138, 698.2325, 736.8905, 774.9041, 871.0599, 964.8705, 1056.4206, 1145.7910, 1233.0585,
            1318.2965, 1401.5750, 1482.9608, 1562.5178, 1640.3068, 1752.3215, 1861.9011, 1969.1242,
            2074.0659, 2176.7983, 2277.3904, 2375.9085, 2472.4160, 2566.9739, 2659.6406, 2780.3044,
            2898.6022, 3014.6029, 3128.3729, 3239.9758, 3349.4730, 3456.9236, 3562.3843, 3665.9099,
            3767.5533
        ]
        self.break_effect_multiply = {
            'Physical': (2, '裂伤', (7, 16), 2), 'Wind': (1.5, '风化', 1, 2), 'Ice': (1, '冻结', 1, 1),
            'Fire': (2, '灼烧', 1, 2), 'Lightning': (1, '触电', 2, 2), 'Quantum': (0.5, '纠缠', 0.6, 1),
            'Imaginary': (0.5, '禁锢', 0, 1),
        }

        self.relic_piece_main = {
            'head': ['HP'],
            'hand': ['ATK'],
            'body': ['HP%', 'ATK%', 'DEF%', 'crit_rate', 'crit_damage', 'outgoing_healing_boost', 'effect_hit_rate'],
            'feet': ['HP%', 'ATK%', 'DEF%', 'SPD'],
            'sphere': ['HP%', 'ATK%', 'DEF%', "Physical_DMG_Boost", "Fire_DMG_Boost",
                       "Ice_DMG_Boost", "Wind_DMG_Boost", "Lightning_DMG_Boost", "Quantum_DMG_Boost",
                       "Imaginary_DMG_Boost"],
            'rope': ['HP%', 'ATK%', 'DEF%', 'break_effect', 'energy_regeneration_rate'],
        }

        self.relic_stats_dict = {'A': 'ATK', 'A%': 'ATK%', 'BA': 'base_ATK', 'BD': 'base_DEF',
                                 'BE': 'break_effect', 'BH': 'base_HP', 'CD': 'crit_damage',
                                 'CR': 'crit_rate', 'D': 'DEF', 'D%': 'DEF%', 'H': 'HP', 'H%': 'HP%',
                                 'EHR': 'effect_hit_rate', 'ER': 'effect_RES', 'ERR': 'energy_regeneration_rate',
                                 'FDB': 'Fire_DMG_Boost', 'FRB': 'Fire_RES_Boost',
                                 'IDB': 'Imaginary_DMG_Boost', 'IRB': 'Imaginary_RES_Boost',
                                 'LDB': 'Lightning_DMG_Boost', 'LRB': 'Lightning_RES_Boost',
                                 'ME': 'max_energy', 'MS': 'main_stat', 'OHB': 'outgoing_healing_boost',
                                 'PDB': 'Physical_DMG_Boost', 'PRB': 'Physical_RES_Boost',
                                 'QDB': 'Quantum_DMG_Boost', 'QRB': 'Quantum_RES_Boost',
                                 'S': 'SPD', 'SS': 'sub_stat',
                                 'WDB': 'Wind_DMG_Boost', 'WRB': 'Wind_RES_Boost',
                                 'IcDB': 'Ice_DMG_Boost', 'IcRB': 'Ice_RES_Boost',
                                 }


class Level_Const:
    def __init__(self):
        import numpy as np
        self.label = ['ATK', 'DEF', 'HP', 'SPD']
        self.Enemy_Const = np.array([['0.640000', '1.000000', '0.800000', '1.00'],
                                     ['0.766887', '1.047619', '1.050000', '1.00'],
                                     ['0.814786', '1.095238', '1.100000', '1.00'],
                                     ['1.125528', '1.142857', '1.362518', '1.00'],
                                     ['1.181478', '1.190476', '1.428762', '1.00'],
                                     ['1.238469', '1.238095', '1.496191', '1.00'],
                                     ['1.296802', '1.285714', '1.564808', '1.00'],
                                     ['1.373344', '1.333333', '1.634615', '1.00'],
                                     ['1.416696', '1.380952', '1.705617', '1.00'],
                                     ['1.460110', '1.428571', '1.777814', '1.00'],
                                     ['1.608240', '1.476190', '1.902566', '1.00'],
                                     ['1.756371', '1.523810', '2.027318', '1.00'],
                                     ['1.904501', '1.571429', '2.152070', '1.00'],
                                     ['2.052631', '1.619048', '2.276821', '1.00'],
                                     ['2.200761', '1.666667', '2.401573', '1.00'],
                                     ['2.348891', '1.714286', '2.526325', '1.00'],
                                     ['2.497022', '1.761905', '2.651077', '1.00'],
                                     ['2.645152', '1.809524', '2.775828', '1.00'],
                                     ['2.793282', '1.857143', '2.900580', '1.00'],
                                     ['2.941412', '1.904762', '3.025332', '1.00'],
                                     ['3.191520', '1.952381', '3.247060', '1.00'],
                                     ['3.441627', '2.000000', '3.468788', '1.00'],
                                     ['3.691735', '2.047619', '3.690516', '1.00'],
                                     ['3.941842', '2.095238', '3.912244', '1.00'],
                                     ['4.191950', '2.142857', '4.133972', '1.00'],
                                     ['4.442057', '2.190476', '4.355701', '1.00'],
                                     ['4.692165', '2.238095', '4.577429', '1.00'],
                                     ['4.942272', '2.285714', '4.799157', '1.00'],
                                     ['5.192380', '2.333333', '5.020885', '1.00'],
                                     ['5.442487', '2.380952', '5.242613', '1.00'],
                                     ['5.761692', '2.428571', '5.670810', '1.00'],
                                     ['6.080898', '2.476190', '6.099006', '1.00'],
                                     ['6.400103', '2.523810', '6.527203', '1.00'],
                                     ['6.719308', '2.571429', '6.955400', '1.00'],
                                     ['7.038513', '2.619048', '7.383597', '1.00'],
                                     ['7.357718', '2.666667', '7.811794', '1.00'],
                                     ['7.676923', '2.714286', '8.239990', '1.00'],
                                     ['7.996129', '2.761905', '8.668187', '1.00'],
                                     ['8.315334', '2.809524', '9.096384', '1.00'],
                                     ['8.634539', '2.857143', '9.524581', '1.00'],
                                     ['9.071262', '2.904762', '10.786134', '1.00'],
                                     ['9.507986', '2.952381', '12.047688', '1.00'],
                                     ['9.944709', '3.000000', '13.309242', '1.00'],
                                     ['10.381433', '3.047619', '14.570795', '1.00'],
                                     ['10.818156', '3.095238', '15.832349', '1.00'],
                                     ['11.254880', '3.142857', '17.093903', '1.00'],
                                     ['11.691603', '3.190476', '18.355456', '1.00'],
                                     ['12.128327', '3.238095', '19.617010', '1.00'],
                                     ['12.565050', '3.285714', '20.878564', '1.00'],
                                     ['13.001774', '3.333333', '22.140117', '1.00'],
                                     ['13.581057', '3.380952', '25.198520', '1.00'],
                                     ['14.160340', '3.428571', '28.256923', '1.00'],
                                     ['14.739623', '3.476190', '31.315326', '1.00'],
                                     ['15.318906', '3.523810', '34.373729', '1.00'],
                                     ['15.898189', '3.571429', '37.432132', '1.00'],
                                     ['16.477472', '3.619048', '40.490535', '1.00'],
                                     ['17.056735', '3.666667', '43.548938', '1.00'],
                                     ['17.636038', '3.714286', '46.607341', '1.00'],
                                     ['18.215321', '3.761905', '49.665744', '1.00'],
                                     ['18.794605', '3.809524', '52.724147', '1.00'],
                                     ['19.336283', '3.857143', '56.950449', '1.00'],
                                     ['19.877961', '3.904762', '61.176751', '1.00'],
                                     ['20.419640', '3.952381', '65.403053', '1.00'],
                                     ['20.961318', '4.000000', '69.629355', '1.00'],
                                     ['21.502996', '4.047619', '73.855657', '1.10'],
                                     ['22.044675', '4.095238', '78.081959', '1.10'],
                                     ['22.586353', '4.142857', '82.308261', '1.10'],
                                     ['23.128032', '4.190476', '86.534563', '1.10'],
                                     ['23.669710', '4.238095', '90.760865', '1.10'],
                                     ['24.211388', '4.285714', '94.987167', '1.10'],
                                     ['24.858698', '4.333333', '100.289552', '1.10'],
                                     ['25.506008', '4.380952', '105.591938', '1.10'],
                                     ['26.153318', '4.428571', '110.894324', '1.10'],
                                     ['26.800628', '4.476190', '116.196710', '1.10'],
                                     ['27.447938', '4.523810', '121.499095', '1.10'],
                                     ['28.095248', '4.571429', '126.801481', '1.10'],
                                     ['28.742558', '4.619048', '132.103867', '1.10'],
                                     ['29.389868', '4.666667', '137.406253', '1.20'],
                                     ['30.037178', '4.714286', '142.708639', '1.20'],
                                     ['30.684488', '4.761905', '148.011024', '1.20'],
                                     ['31.298178', '4.809524', '155.487432', '1.20'],
                                     ['31.911868', '4.857143', '163.240467', '1.20'],
                                     ['32.525558', '4.904762', '171.280364', '1.20'],
                                     ['33.139247', '4.952381', '179.617738', '1.20'],
                                     ['33.752937', '5.000000', '188.263594', '1.20'],
                                     ['34.366627', '5.047619', '197.229347', '1.32'],
                                     ['34.980317', '5.095238', '206.526833', '1.32'],
                                     ['35.594006', '5.142857', '216.168326', '1.32'],
                                     ['36.207696', '5.190476', '226.166554', '1.32'],
                                     ['36.821386', '5.238095', '236.534716', '1.32'],
                                     ['37.435076', '5.285714', '247.286501', '1.32'],
                                     ['38.048765', '5.333333', '258.436102', '1.32'],
                                     ['38.662455', '5.380952', '269.998237', '1.32'],
                                     ['39.276145', '5.428571', '281.988172', '1.32'],
                                     ['39.889835', '5.476190', '294.421734', '1.32'],
                                     ['40.503525', '5.523810', '307.315339', '1.32'],
                                     ['41.117214', '5.571429', '320.686006', '1.32'],
                                     ['41.730904', '5.619048', '334.551388', '1.32'],
                                     ['42.344594', '5.666667', '348.929790', '1.32'],
                                     ['42.958284', '5.714286', '363.840192', '1.32']], dtype=float)
        character_and_Light_Cone_const = []
        c, l = 100, 100
        for i in range(80):
            if i in [20, 30, 40, 50, 60, 70]:
                c += 40
            if i == 20:
                l += 120
            elif i in [30, 40, 50, 60, 70]:
                l += 160
            character_and_Light_Cone_const.append([c, l])
            c += 5
            l += 15
        self.ch_lc = character_and_Light_Cone_const

    def get_enemy(self, level, label=None):
        if label is None:
            return self.Enemy_Const[level - 1]
        return self.Enemy_Const[level - 1][self.label.index(label)]

    def get_ch(self, level):
        return self.ch_lc[level - 1][0] / 100

    def get_lc(self, level):
        return self.ch_lc[level - 1][1] / 100

    def __sizeof__(self):
        return self.Enemy_Const

    def __len__(self):
        return len(self.Enemy_Const)
