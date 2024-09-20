#!/usr/bin/env python3

import os
from .utils import *
from .scis_logger import queue_configurer

class ScanImageSlicerImage:
    def __init__(self, id, path, name, format, mtime, size):
        self.id = id
        self.path = path
        self.name = name
        self.format = format
        self.mtime = mtime
        self.size = size
        self.size_mb = convert_bytes(size)
        self.filepath = os.path.join(path, name)
        self.slice_count = 0
        self.false_slice_count = 0

    # Count slices inside scanned image
    def count_slices(self, queue, p):
        logger = queue_configurer(queue)
        img = pil_open_image(self.filepath)

        if not img:
            return 0

        img = pil_to_cv(img)
        img_resized = cv_resize(img, w=min(900, img.shape[1]))

        for cnt in cv_detect_slices(cv_apply_wt(img_resized, p.white_threshold)):
            if cv_is_cnt_in_range(img_resized, cnt, p.minimum_size, p.maximum_size):
                self.slice_count += 1

        # Output warning if no images found
        if not self.slice_count:
            logger.warning(f"[ID:{self.id}] - ({self.name}) - No images found, skipping it..")
            return 0

        return self.slice_count

    # Slice images and save them to the output folder
    def save_slices(self, queue, p):
        logger = queue_configurer(queue)
        img = pil_open_image(self.filepath)

        if not img:
            return 0

        img = pil_to_cv(img)
        img_resized = cv_resize(img, w=min(900, img.shape[1]))

        # Define file format settings
        file_params = {}
        file_params.setdefault("format", p.save_format)

        if p.save_format == "png":
            savefile_suffix = ".png"
            file_params.setdefault("optimize", p.png_optimize)
            file_params.setdefault("compress_level", p.png_compression)
        if p.save_format == "jpeg":
            savefile_suffix = ".jpg"
            file_params.setdefault("optimize", p.jpeg_optimize)
            file_params.setdefault("quality", p.jpeg_quality)
        if p.save_format == "webp":
            savefile_suffix = ".webp"
            file_params.setdefault("lossless", p.webp_lossless)
            file_params.setdefault("method", p.webp_method)
            file_params.setdefault("quality", p.webp_quality)

        # Define filters
        filters = [
            p.filter_color,
            p.filter_contrast,
            p.filter_brightness,
            p.filter_sharpness,
            p.filter_denoise,
            p.filter_lut_strength,
            p.filter_lut_path
        ]

        # Define save path
        save_path = os.path.normpath(os.path.join(p.unique_path, os.path.relpath(self.path, p.input)))

        # Create save path
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)

        # Make sure path was created
        if not os.path.exists(save_path):
            logger.error(f"Could not create directory: {save_path}")
            return 0

        # Loop through cnts and save slices
        for cnt in cv_detect_slices(cv_apply_wt(img_resized, p.white_threshold)):

            # Make sure the area is between min/max sizes
            if cv_is_cnt_in_range(img_resized, cnt, p.minimum_size, p.maximum_size):

                # Slice the image
                sliced_img = cv_slice_img(img, img_resized, cnt, p.perspective_fix)

                # Resize the slice
                if p.scale_factor:
                    sliced_img = cv_resize(sliced_img, scale=p.scale_factor)

                if p.scale_width:
                    sliced_img = cv_resize(sliced_img, w=p.scale_width)

                if p.scale_height:
                    sliced_img = cv_resize(sliced_img, h=p.scale_height)

                # Auto-rotate the slice
                if p.auto_rotate in ["cw", "ccw"]:
                    sliced_img = cv_auto_rotate(sliced_img, p.auto_rotate)

                # Apply filters to slice
                sliced_img = pil_filter_image(sliced_img, filters)

                # Define temporary filename
                filename = "tmp_file_" + random_string(self.name, str(self.size), str(self.slice_count)) + savefile_suffix

                # Save the slice (make sure it does not exist)
                if not os.path.isfile(os.path.join(save_path, filename)):
                    sliced_img.save(os.path.join(save_path, filename), **file_params)
                else:
                    logger.error(f"File already exists: {filename}")
                    return 0

                # Up the counter
                self.slice_count += 1

        # Output warning if no images found
        if not self.slice_count:
            logger.warning(f"[ID:{self.id}] - ({self.name}) - No images found, skipping it..")
            return 0

        return self.slice_count

    # Create test image for GUI
    def create_test_image(self, p):
        # Load image
        img = pil_to_cv(pil_open_image(self.filepath))
        img_resized = cv_resize(img, w=900)

        # Define detection colors (BGR format)
        color_1 = (230, 97, 0)
        color_2 = (93, 58, 155)

        # Detect and draw slices
        for cnt in cv_detect_slices(cv_apply_wt(img_resized, p.white_threshold)):

            # Valid slice detected
            if cv_is_cnt_in_range(img_resized, cnt, p.minimum_size, p.maximum_size):
                self.slice_count += 1
                cv_draw_cnt(img_resized, cnt, color_1, 4)

            # Non-valid slice detected
            else:
                self.false_slice_count += 1
                cv_draw_cnt(img_resized, cnt, color_2, 4)

        # Return detected slices
        img_resized = cv_resize(img_resized, w=min(img_resized.shape[1], p.view_width))
        img_resized = cv_resize(img_resized, h=min(img_resized.shape[0], p.view_height))

        return cv_to_pil(img_resized)

    # Create array for preview images for the GUI
    def create_preview_images(self, p):
        # Array for slices
        preview_images = []

        # Load image
        img = pil_to_cv(pil_open_image(self.filepath))
        img_resized = cv_resize(img, w=900)

        for cnt in cv_detect_slices(cv_apply_wt(img_resized, p.white_threshold)):

            # Make sure the area is larger than minimum area size
            if cv_is_cnt_in_range(img_resized, cnt, p.minimum_size, p.maximum_size):

                # Slice the image
                sliced_img = cv_slice_img(img, img_resized, cnt, p.perspective_fix)

                # Auto-rotate the slice
                if p.auto_rotate in ["cw", "ccw"]:
                    sliced_img = cv_auto_rotate(sliced_img, p.auto_rotate)

                # Append slice
                preview_images.append(sliced_img)

        # Return array of slices
        return preview_images