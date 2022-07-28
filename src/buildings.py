
buildings =[
	{"name":"Woodcutter",  "cost": [  40, 100,  50,  60], "k":1.67, "cu":2,	"cp":1, "time":(1780/3,1.6, 1000/3),"maxlvl":22, "extra":1, "type":1, "desc":"Maximum level is 10, except capital — limited by stockyards there.", "req": {"capital": 10}},
	{"name":"Clay Pit",  "cost": [  80,  40,  80,  50], "k":1.67, "cu":2,	"cp":1, "time":(1660/3,1.6, 1000/3),"maxlvl":22, "extra":1, "type":1, "desc":"Maximum level is 10, except capital — limited by stockyards there.", "req": {"capital": 10}},
	{"name":"Iron Mine",  "cost": [ 100,  80,  30,  60], "k":1.67, "cu":3,	"cp":1, "time":(2350/3,1.6, 1000/3),"maxlvl":22, "extra":1, "type":1, "desc":"Maximum level is 10, except capital — limited by stockyards there.", "req": {"capital": 10}},
	{"name":"Cropland",  "cost": [  70,  90,  70,  20], "k":1.67, "cu":0,	"cp":1, "time":(1450/3,1.6, 1000/3),"maxlvl":22, "extra":1, "type":1, "desc":"Maximum level is 10, except capital — limited by stockyards there.", "req": {"capital": 10}},
	{"name":"Sawmill",  "cost": [ 520, 380, 290,  90], "k":1.80, "cu":4,	"cp":1, "time":( 5400, 1.5,  2400), "maxlvl":5,  "extra":2, "type":1, "desc":"Increases lumber production in village.<br/>Bonus from oases is added, not multiplied.", "breq": {'1':10, '15':5}},
	{"name":"Brickyard",  "cost": [ 440, 480, 320,  50], "k":1.80, "cu":3,	"cp":1, "time":( 5240, 1.5,  2400), "maxlvl":5,  "extra":2, "type":1, "desc":"Increases clay production in village.<br/>Bonus from oases is added, not multiplied.", "breq": {'2':10, '15':5}},
	{"name":"Iron Foundry",  "cost": [ 200, 450, 510, 120], "k":1.80, "cu":6,	"cp":1, "time":( 6480, 1.5,  2400), "maxlvl":5,  "extra":2, "type":1, "desc":"Increases iron production in village.<br/>Bonus from oases is added, not multiplied.", "breq": {'3':10, '15':5}},
	{"name":"Grain Mill",  "cost": [ 500, 440, 380,1240], "k":1.80, "cu":3,	"cp":1, "time":( 4240, 1.5,  2400), "maxlvl":5,  "extra":2, "type":1, "desc":"Increases crop production in village.<br/>Bonus from oases is added, not multiplied.", "breq": {'4':5}},
	{"name":"Bakery",  "cost": [1200,1480, 870,1600], "k":1.80, "cu":4,	"cp":1, "time":( 6080, 1.5,  2400), "maxlvl":5,  "extra":2, "type":1, "desc":"Increases crop production in village.<br/>Bonus from oases is added, not multiplied.", "breq": {'4':10, '8':5, '15':5}},
	{"name":"Warehouse", "cost": [ 130, 160,  90,  40], "k":1.28, "cu":1,	"cp":1, "time":( 3875), "maxlvl":20, "extra":3, "type":1, "desc":"Limits maximum amount of resources available in village.<br/>When no stockyards, capacity is 800.", "breq": {'15':1}, "req":{"multi":True}},
	{"name":"Granary", "cost": [  80, 100,  70,  20], "k":1.28, "cu":1,	"cp":1, "time":( 3475), "maxlvl":20, "extra":3, "type":1, "desc":"Limits maximum amount of crop available in village.<br/>When no stockyards, capacity is 800.", "breq": {'15':1}, "req":{"multi":True}},
	{"name":"EMPTY"},
	{"name":"Smithy", "cost": [180, 250, 500, 160], "k":1.28, "cu":4,	"cp":2, "time":( 3875), "maxLvl":20, "extra":12, "type":2, "desc":"Troops' armors and weapons are enhanced here. Each village has separate upgrades.<br/>Upgrades remain after this building is torn down, but vanish after conquer." },
	{"name":"Tournament Square", "cost": [1750,2250,1530,	240], "k":1.28, "cu":1,	"cp":1, "time":( 5375), "maxlvl":20, "extra":4, "type":2, "desc":"Increases army speed, but only for part of distance exceeding 20 squares. Doesn't affect merchants.", "breq": {'16':15}},
	{"name":"Main Building", "cost": [  70,  40,  60,  20], "k":1.28, "cu":2,	"cp":2, "time":( 3875), "maxlvl":20, "extra":7, "type":3, "desc":"Affects construction speed of other buildings. Building speed is 5x slower on 0th level (destroyed) comparing to 1st level."},
	{"name":"Rally Point", "cost": [ 110, 160,  90,	 70], "k":1.28, "cu":1,	"cp":1, "time":( 3875), "maxlvl":20, "extra":13,"type":2, "desc":"In T4 rally point level N detects types of units in incomgin attacks, unless there're &ge; N units in that attack."},
	{"name":"Marketplace", "cost": [  80,  70, 120,  70], "k":1.28, "cu":4,	"cp":3, "time":( 3675), "maxlvl":20, "extra":14,"type":3, "desc":"Could be used as extra stockyard (but not a cranny!), by placing sell offer.<br/>Keep in mind, that resources could be stolen in raid.", "breq": {'15':3, '10':1, '11':1}},
	{"name":"Embassy", "cost": [ 180, 130, 150,	 80], "k":1.28, "cu":3, "cp":4, "time":( 3875), "maxlvl":20, "extra":8, "type":3, "desc":"Limits maximum alliance size. Embassy with maximum level among all alliance members is considred, not only from the founder's villages.", "breq": {'15':1}},
	{"name":"Barracks", "cost": [ 210, 140, 260,	120], "k":1.28, "cu":4,	"cp":1, "time":( 3875), "maxlvl":20, "extra":7, "type":2, "desc":"Once troops queued for training, their training time won't be changed disregarding of further changes in barracks level, effect from artifacts or items(T4).<br/>Even if barracks would be demolished, troops training will be continued.<br/>On classic (2.5) servers train speed is 20% slower.", "breq": {'15':3, '16':1}},
	{"name":"Stable", "cost": [ 260, 140, 220,	100], "k":1.28, "cu":5,	"cp":2, "time":( 4075), "maxlvl":20, "extra":7, "type":2, "desc":"Once cavalry queued for training, their training time won't be changed disregarding of further changes in stable level, effect from artifacts or items(T4).<br/>Even if stable would be demolished, cavalry training will be continued.<br/>On classic (2.5) servers train speed is 20% slower.", "breq": {'12':3, '22':5}},
	{"name":"Workshop", "cost": [ 460, 510, 600,	320], "k":1.28, "cu":3,	"cp":3, "time":( 4875), "maxlvl":20, "extra":7, "type":2, "desc":"Once war machines queued for building, their building time won't be changed disregarding of future changes in workshop level or effect from artifacts.<br/>Even if workshop would be demolished, constructing will be continued.", "breq": {'15':5, '22':10}},
	{"name":"Academy", "cost": [ 220, 160,  90,  40], "k":1.28, "cu":4,	"cp":4, "time":( 3875), "maxlvl":20, "extra":0, "type":2, "desc":"New types of troops are researched here. Researches remain after this building is torn down, but vanish after conquer.", "breq": {'15':3, '19':3}},
	{"name":"Cranny", "cost": [  40,  50,  30,  10], "k":1.28, "cu":0,	"cp":1, "time":(2175, 1.16, 1875), "maxlvl":10, "extra":3, "type":3, "desc":"Capacity for each of 4 resouce types. Gaulish cranny is 2x larger.<br/>Crannies have 20% less capacity against teuton raids.", "req":{"multi":True}},
	{"name":"Town Hall", "cost": [1250,1110,1260, 600], "k":1.28, "cu":4,	"cp":5, "time":(14375), "maxlvl":20, "extra":0, "type":3, "desc":"Celebrations are kept here. Resources are taken before start and culture points are added after the end.<br/>Great celebration increases effectiveness of administrators.", "breq": {'15':10, '22':10}},
	{"name":"Residence", "cost": [ 580, 460, 350,	180], "k":1.28, "cu":1,	"cp":2, "time":( 3875), "maxlvl":20, "extra":9, "type":3, "desc":"Increases village defense a bit and opens access to 2 expansion slots: on 10<sup>th</sup> and 20<sup>th</sup> levels.<br/>While not destroyed, prevents from loyalty descending in certain village and even increases it with rate = %*building level/hour.<br/>Also its level affect train time of settlers and administrators.", "breq": {'15':5, '26':-1}},
	{"name":"Palace", "cost": [ 550, 800, 750,	250], "k":1.28, "cu":1,	"cp":5, "time":( 6875), "maxlvl":20, "extra":9, "type":3, "desc":"Similar to residence, but gives an option to move your capital and extra expansion slot on 15<sup>th</sup> level.", "breq": {'15':5, '18':1, '25':-1}},
	{"name":"Treasury", "cost": [2880,2740,2580,	990], "k":1.26, "cu":4,	"cp":6, "time":( 9875), "maxlvl":20, "extra":15,"type":3, "desc":"Artifacts are kept here. In classic version max level is 10 and treasury couldn't be built in captial.<br/>", "breq": {'15':10, '40':-1}},
	{"name":"Trade Office", "cost": [1400,1330,1200,	400], "k":1.28, "cu":3,	"cp":3, "time":( 4875), "maxlvl":20, "extra":3, "type":3, "desc":"Increase merchants' capacity by 20%/level.<br/>For Romans bonus is 40%.", "breq": {'17':20, '20':10}},
	{"name":"Great Barracks", "cost": [ 630, 420, 780,	360], "k":1.28, "cu":4,	"cp":1, "time":( 3875), "maxlvl":20, "extra":7, "type":2, "desc":"Allows to build infantry simultaneously with normal barracks, but for 3x more resources.", "breq": {'19':20}, "req":{"capital":-1}},
	{"name":"Great Stable", "cost": [ 780, 420, 660,	300], "k":1.28, "cu":5,	"cp":2, "time":( 4075), "maxlvl":20, "extra":7, "type":2, "desc":"The same as great barracks, but for cavalry.", "breq": {'20':20}, "req":{"capital":-1}},
	{"name":"City Wall", "cost": [  70,  90, 170,  70], "k":1.28, "cu":0,	"cp":1, "time":( 3875), "maxlvl":20, "extra":9, "type":2, "desc":"1x durability. Disappear after conquering of the village.", "req": {"race":1}},
	{"name":"Earth Wall", "cost": [ 120, 200,   0,  80], "k":1.28, "cu":0,	"cp":1, "time":( 3875), "maxlvl":20, "extra":9, "type":2, "desc":"5x durability. Disappear after conquering of the village.", "req": {"race":2}},
	{"name":"Palisade", "cost": [ 160, 100,  80,  60], "k":1.28, "cu":0,	"cp":1, "time":( 3875), "maxlvl":20, "extra":9, "type":2, "desc":"2x durability. Disappear after conquering of the village.", "req": {"race":3}},
	{"name":"Stonemason", "cost": [ 155, 130, 125,  70], "k":1.28, "cu":2,	"cp":1, "time":( 5950,2), "maxlvl":20, "extra":5, "type":2, "desc":"Increases durability of all buildings in capital, including resourcefields and wall.<br/>It is always the last building destroyed by catapults. If village is affected by random targets artifact, it is the last building among inner ones (i.e. excluding resourcefields)", "breq": {'15':5,'26':3}, "req":{"version":[3,9], "capital": 1}},
	{"name":"Brewery", "cost": [3210,2050,2750,3830], "k":1.24, "cu":6,	"cp":4, "time":(11750,2), "maxlvl":20, "extra":6, "type":3, "desc":"If you change level of a brewery after start of celebration, this will have no effect on started celebration.", "breq": {'11':20,'16':10}, "req":{"race":2, "version":[3,9]}},
	{"name":"Trapper", "cost": [80, 120, 70, 90], "k":1.28, "cu":4,	"cp":1, "time":( 2000,0), "maxlvl":20, "extra":10,"type":2, "desc":"Multiple trappers don't build/repair traps simultaneously. Repair time is always 1 minute and doesn't depend on server speed or level of trapper.", "breq": {'16':1}, "req":{"race":3, "multi":True, "version":[3,9]}},
	{"name":"Hero's Mansion", "cost": [ 700, 670, 700, 240], "k":1.33, "cu":2,	"cp":1, "time":( 2300,0), "maxlvl":20, "extra":11,"type":2, "desc":"In T4 adventures spawn around villages, which have this building and<br/>Capital is always considered as having this building.", "breq": {'15':3, '16':1}, "req":{"version":[3,4]}},
	{"name":"Great Warehouse", "cost": [ 650, 800, 450, 200], "k":1.28, "cu":1,	"cp":1, "time":(10875), "maxlvl":20, "extra":3, "type":1, "desc":"Just a 3 times larger warehouse. Can be built either in WW village, or in villages affected by special artifact.<br/>In second case, artifact is required not only for constructing of 1st level.", "breq": {'15':10}, "req":{"multi":True}},
	{"name":"Great Granary", "cost": [ 400, 500, 350, 100], "k":1.28, "cu":1,	"cp":1, "time":( 8875), "maxlvl":20, "extra":3, "type":1, "desc":"Just a 3 times larger granary. Can be built either in WW village, or in villages affected by special artifact.<br/>In second case, artifact is required not only for constructing of 1st level.", "breq": {'15':10}, "req":{"multi":True}},
	{"name":"Horse Drinking Trough", "cost": [ 780, 420, 660, 540], "k":1.28, "cu":5,	"cp":3, "time":( 5950,2), "maxlvl":20, "extra":7, "type":3, "desc":"Increases training speed of roman cavalry in certain village.<br/>Decreases crop consumption of roman cavalry, fed (supplied) from that village.", "breq": {'16':10, '20':20}, "req":{"race":1, "version":[3,9]}},
	{"name":"Stone Wall","cost": [ 110, 160,  70,  60], "k":1.28,"cu":0,"cp":1, "time":( 3875), "maxlvl":20, "extra":9, "type":2, "desc":"5x durability. Disappear after conquering of the village.", "req": {"race":6,"version":[4.2,5]}},
	{"name":"Makeshift Wall", "cost": [  50,  80,  40,  30], "k":1.28, "cu":0,	"cp":1, "time":( 3875), "maxlvl":20, "extra":9, "type":2, "desc":"1x durability. Disappear after conquering of the village.", "req": {"race":7,"version":[4.2,4]}},
	{"name":"Command Center", "cost": [1600,1250,1050, 200], "k":1.22, "cu":1,	"cp":2, "time":( 3875), "maxlvl":20, "extra":9, "type":3, "desc":"Best of Residence and Palace: 3 chiefs, can be built in every village.", "req": {"race":7,"version":[4.2,4]}, "breq": {'15':5, '25':-1, '26':-1}},
	{"name":"Waterworks", "cost": [ 910, 945, 910, 340], "k":1.31, "cu":1,	"cp":2, "time":( 3875), "maxlvl":20, "extra":2, "type":1, "desc":"Increases oases bonus", "req": {"race":6,"version":[4.2,4]}, "breq": {'37':10}},
	{"name":"Hospital", "cost": [ 320, 280 , 420, 360], "k":1.28, "cu":3,"cp":4, "time":( 4875), "maxlvl":20, "extra":2, "type":2, "desc":"Heals up to 40% troops lost", "req": {"version":[4.31,4.32,4.51,4.6]}, "breq": {'22':15,'15':10}}
]

def timecalc(gid, lvl):
	time = buildings[gid-1]["time"]
	a=time[0]
	if len(time) < 3:
		k=1.16
		if len(time) == 1:
			k = 1
		b = 1875*k
	else:
		k = time[1]
		b =time[2]
	return a * (k**(lvl-1)) - b

def costandupkeepcalc(gid, lvl):
	cost = buildings[gid - 1]["cost"]
	k = buildings[gid - 1]["k"]
	result = [0,0,0,0]
	for i in range(4):
		result[i] = round((cost[i] * (k**(lvl-1))) / 5) * 5
	return result

def upkeepcalc(gid, lvl):
	cu = buildings[gid-1]["cu"]
	if lvl == 1:
		result = cu
	else:
		result = round((5*cu + lvl-1)/10)
	return result

def culturecalc(gid, lvl):
	cp = buildings[gid-1]["cp"]
	return round(cp * (1.2 ** lvl))

def namecalc(gid):
	return buildings[gid-1]["name"]

def costandupkeepcalc(gid, lvl):
	return costandupkeepcalc(gid, lvl) + [upkeepcalc(gid, lvl)]

# def calcstats(gid, lvl):
# 	return [namecalc(gid), ]

print(costandupkeepcalc(1,5))

