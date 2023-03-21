import numpy as np
import argparse
import os, sys
from gui import GuiMain, GuiImage
import cv2
import logging
import magic
from subprocess import Popen, PIPE
import re

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def tmsu_init(base):
    logger = logging.getLogger(__name__)
    if not os.path.exists(os.path.join(base, ".tmsu")):
        logger.info("TMSU database does not exist, creating ...")
        proc = Popen(["tmsu", "init"], cwd=base)
        proc.wait()
        logger.debug("TMSU returncode: {}".format(proc.returncode))
        if proc.returncode != 0:
            logger.error("Could not initialize TMSU database.")
            return False
    return True

def tmsu_tags(base, file):
    logger = logging.getLogger(__name__)
    logger.debug("Getting existing tags for file {}".format(file))
    tags = set()
    proc = Popen(["tmsu", "tags", file], cwd=base, stdout=PIPE, stderr=PIPE)
    proc.wait()
    logger.debug("TMSU returncode: {}".format(proc.returncode))
    if proc.returncode == 0:
        tags.update(re.split("\s", proc.stdout.read().decode())[1:-1])
    else:
        logger.error("Could not get tags for file {}".format(file))
    return tags

def tmsu_tag(base, file, tags, untag=True):
    logger = logging.getLogger(__name__)
    if untag:
        logger.debug("Untagging file")
        proc = Popen(["tmsu", "untag", "--all", file], cwd=base, stdout=PIPE, stderr=PIPE)
        proc.wait()
        if proc.returncode != 0:
            logger.error("Could not untag file {}".format(file))
    if tags:
        logger.debug("Writing tags {}".format(tags))
        proc = Popen(["tmsu", "tag", file] + list(tags), cwd=base, stdout=PIPE, stderr=PIPE)
        proc.wait()
        if proc.returncode != 0:
            logger.error("Could not write tags to file {}".format(file))
    else:
        logger.info("Tags are empty, ignoring")

def walk(args):
    logger = logging.getLogger(__name__)
    logger.info("Walking files ...")
    mime = magic.Magic(mime=True)
    files = [os.path.abspath(os.path.join(dp, f)) for dp, dn, filenames in os.walk(args["base"]) for f in filenames]
    logger.debug("Files: {}".format(files))
    logger.info("Number of files found: {}".format(len(files)))

    if args["predict_images"]:
        from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
        from tensorflow.keras.preprocessing import image
        from tensorflow.keras.models import Model
        model = ResNet50(weights="imagenet")

    for file_path in files:
        logger.info("Handling file {}".format(file_path))
        tags = tmsu_tags(args["base"], file_path)
        not_empty = bool(tags)
        logger.info("Existing tags: {}".format(tags))
        mime_type = mime.from_file(file_path)
        if mime_type.split("/")[0] == "image":
            logger.debug("File is image")
            img = cv2.imread(file_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, dsize=(800, 800), interpolation=cv2.INTER_CUBIC)
            while(True):
                if args["predict_images"]:
                    logger.info("Predicting image tags ...")
                    array = cv2.resize(img, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
                    array = np.expand_dims(array, axis=0)
                    array = preprocess_input(array)
                    predictions = model.predict(array)
                    classes = decode_predictions(predictions, top=10)
                    logger.debug("Predicted image classes: {}".format(classes[0]))
                    tags.update([name for _, name, _ in classes[0]])
                    logger.info("Predicted tags: {}".format(tags))
                if args["gui_images"]:
                    logger.debug("Showing image GUI ...")
                    ret = GuiImage(img, tags).loop()
                    tags = set(ret[1]).difference({''})
                    if ret[0] == GuiImage.RETURN_ROTATE_90_CLOCKWISE:
                        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    elif ret[0] == GuiImage.RETURN_ROTATE_90_COUNTERCLOCKWISE:
                        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif ret[0] == GuiImage.RETURN_NEXT:
                        break
                    elif ret[0] == GuiImage.RETURN_ABORT:
                        return
                    continue
                break
        logger.info("Tagging {}".format(tags))
        tmsu_tag(args["base"], file_path, tags, untag=not_empty)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tag multiple files using TMSU.')
    parser.add_argument('-b', '--base', nargs='?', default='./test', type=dir_path, help='Base directory for walking (default: %(default)s)')
    parser.add_argument('-g', '--gui', nargs='?', const=1, default=False, type=bool, help='Show main GUI (default: %(default)s)')
    parser.add_argument('--predict-images', nargs='?', const=1, default=False, type=bool, help='Use prediction for image tagging (default: %(default)s)')
    parser.add_argument('--gui-images', nargs='?', const=1, default=False, type=bool, help='Show GUI for image tagging (default: %(default)s)')
    parser.add_argument('--gui-audio', nargs='?', const=1, default=False, type=bool, help='Show GUI for audio tagging (default: %(default)s)')
    parser.add_argument('--gui-video', nargs='?', const=1, default=False, type=bool, help='Show GUI for video tagging (default: %(default)s)')
    parser.add_argument('--open-all', nargs='?', const=1, default=False, type=bool, help='Open all files with system default (default: %(default)s)')
    parser.add_argument('-v', '--verbose', action="count", default=0, help="Verbosity level")
    args = parser.parse_args()

    if args.verbose == 0:
        log_level = logging.WARNING
    elif args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(stream=sys.stdout, level=log_level)
    logger = logging.getLogger(__name__)

    args = {
        "base": args.base,
        "gui": args.gui,
        "predict_images": args.predict_images,
        "gui_images": args.gui_images,
        "gui_audio": args.gui_audio,
        "gui_video": args.gui_video,
        "open_all": args.open_all,
        "verbosity": args.verbose
    }

    logger.debug("args = {}".format(args))

    if args["gui"]:
        logger.debug("Starting main GUI ...")
        args = GuiMain(args).loop()

    if tmsu_init(args["base"]):
        walk(args)
