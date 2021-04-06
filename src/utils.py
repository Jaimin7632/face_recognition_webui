import math
import textwrap
from copy import deepcopy
from itertools import accumulate

import cv2
import numpy as np


def generate_combine_image(images, image_size=(1024, 800)):
    # Add blank image if img is none in images list
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


def overlay_transparent(background, overlay, x, y, opacity=1):
    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
            ],
            axis=2,
        )

    overlay_image = overlay[..., :3]
    mask = opacity

    background[y:y + h, x:x + w] = (1.0 - mask) * background[y:y + h, x:x + w] + mask * overlay_image

    return background


def set_text_with_box(text_dict, background, x, y, box_h_w=[200, 300]):
    overlay = np.full(box_h_w + [3], fill_value=100, dtype=np.uint8)
    overlay[:, :, 0] = 0
    overlay[:, :, 1] = 200
    overlay[:, :, 2] = 200
    dst = overlay_transparent(background, overlay, x, y, opacity=0.8)

    # Put text on Image
    x = x + 15
    for key, value in text_dict.items():
        wrapped_text = textwrap.wrap(f'{str(key)}: {str(value)}', width=18)
        font_size = 0.4
        font_thickness = 1
        font = cv2.FONT_HERSHEY_SIMPLEX

        y = y + 25
        for i, line in enumerate(wrapped_text):
            textsize = cv2.getTextSize(line, font, font_size, font_thickness)[0]

            gap = textsize[1] + 6

            y = y + i * gap
            # if y > box_h_w[0]:
            #     continue

            cv2.putText(dst, line, (x, y), font,
                        font_size,
                        (0, 0, 0),
                        font_thickness,
                        lineType=cv2.LINE_AA)

    return dst
