#!/usr/bin/env python3

import sys
import timeit
import random
import logging as log
import cv2 as cv
import imutils as im
import numpy as np
import ruamel.yaml

from time import sleep
from io import BytesIO
from PIL import Image, ImageTk, ImageEnhance, UnidentifiedImageError
from pillow_lut import load_cube_file, load_hald_image

from .imutils.perspective import four_point_transform


# Rotate image 90 degrees CW/CCW
def cv_auto_rotate(img, direction):

    rot = -90

    # Change direction of rotation if needed
    if direction == "cw":
        rot = 90

    # Rotate the image if it's width is smaller than it's height
    if img.shape[1] < img.shape[0]:
        start = timeit.default_timer()
        img = im.rotate_bound(img, angle=rot)
        stop = timeit.default_timer()

        log.debug(f"Rotate image 90 degrees CCW in {stop - start} seconds")

    return img


# Slice contour area from image
def cv_slice_img(img, img_resized, cnt, pfix):

    start = timeit.default_timer()
    slice = None
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
                log.debug(f"Perspective fix image for {tilt_angle} degree tilt")
            else:
                log.debug(f"Perspective fix image for {90 - tilt_angle} degree tilt")

            slice_with_pfix = True

    # Slice image with pfix
    if slice_with_pfix:
        pts = np.int64(cv.boxPoints(rot_rect))
        slice = four_point_transform(img, pts, (255, 255, 255))

    # Slice image without pfix
    else:
        x, y, w, h = cv.boundingRect(cnt)

        slice = img[
            y:min(y + h, img.shape[0]),
            x:min(x + w, img.shape[1])
            ]

    stop = timeit.default_timer()

    log.debug(f"Slice image ({slice.shape[1]}x{slice.shape[0]}) from scanned image ({img.shape[1]}x{img.shape[0]}) in {stop - start} seconds")

    return slice


# Check if cnt is between range(min, max)
def cv_is_cnt_in_range(img, cnt, min, max):

    img_area = img.data.shape[0] * img.shape[1]
    x, y, w, h = cv.boundingRect(cnt)
    cnt_area = w * h
    cnt_area_in_prc = cnt_area / img_area * 100.0

    if cnt_area_in_prc > min and cnt_area_in_prc < max:
        log.debug(f"Contour area ({cnt_area_in_prc}%) is between {min}% and {max}%)")
        return True

    return False


# Draw rect
def cv_draw_rect(img, rect, color, border=2):

    cv.rectangle(img, (rect.x, rect.y), (rect.x + rect.w, rect.y + rect.h), color, border)

    log.debug(f"Draw rectangle ({rect.w}x{rect.h}) with color {color}")

# Draw contour
def cv_draw_cnt(img, cnt, color, border=2):

    x, y, w, h = cv.boundingRect(cnt)

    log.debug(f"Draw rectangle ({w}x{h}) with color {color}")
    cv.rectangle(img, (x, y), (x + w, y + h), color, border)


# Detect image slices and return them as contours
def cv_detect_slices(img):

    start = timeit.default_timer()

    cnts = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    stop = timeit.default_timer()

    # Grab the contours and return them
    log.debug(f"Detect slice contours in {stop - start} seconds")

    return im.grab_contours(cnts)


# Apply white threshold to OpenCV image
def cv_apply_wt(img, wt):

    start = timeit.default_timer()

    # Apply filters (greyscale, blur)
    img_wt_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_wt_blur = cv.GaussianBlur(img_wt_gray, (5, 5), 0)

    # Apply threshold
    img_wt_thresh = cv.threshold(img_wt_blur, wt, 255, cv.THRESH_BINARY_INV)[1]

    stop = timeit.default_timer()

    # Return the thresholded image
    log.debug(f"Apply threshold ({wt}) in {stop - start} seconds")

    return img_wt_thresh


# Convert image from OpenCV to PIL
def cv_to_pil(img):

    log.debug("Convert image to PIL")

    return Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2RGB))


def cv_denoise(img, strength):

    start = timeit.default_timer()
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

    stop = timeit.default_timer()

    log.debug(f"Denoise image with strength ({strength}/5) in {stop - start} seconds")

    return img_denoise

# Resize OpenCV image
def cv_resize(img, w=None, h=None, scale=None):

    # Resize with scale
    if scale:
        log.debug(f"CV Scale image: ({img.shape[1]}x{img.shape[0]}) -> ({scale * img.shape[1]}x{scale * img.shape[0]})")

        return cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_AREA)

    # Resize with width
    if w:
        log.debug(f"CV Resize image width ({img.shape[1]}) -> ({w})")

        return im.resize(img, width=w)

    # Resize with height
    if h:
        log.debug(f"CV Resize image height ({img.shape[0]}) -> ({h})")

        return im.resize(img, height=h)


