import math
from copy import deepcopy
from itertools import accumulate

import cv2
import numpy as np


def generate_combine_image(images, image_size=(512, 400)):
    #Add blank image if img is none in images list
    images_list = []
    for img in images:
        if img is None:
            img = np.ones((112, 112, 3), dtype=np.uint8)
        images_list.append(img)

    def concat_tile(im_list_2d):
        return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

    if len(images_list) == 1:
        final_image = images_list[0]
    else:
        length_to_split = [2] * int(math.ceil(len(images_list) / 2))
        total_images = sum(length_to_split)
        images_list += [np.ones((112, 112, 3), dtype=np.uint8)] * (total_images - len(images_list))

        # Using islice
        images_list = [cv2.resize(deepcopy(img), image_size) for img in images_list]
        list = [images_list[x - y: x] for x, y in zip(
            accumulate(length_to_split), length_to_split)]

        final_image = concat_tile(list)

    return final_image
