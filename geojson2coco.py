from os import path

from coco import create_coco_dataset
from dataset import split_training_validation_data
from file_utils import (
    copy_to_destination_dir,
    create_dir_if_not_exists,
    get_all_files_in_dir,
    remove_files_in_dir,
    write_json_file,
)

categories = ["snag", "fallen"]
# change directory names here
data_dir = "kenttarova"
snags_dir = path.join(data_dir, "labels_snags")
fallen_dir = path.join(data_dir, "labels_fallen")
img_dir = path.join(data_dir, "rasters_rgb")

training_destination_dir = "training2017"
validation_destination_dir = "validation2017"

# code
images_w_full_path = get_all_files_in_dir(img_dir, "tif")
training_imgs, validation_imgs = split_training_validation_data(images_w_full_path, 0.8)

training_data = create_coco_dataset(
    training_imgs, categories, snags_dir, fallen_dir, training_destination_dir
)
validation_data = create_coco_dataset(
    validation_imgs, categories, snags_dir, fallen_dir, validation_destination_dir
)

write_json_file(f"{data_dir}_training.json", training_data.__dict__())
write_json_file(f"{data_dir}_validation.json", validation_data.__dict__())

create_dir_if_not_exists(training_destination_dir)
remove_files_in_dir(training_destination_dir)
copy_to_destination_dir(training_imgs, training_destination_dir)

create_dir_if_not_exists(validation_destination_dir)
remove_files_in_dir(validation_destination_dir)
copy_to_destination_dir(validation_imgs, validation_destination_dir)
