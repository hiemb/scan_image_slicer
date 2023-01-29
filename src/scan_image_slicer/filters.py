#!/usr/bin/env python3

import cv2 as cv
import imutils as im
import numpy as np

def show_images(topic, images, max_height, preview):
    action = ""
    max_height = max_height
    topic = topic + "|Space for next|Q or ESC to exit"
    index = 0
    
    for i in range(len(images)):
        images[i] = im.resize(images[i], height=min(max_height, images[i].shape[0]))

    while(True):
        cv.imshow(topic, images[index])

        key = cv.waitKey(20)

        if key in [27, 113]:
            action = "exit"
            break
        elif key == 32:
            break
        elif key == 115:
            if preview:
                action = "save"
                break
        elif key == 102:
            if index < len(images) - 1:
                index += 1
            else:
                index = 0
    
    cv.destroyAllWindows()
    return action

def bcg(image, brightness, contrast, gamma):
    lut = np.empty((1, 256), np.uint8)

    for i in range(256):
        lut[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)

    result = cv.convertScaleAbs(image, alpha=contrast, beta=brightness)
    result = cv.LUT(result, lut)

    return result

def denoise(image, strength):
    s = [3, 3]

    if strength != 0:
        if strength == 1:
            s.append(3)
            s.append(3)
        elif strength == 2:
            s.append(5)
            s.append(7)
        elif strength == 3:
            s.append(7)
            s.append(11)
        elif strength == 4:
            s.append(9)
            s.append(15)
        elif strength == 5:
            s.append(11)
            s.append(19)

        result = cv.fastNlMeansDenoisingColored(image, None, s[0], s[1], s[2], s[3])
        return result