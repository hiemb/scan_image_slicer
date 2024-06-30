#!/usr/bin/env python3

import sys
import logging as log

from .confparser import conf_parser_p
from .scis import *
from .utils import create_statusline

# Select log level
# Use log.DEBUG for debugging
LOG_LEVEL = log.INFO


def main():
    if LOG_LEVEL != log.INFO:
        lname = '[%(levelname)s] '
    else:
        lname = ":: "

    log.basicConfig(format=lname + '%(message)s', level=LOG_LEVEL, handlers=[log.StreamHandler(sys.stdout)])

    # Collect the program params
    p = conf_parser_p()

    # Parse params
    p = parse_p(p)

    # Show the statusline
    if LOG_LEVEL > log.DEBUG:
        print(create_statusline(p.name, p.version, p.description, p.path_config_file))

    # Collect images from input path
    images = collect_images(p.input)

    # List compatible images with ID, name and size
    if p.list_images:
        list_images(images)
        print()

    # Save a list of compatible images into output directory
    if p.list_file:
        save_imagelist_as_txt(p.output, p.project_name, images)

    # Add/remove tasks
    tasks = []
    if any([p.add_all, p.add_id, p.add_new, p.add_old, p.add_random, p.remove_id]):
        tasks = handle_tasks(p, images)
        tasks = sorted(tasks, key=int)
        print()

    # List tasks
    if p.list_tasks:
        list_tasks(tasks, images)
        print()

    # Run action mode
    if any([p.test_mode, p.preview_mode, p.slice_mode, p.count_mode]):

        # Only run if there are tasks to do
        if tasks:

            # Run tasks
            run_tasks(p, tasks, images)
            print()

            # Rename output files
            if p.slice_mode:
                sequential_parallel_rename(p)
        else:
            log.info("Add some tasks before using action modes")

if __name__ == "__main__":
    sys.exit(main())
