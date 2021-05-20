from aicsimageio import AICSImage
import matplotlib.pyplot as plt
import numpy as np
import random
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
from functools import partial
from scipy import stats


def get_first_and_last_layer(membrane_data, min_number_of_points):
    first_data_layer = -1
    last_data_layer = -1
    for i, xy in enumerate(membrane_data):
        if np.sum(xy) / 255 < min_number_of_points:
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
    return min_z_span


def get_cells(cell_files, min_number_of_points):
    cells = []
    print("Extracting data from file:")
    for filename in cell_files:
        img = AICSImage(filename)
        membrane_data = img.get_image_data("ZYX", T=0, S=0, C=7)

        print(filename)
        first_data_layer, last_data_layer = get_first_and_last_layer(membrane_data, min_number_of_points)
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


def get_representative_sample(all_coord, num_coord):
    coord_arr = np.asarray(all_coord)
    center_point = coord_arr.mean(axis=0)
    coord_arr = sorted(coord_arr, key=partial(clockwise_sort, center_point))

    step = int(len(coord_arr) / num_coord)
    res = []
    for i in range(0, len(coord_arr), step):
        # just a security check
        if len(res) == num_coord:
            break
        res.append(coord_arr[i])

    return res


def get_vectors(cells, num_coord):
    vectors = []
    for j, cell in enumerate(cells):
        vectors.append([])  # xi
        z = 0
        for i in range(cell["z_first"], cell["z_last"]):
            layer_points = []
            all_indexes = np.where(cell["data"][i] == 255)
            all_coord = list(zip(all_indexes[0], all_indexes[1]))
            # chosen_coord = random.sample(all_coord, num_vectors)  # random sample
            chosen_coord = get_representative_sample(all_coord, num_coord)

            # # Graphs:
            # # real cell layer shape
            # new_cell_x = [point[0] for point in all_coord]
            # new_cell_y = [point[1] for point in all_coord]
            # plt.scatter(new_cell_x, new_cell_y, c='g', s=1)
            # plt.title("Real cell layer shape")
            # # plt.plot(new_cell_x, new_cell_y)
            # plt.show()
            #
            # # approximation
            # new_cell_x = [point[0] for point in chosen_coord]
            # new_cell_y = [point[1] for point in chosen_coord]
            # new_cell_x.append(chosen_coord[0][0])
            # new_cell_y.append(chosen_coord[0][1])
            # # plt.scatter(new_cell_x, new_cell_y)
            # plt.plot(new_cell_x, new_cell_y, '.r-')
            # plt.title("Approximation")
            # plt.show()

            for coord in chosen_coord:
                # append [x, y, z]
                layer_points.append([coord[0], coord[1], z])
                # layer_points.append([128 * coord[0]/cell["x"], 128 * coord[1]/cell["y"], z])

            layer_points = np.asarray(layer_points)
            center_point = layer_points.mean(axis=0)
            layer_points = sorted(layer_points, key=partial(clockwise_sort, center_point))
            layer_points = list(np.asarray(layer_points).flatten())
            vectors[j] += layer_points
            z += 1

    return np.asarray(vectors)


def clockwise_sort(point, center):
    vector = point - center

    # we are only interested in x and y
    vector_length = math.hypot(vector[0], vector[1])
    if vector_length == 0:
        return -1, 0

    vector_normalized = vector / vector_length
    angle = math.atan2(vector_normalized[1], vector_normalized[0])

    if angle < 0:
        angle += 2 * math.pi

    return angle, vector_length


def generate_new_cell(cell_vectors, n):
    print("\nGenerating new cell...")

    average = cell_vectors.mean(axis=0)

    covariance_matrix = np.zeros((cell_vectors.shape[1], cell_vectors.shape[1]))
    for x in cell_vectors:
        covariance_matrix += np.outer((x - average), (x - average))
    covariance_matrix /= (n - 1)

    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    indexes = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[indexes]
    eigenvectors = eigenvectors[:, indexes]

    eigenvalues = eigenvalues.real
    eigenvectors = eigenvectors.real

    return average + (random.random() * 3 * math.sqrt(abs(eigenvalues[0])) * eigenvectors[0])


