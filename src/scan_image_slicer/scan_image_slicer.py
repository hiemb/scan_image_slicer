#!/usr/bin/env python3

import sys
import logging as log

from .scis import ScanImageSlicer
from .confparser import conf_parser

LOG_LEVEL = log.INFO
PROGRAM_NAME = "Scan Image Slicer"

def main():
    if LOG_LEVEL != log.INFO:
        lname = '[%(levelname)s] '
    else:
        lname = ":: "

    log.basicConfig(format=lname + '%(message)s', level=LOG_LEVEL, handlers=[log.StreamHandler(sys.stdout)])
    log.info("%s", PROGRAM_NAME)

    parsed_dicts = conf_parser()
    settings = parsed_dicts[0]
    commands = parsed_dicts[1]

    scis = ScanImageSlicer(settings)

    if commands["list_scans"]:
        scis.list_scanned_images()

    if commands["list_file"]:
        scis.list_scanned_images_to_file()

    if commands["add_all"]:
        scis.add_task_all_images()

    if commands["add_id"]:
        scis.add_task_with_image_id(commands["add_id"])

    if commands["add_new"]:
        scis.add_task_newest_n_images(commands["add_new"])

    if commands["add_old"]:
        scis.add_task_oldest_n_images(commands["add_old"])

    if commands["add_random"]:
        scis.add_task_random_n_images(commands["add_random"])

    if commands["remove_id"]:
        scis.remove_task_with_image_id(commands["remove_id"])

    if commands["list_cmds"]:
        scis.list_commands()

    if commands["list_tasks"]:
        scis.list_tasks()

    if settings["slice_mode"] or settings["test_mode"] or settings["preview_mode"]:
        scis.start(settings["skip_confirm"])

if __name__ == "__main__":
    sys.exit(main())