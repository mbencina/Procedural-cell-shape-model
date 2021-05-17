import czifile
from aicsimageio import AICSImage
import matplotlib.pyplot as plt
import napari_aicsimageio
import napari
import numpy as np
import random


def get_first_and_last_layer(membrane_data):
    first_data_layer = -1
    last_data_layer = -1
    for i, xy in enumerate(membrane_data):
        if np.sum(xy) == 0:
            continue
        if first_data_layer == -1:
            first_data_layer = i
        last_data_layer = i

    return first_data_layer, last_data_layer


def match_z_dims(cells):
    # max allowed "z" (layer) span
    min_z_span = 100
    for cell in cells:
        if cell["z"] < min_z_span:
            min_z_span = cell["z"]

    for cell in cells:
        if cell["z"] > min_z_span:
            diff = cell["z"] - min_z_span
            change_first = True
            for i in range(diff):
                if change_first:
                    cell["z_first"] += 1
                    change_first = False
                else:
                    cell["z_last"] -= 1
                    change_first = True

            cell["z"] = min_z_span


def get_cells(cell_files):
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

    return cells


def get_vectors(cells, num_vectors):
    vectors = []
    for j, cell in enumerate(cells):
        vectors.append([])
        for i in range(cell["z_first"], cell["z_last"]):
            all_indexes = np.where(cell["data"][i] == 255)
            all_coord = list(zip(all_indexes[0], all_indexes[1]))
            # TODO currently we get random vectors, maybe get a better representation
            chosen_coord = random.sample(all_coord, num_vectors)
            for coord in chosen_coord:
                # append x, y, z
                vectors[j].append((coord[0], coord[1], i))  # TODO ne vem a jih je treba dat not kot touple

    return vectors


def main():
    # downloaded cell files
    cell_files = ["data/AICS-10_12_2.ome.tif", "data/AICS-10_13_4.ome.tif", "data/AICS-10_14_9.ome.tif"]

    # extract cell membrane data from files
    cells = get_cells(cell_files)

    # we make sure number of layers (aka "z" dimensions) is the same for every cell
    match_z_dims(cells)

    # we get vectors from cells
    num_of_vectors_per_cell = 16
    vectors = get_vectors(cells, num_of_vectors_per_cell)
    print()

    # with napari.gui_qt():
    #     viewer = napari.view_image(img.data, rgb=True)
    print("success")


if __name__ == "__main__":
    main()
