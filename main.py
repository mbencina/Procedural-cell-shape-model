import czifile
from aicsimageio import AICSImage
import matplotlib.pyplot as plt
import napari_aicsimageio
import napari
import numpy as np


def get_first_and_last_layer(membrane_data):
    first_data_layer = -1
    last_data_layer = -1
    for i, xy in enumerate(membrane_data):
        print(i, ":", np.sum(xy) / 255)
        if np.sum(xy) == 0:
            continue
        if first_data_layer == -1:
            first_data_layer = i
        last_data_layer = i

    return first_data_layer, last_data_layer


def main():
    # downloaded cell files
    cell_files = ["data/AICS-10_12_2.ome.tif", "data/AICS-10_13_4.ome.tif", "data/AICS-10_14_9.ome.tif"]

    cells = []
    for filename in cell_files:
        img = AICSImage(filename)
        membrane_data = img.get_image_data("ZYX", T=0, S=0, C=7)

        print(filename)
        first_data_layer, last_data_layer = get_first_and_last_layer(membrane_data)
        x_dims = img.shape[5]
        y_dims = img.shape[4]
        z_dims = last_data_layer - first_data_layer
        cells.append({"x": x_dims,
                      "y": y_dims,
                      "z": z_dims,
                      "z_first": first_data_layer,
                      "z_last": last_data_layer,
                      "data": membrane_data})
    print()

    print(cells)
    # with napari.gui_qt():
    #     viewer = napari.view_image(img.data, rgb=True)
    print("success")


if __name__ == "__main__":
    main()
