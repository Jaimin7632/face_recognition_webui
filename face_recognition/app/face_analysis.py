from __future__ import division

import collections
from copy import deepcopy

import cv2
import numpy as np
from numpy.linalg import norm

import config
from ..model_zoo import model_zoo
from ..utils import face_align
from sklearn import preprocessing
import config
from ..model_zoo.cordinateReg_landmarks import Handler

__all__ = ['FaceAnalysis',
           'Face']

Face = collections.namedtuple('Face', ['face_crop',
    'bbox', 'landmark', 'det_score', 'embedding', 'gender', 'age', 'embedding_norm', 'normed_embedding'])

Face.__new__.__defaults__ = (None,) * len(Face._fields)


class FaceAnalysis:
    def __init__(self, det_name='retinaface_r50_v1', rec_name='arcface_r100_v1', ga_name='genderage_v1', batch_size=1):
        assert det_name is not None
        self.batch_size = batch_size
        self.det_model = model_zoo.get_model(det_name,model_path=config.FACE_DETECTION_MODEL_PATH)
        if rec_name is not None:
            self.rec_model = model_zoo.get_model(rec_name, model_path=config.FACE_RECOGNITION_MODEL_PATH)
        else:
            self.rec_model = None
        if ga_name is not None:
            self.ga_model = model_zoo.get_model(ga_name)
        else:
            self.ga_model = None

        self.handler = Handler(config.FACE_LANDMARKS_MODEL_PATH, 0, ctx_id=0 if config.USE_GPU else -1, det_size=640)

    def prepare(self, ctx_id, nms=0.4):
        self.det_model.prepare(ctx_id, nms)
        if self.rec_model is not None:
            self.rec_model.prepare(ctx_id)
        if self.ga_model is not None:
            self.ga_model.prepare(ctx_id)

    def get(self, img, det_thresh=0.6, det_scale=1.0, max_num=0):
        bboxes, landmarks = self.det_model.detect(img, threshold=det_thresh, scale=det_scale)
        if bboxes.shape[0] == 0:
            return []
        if max_num > 0 and bboxes.shape[0] > max_num:
            area = (bboxes[:, 2] - bboxes[:, 0]) * (bboxes[:, 3] - bboxes[:, 1])
            img_center = img.shape[0] // 2, img.shape[1] // 2
            offsets = np.vstack(
                [(bboxes[:, 0] + bboxes[:, 2]) / 2 - img_center[1], (bboxes[:, 1] + bboxes[:, 3]) / 2 - img_center[0]])
            offset_dist_squared = np.sum(np.power(offsets, 2.0), 0)
            values = area - offset_dist_squared * 2.0  # some extra weight on the centering
            bindex = np.argsort(values)[::-1]  # some extra weight on the centering
            bindex = bindex[0:max_num]
            bboxes = bboxes[bindex, :]
            landmarks = landmarks[bindex, :]
        ret = []
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            # landmark = landmarks[i]
            x1, y1, x2, y2 = list(map(lambda x: 0 if x < 0 else int(x), bbox.tolist()))
            face_crop = deepcopy(img[y1:y2, x1:x2])

            try:
                preds = self.handler.get(face_crop)[0]
                landmark = np.array([preds[38],
                                     preds[88],
                                     preds[80],
                                     preds[52],
                                     preds[61]])
                _img = face_align.norm_crop(face_crop, landmark=landmark)
            except Exception as e:
                continue

            embedding = None
            embedding_norm = None
            normed_embedding = None
            gender = None
            age = None
            if self.ga_model is not None:
                gender, age = self.ga_model.get(_img)
            face = Face(face_crop=_img, bbox=bbox, landmark=landmark, det_score=det_score, embedding=embedding, gender=gender, age=age
                        , normed_embedding=normed_embedding, embedding_norm=embedding_norm)
            ret.append([_img, face])

        return_data = []
        if self.rec_model is not None:
            embedding_list = self.rec_model.get_embeddings_list([img for img, face in ret], batch_size=self.batch_size)
            for i, data in enumerate(ret):
                img, face = data
                embedding_norm = norm(embedding_list[i])
                normed_embedding = np.array(embedding_list[i]).reshape(1,-1)#embedding_list[i] / embedding_norm
                face = Face(face_crop=face.face_crop, bbox=face.bbox, landmark=face.landmark, det_score=face.det_score, embedding=embedding_list[i], gender=face.gender, age=face.age
                        , normed_embedding= normed_embedding, embedding_norm=embedding_norm)

                return_data.append(face)

        return return_data
