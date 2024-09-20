#!/usr/bin/env python3

import logging
import random
import cv2 as cv
import imutils as im
import numpy as np
import ruamel.yaml

from io import BytesIO
from PIL import Image, ImageTk, ImageEnhance, UnidentifiedImageError
from pillow_lut import load_cube_file

from .imutils.perspective import four_point_transform

def cv_auto_rotate(img, direction):
    logger = logging.getLogger()
    rot = -90

    if direction == "cw":
        rot = 90

    # Rotate the image if it's width is smaller than it's height
    if img.shape[1] < img.shape[0]:
        img = im.rotate_bound(img, angle=rot)
        logger.debug(f"Auto rotating image 90 degrees {direction}")

    return img

# Slice contour area from image
def cv_slice_img(img, img_resized, cnt, pfix):
    logger = logging.getLogger()
    out_slice = None
    rot_rect = None
    slice_with_pfix = False

    x_fac = img.shape[1] / img_resized.shape[1]
    y_fac = img.shape[0] / img_resized.shape[0]
    cnt[:,:,0] = cnt[:,:,0] * x_fac
    cnt[:,:,1] = cnt[:,:,1] * y_fac

    # Do we need perspective fix?
    if pfix != 0:
        rot_rect = cv.minAreaRect(cnt)

        # Calculate tilt angle
        tilt_angle = abs(rot_rect[2])

        # Enable perspective fix if the tilt angle is larger than the maximum allowed tilt angle
        if tilt_angle > pfix and tilt_angle < (90 - pfix):

            if tilt_angle < 45.0:
                logger.debug(f"Perspective fix image for {tilt_angle} degree tilt")
            else:
                logger.debug(f"Perspective fix image for {90 - tilt_angle} degree tilt")

            slice_with_pfix = True

    # Slice image with pfix
    if slice_with_pfix:
        pts = np.int64(cv.boxPoints(rot_rect))
        out_slice = four_point_transform(img, pts, (255, 255, 255))

    # Slice image without pfix
    else:
        x, y, w, h = cv.boundingRect(cnt)

        out_slice = img[
            y:min(y + h, img.shape[0]),
            x:min(x + w, img.shape[1])
            ]

    return out_slice

# Check if cnt is between range(min, max)
def cv_is_cnt_in_range(img, cnt, min, max):
    img_area = img.data.shape[0] * img.shape[1]
    x, y, w, h = cv.boundingRect(cnt)
    cnt_area = w * h
    cnt_area_in_prc = cnt_area / img_area * 100.0

    if cnt_area_in_prc > min and cnt_area_in_prc < max:
        return True

    return False

def cv_draw_rect(img, rect, color, border=2):
    logger = logging.getLogger()
    cv.rectangle(img, (rect.x, rect.y), (rect.x + rect.w, rect.y + rect.h), color, border)
    logger.debug(f"Draw rectangle ({rect.w}x{rect.h}) with color {color}")

def cv_draw_cnt(img, cnt, color, border=2):
    logger = logging.getLogger()
    x, y, w, h = cv.boundingRect(cnt)
    cv.rectangle(img, (x, y), (x + w, y + h), color, border)
    logger.debug(f"Draw rectangle ({w}x{h}) with color {color}")

# Detect image slices and return them as contours
def cv_detect_slices(img):
    cnts = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    return im.grab_contours(cnts)

# Apply white threshold to OpenCV image
def cv_apply_wt(img, wt):
    logger = logging.getLogger()
    img_wt_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_wt_blur = cv.GaussianBlur(img_wt_gray, (5, 5), 0)
    img_wt_thresh = cv.threshold(img_wt_blur, wt, 255, cv.THRESH_BINARY_INV)[1]
    logger.debug(f"Apply threshold with value {wt}")
    return img_wt_thresh

def cv_to_pil(img):
    return Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2RGB))

def cv_denoise(img, strength):
    logger = logging.getLogger()
    strength = int(strength)
    param = [3, 3]

    match strength:
        case 0: return
        case 1: param.extend([3, 3])
        case 2: param.extend([5, 7])
        case 3: param.extend([7, 11])
        case 4: param.extend([9, 15])
        case 5: param.extend([11, 19])

    img_denoise = cv.fastNlMeansDenoisingColored(
        img,
        None,
        param[0],
        param[1],
        param[2],
        param[3]
        )

    logger.debug(f"Apply denoise with params {param}")

    return img_denoise

