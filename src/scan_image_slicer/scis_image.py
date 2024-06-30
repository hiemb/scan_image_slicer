#!/usr/bin/env python3

import os

from .utils import *

# Class for our scanned image object
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
    def count_slices(self, p):

        # Load image 
        img = pil_to_cv(pil_open_image(self.filepath))
        img_resized = cv_resize(img, w=min(900, img.shape[1]))

        # Loop contours and count slices
        for cnt in cv_detect_slices(cv_apply_wt(img_resized, p.white_threshold)):

            # Make sure the area is between min/max
            if cv_is_cnt_in_range(img_resized, cnt, p.minimum_size, p.maximum_size):
                self.slice_count += 1

        return self.slice_count

    # Slice images and save them to the output folder
    def save_slices(self, p):

        # Load image
        img = pil_to_cv(pil_open_image(self.filepath))
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
            log.error(f"Could not create directory: {save_path}")
            sys.exit()

        # Loop through cnts and save slices
        for cnt in cv_detect_slices(cv_apply_wt(img_resized, p.white_threshold)):

            # Make sure the area is larger than minimum area size
            if cv_is_cnt_in_range(img_resized, cnt, p.minimum_size, p.maximum_size):

                # Slice the image
                slice = cv_slice_img(img, img_resized, cnt, p.perspective_fix)

                # Resize the slice
                if p.scale_factor:
                    slice = cv_resize(slice, scale=p.scale_factor)

                if p.scale_width:
                    slice = cv_resize(slice, w=p.scale_width)

                if p.scale_height:
                    slice = cv_resize(slice, h=p.scale_height)

                # Auto-rotate the slice
                if p.auto_rotate in ["cw", "ccw"]:
                    slice = cv_auto_rotate(slice, p.auto_rotate)

                # Apply filters to slice
                slice = pil_filter_image(slice, filters)

                # Define temporary filename
                filename = "tmp_file_" + random_string(self.name, str(self.size), str(self.slice_count)) + savefile_suffix

                # Save the slice (make sure it does not exist)
                if not os.path.isfile(os.path.join(save_path, filename)):
                    slice.save(os.path.join(save_path, filename), **file_params)
                else:
                    log.error(f"File already exists: {filename}")
                    sys.exit()

                # Up the counter
                self.slice_count += 1

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

        # Return detected slices and faces
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
                slice = cv_slice_img(img, img_resized, cnt, p.perspective_fix)

                # Auto-rotate the slice
                if p.auto_rotate in ["cw", "ccw"]:
                    slice = cv_auto_rotate(slice, p.auto_rotate)

                # Append slice
                preview_images.append(slice)

        # Return array of slices
        return preview_images