def remove_noisy_data_and_scale(new_cell, dim_x, dim_y, dim_z):
    # # we can plot the noisy cell
    # ax = plt.axes(projection='3d')
    # ax.scatter3D(new_cell[0::3], new_cell[1::3], new_cell[2::3], color="r", s=1)
    # ax.set_title("Generated cell")
    # plt.show()

    # first we remove noisy data using z-score
    new_cell_vectorized = [new_cell[i:i + 3] for i in range(0, len(new_cell), 3)]
    z_score = np.abs(stats.zscore(new_cell_vectorized))
    cleaned = []
    # this can also be adjusted to some other value
    z_score_threshold = 1.5
    for i, vec in enumerate(z_score):
        if vec[0] > z_score_threshold or vec[1] > z_score_threshold or vec[2] > z_score_threshold:
            continue
        cleaned.append(new_cell_vectorized[i])

    # scaling to given dimensions
    cleaned = np.asarray(cleaned).flatten()
    max_val = max(cleaned[0::3])
    min_val = min(cleaned[0::3])
    cleaned[0::3] = dim_x * ((cleaned[0::3] - min_val) / (max_val - min_val))
    max_val = max(cleaned[1::3])
    min_val = min(cleaned[1::3])
    cleaned[1::3] = dim_y * ((cleaned[1::3] - min_val) / (max_val - min_val))
    max_val = max(cleaned[2::3])
    min_val = min(cleaned[2::3])
    cleaned[2::3] = dim_z * ((cleaned[2::3] - min_val) / (max_val - min_val))

    # # we can plot the polished cell
    # ax = plt.axes(projection='3d')
    # ax.scatter3D(cleaned[0::3], cleaned[1::3], cleaned[2::3], color="g", s=1)
    # ax.set_title("Polished generated cell")
    # plt.show()

    cleaned = [cleaned[i:i + 3] for i in range(0, len(cleaned), 3)]
    cleaned = [list(map(int, vec)) for vec in cleaned]
    return sorted(cleaned, key=lambda x: x[2])


def create_output_file(polished_new_cell, dim_x, dim_y, dim_z, output_file_name, display_only_membrane_points):
    last_ix = 0
    last_output = [0] * dim_y * dim_x
    n = len(polished_new_cell)
    with open(output_file_name, 'bw+') as f:
        for z in range(dim_z):
            points = []
            last_i = -1
            for i in range(last_ix, n):
                if polished_new_cell[i][2] <= z:
                    polished_new_cell[i][2] = z  # in case a point remains from the last layer
                    points.append(polished_new_cell[i])
                else:
                    last_i = i
                    break

            # not enough points for a layer
            if len(points) < 3:
                print("Progress:", '%.3f' % (z / dim_z * 100), '%')
                f.write(bytes(last_output))
                continue

            last_ix = last_i

            points = np.asarray(points)
            center_point = points.mean(axis=0)
            points_clockwise = sorted(points, key=partial(clockwise_sort, center_point))
            points_clockwise = np.asarray(points_clockwise).tolist()

            poly = Polygon(points_clockwise)

            output = []
            for y in range(dim_y):
                for x in range(dim_x):
                    if any(np.equal(points_clockwise, [x, y, z]).all(1)):
                        output.append(255)
                    elif poly.contains(Point(x, y, z)) and not display_only_membrane_points:
                        output.append(255)
                    else:
                        output.append(0)

            print("Progress:", '%.3f' % (z / dim_z * 100), '%')
            f.write(bytes(output))
            last_output = output

    print("Progress:", '%.3f' % 100, '%\n')
    print("Output file successfully generated!")
    print("x=" + str(dim_x) + " y=" + str(dim_y) + " z=" + str(dim_z))


def main():
    random.seed(123)
    output_file_name = "generated_cell.raw"

    # --------------Adjustable basic cell shape parameters--------------
    # higher number means better cell layer approximation. higher number can result in a smaller z-coordinate
    num_of_points_per_layer = 32
    # whether or not to display the interior of the cell or just the membrane
    display_only_membrane_points = False
    # output x and y dimensions
    dim_x = 128
    dim_y = 128
    # ------------------------------------------------------------------

    # training cells. downloaded from: https://www.allencell.org/3d-cell-viewer.html
    cell_files = ["data/AICS-10_12_2.ome.tif", "data/AICS-10_13_4.ome.tif", "data/AICS-10_14_9.ome.tif"]

    # extract cell membrane data from files
    cells = get_cells(cell_files, num_of_points_per_layer)

    # we make sure number of layers (aka "z" dimensions) is the same for every cell
    dim_z = match_z_dims(cells)

    # we obtain data vectors from cells
    cell_vectors = get_vectors(cells, num_of_points_per_layer)

    # generate new cell based on obtained data using statistical shape modeling
    new_cell = generate_new_cell(cell_vectors, len(cells))

    # remove noisy points and scale cell to given dimensions
    polished_new_cell = remove_noisy_data_and_scale(new_cell, dim_x, dim_y, dim_z)

    # create a 3D .raw binary output file
    create_output_file(polished_new_cell, dim_x, dim_y, dim_z, output_file_name, display_only_membrane_points)


if __name__ == "__main__":
    main()
