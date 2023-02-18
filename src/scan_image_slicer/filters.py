#!/usr/bin/env python3

import cv2 as cv
import imutils as im
import numpy as np

def show_images(topic, images, max_height, preview=False, name=False, infobar_settings=False):
    action = ""
    max_height = max_height
    topic = topic + "|Space for next|Q or ESC to exit"
    index = 0

    if infobar_settings:
        if infobar_settings["show_infobar"]:
            show_infobar = True
        else:
            show_infobar = False
    else:
        show_infobar = False

    if name and show_infobar:
        infobar_bg_color = (255, 255, 255)
        font_type = 1
        font_scale = infobar_settings["font_scale"]
        font_color = (25, 25, 25)
        font_thickness = 1

        infobar = {
            "Name: ": name,
            "Dimension: ": str(images[0].shape[1]) + "x" + str(images[0].shape[0]),
        }

        infobar_width = []
        infobar_height = []

        for key, value in infobar.items():
            (line_width, line_height), baseline = cv.getTextSize(
                key + value,
                font_type,
                font_scale,
                font_thickness
            )

            infobar_width.append(line_width)
            infobar_height.append(line_height + baseline)

    for i in range(len(images)):
        images[i] = im.resize(images[i], height=min(max_height, images[i].shape[0]))

    while(True):
        if show_infobar:
            margin = 5
            infobar_pt1 = (0, 0)
            infobar_pt2 = (max(infobar_width) + 0, sum(infobar_height) + 0)
            cv.rectangle(
                images[index],
                infobar_pt1,
                (infobar_pt2[0] + 2 * margin,
                infobar_pt2[1] + 2 * margin),
                infobar_bg_color, -1
                )

            line_count = 0
            line_start = infobar_height[0]

            for key, value in infobar.items():
                cv.putText(
                    images[index],
                    key + value,
                    (infobar_pt1[0] + margin, infobar_pt1[1] + margin + line_start),
                    font_type,
                    font_scale,
                    font_color,
                    font_thickness
                )

                line_start += infobar_height[line_count]
                line_count += 1

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