import random
from pathlib import Path
import datetime

class Settings:

    firefox_extension_path: str = ''
    browser_speed: float = 1.0
    # loginurl = 'https://ts30.x3.europe.travian.com/'
    # loginurl = 'https://ts7.x1.international.travian.com/'
    # username = 'Fieryfrost'
    # password = 'Po9SV7Rk8kG49kX8'
    # race = 'roman'
    loginurl = 'https://ts2.x1.europe.travian.com/'
    username = 'Defman'
    password = 'U9CFtq5rvnnWWFq'
    tribe = 'roman'
    gamespeed = 1
    base_dir = Path(__file__).resolve().parents[1]
    geckodriver_dir = str(base_dir.joinpath('Geckodriver', 'Linux', 'geckodriver'))
    firefox_dir = str(base_dir.joinpath('FirefoxPortable', 'App', 'Firefox', 'firefox'))
    # firefox_profile_dir = str(base_dir.joinpath('FirefoxPortable', 'Data', 'profile', 'yt5y3tv3.Travian'))
    firefox_profile_dir = str(base_dir.joinpath('FirefoxPortable', 'Data', 'profile', 'ijrma7ke.Test'))
    log_dir = str(base_dir.joinpath('log.txt'))
    bot_minsleeptime: int = round(8 / gamespeed)
    bot_maxsleeptime: int = round(10 / gamespeed)
    bot_min_logintime: int = round(3600 / gamespeed)
    bot_max_logintime: int = round(5400 / gamespeed)
    bot_min_logout_ratio: float = 0.10
    bot_max_logout_ratio: float = 0.15
    analyze_all_minsleeptime: int = round(1200 / gamespeed)
    analyze_all_maxsleeptime: int = round(1500 / gamespeed)
    hero_res_retry_time: int = round(300 / gamespeed)
    min_hero_resources = {'Lumber': 1, 'Clay': 1, 'Iron': 1, 'Crop': 1}
    use_quests_for_resources = True


class Gameconstants:

    buildingtypes = {5:['Sawmill','resources'],6:['Brickyard','resources'],7:['Iron Foundry','resources'],8:['Grain Mill','resources'],9:['Bakery','resources'],10:['Warehouse','infrastructure'],11:['Granary','infrastructure'],13:['Smithy','military'],14:['Tournament Square','military'],15:['Main Building','infrastructure'],16:['Rally Point','static'],17:['Marketplace','infrastructure'],18:['Embassy','infrastructure'],19:['Barracks','military'],20:['Stable','military'],21:['Workshop','military'],22:['Academy','military'],23:['Cranny','infrastructure'],24:['Town Hall','infrastructure'],25:['Residence','infrastructure'],26:['Palace','infrastructure'],27:['Treasury','infrastructure'],28:['Trade Office','infrastructure'],29:['Great Barracks','military'],30:['Great Stable','military'],31:['City Wall','military'],32:['Earth Wall','military'],33:['Palisade','military'],34:['Stonemasons Lodge','infrastructure'],35:['Brewery','infrastructure'],36:['Trapper','military'],37:['Heros Mansion','military'],38:['Great Warehouse','infrastructure'],39:['Great Granary','infrastructure'],40:['Wonder of the World','infrastructure'],41:['Horse Drinking Trough','infrastructure'],42:['Stone Wall','military'],43:['Command Center','infrastructure'],44:['Makeshift Wall','military'],45:['Waterworks','resources'],46:['Hospital','military']}
    fieldnames = {'Woodcutter': 1, 'Clay Pit': 2, 'Iron Mine': 3, 'Cropland': 4}
    hero_resources_dict = {'Lumber': 0, 'Clay': 0, 'Iron': 0, 'Crop': 0}
    hero_resource_ids = {'Lumber': 145, 'Clay': 146, 'Iron': 147, 'Crop': 148}
    reslist = ['Lumber', 'Clay', 'Iron', 'Crop', 'Free Crop']
    hero_points_dict = {'str': "fightingStrength",'off':"offBonus",'def':"defBonus",'res':"resourceProduction"}
    account_timers: dict = {
        'analyze_all': datetime.datetime.now(),
        'hero_res': datetime.datetime.now(),
        'logintime': datetime.datetime.now(),
        'logouttime': datetime.datetime.now(),
    }
    villagelist = [
        {'id': None,
         'resources': {'Warehouse': 0, 'Granary': 0, 'Lumber': 0, 'Clay': 0, 'Iron': 0, 'Crop': 0, 'Free Crop': 0, 'update_time':datetime.datetime.now()},
         'res_prod': {'Lumber': 0, 'Clay': 0, 'Iron': 0, 'Crop': 0},
         'layout': [{'level': 0, 'gid': 0} for x in range(41)],
         'buildqueue': [0,0],
         'fieldlist': [],
         'townlist': [],
         'buildable_fieldlist': [],
         'buildable_townlist': [],
         'timers': {'fieldqueue': datetime.datetime.now(),
                    'townqueue': datetime.datetime.now()},
         'hero_res_usable': 1
         }
    ]
