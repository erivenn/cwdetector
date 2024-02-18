from datetime import date
from os import path
import geopandas as gpd
from PIL import Image
from osgeo import gdal
import logging

from file_utils import get_all_files_in_dir, get_filename_without_extension

# COCO dataset classes and converter functions


class CocoAnnotation:
    def __init__(
        self, category_id: int, bbox: tuple[int, int, int, int], image_id: int
    ):
        self.category_id = category_id
        self.bbox = bbox
        self.image_id = image_id

    def __dict__(self):
        return {
            "category_id": self.category_id,
            "bbox": self.bbox,
            "image_id": self.image_id,
        }


class CocoImage:
    def __init__(self, id: int, file_name: str, width: int, height: int):
        self.id = id
        self.file_name = file_name
        self.height = height
        self.width = width

    def __dict__(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "height": self.height,
            "width": self.width,
        }


class CocoCategory:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __dict__(self):
        return {"id": self.id, "name": self.name}


class CocoDataset:
    def __init__(
        self,
        annotations: list[CocoAnnotation],
        categories: list[CocoCategory],
        images: list[CocoImage],
    ):
        self.images = images
        self.annotations = annotations
        self.categories = categories
        self.info = {
            "description": "Riki's dataset",
            "date_created": date.today().strftime("%Y/%m/%d"),
            "version": "1.0",
        }
        self.licenses = []

    def __dict__(self):
        return {
            "info": self.info,
            "licenses": self.licenses,
            "categories": [category.__dict__() for category in self.categories],
            "images": [image.__dict__() for image in self.images],
            "annotations": [annotation.__dict__() for annotation in self.annotations],
        }


def convert_gdf_to_coco_annotations(
    gdf: gpd.GeoDataFrame, img_path: str, image_id: int, category_name: str
) -> list[CocoAnnotation]:
    annotations = []
    for _, row in gdf.iterrows():
        bbox = convert_bounds_to_pixel_bbs(row.geometry.bounds, img_path)
        category_id = category_name_to_id(category_name)
        annotations.append(CocoAnnotation(category_id, bbox, image_id))

    return annotations


def convert_image_to_coco_image(
    img_path: str, image_id: int, destination_dir: str
) -> CocoImage:
    img = Image.open(img_path)
    width, height = img.size
    return CocoImage(image_id, path.basename(img_path), width, height)


def category_name_to_id(name: str) -> int:
    if name == "snag":
        return 1
    elif name == "fallen":
        return 2
    else:
        raise ValueError(f"Invalid category name '${name}'")


def create_coco_dataset(
    img_paths: list[str],
    category_names: list[str],
    snags_dir: str,
    fallen_dir: str,
    img_destination_dir: str,
):
    annotations: list[CocoAnnotation] = []
    images: list[CocoImage] = []

    for i, img_path in enumerate(img_paths):
        images.append(convert_image_to_coco_image(img_path, i, img_destination_dir))
        for geojson_dir in [snags_dir, fallen_dir]:
            label_path = path.join(
                geojson_dir, f"{get_filename_without_extension(img_path)}.geojson"
            )
            gdf = None
            try:
                gdf = gpd.read_file(label_path)
            except Exception as e:
                print(f"No labels found for {label_path}")
            if gdf is None:
                continue
            print(f'Converting {label_path}')
            category_name = 'snag' if geojson_dir == snags_dir else 'fallen'
            for annotation in convert_gdf_to_coco_annotations(gdf, img_path, i, category_name):
                annotations.append(annotation)
            

    categories: list[CocoCategory] = [
        CocoCategory(category_name_to_id(name), name) for name in category_names
    ]
    return CocoDataset(annotations, categories, images)


def convert_coords_to_pixels(
    points_list: list[tuple[int, int]], img_path
) -> list[tuple[int, int]]:
    dataset = gdal.Open(img_path)
    transform = dataset.GetGeoTransform()

    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = -transform[5]

    pixels_bbox = []
    for point in points_list:
        col = int((point[0] - xOrigin) / pixelWidth)
        row = int((yOrigin - point[1]) / pixelHeight)
        pixels_bbox.append([col, row])

    return pixels_bbox


def convert_bounds_to_pixel_bbs(
    bounds: tuple[
        int,
        int,
        int,
        int,
    ],
    img_path: str,
):
    x_min, y_min, x_max, y_max = bounds
    [x_min, y_min], [x_max, y_max] = convert_coords_to_pixels(
        [(x_min, y_min), (x_max, y_max)], img_path
    )
    return (x_min, y_min, x_max, y_max)
