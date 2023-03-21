# file-tagger

*file-tagger* is a tool for bulk-tagging files.  
It uses the tagging system [TMSU](https://tmsu.org/) as backend.  
For images, it uses tensorflow and ResNet50 to predict keywords automatically,
and comes with a GUI to fastly preview the image and add new tags.

## Requirements

- [TMSU](https://tmsu.org/)
- OpenCV (optional)
- Numpy (optional)
- tkinter (optional)
- tensorflow (optional)

## Usage

```
usage: file-tagger.py [-h] [-b [BASE]] [-f [FILE_DIR]] [-g [GUI]] [--predict-images [PREDICT_IMAGES]] [--predict-images-top [PREDICT_IMAGES_TOP]]
                      [--gui-tag [GUI_TAG]] [--open-system [OPEN_SYSTEM]] [-i [INDEX]] [-v]

Tag multiple files using TMSU.

options:
  -h, --help            show this help message and exit
  -b [BASE], --base [BASE]
                        Base directory with database (default: .)
  -f [FILE_DIR], --file-dir [FILE_DIR]
                        File directory for walking (default: .)
  -g [GUI], --gui [GUI]
                        Show main GUI (default: False)
  --predict-images [PREDICT_IMAGES]
                        Use prediction for image tagging (default: False)
  --predict-images-top [PREDICT_IMAGES_TOP]
                        Defines how many top prediction keywords should be used (default: 10)
  --gui-tag [GUI_TAG]   Show GUI for tagging (default: False)
  --open-system [OPEN_SYSTEM]
                        Open all files with system default (default: False)
  -i [INDEX], --index [INDEX]
                        Start tagging at the given file index (default: 0)
  -v, --verbose         Verbosity level
```

## Getting started

1. Install requirements `pip install tensorflow numpy tkinter opencv-python`
2. Run the main script given the base directory `python file-tagger.py --base <base> --gui --gui-tag --predict-images`
3. Consecutively tag the files by entering comma-separated tags to the entry and pressing `Next`
4. If you want to take a break from tagging, remember the current index and give it as start index next time. Mind that adding/removing files will invalidate the index.