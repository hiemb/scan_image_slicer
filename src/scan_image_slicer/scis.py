#!/usr/bin/env python3

import os
import sys
import logging as log
import cv2 as cv
import numpy as np
import imutils as im
import random

from operator import itemgetter
from tqdm.auto import tqdm
from time import strftime, localtime, time_ns, gmtime
from .filters import denoise, bcg, show_images
from .imutils.perspective import four_point_transform

class ScanImageSlicer:
    def __init__(self, settings, path_config, infobar):
        self.settings = settings
        self.infobar = infobar
        self.path_config = path_config
        self.scanned_images = self.collect_scanned_images()
        self.tasks = []
        self.cmds = []
        self.dots = ".........."
        self.output_counter = {}

        inpath = os.path.split(self.settings["input"])
        outpath = os.path.split(self.settings["output"])

        if inpath[1] == "":
            self.settings["input"] = inpath[0]
        else:
            self.settings["input"] = os.path.join(inpath[0], inpath[1])

        if outpath[1] == "":
            self.settings["output"] = outpath[0]
        else:
            self.settings["output"] = os.path.join(outpath[0], outpath[1])

    def slice(self, scanned_image):
        image_count = 0
        false_image_count = 0
        log.debug("Processing scanned image: %s", scanned_image[0])

        try:
            mat_source = cv.imread(scanned_image[1])

            if mat_source.shape[0] > 0:
                pass

        except AttributeError:
            log.error("Could not open file at: %s", scanned_image[1])
            sys.exit()

        image_area_px = mat_source.data.shape[0] * mat_source.shape[1]

        res_width = min(900, mat_source.shape[1])

        mat_res = im.resize(mat_source, width=res_width)
        mat_thresh = cv.cvtColor(mat_res, cv.COLOR_BGR2GRAY)
        mat_thresh = cv.GaussianBlur(mat_thresh, (5, 5), 0)
        mat_thresh = cv.threshold(mat_thresh,
                                  self.settings["white_threshold"],
                                  255,
                                  cv.THRESH_BINARY_INV)[1]

        contours = cv.findContours(mat_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = im.grab_contours(contours)

        if self.settings["test_mode"]:
            for contour in contours:
                contour_area_pct = (100 / image_area_px * cv.contourArea(contour)) * 100
                x, y, w, h = cv.boundingRect(contour)
                blue = (255, 33, 33)
                purple = (255, 33, 255)
                border = 2

                if contour_area_pct > self.settings["minimum_size"]:
                    cv.rectangle(mat_res, (x, y), (x + w, y + h), blue, border)
                    image_count += 1
                else:
                    cv.rectangle(mat_res, (x, y), (x + w, y + h), purple, border)
                    false_image_count += 1

            log.debug("%s: %s images (%s real, %s false)",
                    "|" + scanned_image[0],
                    image_count + false_image_count,
                    image_count,
                    false_image_count)

            if show_images(
                scanned_image[0],
                list([mat_res]),
                self.settings["view_height"]
                ) == "exit":
                sys.exit()

        elif self.settings["slice_mode"] or self.settings["preview_mode"]:
            for contour in contours:
                p_fix = self.settings["perspective_fix"]
                contour_area_pct = (100 / image_area_px * cv.contourArea(contour)) * 100

                if contour_area_pct > self.settings["minimum_size"]:
                    x_fac = mat_source.shape[1] / mat_res.shape[1]
                    y_fac = mat_source.shape[0] / mat_res.shape[0]
                    contour[:,:,0] = contour[:,:,0] * x_fac
                    contour[:,:,1] = contour[:,:,1] * y_fac

                    need_p_fix = False

                    if p_fix != 0:
                        persp_rect = cv.minAreaRect(contour)
                        tilt_angle = round(persp_rect[2])

                        if tilt_angle in range(p_fix, 90 - p_fix):
                            need_p_fix = True

                    if need_p_fix:
                        points = np.int0(cv.boxPoints(persp_rect))
                        clear_color = self.settings["white_threshold"]
                        bvalue = (clear_color, clear_color, clear_color)
                        mat_save = four_point_transform(mat_source, points, bvalue)
                    else:
                        x, y, w, h = cv.boundingRect(contour)
                        mat_save = mat_source[y:min(y + h, mat_source.shape[0]),
                                              x:min(x + w, mat_source.shape[1])]

                    scaled = False

                    if self.settings["scale_factor"] != 0:
                        scale_factor = self.settings["scale_factor"]
                        mat_save = cv.resize(mat_save, None, fx=scale_factor, fy=scale_factor, interpolation=cv.INTER_AREA)
                        scaled = True

                    if not scaled and self.settings["scale_width"] != 0:
                        scale_width = self.settings["scale_width"]
                        mat_save = im.resize(mat_save, width=scale_width)
                        scaled = True

                    if not scaled and self.settings["scale_height"] != 0:
                        scale_height = self.settings["scale_height"]
                        mat_save = im.resize(mat_save, height=scale_height)

                    if self.settings["filter_denoise"] != 0:
                        mat_filt = denoise(mat_save, self.settings["filter_denoise"])

                    if self.settings["filter_brightness"] != 1.0 or \
                       self.settings["filter_contrast"] != 1.0 or \
                       self.settings["filter_gamma"] != 1.0:
                        mat_filt = bcg(mat_filt, self.settings["filter_brightness"],
                                                 self.settings["filter_contrast"],
                                                 self.settings["filter_gamma"])

                    # Figure out the filename before previewing the image.

                    file_name = ""
                    file_name_divider = "-"
                    inpath = self.settings["input"]
                    outpath = self.settings["output"]
                    abs_path = scanned_image[1]
                    dest_path = scanned_image[2]
                    rel_path = scanned_image[3]

                    if rel_path == ".":
                        file_name += os.path.split(inpath)[1] + file_name_divider
                    else:
                        parts = rel_path.split(os.sep)

                        for part in parts:
                            file_name += part + file_name_divider

                    if file_name in self.output_counter.keys():
                        self.output_counter[file_name] += 1
                    else:
                        self.output_counter[file_name] = 1

                    file_name += str(self.output_counter[file_name])

                    if self.settings["save_format"] == "PNG":
                        file_name += ".png"
                        params = [int(cv.IMWRITE_PNG_COMPRESSION), self.settings["png_compression"]]
                    elif self.settings["save_format"] == "JPEG":
                        file_name += ".jpg"
                        params = [int(cv.IMWRITE_JPEG_QUALITY), self.settings["jpeg_quality"]]
                    elif self.settings["save_format"] == "WEBP":
                        file_name += ".webp"
                        params = [int(cv.IMWRITE_WEBP_QUALITY), self.settings["webp_quality"]]

                    outfile = os.path.normpath(os.path.join(dest_path, file_name))

                    action = ""
                    if self.settings["preview_mode"]:
                        action = show_images(
                            "|S to save|F to toggle filters",
                            list([mat_save, mat_filt]),
                            self.settings["view_height"],
                            True,
                            file_name,
                            self.infobar
                            )

                    if action == "exit":
                        sys.exit()

                    if action == "save" or self.settings["slice_mode"]:

                        if not os.path.exists(scanned_image[2]):
                            os.makedirs(scanned_image[2])

                        cv.imwrite(outfile, mat_filt, params)
                        image_count += 1

                        log.debug("Saved file: %s", outfile)
        else:
            log.error("Unknown mode")
            sys.exit()

        return image_count

    def start(self, skip_confirm):
        print()
        start = False
        sliced_images_count = 0
        log.info("Starting slicer with these settings:")
        for option in self.settings:
            log.info("%s: %s", option, self.settings[option])
        print()
        log.info("Tasks to complete: %s", len(self.tasks))
        if not self.tasks:
            log.info("No tasks were completed")
            sys.exit()

        if not skip_confirm:
            log.info("Continue? y/n")

            while True:
                try:
                    answer = input(":: Answer: ").lower()

                    if answer == 'y':
                        start = True
                        break
                    elif answer == 'n':
                        print()
                        log.info("Aborting")
                        sys.exit()
                    else:
                        continue
                except OSError as e:
                    sys.exit(e)
        else:
            start = True

        if start:
            timer_start = time_ns()
            print()
            log.info("Process start @ %s", strftime("%a %d %b %Y %H:%M:%S", localtime()))

            if log.getLogger().getEffectiveLevel() > log.DEBUG:
                pbar = tqdm(self.tasks, desc=":: Progress", unit="image", ncols=100)
                for task in pbar:
                    image = self.scanned_images[task]
                    image_count = self.slice(image)
                    sliced_images_count += image_count
            else:
                for task in self.tasks:
                    image = self.scanned_images[task]
                    image_count = self.slice(image)
                    sliced_images_count += image_count

            timer_stop = time_ns()
            seconds = (timer_stop - timer_start) / 1000000000
            timer_result = strftime("%H hours, %M minutes and %S seconds.", gmtime(seconds))

            log.info("Process finish @ %s", strftime("%a %d %b %Y %H:%M:%S", localtime()))
            print()
            action = "Saved"
            if self.settings["test_mode"]: action = "Detected"
            log.info("%s %s images from %s scanned images", action, sliced_images_count, len(self.tasks))
            log.info("Time lapsed: %s", timer_result)

    def list_tasks(self):
        print()
        dots = self.dots
        log.info("Listing tasks (%s)", len(self.tasks))

        if self.tasks:
            for i in range(len(self.tasks)):
                if i in [9, 99, 999, 9999, 99999, 999999]:
                    dots = dots[1:]

                log.info("TASK #%s %s %s [ID:%s]", i + 1, dots, self.scanned_images[self.tasks[i]][0], self.tasks[i])
        else:
            log.info("Task list is empty")

    def list_commands(self):
        print()
        log.info("Listing commands (%s)", len(self.cmds))
        if self.cmds:
            for cmd in self.cmds:
                log.info(cmd)
        else:
            log.info("Command list is empty")

    def remove_task_with_image_id(self, ids):
        removed = []

        for id in ids:
            if id in self.tasks:
                self.tasks.remove(id)
                removed.append(id)
            else:
                self.cmds.append(f"[x] Image with ID [{id}] is not on the task list")

        if removed:
            self.cmds.append(f"[-] Removed image with ID {removed} from the task list")

    def add_task_newest_n_images(self, n):
        added = []

        if n > len(self.scanned_images):
            log.error("Cannot add more than %s newest images", len(self.scanned_images))
            sys.exit()

        for i in range(n):
            id = (len(self.scanned_images) - i) - 1

            if id in self.tasks:
                self.cmds.append(f"[x] Image with ID [{id}] is already on the task list")
            else:
                self.tasks.append(id)
                added.append(id)

        if added:
            self.cmds.append(f"[+] Added image with ID {added} to the task list")

    def add_task_oldest_n_images(self, n):
        added = []

        if n > len(self.scanned_images):
            log.error("Cannot add more than %s oldest images", len(self.scanned_images))
            sys.exit()

        for i in range(n):
            id = i

            if id in self.tasks:
                self.cmds.append(f"[x] Image with ID [{id}] is already on the task list")
            else:
                self.tasks.append(id)
                added.append(id)

        if added:
            self.cmds.append(f"[+] Added image with ID {added} to the task list")

    def add_task_with_image_id(self, ids):
        added = []

        for id in ids:
            if id in self.tasks:
                self.cmds.append(f"[x] Image with ID [{id}] is already on the task list")
            elif not id in range(0, len(self.scanned_images)):
                self.cmds.append(f"[x] Image with ID [{id}] does not exist")
            else:
                self.tasks.append(id)
                added.append(id)

        if added:
            self.cmds.append(f"[+] Added image with ID {added} to the task list")

    def add_task_all_images(self):
        self.cmds.append("[+] Added all scanned images to task list")
        self.tasks = []

        for i in range(len(self.scanned_images)):
            self.tasks.append(i)

    def add_task_random_n_images(self, n):
        added = []
        ids = []
        pool = []

        for i in range(0, len(self.scanned_images) - 1):
            pool.append(i)

        if n > len(self.scanned_images) - 1:
            log.error("Cannot add more than %s random images", len(self.scanned_images) - 1)
            sys.exit()

        while len(ids) != n:
            pick = random.choice(pool)
            pool.remove(pick)
            ids.append(pick)

        for id in ids:
            if id in self.tasks:
                self.cmds.append(f"[x] Image with ID [{id}] is already on the task list")
            else:
                self.tasks.append(id)
                added.append(id)

        if added:
            self.cmds.append(f"[+] Added image with ID {added} to the task list")

    def list_scanned_images(self):
        print()
        dots = self.dots
        log.info("Listing scanned images (%s)", len(self.scanned_images))

        for i in range(len(self.scanned_images)):
            if i in [10, 100, 1000, 10000, 100000, 1000000]:
                dots = dots[1:]

            log.info("ID %s %s %s", i, dots, self.scanned_images[i][0])

    def list_scanned_images_to_file(self):
        print()
        dots = self.dots
        lines = []

        filepath = os.path.join(self.path_config, "list of scanned images.txt")

        for i in range(len(self.scanned_images)):
            if i in [10, 100, 1000, 10000, 100000, 1000000]:
                dots = dots[1:]

            lines.append(f"ID {i} {dots} {self.scanned_images[i][0]}\n")

        with open(filepath, 'w') as outfile:
            try:
                outfile.writelines(lines)
                outfile.close()
                log.info("Saved list of scanned images to file: %s", filepath)
            except OSError as e:
                sys.exit(e)

    def collect_scanned_images(self):
        scanned_images = []
        accepted_formats = [
            ".bmp",
            ".dib",
            ".jpeg",
            ".jpg",
            ".jpe",
            ".jp2",
            ".png",
            ".webp",
            ".pbm",
            ".pgm",
            ".ppm",
            ".pxm",
            ".pnm",
            ".sr",
            ".ras",
            ".tiff",
            ".tif",
            ".exr",
            ".hdr",
            ".pic"
        ]

        inpath = self.settings["input"]
        outpath = self.settings["output"]

        for path, dirs, files in os.walk(inpath):
            for f in files:
                abs_path = os.path.join(path, f)
                rel_path = os.path.relpath(path, inpath)
                dest_path = os.path.join(outpath, rel_path)
                ctime = os.stat(abs_path).st_ctime
                data = [f, abs_path, dest_path, rel_path, ctime]

                for suffix in accepted_formats:
                    if f.lower().endswith(suffix):
                        scanned_images.append(data)

        if scanned_images:
            log.debug("Found %s scanned images at: %s", len(scanned_images), self.settings["input"])
            scanned_images = sorted(scanned_images, key=itemgetter(4))

            for scanned_image in scanned_images:
                scanned_image.pop()

            return scanned_images
        else:
            log.error("Could not find any scanned images at: %s", self.settings["input"])
            sys.exit()