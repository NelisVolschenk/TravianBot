import cv2
import numpy as np

img_rgb = cv2.imread('data/mapdata/-20.-80.-11.-71.png')
template = cv2.imread('data/mapdata/tiletypes/O_27_27.jpg')
w, h = template.shape[:-1]

res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
threshold = .8
loc = np.where(res >= threshold)
print(loc)
startx = -20
starty = -71

for pt in zip(*loc[::-1]):  # Switch collumns and rows
    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    print(pt)
    x = startx + (pt[0] // 60)
    y = starty - (pt[1] // 60)

    print(x,y)
# cv2.imwrite('result.png', img_rgb)