def cv_resize(img, w=None, h=None, scale=None):
    logger = logging.getLogger()

    if scale:
        logger.debug(f"CV Scale image: ({img.shape[1]}x{img.shape[0]}) -> ({scale * img.shape[1]}x{scale * img.shape[0]})")

        return cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_AREA)

    if w:
        logger.debug(f"CV Resize image width ({img.shape[1]}) -> ({w})")

        return im.resize(img, width=w)

    if h:
        logger.debug(f"CV Resize image height ({img.shape[0]}) -> ({h})")

        return im.resize(img, height=h)

def pil_resize(img, w=None, h=None, scale=None):
    logger = logging.getLogger()

    if scale:
        logger.debug(f"PIL Scale image {img.size} -> {scale * img.size}")

        new_w, new_h = (int(img.width * scale), int(img.height * scale))
        return img.resize((new_w, new_h))

    if w:
        ratio = w / img.width

        if w != img.width:
            logger.debug(f"PIL Resize image width ({img.width}) -> ({w})")
            return img.resize((w, int(img.height * ratio)))
        else:
            return img

    if h:
        ratio = h / img.height

        if h != img.height:
            logger.debug(f"PIL Resize image height ({img.height}) -> ({h})")
            return img.resize((int(img.width * ratio), h))
        else:
            return img

def pil_open_image(filepath):
    logger = logging.getLogger()
    img = None

    try:
        img = Image.open(filepath)
    except (FileNotFoundError, UnidentifiedImageError) as e:
        logger.error(e)

    return img

def pil_to_cv(img):
    return cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)

def pil_to_buffer(img):
    with BytesIO() as buf:
        img.save(buf, format="PNG")
        output = buf.getvalue()

    return output

def pil_filter_image(img, filters):
    logger = logging.getLogger()
    color = filters[0]
    contrast = filters[1]
    brightness = filters[2]
    sharpness = filters[3]
    denoise = filters[4]
    lut_str = filters[5]
    lut_path = filters[6]

    if denoise:
        img_filter = cv_to_pil(cv_denoise(img, denoise))
    else:
        img_filter = cv_to_pil(img)

    if lut_path and lut_str > 0.0:
        lut = load_cube_file(lut_path)
        img_filter_lut = img_filter.filter(lut)
        img_filter = Image.blend(img_filter, img_filter_lut, lut_str)

        logger.debug(f"Filter image with LUT using strength: {lut_str}")

    if color != 1.0:
        enhanced_img = ImageEnhance.Color(img_filter)
        img_filter = enhanced_img.enhance(color)
        logger.debug(f"Filter color with value: {color}")

    if contrast != 1.0:
        enhanced_img = ImageEnhance.Contrast(img_filter)
        img_filter = enhanced_img.enhance(contrast)
        logger.debug(f"Filter contrast with value: {contrast}")

    if brightness != 1.0:
        enhanced_img = ImageEnhance.Brightness(img_filter)
        img_filter = enhanced_img.enhance(brightness)
        logger.debug(f"Filter brightness with value: {brightness}")

    if sharpness != 1.0:
        enhanced_img = ImageEnhance.Sharpness(img_filter)
        img_filter = enhanced_img.enhance(sharpness)
        logger.debug(f"Filter sharpness with value: {sharpness}")

    return img_filter

def random_string(rand1, rand2, rand3):
    random.seed(rand1 + rand2 + rand3)
    return str(random.random()).replace("0.", "")

def remove_suffix(this):
    count = 0
    first_dot_index = 0

    for char in reversed(this):
        if char == ".":
            first_dot_index = count
            break
        else:
            count += 1

    return this[:-first_dot_index - 1]

def convert_bytes(size):
    power = 2**10
    n = 0
    labels = {0: '', 1: ' Kb', 2: ' Mb', 3: ' Gb', 4: ' Tb'}

    while size > power:
        size /= power
        n += 1

    return str(round(size)) + str(labels[n])

def yaml_change_value(path, yaml_key, new_val):
    with open(path, 'r') as f:
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        data = yaml.load(f)

    data[yaml_key] = new_val

    with open(path, 'w') as f:
        yaml.dump(data, f)

def create_statusline(name, version, description, config):
    desc_words = description.split(" ")

    art_lines = [
        "   ___________   ",
        "  |  __   __  |  %s - version: %s" % (name, version),
        "  | |S | |C | |  ",
        "  | |__| |__| |  %s " % " ".join(desc_words[:6]).strip("\n"),
        "  |  __   __  |  %s" % " ".join(desc_words[6:]).strip("\n"),
        "  | |I | |S | |  ",
        "  | |__| |__| |  %s" % "Config file:",
        "  |___________|  %s" % config,
    ]

    art = "\n".join(art_lines)
    art += "\n"

    return art
