Scan Image Slicer
---
Scan image slicer is a tool for detecting and separating images from a scanned image (or any image). The designed use case is for digitizing old photos, paper clippings and the like.

### Workflow
- create an empty input folder for the scanned images
- (optional) create a folder structure inside the input folder that is then used for naming and organizing the output images
- create an empty output folder (the folder structure will be mirrored here from the input folder)
- scan as many images as you like and place/organize them inside the input folder
- configure the tool using the config file and command line arguments
- slice and dice


### Installation using pip
```
pip install scan-image-slicer
```

### Requirements with pip install
- Python 3.6+
- pip

Using the tool
---
```
scan-image-slicer [options]
```
The easiest way to use the tool is to first edit the default config file and then override the settings when needed with command line arguments, which are explained below.
- **you need to run the tool once for the default config file to be created**
- location on Windows: Documents -> ScanImageSlicer -> config.yaml
- location on Linux: ~/.config/ScanImageSlicer/config.yaml
### Help
- `-h`, `--help` Display help

### Quickstart

- `-skip`, `--skip-confirm` skip the confirm start question

### Modes
Only one mode can be used at a time.

- `-test`, `--test-mode`

    Test mode shows you the scanned image with added colored rectangles that depict detected and ignored images.
    - blue rectangles are images that would be saved
    - purple rectangles are images that would be ignored

- `-pre`, `--preview-mode`

    Preview mode shows you the individual sliced images one by one but does not save them unless you press the S key. Toggle filters with the F key.

- `-slice`, `--slice-mode`

    Slice mode slices each scanned image on the task list and saves the slices to the output folder. Use it after you have finalized your settings.

### Paths
- `-i PATH`, `--input PATH` input folder for the scanned images

- `-o PATH`, `--output PATH` output folder for the sliced images

- `-c FILE`, `--config FILE` path to the custom config file

### Image detection & viewing
- `-white 0..255`, `--white-threshold 0..255` _(default is 230)_

    The white threshold value is used for image detection. Tweak it to match your scanner's background white color (the space between images). If possible, bump up your gamma value slightly in your scanning software for easier image detection.

- `-min N`, `--minimum-size N` _(default is 3)_

    Minimum size is used to discard too small images that are likely false positives. The value is in % of the total scanned image area.

- `-view N`, `--view-height N` _(default is 800)_

    The height of the image inside the image viewer (won't be upscaled).

### Scaling
- `-scaleF N`, `--scale-factor N` scale sliced image using a scale factor value

- `-scaleW N`, `--scale-width N` scale sliced image using a new width value

- `-scaleH N`, `--scale-height N` scale sliced image using a new height value

    Only one method of scaling can be used at a time. All methods preserve the aspect ratio. A value of zero means the option is disabled.

### Filters
- `-filtD 0..5`, `--filter-denoise 0..5` _(default is 1)_

    Remove scanner noise from the sliced image. Higher values take more time. A value of zero means the option is disabled.

- `-filtB N > 1.0`, `--filter-brightness N > 1.0` _(default is 1.0)_

    Add brightness to the sliced image with values above 1.0.

- `-filtC N > 1.0`, `--filter-contrast N > 1.0` _(default is 1.0)_

    Add contrast to the sliced image with values above 1.0.

- `-filtG N > 1.0`, `--filter-gamma N > 1.0` _(default is 1.0)_

    Add gamma correction to the sliced image with values above 1.0.

### File format
- `-save JPEG|PNG|WEBP`, `--save-format JPEG|PNG|WEBP` _(default is PNG)_
- `-png 0..9`, `--png-compression 0..9` _(default is 3)_

    Note: higher compression levels take more time per sliced image.

- `-jpeg 0..100`, `--jpeg-quality 0..100` _(default is 95)_

- `-webp 1..101`, `--webp-quality 1..101` _(default is 90)_

    Note: quality level of 101 is lossless.

### List information
- `-listS`, `--list-scans` list scanned images name and ID

- `-listF`, `--list-file` save scanned images name and ID as a text file at default config dir

- `-listT`, `--list-tasks` list added tasks

- `-listC`, `--list-cmds` list given commands

### Add/Remove images to/from the task list
- `-addA`, `--add-all` add all scanned images

- `-addID [ID ...]`, `--add-id [ID ...]` add scanned images using IDs eg. 1 2 3

- `-addN N`, `--add-new N` add N amount of newest scanned images by creation time (ctime)

- `-addO N`, `--add-old N` add N amount of oldest scanned images by creation time (ctime)

- `-addR N`, `--add-random N` add N amount of random scanned images

- `-remID [ID ...]`, `--remove-id [ID ...]` remove scanned images using IDs eg. 1 2 3