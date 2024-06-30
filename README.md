Scan-Image-Slicer (SCIS)
---
**Scan-Image-Slicer (SCIS)** is a versatile tool designed for detecting and slicing images from scanned documents or photographs. Whether you're digitizing old photos, processing paper clippings, or working with large batches of images, SCIS offers efficient and customizable solutions to streamline your workflow.

### Modes:
SCIS offers four distinct modes of operation, each tailored to specific tasks and requirements:

#### 1. Count Mode
- Use this mode to count the slices within images without performing any further processing. Ideal for estimating the space needed for the image slices. Supports multicore processing for faster performance.

#### 2. Test Mode
- Enables a graphical user interface (GUI) for fine-tuning image detection parameters. Useful for adjusting detection sensitivity and minimum/maximum slice size to achieve optimal results.

#### 3. Preview Mode
- Provides a GUI for previewing sliced images and adjusting filtering options. Allows users to customize filters to their preferences before slicing.

#### 4. Slice Mode
- Initiates the slicing process, creating individual images from slices and saving them to the designated output folder. Supports multicore processing  for efficient batch slicing.

Suggested Workflow
---

#### 1. Scan items (photos, paper clippings etc..):
- Begin by scanning your items, preferably in large batches to streamline the process. Leave some space between the items for easier detection. Save the scans in one of the following file formats: **JPEG, PNG, WEBP, BMP or TIFF**.
- Name the scans however you like as **SCIS does not re-use the file names**.
- Take advantage of the auto-rotate option (**--auto-rotate**), which automatically rotates slices 90 degrees clockwise/counter-clockwise if the slice width is smaller than its height.
- Organize your scans into folders within the designated input directory. For example, if you have wedding photos, create a folder named "Weddings" inside the input folder and place your scans there.
- **The naming of sliced images is derived from the folder structure within the input directory**. Each subfolder adds a layer to the naming scheme. Alternatively, you can place scanned images directly into the input folder, and they will be named generically.

#### 2. Install SCIS:
- Install latest Python with TkInter support.
- Install SCIS using pip (or pipx).

        pip install scan-image-slicer
- **Run the app once to create the default configuration file.**

- Address missing input/output paths as prompted by editing the default config file.

#### 3. Test Mode:
- Use the test mode to fine-tune image detection. Remember to **save** your detection parameters for optimal results.

        scan-image-slicer --test-mode --add-random 5

#### 4. Preview Mode:
- Utilize the preview mode to preview sliced images and adjust filtering options according to your preferences.

        scan-image-slicer --preview-mode --add-random 5

#### 5. Slice Mode:
- Initiate the slice mode to create images from slices and save them to the designated output folder.

        scan-image-slicer --slice-mode --add-all

#### 6. Additional Information:
- For more details on available options, refer to the configuration file or run the help command.

        scan-image-slicer --help

Examples:
---

#### Basic Usage:
- List all compatible images in the input folder showing image ID, name and size:

        scan-image-slicer --list-images

- Test image detection by counting the slices from the first (ID = 0) image:

        scan-image-slicer --count-mode --add-id 0 --white-threshold 235 --minimum-size 5 --maximum-size 40

- Slice 5 randomly picked scanned images and save the slices in WebP format:

        scan-image-slicer --slice-mode --add-random 5 --save-format webp --threads 4

Further info:
---

List of command-line arguments with explanation on each [here](./COMMANDS.md).
