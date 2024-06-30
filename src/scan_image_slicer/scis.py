#!/usr/bin/env python3

import os
import sys
import timeit
import logging as log
from datetime import datetime
import random

from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Value
from operator import itemgetter
from tqdm.auto import tqdm
from time import strftime, localtime, gmtime
from .gui import show_preview_gui, show_test_gui
from .scis_image import ScanImageSlicerImage
from .utils import *


# Class for our program parameters
class Param:
    pass


# Run all action modes with this func
def run_tasks(p, tasks, images):

    # Create unique run id
    p.run_id = p.project_name + "_{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())

    # Create unique run path
    p.unique_path = os.path.join(p.output, p.run_id)

    # Value for results
    result = 0

    # Set initial amount of workers
    workers = 1

    # Create msg for run mode
    if p.test_mode:
        run_mode = "testmode"
    elif p.preview_mode:
        run_mode = "preview mode"
    elif p.slice_mode:
        run_mode = "slice mode"
    elif p.count_mode:
        run_mode = "count mode"

    log.info(f"About to start {run_mode} with {len(tasks)} tasks")

    # Skip confirm?
    if not p.skip_confirm:
        if not confirm():
            log.info("Aborting.")
            sys.exit()

    # Start the timer
    start = timeit.default_timer()
    print()
    log.info("%s started @ %s", run_mode.capitalize(), strftime("%a %d %b %Y %H:%M:%S", localtime()))

    # Enable more workers if needed
    if p.count_mode or p.slice_mode:
        workers = p.threads

    # Do we need multiprocessing?
    if workers > 1 and len(tasks) > 1:

        log.info(f"Use multiprocessing with {workers} workers")

        with ProcessPoolExecutor(max_workers=workers) as executor:

            # Create progress bar for our tasks
            with tqdm(total=len(tasks), desc=":: Progress", unit=" images", ncols=100) as pbar:
                futures = {}

                # Split our tasks for the executor
                for i, task in enumerate(tasks):

                    if p.count_mode:
                        future = executor.submit(images[task].count_slices, p)
                    elif p.slice_mode:
                        future = executor.submit(images[task].save_slices, p)

                    futures[future] = i

                for future in as_completed(futures):
                    i = futures[future]
                    result += future.result()
                    pbar.update(1)
    else:

        # Create progress bar for our tasks
        pbar = tqdm(tasks, desc=":: Progress", unit=" images", ncols=100)

        # Go over tasks one by one
        for task in pbar:

            if p.count_mode:

                # Only count the slices
                result += images[task].count_slices(p)

            if p.test_mode:

                # Show test mode GUI
                result += show_test_gui(p, images[task])

            elif p.preview_mode:

                # Show preview mode GUI
                result += show_preview_gui(p, images[task])

            elif p.slice_mode:

                # Slice and save images
                result += images[task].save_slices(p)

    # Stop timer and calculate time lapsed
    stop = timeit.default_timer()
    seconds = (stop - start)
    timer_result = strftime("%H hours, %M minutes and %S seconds", gmtime(seconds))

    log.info("%s finished @ %s", run_mode.capitalize(), strftime("%a %d %b %Y %H:%M:%S", localtime()))
    print()
    log.info("Time lapsed: %s", timer_result)

    # Report results
    if any([p.count_mode, p.test_mode]):
        log.info(f"Detected {result} images inside {len(tasks)} scanned images")
    if p.preview_mode:
        log.info(f"Detected {result} images")
    if p.slice_mode:
        log.info(f"Sliced {result} images from {len(tasks)} scanned images")


