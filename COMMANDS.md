Scan-Image-Slicer (SCIS) command-line arguments
---
### General:
Short|Long|Input|Explanation
:-|:-|:-|:-
-h|--help|-|Show help
-conf|--config-file |PATH|Path to custom config file
-skip|--skip-confirm|-|Skip the need to confirm action modes
-t|--threads|NUM|Number of worker threads for multiprocessing
-name|--project-name|TEXT|Project name
- Project name is used to create unique path inside output directory (project_name+timestamp).
- Every slice run creates a new unique directory.
---
### Modes:
Short|Long|Explanation
:-|:-|:-
-test|--test-mode|Enable test mode
-count|--count-mode|Enable count mode
-preview|--preview-mode|Enable preview mode
-slice|--slice-mode|Enable slice mode
---
### Paths:
Short|Long|Input|Explanation
:-|:-|:-|:-
-i|--input|PATH|Path to input directory
-o|--output|PATH|Path to output directory
-lutP|--filter-lut-path|PATH|Path to LUT .cube file
---
### Image slice detection:
Short|Long|Input|Range|Explanation
:-|:-|:-|:-|:-
-white|--white-threshold|NUM|0-255|White level between slices
-min|--minimum-size|NUM|0-100|Minimum slice size in %
-max|--maximum-size|NUM|0-100|Maximum slice size in %
- Min/max values are in percent of the entire scanned image
---
### Image slice scaling:
Short|Long|Input|Explanation
:-|:-|:-|:-
-scaleF|--scale-factor|NUM|Scale slice with factor value
-scaleW|--scale-width|NUM|Scale slice to new width value
-scaleH|--scale-height|NUM|Scale slice to new height value
- All scaling options keep the aspect ratio.
- Scaling is applied in top to bottom order as they appear above.
---
### Image slice filters:
Short|Long|Input|Range|Explanation
:-|:-|:-|:-|:-
-denoise|--filter-denoise|NUM|0-5|Remove noise from slice
-lutS|--filter-lut-strength|NUM|0.0 - 1.0|Adjust LUT strength value
-color|--filter-color|NUM|0.0 - 2.0|Add or remove color from slice
-contrast|--filter-contrast|NUM|0.0 - 2.0|Add or remove contrast from slice
-brightness|--filter-brightness|NUM|0.0 - 2.0|Add or remove brightness from slice
-sharpness|--filter-sharpness|NUM|0.0 - 2.0|Add or remove sharpness from slice
- Filters are applied in top to bottom order as they appear above.
---
### Image slice tweaks:
Short|Long|Input|Range|Explanation
:-|:-|:-|:-|:-
-pfix|--perspective-fix|NUM|0-89|Fix slice tilt
-autoR|--auto-rotate|TEXT|disable, cw, ccw|Rotate slice 90 deg CW/CCW if w < h
- Fixing a very large tilt might result in visible artifacts on the edges of the sliced image.
---
### Image slice format:
Short|Long|Input|Range|Explanation
:-|:-|:-|:-|:-
-save|--save-format|TEXT|jpeg, png, webp|File format for slices
-pngO|--png-optimize|-|-|Try to optimize PNG file
-pngC|--png-compression|NUM|0-9|Try to compress PNG file
-jpegO|--jpeg-optimize|-|-|Optimize JPEG file
-jpegQ|--jpeg-quality|NUM|0-100|Quality of JPEG file
-webpL|--webp-lossless|-|-|Save WebP as lossless
-webpM|--webp-method|NUM|0-6|WebP saving quality/speed tradeoff
-webpQ|--webp-quality|NUM|1-100|Quality of WebP file
- WebP quality becomes the compression rate if WebP lossless is enabled.
- PNG is always lossless thus the compression rate might not work as expected.
---
### List information:
Short|Long|Explanation
:-|:-|:-
-listI|--list-images|List all compatible scanned images
-listF|--list-file|Save list of compatible scanned images as text file
-listT|--list-tasks|List tasks
- Created list of compatible images will be saved in the output directory.
---
### Task handling:
Short|Long|Input|Explanation
:-|:-|:-|:-
-addA|--add-all|NUM|Add all compatible images
-addID|--add-id|NUM|Add compatible images by ID
-addN|--add-new|NUM|Add compatible images by modified timestamp (newest)
-addO|--add-old|NUM|Add compatible images by modified timestamp (oldest)
-addR|--add-random|NUM|Add compatible images randomly
-remID|--remove-id|NUM|Remove already added compatible images by ID
- Input ID numbers without comma e.g: 1 2 3 4 5
---
### GUI settings:
Short|Long|Input|Explanation
:-|:-|:-|:-
-fontS|--font-scale|NUM|Font scale for GUI
-theme|--theme|TEXT|Color theme for FreeSimpleGUI
-viewW|--view-width|NUM|Max image width inside GUI
-viewH|--view-height|NUM|Max image height inside GUI
---