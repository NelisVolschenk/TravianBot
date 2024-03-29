from pathlib import Path


class Settings:

    firefox_extension_path: str = ''
    browser_speed: float = 2.0
    # loginurl = 'https://ts30.x3.europe.travian.com/'
    # loginurl = 'https://ts7.x1.international.travian.com/'
    # username = 'Fieryfrost'
    # password = 'Po9SV7Rk8kG49kX8'
    # race = 'roman'
    loginurl = 'https://ts2.x1.international.travian.com/'
    username = 'Defman'
    password = 'U9CFtq5rvnnWWFq'
    tribe = 'roman'
    base_dir = Path(__file__).resolve().parents[1]
    geckodriver_dir = str(base_dir.joinpath('Geckodriver', 'Linux', 'geckodriver'))
    firefox_dir = str(base_dir.joinpath('FirefoxPortable', 'App', 'Firefox', 'firefox'))
    # firefox_profile_dir = str(base_dir.joinpath('FirefoxPortable', 'Data', 'profile', 'yt5y3tv3.Travian'))
    firefox_profile_dir = str(base_dir.joinpath('FirefoxPortable', 'Data', 'profile', 'ijrma7ke.Test'))
    log_dir = str(base_dir.joinpath('log.txt'))
    build_minsleeptime: int = 10#49
    build_maxsleeptime: int = 14#73
    refresh_minsleeptime: int = 150#1200
    refresh_maxsleeptime: int = 180#1500
    min_hero_resources = {'Lumber': 1, 'Clay': 1, 'Iron': 1, 'Crop': 1}
    use_quests_for_resources = True


class Gameconstants:

    buildingtypes = {5:['Sawmill','resources'],6:['Brickyard','resources'],7:['Iron Foundry','resources'],8:['Grain Mill','resources'],9:['Bakery','resources'],10:['Warehouse','infrastructure'],11:['Granary','infrastructure'],13:['Smithy','military'],14:['Tournament Square','military'],15:['Main Building','infrastructure'],16:['Rally Point','static'],17:['Marketplace','infrastructure'],18:['Embassy','infrastructure'],19:['Barracks','military'],20:['Stable','military'],21:['Workshop','military'],22:['Academy','military'],23:['Cranny','infrastructure'],24:['Town Hall','infrastructure'],25:['Residence','infrastructure'],26:['Palace','infrastructure'],27:['Treasury','infrastructure'],28:['Trade Office','infrastructure'],29:['Great Barracks','military'],30:['Great Stable','military'],31:['City Wall','military'],32:['Earth Wall','military'],33:['Palisade','military'],34:['Stonemasons Lodge','infrastructure'],35:['Brewery','infrastructure'],36:['Trapper','military'],37:['Heros Mansion','military'],38:['Great Warehouse','infrastructure'],39:['Great Granary','infrastructure'],40:['Wonder of the World','infrastructure'],41:['Horse Drinking Trough','infrastructure'],42:['Stone Wall','military'],43:['Command Center','infrastructure'],44:['Makeshift Wall','military'],45:['Waterworks','resources'],46:['Hospital','military']}
    fieldnames = {'Woodcutter': 1, 'Clay Pit': 2, 'Iron Mine': 3, 'Cropland': 4}
    resources_dict = {'Warehouse': 0, 'Granary': 0, 'Lumber': 0, 'Clay': 0, 'Iron': 0, 'Crop': 0, 'Free Crop': 0}
    hero_resources_dict = {'Lumber': 0, 'Clay': 0, 'Iron': 0, 'Crop': 0}
    layout_list = [{'level': 0, 'gid': 0} for x in range(41)]
    hero_resource_ids = {'Lumber': 145, 'Clay': 146, 'Iron': 147, 'Crop': 148}
    reslist = ['Lumber', 'Clay', 'Iron', 'Crop', 'Free Crop']
    hero_points_dict = {'str': "fightingStrength",'off':"offBonus",'def':"defBonus",'res':"resourceProduction"}