import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from PIL import Image
from coco import CocoAnnotation, CocoDataset
import numpy as np
from file_utils import create_dir_if_not_exists, get_all_files_in_dir, remove_files_in_dir

NOF_COLUMNS = 6


def get_rows(nof_imgs: int):
    nof_rows = nof_imgs // NOF_COLUMNS
    if nof_imgs % NOF_COLUMNS != 0:
        nof_rows += 1
    print(nof_rows, nof_imgs, NOF_COLUMNS)
    return nof_rows


def get_img_position(img_n, columns) -> tuple[int, int]:
    return img_n // columns, img_n % columns


def read_annotations_from_file(annotation_file: str) -> dict:
    with open(annotation_file, "r") as f:
        return json.load(f)


def get_img_id(data: dict, img: str):
    img_name = os.path.basename(img)
    maybe_img_id = [img["id"] for img in data["images"] if img["file_name"] == img_name]
    if len(maybe_img_id) == 0:
        return None
    return maybe_img_id[0]


def get_img_annotations_with_metadata(data: dict, img: str):
    img_id = get_img_id(data, img)
    if img_id is None:
        return []
    return [ann for ann in data["annotations"] if ann["image_id"] == img_id]


data_dir = "kenttarova"
img_dir = os.path.join(data_dir, "rasters_rgb")
training_annotation_file = f"{data_dir}_training.json"
validation_annotation_file = f"{data_dir}_validation.json"

training_data = read_annotations_from_file(training_annotation_file)
validation_data = read_annotations_from_file(validation_annotation_file)

imgs = get_all_files_in_dir(img_dir, "tif")
rows = get_rows(len(imgs))

#fig, axs = plt.subplots(rows, NOF_COLUMNS, figsize=(NOF_COLUMNS * 2, rows * 2))
create_dir_if_not_exists('plot')
remove_files_in_dir('plot')

for i, img in enumerate(imgs):
    print(f"Plotting image {img}")
    im = Image.open(img)
    #ax = axs[get_img_position(i, NOF_COLUMNS)] if len(imgs) > NOF_COLUMNS else axs[i]
    fig, ax = plt.subplots()
    ax.imshow(im)

    img_annotations = get_img_annotations_with_metadata(training_data, img)
    img_annotations += get_img_annotations_with_metadata(validation_data, img)
    for ann in img_annotations:
        bbox = ann["bbox"]
        category = ann["category_id"]
        x_min, y_min, x_max, y_max = bbox
        rect = patches.Rectangle(
            (x_min, y_min),
            x_max - x_min,
            y_max - y_min,
            linewidth=1,
            edgecolor="g" if category == 1 else "r",
            facecolor="none",
        )
        ax.add_patch(rect)
        ax.set_axis_off()
        plt.savefig(os.path.join('plot', os.path.basename(img)))

print("done")