# Resize PIL image
def pil_resize(img, w=None, h=None, scale=None):

    if scale:
        log.debug(f"PIL Scale image {img.size} -> {scale * img.size}")

        new_w, new_h = (int(img.width * scale), int(img.height * scale))
        return img.resize((new_w, new_h))

    if w:
        ratio = w / img.width

        if w != img.width:
            log.debug(f"PIL Resize image width ({img.width}) -> ({w})")
            return img.resize((w, int(img.height * ratio)))
        else:
            return img

    if h:
        ratio = h / img.height

        if h != img.height:
            log.debug(f"PIL Resize image height ({img.height}) -> ({h})")
            return img.resize((int(img.width * ratio), h))
        else:
            return img


# Open image with PIL
def pil_open_image(filepath):

    start = timeit.default_timer()

    try:
        img = Image.open(filepath)

    except FileNotFoundError:
        log.error(f"Could not find image at {filepath}")
        sys.exit()

    except UnidentifiedImageError:
        log.error(f"Could not open image at {filepath}")
        sys.exit()

    stop = timeit.default_timer()

    log.debug(f"Open image {filepath} in {stop - start} seconds")

    return img


# Convert image from PIL to OpenCV
def pil_to_cv(img):
    log.debug(f"Convert image from PIL to OpenCV")

    return cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)


# Save image into buffer
def pil_to_buffer(img):
    log.debug("Convert image to bytebuffer")

    with BytesIO() as buf:
        img.save(buf, format="PNG")
        output = buf.getvalue()

    return output


# Filter image
def pil_filter_image(img, filters):

    color = filters[0]
    contrast = filters[1]
    brightness = filters[2]
    sharpness = filters[3]
    denoise = filters[4]
    lut_str = filters[5]
    lut_path = filters[6]

    # Apply denoise
    if denoise:
        img_filter = cv_to_pil(cv_denoise(img, denoise))
    else:
        img_filter = cv_to_pil(img)

    # Apply LookUp-Table (LUT)
    if lut_path and lut_str > 0.0:
        lut = load_cube_file(lut_path)
        img_filter_lut = img_filter.filter(lut)
        img_filter = Image.blend(img_filter, img_filter_lut, lut_str)

        log.debug(f"Filter image with LUT using strength: {lut_str}")

    # Apply color:
    if color != 1.0:
        enhanced_img = ImageEnhance.Color(img_filter)
        img_filter = enhanced_img.enhance(color)
        log.debug(f"Filter color with value: {color}")

    # Apply contrast
    if contrast != 1.0:
        enhanced_img = ImageEnhance.Contrast(img_filter)
        img_filter = enhanced_img.enhance(contrast)
        log.debug(f"Filter contrast with value: {contrast}")

    # Apply brightness
    if brightness != 1.0:
        enhanced_img = ImageEnhance.Brightness(img_filter)
        img_filter = enhanced_img.enhance(brightness)
        log.debug(f"Filter brightness with value: {brightness}")

    # Apply sharpness
    if sharpness != 1.0:
        enhanced_img = ImageEnhance.Sharpness(img_filter)
        img_filter = enhanced_img.enhance(sharpness)
        log.debug(f"Filter sharpness with value: {sharpness}")

    return img_filter


# Create random string
def random_string(rand1, rand2, rand3):
    random.seed(rand1 + rand2 + rand3)

    return str(random.random()).replace("0.", "")


# Remove suffix from file
def remove_suffix(this):

    # Go over chars until the first dot from right
    count = 0
    first_dot_index = 0

    for char in reversed(this):
        if char == ".":
            first_dot_index = count
            break
        else:
            count += 1

    return this[:-first_dot_index - 1]


# Get human readable sizes
def convert_bytes(size):

    power = 2**10
    n = 0
    labels = {0: '', 1: ' Kb', 2: ' Mb', 3: ' Gb', 4: ' Tb'}

    while size > power:
        size /= power
        n += 1

    return str(round(size)) + str(labels[n])


# Change value in yaml file
def yaml_change_value(path, yaml_key, new_val):

    # Open the file
    with open(path, 'r') as f:
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        data = yaml.load(f)

    # Edit value
    data[yaml_key] = new_val

    # Save the file
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
