#!/usr/bin/env python3

import os
import sys
import timeit
import logging as log
import FreeSimpleGUI as sg

from PIL import Image
from .utils import *
from .gui_widgets import *


# Popup info message
def popup_msg(msg):
    sg.popup(f"{msg}", auto_close=True, auto_close_duration=3, no_titlebar=True)


# Show preview of sliced image
def show_preview_gui(p, scis_img):

    # Setup GUI
    sg.theme(p.theme)
    window_title = "Scan-Image-Slicer - Preview mode"
    layout = []
    widgets = []
    preview_images = scis_img.create_preview_images(p)
    image_count = len(preview_images)
    image_index = 0
    applied_filters = [
        p.filter_color,
        p.filter_contrast,
        p.filter_brightness,
        p.filter_sharpness,
        p.filter_denoise,
        p.filter_lut_strength,
        p.filter_lut_path
    ]
    unapplied_filters = []
    filter_time = 0

    # Create menu strings
    def str_slice_size():
        img = preview_images[image_index]
        return f"Size: {img.shape[0]}x{img.shape[1]} px"

    def str_slice_n():
        img = preview_images[image_index]
        return f"Slice {image_index+1} of {image_count}"

    def str_filter_time():
        return f"Filter time: {filter_time} seconds"

    # Use LUT?
    if p.filter_lut_path:
        use_lut = True
    else:
        use_lut = False

    # Info section
    widgets.append([Header(p, scis_img.name)])
    widgets.append([Text(p, str_slice_n(), key="slice_n")])
    widgets.append([Text(p, str_slice_size(), key="slice_size")])
    widgets.append([Text(p, str_filter_time(), key="filter_time", visible=False)])
    widgets.append([sg.HorizontalSeparator(p=(0, 5))])

    # Filters section
    widgets.append([Header(p, "Denoise:")])
    widgets.append([Slider(p, "int", (0, 5), p.filter_denoise, key="filter_denoise")])
    widgets.append([Header(p, "LUT:", visible=use_lut)])
    widgets.append([Slider(p, "float", (0.0, 1.0), p.filter_lut_strength, key="filter_lut_strength", visible=use_lut)])
    widgets.append([Header(p, "Color:")])
    widgets.append([Slider(p, "float", (0.0, 2.0), p.filter_color, key="filter_color")])
    widgets.append([Header(p, "Contrast:")])
    widgets.append([Slider(p, "float", (0.0, 2.0), p.filter_contrast, key="filter_contrast")])
    widgets.append([Header(p, "Brightness:")])
    widgets.append([Slider(p, "float", (0.0, 2.0), p.filter_brightness, key="filter_brightness")])
    widgets.append([Header(p, "Sharpness:")])
    widgets.append([Slider(p, "float", (0.0, 2.0), p.filter_sharpness, key="filter_sharpness")])
    widgets.append([Text(p, "")])
    widgets.append([Button(p, "Apply filters", key="apply_filters", disabled=True), Button(p, "Save filters", key="save_filters")])
    widgets.append([sg.HorizontalSeparator(p=(0, 5))])

    # Actions section
    widgets.append([Header(p, "Actions:")])
    widgets.append([Button(p, "Save image"), Button(p, "Open image")])

    if image_count > 1:
        widgets.append([Button(p, "Last slice", disabled=True), Button(p, "Next slice")])

    widgets.append([Button(p, "Abort"), Button(p, "Next image")])

    # Apply filters on sliced image
    filter_image = pil_filter_image(preview_images[image_index], applied_filters)

    # Resize filtered image to fit GUI
    filter_image = pil_resize(filter_image, h=min(filter_image.height, p.view_height))
    filter_image = pil_resize(filter_image, w=min(filter_image.width, p.view_width))

    layout.append([Image(pil_to_buffer(filter_image), key="preview_image"), Column(widgets)])

    # Create the GUI window
    window = Window(window_title, layout)

    # Run the GUI
    while True:
        event, values = window.read()

        # Abort run
        if event in [sg.WIN_CLOSED, "Abort"]:
            log.info("Aborting")
            window.close()
            sys.exit()

        # Next image
        if event == "Next image":
            break

        # Update filter values on slider events
        if event in ["filter_color", "filter_contrast", "filter_brightness", "filter_sharpness", "filter_denoise", "filter_lut_strength"]:
            unapplied_filters = [
                values["filter_color"],
                values["filter_contrast"],
                values["filter_brightness"],
                values["filter_sharpness"],
                values["filter_denoise"],
                values["filter_lut_strength"],
                p.filter_lut_path
            ]

            if unapplied_filters != applied_filters:
                window["apply_filters"].update(disabled=False)
            else:
                window["apply_filters"].update(disabled=True)

        # Apply filters to image
        if event == "apply_filters":

            p.filter_color = values["filter_color"]
            p.filter_contrast = values["filter_contrast"]
            p.filter_brightness = values["filter_brightness"]
            p.filter_sharpness = values["filter_sharpness"]
            p.filter_denoise = int(values["filter_denoise"])
            p.filter_lut_strength = values["filter_lut_strength"]

            # Time filters
            start = timeit.default_timer()
            filter_image = pil_filter_image(preview_images[image_index], unapplied_filters)
            stop = timeit.default_timer()
            filter_time = round(stop - start, 4)

            # Resize filtered image to fit GUI
            filter_image = pil_resize(filter_image, h=min(filter_image.height, p.view_height))
            filter_image = pil_resize(filter_image, w=min(filter_image.width, p.view_width))

            window["preview_image"].update(pil_to_buffer(filter_image))

            window["apply_filters"].update(disabled=True)
            window["filter_time"].update(str_filter_time(), visible=True)
            applied_filters = unapplied_filters

        # Save filter values to config file
        if event == "save_filters":
            yaml_change_value(p.path_config_file, "filter-color", values["filter_color"])
            yaml_change_value(p.path_config_file, "filter-contrast", values["filter_contrast"])
            yaml_change_value(p.path_config_file, "filter-brightness", values["filter_brightness"])
            yaml_change_value(p.path_config_file, "filter-sharpness", values["filter_sharpness"])
            yaml_change_value(p.path_config_file, "filter-denoise", int(values["filter_denoise"]))
            yaml_change_value(p.path_config_file, "filter-lut-strength", values["filter_lut_strength"])
            popup_msg(f"New filter values saved to:\n {p.path_config_file}")

        # Open image with OS default handler
        if event == "Open image":
            img = pil_filter_image(preview_images[image_index], applied_filters)
            img.show()

        # Save image to desired location
        if event == "Save image":

            # Get file path where to save image
            filepath = sg.popup_get_file(
                "Save image",
                default_path=os.path.join(
                    p.output,
                    f"slice_{image_index+1}_from_" + scis_img.name
                ),
                save_as=True,
            )

            # Try to save the file
            if filepath:
                img = pil_filter_image(preview_images[image_index], applied_filters)
                img.save(filepath)
                popup_msg(f"Saved image to:\n {filepath}")

        # Load next slice
        if event == "Next slice":
            image_index += 1

            # Handle navigation
            if image_index in range(0, image_count-1):
                window["Next slice"].update(disabled=False)
            else:
                window["Next slice"].update(disabled=True)

            if image_index == 1:
                window["Last slice"].update(disabled=False)

        # Load last image
        if event == "Last slice":
            image_index -= 1

            # Handle navigation
            if image_index in range(1, image_count):
                window["Last slice"].update(disabled=False)
            else:
                window["Last slice"].update(disabled=True)

            if image_index == image_count-2:
                window["Next slice"].update(disabled=False)

        if event in ["Next slice", "Last slice"]:

            if window["apply_filters"].Disabled:
                applied_filters = [
                    p.filter_color,
                    p.filter_contrast,
                    p.filter_brightness,
                    p.filter_sharpness,
                    p.filter_denoise,
                    p.filter_lut_strength,
                    p.filter_lut_path
                ]

            # Update data
            window["slice_n"].update(str_slice_n())
            window["slice_size"].update(str_slice_size())

            # Time filter
            start = timeit.default_timer()
            filter_image = pil_filter_image(preview_images[image_index], applied_filters)
            stop = timeit.default_timer()
            filter_time = round(stop - start, 4)

            # Resize filtered image to fit GUI
            filter_image = pil_resize(filter_image, h=min(filter_image.height, p.view_height))
            filter_image = pil_resize(filter_image, w=min(filter_image.width, p.view_width))

            window["preview_image"].update(pil_to_buffer(filter_image))
            window["filter_time"].update(str_filter_time(), visible=True)

    window.close()
    return image_count


