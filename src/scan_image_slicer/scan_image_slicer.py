#!/usr/bin/env python3

import os
import sys
import multiprocessing

from .confparser import conf_parser_p
from .scis import *
from .utils import create_statusline
from .scis_logger import *

class Param:
    pass

def main():
    p = Param()
    tasks = []
    queue = multiprocessing.Manager().Queue(-1)

    # Create path for config file based on platform
    if sys.platform in ["win32", "cygwin"]:
        p.path_config_dir = os.path.join(os.path.expanduser("~"), "Documents", "ScanImageSlicer")
    elif sys.platform == "darwin":
        p.path_config_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ScanImageSlicer")
    elif sys.platform == "linux":
        p.path_config_dir = os.path.join(os.path.expanduser("~"), ".config", "ScanImageSlicer")
    else:
        p.path_config_dir = os.path.join(os.path.expanduser("~"), ".ScanImageSlicer")

    p.log_path = os.path.join(p.path_config_dir, "last_run.log")

    # Create the default config file directory if needed
    if not os.path.exists(p.path_config_dir):
        os.mkdir(p.path_config_dir)

    listener = multiprocessing.Process(
        target=listener_process,
        args=(p, queue, listener_configurer)
    )

    listener.start()
    logger = queue_configurer(queue)

    # Collect the program params
    p = conf_parser_p(p)

    if p.cont:
        # Print the statusline
        print(create_statusline(p.name, p.version, p.description, p.path_config_file), flush=True)

        # Parse params
        p = parse_p(p)

    if p.cont:
        # Collect images from input path
        images = collect_images(p.input)

        if images:
            # List all compatible images from input directory
            if p.list_images:
                list_images(images)

            # Save a list of compatible images into output directory
            if p.list_file:
                save_imagelist_as_txt(p.output, p.project_name, images)

            # Add or remove tasks
            if any([p.add_all, p.add_id, p.add_new, p.add_old, p.add_random, p.remove_id]):
                tasks = handle_tasks(p, images)
                tasks = sorted(tasks, key=int)

            # List tasks
            if p.list_tasks:
                list_tasks(tasks, images)

            # Run tasks
            if any([p.test_mode, p.preview_mode, p.slice_mode, p.count_mode]):
                if tasks:
                    if confirm(p.skip_confirm, len(tasks), p.run_mode):
                        run_tasks(queue, p, tasks, images)

                        if p.slice_mode:
                            sequential_parallel_rename(p)
                else:
                    logger.info("Add some tasks before using action modes\n")
        else:
            logger.info(f"No compatible images found at: {p.input}\n")

    if p.run_mode:
        logger.info(f"View runlog at: {p.log_path}\n")

    # Stop queue logger
    queue.put_nowait(None)
    listener.join()

if __name__ == "__main__":
    sys.exit(main())