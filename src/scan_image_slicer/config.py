#!/usr/bin/env python3

config_raw = r'''# NOTE: on windows backslash needs to be escaped like so:
# input: "C:\\my path\\to\\input"
# output: "C:\\my path\\to\\output"

# Project name
# This is used to create an unique path for your project inside output directory
# Each slice run creates a new unique path (project_name+timestamp)
# Example: output/MyProject_2024_06_22_17_48_45
project-name: "MyProject"

# Path to input directory
# Create subfolders inside this directory to organize your scans
# Each subfolder adds a layer to the naming scheme
# Example: input/Birthdays/2010/Michael -> Birthdays_2010_Michael_1.jpg, Birthdays_2010_Michael_2.jpg ...
# Each subfolder is also mirrored in the output directory for convenience
input: "/path/to/input/"

# Path to output directory
# Your slices will be placed here under unique directory
output: "/path/to/output/"

# Number of Worker threads for multiprocessing
# Use half of physical cpu cores as a safe default value
threads: 2

# Skip the need to confirm action modes (True/False)
skip-confirm: False

# Detection sensitivity (0-255)
# Try to match this with the color between scanned items (in grayscale)
white-threshold: 230

# Minimum size of the sliced image in % compared to scanned image (0-100)
minimum-size: 1.00

# Maximum size of the sliced image in % compared to scanned image (0-100)
maximum-size: 40.00

# Enable count mode (True/False)
count-mode: False

# Enable test mode (True/False)
test-mode: False

# Enable preview mode (True/False)
preview-mode: False

# Enable slice mode (True/False)
slice-mode: False

# Scale using factor value (e.g: 0.5, 1.5, 50.0)
# 0 = disabled
scale-factor: 0

# Scale using new width value in pixels
# Image will not be upscaled
# Keeps aspect ratio
# 0 = disabled
scale-width: 0

# Scale using new height value in pixels
# Image will not be upscaled
# Keeps aspect ratio
# 0 = disabled
scale-height: 0

# Remove noise from slice (0-5)
# Anything over 3 is slow
# 0 = disabled
filter-denoise: 1

# Add color (values over 1.0)
# Remove color (values under 1.0)
filter-color: 1.0

# Add contrast (values over 1.0)
# Remove contrast (values under 1.0)
filter-contrast: 1.0

# Add brightness (values over 1.0)
# Remove brightness (values under 1.0)
filter-brightness: 1.0

# Add sharpness (values over 1.0)
# Remove sharpness (values under 1.0)
filter-sharpness: 1.0

# Adjust LUT strength value (0.0 - 1.0)
# 0.0 returns the original image while 1.0 returns the LUT image
filter-lut-strength: 1.0

# Path to the LUT file
# Has to be in cube format (.cube)
# "" = disabled
filter-lut-path: ""

# Use perspective fix (0-89)
# Maximum allowed tilt value of the sliced image in degrees
# 0 = disabled
perspective-fix: 0

# Use auto-rotate (disable/cw/ccw)
# Rotates slices automatically 90 degrees CW or CCW
# if the slice width is smaller than it's height
auto-rotate: "disable"

# Save format (png|jpeg|webp)
save-format: "jpeg"

# Optimize PNG files (True/False)
png-optimize: True

# Level of PNG compression (0-9)
# 0 = disabled
png-compression: 3

# Optimize JPEG files (True/False)
jpeg-optimize: True

# Level of JPEG quality (0-100)
jpeg-quality: 95

# Save WEBP as lossless image (True/False)
webp-lossless: False

# WEBP saving file quality/speed tradeoff (0-6)
# 0=fast, 6=slower-better
webp-method: 4

# Level of WEBP quality (0-100)
# Note: if you enable lossless webp then this value becomes the compression rate
webp-quality: 90

# GUI font scale
font-scale: 1.0

# GUI theme
# Check FreeSimpleGUI github page for theme names, some examples:
# Light: LightGray1, Material2, SystemDefault
# Dark: Black, Dark, DarkGrey5
theme: "DarkBlack"

# Max image width inside GUI
view-width: 960

# Max image height inside GUI
view-height: 800

'''