# Parse parameters
def parse_p(p):
    errors = []

    # Sanitize value paths
    p.input = os.path.normpath(os.path.expanduser(p.input))
    p.output = os.path.normpath(os.path.expanduser(p.output))

    if p.filter_lut_path:
        p.filter_lut_path = os.path.normpath(os.path.expanduser(p.filter_lut_path))

    # Make sure we have some project name
    if not p.project_name:
        p.project_name = "NewProject"

    # Make sure input path exists
    if not os.path.exists(p.input):
        errors.append(f"Input path does not exist: {p.input}")

    # Make sure output path exists
    if not os.path.exists(p.output):
        errors.append(f"Output path does not exist: {p.output}")

    # Make sure we have valid LUT file
    if p.filter_lut_path:
        if os.path.isfile(p.filter_lut_path):
            if not p.filter_lut_path.lower().endswith(".cube"):
                errors.append(f"LUT should be a valid .cube file")
        else:
            errors.append(f"Could not find LUT file at: {p.filter_lut_path}")

    # Go over value ranges
    if not p.white_threshold in range(0, 256):
        errors.append("Value of '-white/--white-threshold' should be between 0 and 255")

    if not int(p.minimum_size) in range(0, 101):
        errors.append("Value of '-min/--minimum-size' should be between 0 and 100")

    if not int(p.maximum_size) in range(0, 101):
        errors.append("Value of '-max/--maximum-size' should be between 0 and 100")

    if not p.view_height >= 100:
        errors.append("Value of '-viewH/--view_height' should be at least 100")

    if not p.view_width >= 100:
        errors.append("Value of '-viewW/--view_width' should be at least 100")

    if not p.filter_denoise in range(0, 6):
        errors.append("Value of '-denoise/--filter-denoise' should be between 0 and 5")

    if not int(p.filter_color * 100.0) in range(0, 201):
        errors.append("Value of '-color/--filter-color' should be between 0.0 and 2.0")

    if not int(p.filter_contrast * 100.0) in range(0, 201):
        errors.append("Value of '-contrast/--filter-contrast' should be between 0.0 and 2.0")

    if not int(p.filter_brightness * 100.0) in range(0, 201):
        errors.append("Value of '-brightness/--filter-brightness' should be between 0.0 and 2.0")

    if not int(p.filter_sharpness * 100.0) in range(0, 201):
        errors.append("Value of '-sharpness/--filter-sharpness' should be between 0.0 and 2.0")

    if not int(p.filter_lut_strength * 100.0) in range(0, 101):
        errors.append("Value of '-lutS/--filter-lut-strength' should be between 0.0 and 1.0")

    if not p.perspective_fix in range(0, 90):
        errors.append("Value of '-pfix/--perspective-fix' should be between 0 and 89")

    if not p.auto_rotate in ["disable", "cw", "ccw"]:
        errors.append("Value of '-autoR/--auto-rotate' should be one of disable, cw or ccw")

    if not p.save_format in ["jpeg", "png", "webp"]:
        errors.append("Value of '-save/--save-format' should be one of jpeg, png or webp")

    if not p.png_compression in range(0, 10):
        errors.append("Value of '-pngC/--png-compression' should be between 0 and 9")

    if not p.jpeg_quality in range(0, 96):
        errors.append("Value of '-jpegQ/--jpeg-quality' should be between 0 and 95")

    if not p.webp_method in range(0, 7):
        errors.append("Value of '-webpM/--webp-method' should be between 0 and 6")

    if not p.webp_quality in range(1, 101):
        errors.append("Value of '-webpQ/--webp-quality' should be between 1 and 100")

    # Abort on errors
    if errors:
        log.error("Fix the following errors to continue:")
        for error in errors:
            log.error(error)
        sys.exit()

    return p


# Confirm the function
def confirm():

    while True:
        try:
            answer = input(":: Continue y/n: ").lower()

            if answer == 'y':
                return True
            elif answer == 'n':
                return False
            else:
                continue
        except OSError as e:
            sys.exit(e)


# Function to create the correct amount of dots
def create_dots(chars):
    cutoff_point = 6
    cutoff_amount = chars - cutoff_point
    dots = " .......... "
    dots = dots.replace('.', "", cutoff_amount)

    return dots


# List compatible images
def list_images(images):

    log.info("List images:")

    for key in images.keys():
        line = "[ID:" + str(images[key].id) + "]"
        line += create_dots(len(line)) + images[key].name
        line += " (" + images[key].size_mb + ")"
        log.info(line)


# Save list of compatible scanned images as a txt file inside output directory
def save_imagelist_as_txt(path, name, images):

    fn = f"{name}_compatible_images.txt"
    fp = os.path.join(path, fn)
    lines = []

    for key in images.keys():
        line = "[ID:" + str(images[key].id) + "]"
        line += create_dots(len(line)) + images[key].name
        line += " (" + images[key].size_mb + ")"
        lines.append(line + "\n")

    with open(fp, 'w') as outfile:
        try:
            outfile.writelines(lines)
            outfile.close()
        except OSError as err:
            sys.exit(err)

    if os.path.exists(fp):
        log.info("Saved file: %s", fp)


# Add/remove tasks
def handle_tasks(p, images):
    tasks = []
    warns = []

    def add_valid_task(task_id):

        if not task_id in tasks:
            if task_id in images:
                tasks.append(task_id)
            else:
                warns.append(f"Image not found with ID: {task_id}")
        else:
            warns.append(f"Task already created for image with ID: {task_id}")

    def remove_valid_task(task_id):

        if task_id in tasks:
            tasks.remove(task_id)
        else:
            warns.append(f"No image in tasks with ID: {task_id}")

    # Add all compatible images
    if p.add_all:

        log.info(f"Add all {len(images)} images")

        tasks = list(images.keys())

    # Add compatible images with ID
    if p.add_id:

        log.info(f"Add images with ID: {p.add_id}")

        for i in p.add_id:
            add_valid_task(i)

    # Add compatible new images by mtime
    if p.add_new:

        log.info(f"Add {p.add_new} images by mtime (newest)")

        for i in range(p.add_new):
            add_valid_task(i)

    # Add compatible old images by mtime
    if p.add_old:
        
        log.info(f"Add {p.add_old} images by mtime (oldest)")

        for i in range(p.add_old):
            add_valid_task((len(images)-1)-i)

    # Add compatible random images
    if p.add_random:

        pool = list(images.keys())
        picks = []

        for i in range(p.add_random):
            pick = random.choice(pool)

            if not pick in picks:
                picks.append(pick)
                pool.remove(pick)
    
        log.info(f"Add random images with ID: {picks}")

        for pick in picks:
            add_valid_task(pick)

    # Remove tasks by ID
    if p.remove_id:

        log.info(f"Remove images with ID: {p.remove_id}")

        for i in p.remove_id:
            remove_valid_task(i)

    # Show warnings
    if warns:
        for warn in warns:
            log.warn(warn)

    return tasks


