#!/usr/bin/env python3

import os
import logging
import configargparse
from .__init__ import __doc__
from .__version__ import __version__
from .config import config_raw
from .utils import create_statusline

def conf_parser_p(p):
    logger = logging.getLogger()
    p.cont = True
    p.version = __version__
    p.name = "Scan-Image-Slicer"
    p.description = __doc__

    # Create the default config file if it does not exist
    p.name_config_file = "v" + __version__.replace(".", "") + "_config.yaml"
    p.path_config_file = os.path.join(p.path_config_dir, p.name_config_file)

    if not os.path.isfile(p.path_config_file):
        with open(p.path_config_file, 'w') as outfile:
            try:
                outfile.writelines(config_raw)
                outfile.close()
            except OSError as e:
                logger.error(e)
                p.cont = False

        # Notify the user about default config file being created
        if os.path.isfile(p.path_config_file):
            logger.info("Created default config file:")
            logger.info(p.path_config_file + "\n")
        else:
            # Exit if unable to create config file
            logger.error(f"Could not create default config file: {p.path_config_file}")
            p.cont = False

    if not p.cont:
        return p

    # Setup confargparser
    description = create_statusline(p.name, p.version, p.description, p.path_config_file)

    parser = configargparse.ArgumentParser(
        default_config_files=[p.path_config_file],
        description=description,
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        formatter_class=configargparse.RawTextHelpFormatter,
        exit_on_error=False,
        allow_abbrev=True
    )

    parser.add_argument("-conf", "--config-file", metavar="FILE", is_config_file=True, help="Path to custom config file")
    parser.add_argument("-skip", "--skip-confirm", action="store_true", help="Skip the need to confirm action modes")
    parser.add_argument("-work", "--workers", metavar="NUM", type=int, help="Number of workers for multiprocessing")
    parser.add_argument("-name", "--project-name", metavar="TEXT", type=str, help="Project name")

    mode_group = parser.add_argument_group("Modes")
    mode_select_group = mode_group.add_mutually_exclusive_group()
    mode_select_group.add_argument("-test", "--test-mode", action="store_true", help="Enable test mode")
    mode_select_group.add_argument("-count", "--count-mode", action="store_true", help="Enable count mode")
    mode_select_group.add_argument("-preview", "--preview-mode", action="store_true", help="Enable preview mode")
    mode_select_group.add_argument("-slice", "--slice-mode", action="store_true", help="Enable slice mode")

    path_group = parser.add_argument_group("Paths")
    path_group.add_argument("-i", "--input", metavar="PATH", type=str, help="PATH to input directory")
    path_group.add_argument("-o", "--output", metavar="PATH", type=str, help="PATH to output directory")
    path_group.add_argument("-lutP", "--filter-lut-path", metavar="FILE", type=str, help="Path to lut .cube file")

    detect_group = parser.add_argument_group("Image slice detection")
    detect_group.add_argument("-white", "--white-threshold", metavar="NUM", type=int, help="White level between slices (1-255)")
    detect_group.add_argument("-min", "--minimum-size", metavar="NUM", type=float, help="Minimum slice size in %% (1-100)")
    detect_group.add_argument("-max", "--maximum-size", metavar="NUM", type=float, help="Maximum slice size in %% (1-100)")

    scale_group = parser.add_argument_group("Image slice scaling")
    scale_group.add_argument("-scaleF", "--scale-factor", metavar="NUM", type=float, help="Scale slice with factor value")
    scale_group.add_argument("-scaleW", "--scale-width", metavar="NUM", type=int, help="Scale slice to new width (no upscale)")
    scale_group.add_argument("-scaleH", "--scale-height", metavar="NUM", type=int, help="Scale slice to new height (no upscale)")

    filter_group = parser.add_argument_group("Image slice filters")
    filter_group.add_argument("-denoise", "--filter-denoise", metavar="NUM", type=int, help="Remove noise from slice (0-5)")
    filter_group.add_argument("-lutS", "--filter-lut-strength", metavar="NUM", type=float, help="Adjust LUT strength value (0.0-1.0)")
    filter_group.add_argument("-color", "--filter-color", metavar="NUM", type=float, help="Add or remove color from slice (0.0-2.0)")
    filter_group.add_argument("-contrast", "--filter-contrast", metavar="NUM", type=float, help="Add or remove contrast from slice (0.0-2.0)")
    filter_group.add_argument("-brightness", "--filter-brightness", metavar="NUM", type=float, help="Add or remove brightness from slice (0.0-2.0)")
    filter_group.add_argument("-sharpness", "--filter-sharpness", metavar="NUM", type=float, help="Add or remove sharpness from slice (0.0-2.0)")

    fixes_group = parser.add_argument_group("Image slice tweaks")
    fixes_group.add_argument("-pfix", "--perspective-fix", metavar="NUM", type=int, help="Fix slice tilt (0-89)")
    fixes_group.add_argument("-autoR", "--auto-rotate", metavar="TEXT", type=str, help="Rotate slice 90 deg CW/CCW if w < h")

    format_group = parser.add_argument_group("File format")
    format_group.add_argument("-save", "--save-format", metavar="TEXT", type=str, help="File format for slices")
    format_group.add_argument("-pngO", "--png-optimize", action="store_true", help="Try to optimize PNG file")
    format_group.add_argument("-pngC", "--png-compression", metavar="NUM", type=int, help="Try to compress PNG file (0-9)")
    format_group.add_argument("-jpegO", "--jpeg-optimize", action="store_true", help="Optimize JPEG file")
    format_group.add_argument("-jpegQ", "--jpeg-quality", metavar="NUM", type=int, help="Quality of JPEG file (0-100)")
    format_group.add_argument("-webpL", "--webp-lossless", action="store_true", help="Save WebP as lossless")
    format_group.add_argument("-webpM", "--webp-method", metavar="NUM", type=int, help="WebP saving speed/quality tradeoff (0-6)")
    format_group.add_argument("-webpQ", "--webp-quality", metavar="NUM", type=int, help="Quality of WebP file (1-100)")

    list_group = parser.add_argument_group("List information")
    list_group.add_argument("-listI", "--list-images", action="store_true", default=False, help="List all compatible scanned images")
    list_group.add_argument("-listF", "--list-file", action="store_true", default=False, help="Save list of compatible scanned images as text file")
    list_group.add_argument("-listT", "--list-tasks", action="store_true", default=False, help="List tasks")

    task_group = parser.add_argument_group("Task handling")
    task_group.add_argument("-addA", "--add-all", action="store_true", default=False, help="Add all compatible images")
    task_group.add_argument("-addID", "--add-id", nargs="+", metavar="NUM", type=int, help="Add compatible images by ID")
    task_group.add_argument("-addN", "--add-new", metavar="NUM", type=int, help="Add compatible images by modified timestamp (newest)")
    task_group.add_argument("-addO", "--add-old", metavar="NUM", type=int, help="Add compatible images by modified timestamp (oldest)")
    task_group.add_argument("-addR", "--add-random", metavar="NUM", type=int, help="Add compatible images randomly")
    task_group.add_argument("-remID", "--remove-id", nargs="+", metavar="NUM", type=int, help="Remove already added compatible images by ID")

    gui_group = parser.add_argument_group("GUI Settings")
    gui_group.add_argument("-fontS", "--font-scale", metavar="NUM", type=float, help="Font scale for GUI")
    gui_group.add_argument("-theme", "--theme", metavar="TEXT", type=str, help="Color theme for FreeSimpleGUI")
    gui_group.add_argument("-viewW", "--view-width", metavar="NUM", type=int, help="Max image width inside GUI")
    gui_group.add_argument("-viewH", "--view-height", metavar="NUM", type=int, help="Max image height inside GUI")

    unknown = None

    try:
        args, unknown = parser.parse_known_args(namespace=p)
    except configargparse.ArgumentError as e:
        logger.error(e)
        logger.info("Use -h or --help to view command-line arguments\n")
        p.cont = False
    except SystemExit:
        p.cont = False

    # Handle typos in arguments
    if unknown:
        for arg in unknown:
            logger.error(f"Unknown argument: {arg}")

        p.cont = False
        logger.info("Use -h or --help to view command-line arguments\n")

    # Handle custom config file
    if p.config_file:
        p.path_config_file = p.config_file

    if p.test_mode:
        p.run_mode = "test mode"
    elif p.preview_mode:
        p.run_mode = "preview mode"
    elif p.slice_mode:
        p.run_mode = "slice mode"
    elif p.count_mode:
        p.run_mode = "count mode"
    else:
        p.run_mode = ""

    return p