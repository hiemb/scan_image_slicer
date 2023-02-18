#!/usr/bin/env python3

config_raw = r'''# NOTE: on windows backslash needs to be escaped like so:
# C:\\my path\\to\\input

# Place your scanned images here
input: "/path/to/input/"

# Your sliced images will be created here
output: "/path/to/output/"

# Skip the confirmation
skip-confirm: False

# Match with your scanners natural white color (0-255)
white-threshold: 230

# Min size of the sliced image in % compared to scanned image area (0-100)
minimum-size: 3

# Use test mode (True/False)
test-mode: False

# Use preview mode (True/False)
preview-mode: False

# Use slice mode (True/False)
slice-mode: False

# Height of test/preview mode image
view-height: 800

# Scale using factor value
# 0 = disabled
scale-factor: 0

# Scale using width value in pixels
# 0 = disabled
scale-width: 0

# Scale using height value in pixels
# 0 = disabled
scale-height: 0

# Filter out scanner noise (0-5)
# 0 = disabled
filter-denoise: 1

# Add brightness (values over 1.0)
# Remove brightness (values under 1.0)
filter-brightness: 1.0

# Add contrast (values over 1.0)
# Remove contrast (values under 1.0)
filter-contrast: 1.0

# Add gamma correction (values over 1.0)
# Remove gamma correction  (values under 1.0)
filter-gamma: 1.0

# Add perspective fix (0-89)
# Maximum allowed tilt value of the sliced image in degrees
# 0 = disabled
perspective-fix: 0

# Save format (PNG|JPEG|WEBP)
save-format: "PNG"

# Level of PNG compression (0-9)
# 0 = disabled
png-compression: 3

# Level of JPEG quality (0-100)
jpeg-quality: 95

# Level of WEBP quality (1-101)
# 101 = lossless
webp-quality: 90

# Show infobar (True/False)
show-infobar: False

# Infobar font scale
font-scale: 1.0
'''