def list_tasks(tasks, images):

    log.info("List tasks:")

    if tasks:
        for task in tasks:
            image = images[task]
            line = "[ID:" + str(image.id) + "]"
            line += create_dots(len(line)) + image.name
            line += " (" + image.size_mb + ")"
            log.info(line)
    else:
        log.info("Tasklist is empty")


# Rename output temp files
def sequential_parallel_rename(p):

    output_images = []
    counter = 0
    cur_path = ""
    result = 0

    if p.save_format == "png":
        suffix = ".png"
    if p.save_format == "jpeg":
        suffix = ".jpg"
    if p.save_format == "webp":
        suffix = ".webp"

    # Walk through the unique directory inside output path and collect temporary images
    for path, dirs, files in os.walk(os.path.normpath(p.unique_path)):

        # Go through files one by one and rename them based on the directory names
        for file in files:

            # Only handle files with the right name and format
            if file.lower().startswith("tmp_file_") and file.lower().endswith(suffix):

                # Reset counter if our path changes
                if cur_path != path:
                    counter = 0
                    cur_path = path

                counter += 1

                # Get relative path of file
                rel_path = os.path.relpath(path, p.unique_path)

                # Handle files that are in the root dir (.)
                if rel_path == ".":
                    image = [
                        os.path.join(path, file),
                        os.path.join(path, "output_" + str(counter)) + suffix
                    ]

                    output_images.append(image)

                # Handle files within folders
                else:
                    filename = ""
                    parts = rel_path.split(os.sep)

                    for part in parts:
                        filename += part + "_"

                    image = [
                        os.path.join(path, file),
                        os.path.join(path, filename + str(counter) + suffix)
                    ]

                    output_images.append(image)

    # Do we need multiprocessing?
    if p.threads > 1 and len(output_images) > 1:
        log.info("Rename output files sequentially")

        with ProcessPoolExecutor(max_workers=p.threads) as executor:

            # Split our output images for the executor
            for i, output_image in enumerate(output_images):
                executor.submit(os.rename, output_image[0], output_image[1])
                log.debug(f"Rename {output_image[0]} to {output_image[1]}")
                result += i

    # Go over our output images and rename them sequentially
    else:
        log.info("Rename output files sequentially")

        for output_image in output_images:
            os.rename(output_image[0], output_image[1])
            log.debug(f"Rename {output_image[0]} to {output_image[1]}")


# Collect compatible images from input directory
def collect_images(input):
    id = 0
    sorted_images = {}
    scanned_images = []

    # Only accept these formats for the Image
    accepted_formats = [
                ".bmp",
                ".jpeg",
                ".jpg",
                ".png",
                ".webp",
                ".tiff",
            ]

    # Walk through the input folder and collect compatible images
    for path, dirs, files in os.walk(os.path.normpath(input)):

        # Go through files one by one
        for file in files:
            skip_file = True
            format = ""

            # Only accept image formats defined above
            for suffix in accepted_formats:
                if file.lower().endswith(suffix):
                    format = suffix[1:]
                    skip_file = False

            if not skip_file:

                # Append our found data
                image = [
                    path,
                    file,
                    format,
                    os.stat(os.path.join(path, file)).st_mtime,
                    os.stat(os.path.join(path, file)).st_size]

                scanned_images.append(image)

    if scanned_images:

        # Sort our images from newest to oldest (mtime)
        scanned_images = sorted(scanned_images, key=itemgetter(3), reverse=True)

        for scanned_image in scanned_images:

                image = ScanImageSlicerImage(
                    id,
                    scanned_image[0],
                    scanned_image[1],
                    scanned_image[2],
                    scanned_image[3],
                    scanned_image[4],
                )

                # Add our image to dictionary using the image id as key
                sorted_images[image.id] = image
                id += 1

        # Return our sorted images as a dictionary
        return sorted_images
    else:
        log.error(f"Could not find any compatible images at {input}")
        sys.exit()