# Show test image inside GUI
def show_test_gui(p, scis_img):

    # Setup GUI
    sg.theme(p.theme)
    window_title = "Scan-Image-Slicer - Test mode"
    layout = []
    widgets = []
    test_image = scis_img.create_test_image(p)

    # Create info strings
    def update_detection_count_txt(count):
        return f"Detected images (blue): {count}"

    def update_ignored_count_txt(count):
        return f"Detected false images (red): {count}"

    # Create layout for GUI widgets
    widgets.append([Header(p, scis_img.name)])
    widgets.append([Text(p, update_detection_count_txt(scis_img.slice_count), key="slice_count")])
    widgets.append([Text(p, update_ignored_count_txt(scis_img.false_slice_count), key="false_slice_count")])
    widgets.append([sg.HorizontalSeparator(p=(0, 5))])
    widgets.append([Header(p, "Image detection sensitivity:")])
    widgets.append([Slider(p, "int", (0, 255), p.white_threshold, key="white_threshold")])
    widgets.append([Text(p, "Hint: try values between 220-250")])
    widgets.append([Header(p, "Minimum slice size in %:")])
    widgets.append([Slider(p, "float", (0.01, 99.99), p.minimum_size, resolution=0.01, key="minimum_size")])
    widgets.append([Header(p, "Maximum slice size in %:")])
    widgets.append([Slider(p, "float", (0.01, 99.99), p.maximum_size, resolution=0.01, key="maximum_size")])
    widgets.append([sg.Text("", p=(0, 2))])
    widgets.append([Button(p, "Detect images", disabled=False), Button(p, "Save values")])
    widgets.append([sg.HorizontalSeparator(p=(0, 5))])
    widgets.append([Header(p, "Actions:")])
    widgets.append([Button(p, "Save image"), Button(p, "Open image")])
    widgets.append([Button(p, "Abort"), Button(p, "Next image")])

    # Create layout for GUI window
    layout.append([Image(pil_to_buffer(test_image), key="test_image"), Column(widgets)])

    # Create the GUI window
    window = Window(window_title, layout)

    # Run the GUI
    while True:
        event, values = window.read()

        # Abort run.
        if event in [sg.WIN_CLOSED, "Abort"]:
            log.info("Aborting")
            window.close()
            sys.exit()

        # Load next image
        if event == "Next image":
            break

        # Open image with OS default handler
        if event == "Open image":
            test_image.show()

        # Save image to desired location
        if event == "Save image":

            # Get file path where to save image
            filepath = sg.popup_get_file("Save image", default_path=os.path.join(p.output, scis_img.name), save_as=True)

            # Try to save the file.
            if filepath:
                test_image.save(filepath)
                popup_msg(f"Saved image to:\n {filepath}")

        # Save values.
        if event == "Save values":
            yaml_change_value(p.path_config_file, "white-threshold", int(values["white_threshold"]))
            yaml_change_value(p.path_config_file, "minimum-size", values["minimum_size"])
            yaml_change_value(p.path_config_file, "maximum-size", values["maximum_size"])
            p.white_threshold = values["white_threshold"]
            p.minimum_size = values["minimum_size"]
            p.maximum_size = values["maximum_size"]
            popup_msg(f"Values saved to:\n {p.path_config_file}")

        # Detect images
        if event == "Detect images":
            scis_img.slice_count = 0
            scis_img.false_slice_count = 0
            p.white_threshold = values["white_threshold"]
            p.minimum_size = values["minimum_size"]
            p.maximum_size = values["maximum_size"]
            test_image = scis_img.create_test_image(p)
            window["test_image"].update(pil_to_buffer(test_image))
            window["slice_count"].update(update_detection_count_txt(scis_img.slice_count))
            window["false_slice_count"].update(update_ignored_count_txt(scis_img.false_slice_count))

    # Close the window and return the slice counter
    window.close()
    return scis_img.slice_count