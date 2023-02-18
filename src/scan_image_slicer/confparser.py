#!/usr/bin/env python3

import os
import sys
import logging as log
import configargparse
from .config import config_raw

def conf_parser():

    if sys.platform in ["win32", "cygwin"]:
        path_config = os.path.join(os.path.expanduser("~"), "Documents", "ScanImageSlicer")
    elif sys.platform == "darwin":
        path_config = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ScanImageSlicer")
    elif sys.platform == "linux":
        path_config = os.path.join(os.path.expanduser("~"), ".config", "ScanImageSlicer")
    else:
        path_config = os.path.join(os.path.expanduser("~"), ".ScanImageSlicer")

    if not os.path.exists(path_config):
        os.mkdir(path_config)

    path_config_file = os.path.join(path_config, "config.yaml")
    if not os.path.isfile(path_config_file):
        with open(path_config_file, 'w') as outfile:
            try:
                outfile.writelines(config_raw)
                outfile.close()
            except OSError as e:
                sys.exit(e)

        if os.path.isfile(path_config_file):
            log.info("Created default config file: %s", path_config_file)

    line = ""
    n = "\n"
    title = "  Scan Image Slicer: Detect and slice images from a scanned image (or any image)  "
    for c in title:
        line += "-"
    info = f"  Config file at: {path_config_file}"

    description = line + n + n + title + n + info + n + n + line

    parser = configargparse.ArgumentParser(
        default_config_files=[path_config_file],
        description=description,
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        formatter_class=configargparse.RawTextHelpFormatter,
        allow_abbrev=False)

    parser.add_argument("-c", "--config_file", metavar="FILE", is_config_file=True, help="path to custom config file")

    parser.add_argument("-skip", "--skip-confirm", action="store_true", help="skip the confirm start question")

    mode_group = parser.add_argument_group("settings|modes")
    mode_select_group = mode_group.add_mutually_exclusive_group()

    mode_select_group.add_argument("-test", "--test-mode", action="store_true", help="enable test mode")

    mode_select_group.add_argument("-pre", "--preview-mode", action="store_true", help="enable preview mode")

    mode_select_group.add_argument("-slice", "--slice-mode", action="store_true", help="enable slice mode")

    path_group = parser.add_argument_group("settings|paths")

    path_group.add_argument("-i", "--input", metavar="PATH", type=str, help="input folder for the scanned images")

    path_group.add_argument("-o", "--output", metavar="PATH", type=str, help="output folder for the sliced images")

    detect_group = parser.add_argument_group("settings|image detection")

    detect_group.add_argument("-white", "--white-threshold", metavar="0..255", type=int, help="a value used for image detection")

    detect_group.add_argument("-min", "--minimum-size", metavar="0..100", type=int, help="a value used for discarding too small (false) images")

    detect_group.add_argument("-view", "--view-height", metavar="N", type=int, help="the height of the image inside the image viewer")

    scale_group = parser.add_argument_group("settings|scaling")

    scale_group.add_argument("-scaleF", "--scale-factor", metavar="F", type=float, help="scale sliced image using a scale factor value")

    scale_group.add_argument("-scaleW", "--scale-width", metavar="N", type=int, help="scale sliced image using a new width value")

    scale_group.add_argument("-scaleH", "--scale-height", metavar="N", type=int, help="scale sliced image using a new height value")

    filter_group = parser.add_argument_group("settings|filters & fixes")

    filter_group.add_argument("-filtD", "--filter-denoise", metavar="0..5", type=int, help="remove scanner noise from the sliced image")

    filter_group.add_argument("-filtB", "--filter-brightness", metavar="N > 1.0", type=float, help="add brightness to the sliced image")

    filter_group.add_argument("-filtC", "--filter-contrast", metavar="N > 1.0", type=float, help="add contrast to the sliced image")

    filter_group.add_argument("-filtG", "--filter-gamma", metavar="N > 1.0", type=float, help="add gamma correction to the sliced image")

    filter_group.add_argument("-pfix", "--perspective-fix", metavar="0..89", type=int, help="add perspective fix to the sliced image")

    io_group = parser.add_argument_group("settings|file format")

    io_group.add_argument("-save", "--save-format", metavar="JPEG|PNG|WEBP", type=str, help="the file format of the sliced image")

    io_group.add_argument("-png", "--png-compression", metavar="0..9", type=int, help="PNG compression level")

    io_group.add_argument("-jpeg", "--jpeg-quality", metavar="0..100", type=int, help="JPEG quality level")

    io_group.add_argument("-webp", "--webp-quality", metavar="1..101", type=int, help="WEBP quality level")

    list_group = parser.add_argument_group("commands|lists")

    list_group.add_argument("-listS", "--list-scans", action="store_true", default=False, help="list scanned images name and ID")

    list_group.add_argument("-listF", "--list-file", action="store_true", default=False, help="save scanned images name and ID as a text file")

    list_group.add_argument("-listT", "--list-tasks", action="store_true", default=False, help="list added tasks")

    list_group.add_argument("-listC", "--list-cmds", action="store_true", default=False, help="list given commands")

    task_group = parser.add_argument_group("commands|tasks")

    task_group.add_argument("-addA", "--add-all", action="store_true", default=False, help="add all scanned images")

    task_group.add_argument("-addID", "--add-id", nargs="+", metavar="ID", type=int, help="add scanned images using IDs eg. 1 2 3")

    task_group.add_argument("-addN", "--add-new", metavar="N", type=int, help="add N amount of newest scanned images by creation time (ctime)")

    task_group.add_argument("-addO", "--add-old", metavar="N", type=int, help="add N amount of oldest scanned images by creation time (ctime)")

    task_group.add_argument("-addR", "--add-random", metavar="N", type=int, help="add N amount of random scanned images")

    task_group.add_argument("-remID", "--remove-id", nargs="+", metavar="ID", type=int, help="remove scanned images using IDs eg. 1 2 3")

    infobar_group = parser.add_argument_group("infobar")

    infobar_group.add_argument("-info", "--show-infobar", action="store_true", help="show the infobar")

    infobar_group.add_argument("-fontS", "--font-scale", metavar="N", type=float, help="change infobar font scale")

    args = parser.parse_args()

    settings = {}
    errors = []
    inpath = os.path.normpath(os.path.expanduser(args.input))
    outpath = os.path.normpath(os.path.expanduser(args.output))

    if args.skip_confirm:
        settings["skip_confirm"] = True
    else:
        settings["skip_confirm"] = False

    if os.path.exists(inpath) and not os.path.isfile(inpath):
        if inpath == "":
            errors.append("Use a valid input path")
        else:
            settings["input"] = inpath
    else:
        errors.append(f"Input folder does not exist: {inpath}")

    if os.path.exists(outpath) and not os.path.isfile(outpath):
        if outpath == "":
            errors.append("Use a valid output path")
        else:
            settings["output"] = outpath
    else:
        errors.append(f"Output folder does not exist: {outpath}")

    if args.white_threshold in range(0, 256):
        settings["white_threshold"] = args.white_threshold
    else:
        errors.append("Value of white_threshold should be between 0 and 255")

    if args.minimum_size in range(0, 101):
        settings["minimum_size"] = args.minimum_size
    else:
        errors.append("Value of minimum_size should be between 0 and 100")

    if args.test_mode:
        settings["test_mode"] = args.test_mode
    else:
        settings["test_mode"] = False

    if args.preview_mode:
        settings["preview_mode"] = args.preview_mode
    else:
        settings["preview_mode"] = False

    if args.slice_mode:
        settings["slice_mode"] = args.slice_mode
    else:
        settings["slice_mode"] = False

    if args.view_height > 0:
        settings["view_height"] = args.view_height
    else:
        errors.append("Value of view_height must be positive int value")

    if args.scale_factor != 0:
        settings["scale_factor"] = args.scale_factor
    else:
        settings["scale_factor"] = 0

    if args.scale_width != 0:
        settings["scale_width"] = args.scale_width
    else:
        settings["scale_width"] = 0

    if args.scale_height != 0:
        settings["scale_height"] = args.scale_height
    else:
        settings["scale_height"] = 0

    if args.filter_denoise in range(0, 6):
        settings["filter_denoise"] = args.filter_denoise
    else:
        errors.append("Value of filter_denoise should be between 0 and 5")

    if args.filter_brightness != 1.0:
        settings["filter_brightness"] = args.filter_brightness
    else:
        settings["filter_brightness"] = 1.0

    if args.filter_contrast != 1.0:
        settings["filter_contrast"] = args.filter_contrast
    else:
        settings["filter_contrast"] = 1.0

    if args.filter_gamma != 1.0:
        settings["filter_gamma"] = args.filter_gamma
    else:
        settings["filter_gamma"] = 1.0

    if args.perspective_fix in range(0, 90):
        settings["perspective_fix"] = args.perspective_fix
    else:
        errors.append("Value of perspective_fix should be between 0 and 89")

    if args.save_format in ["JPEG", "PNG", "WEBP"]:
        settings["save_format"] = args.save_format
    else:
        errors.append("Save format should be one of JPEG, PNG or WEBP")

    if args.png_compression in range(0, 10):
        settings["png_compression"] = args.png_compression
    else:
        errors.append("Value of png_compression should be between 0 and 9")

    if args.jpeg_quality in range(0, 101):
        settings["jpeg_quality"] = args.jpeg_quality
    else:
        errors.append("Value of jpeg_quality should be between 0 and 100")

    if args.webp_quality in range(1, 102):
        settings["webp_quality"] = args.webp_quality
    else:
        errors.append("Value of webp_quality should be between 1 and 101")

    infobar = {}

    if args.font_scale != 1.0:
        infobar["font_scale"] = args.font_scale
    else:
        infobar["font_scale"] = 1.0

    if args.show_infobar:
        infobar["show_infobar"] = True
    else:
        infobar["show_infobar"] = False

    commands = {}

    if args.list_scans:
        commands["list_scans"] = True
    else:
        commands["list_scans"] = False

    if args.list_file:
        commands["list_file"] = True
    else:
        commands["list_file"] = False

    if args.list_tasks:
        commands["list_tasks"] = True
    else:
        commands["list_tasks"] = False

    if args.list_cmds:
        commands["list_cmds"] = True
    else:
        commands["list_cmds"] = False

    if args.add_all:
        commands["add_all"] = True
    else:
        commands["add_all"] = False

    if type(args.add_id) is list:
        commands["add_id"] = args.add_id
    else:
        commands["add_id"] = False

    if type(args.add_new) is int:
        commands["add_new"] = args.add_new
    else:
        commands["add_new"] = False

    if type(args.add_old) is int:
        commands["add_old"] = args.add_old
    else:
        commands["add_old"] = False

    if type(args.add_random) is int:
        commands["add_random"] = args.add_random
    else:
        commands["add_random"] = False

    if type(args.remove_id) is list:
        commands["remove_id"] = args.remove_id
    else:
        commands["remove_id"] = False

    if errors:
        print()
        log.info("Please fix the following errors:")
        for error in errors:
            log.error(error)
        sys.exit()

    return [settings, commands, path_config, infobar]