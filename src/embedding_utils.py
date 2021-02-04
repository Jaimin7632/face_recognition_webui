import config
import pickle
from pathlib import Path
import cv2
import os
from face_recognition import face_analysis
import torch
import mxnet as mx

"""
Face Embedding Management 
"""

# Init gallery varible
ref_dir = None
precomputed_dist, gallery_class_names, gallery_imgs_emb = None, None, None


def load_gallery(self):
    """
    Load gallery if gallery's json file available if not then load from gallery folder path
    Read crop dirs' images, preprocess them, store in ref_dir (Embeddings and face pose) and store in DB.
    :return:
    """
    print("Loading gallery data...")
    gallery_path = Path(config.ENROLLED_DATA_PATH)
    gallery_file_path = gallery_path / "gallery.pickle"

    if gallery_file_path.exists():
        with open(gallery_file_path, 'rb') as handle:
            self.ref_dir = pickle.load(handle)
    else:
        if not gallery_path.exists():
            gallery_path.mkdir(parents=True)
        embedding_dict = {}

        # # Update database
        # db_utils.delete_all_tables()
        # db_utils.db_init()

        embedding_dict['embeddings'] = {}
        for person_dir in gallery_path.iterdir():
            person_name = person_dir.name
            if not person_dir.is_dir():
                continue

            embedding_dict['embeddings'][person_name] = {}

            # db_utils.add_person(person_name)
            deleted_files = 0

            for img_path in person_dir.iterdir():
                img_name = img_path.name
                img = cv2.imread(str(img_path))

                # if detect_face_mask(img):
                #     deleted_files += 1
                #     os.remove(img_path)
                #     continue

                img = self.image_pre_process(img)
                if not self.is_image_gallery_compatible(img=img):
                    deleted_files += 1
                    os.remove(img_path)
                    continue

                emb = face_analysis.rec_model.get_embedding(img).tolist()
                if self.is_matched_with_blackimg_emb(emb):
                    continue

                embedding_dict['embeddings'][person_name][img_name] = emb

            if deleted_files > 0 : print(f'{person_name} - {deleted_files} deleted. No face found after align.')

        ref_dir = embedding_dict
    save_ref_file()
    print("Gallery Loaded.")

def save_ref_file():
    """
    save gallery data
    :return:
    """
    global gallery_imgs_emb, gallery_class_names, precomputed_dist

    print("Saving reference file and update dependent var...")

    file_path = os.path.join(config.ENROLLED_DATA_PATH, "gallery.pickle")
    with open(file_path, 'wb') as handle:
        pickle.dump(ref_dir, handle, protocol=pickle.HIGHEST_PROTOCOL)

    gallery_imgs_emb = []
    gallery_class_names = []
    for class_name, images_embed in ref_dir['embeddings'].items():
        for img_name, embedding in images_embed.items():
            gallery_imgs_emb.append(embedding[0])
            gallery_class_names.append(class_name)

    gallery_imgs_emb = torch.Tensor(gallery_imgs_emb).to(
        '0' if mx.context.num_gpus() else "cpu")
    precomputed_dist = torch.Tensor.sum(gallery_imgs_emb ** 2, dim=1)

def compare_with_enrolled_data(query):
    """
    compare query embedding with enrolled embedding
    Parameters
    ----------
    query

    Returns
    -------
    sorted_distance_with_enrolled_data
    """
    global gallery_imgs_emb, gallery_class_names, precomputed_dist

    emb = torch.Tensor(query).reshape(1, 512).to(
                             '0' if mx.context.num_gpus() else "cpu")
    dist = torch.Tensor.sum(emb ** 2, dim=1) + precomputed_dist - 2 * emb.mm(
        torch.transpose(gallery_imgs_emb, 0, 1))
    dist = torch.sqrt_(torch.abs(dist)).tolist()[0]
    output_dict = {}
    for i, val in enumerate(dist):
        output_dict.setdefault(gallery_class_names[i], []).append(val)
    for key, val in output_dict.items():
        value = sorted(val)
        output_dict[key] = sum(value[:3]) / 3 if len(value) > 2 else len(value)

    class_dist = sorted(output_dict.items(), key=lambda x: x[1])

    if not class_dist:
        return ["unknown", 100000]

    return class_dist[0]