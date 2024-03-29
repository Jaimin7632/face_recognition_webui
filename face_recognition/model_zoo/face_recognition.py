from __future__ import division

import cv2
import mxnet as mx
import numpy as np
from copy import deepcopy
import math

__all__ = ['FaceRecognition',
           'arcface_r100_v1', 'arcface_outofreach_v1', 'arcface_mfn_v1',
           'get_arcface']

from sklearn import preprocessing


class FaceRecognition:
    def __init__(self, name, download, param_file):
        self.name = name
        self.download = download
        self.param_file = param_file
        self.image_size = (112, 112)
        if download:
            assert param_file

    def prepare(self, ctx_id):
        if self.param_file:
            pos = self.param_file.rfind('-')
            prefix = self.param_file[0:pos]
            pos2 = self.param_file.rfind('.')
            epoch = int(self.param_file[pos + 1:pos2])
            sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
            all_layers = sym.get_internals()
            sym = all_layers['fc1_output']
            if ctx_id >= 0:
                ctx = mx.gpu(ctx_id)
            else:
                ctx = mx.cpu()
            model = mx.mod.Module(symbol=sym, context=ctx, label_names=None)
            data_shape = (1, 3) + self.image_size
            model.bind(data_shapes=[('data', data_shape)])
            model.set_params(arg_params, aux_params)
            # warmup
            data = mx.nd.zeros(shape=data_shape)
            db = mx.io.DataBatch(data=(data,))
            model.forward(db, is_train=False)
            embedding = model.get_outputs()[0].asnumpy()
            self.model = model
        else:
            pass

    def get_embedding(self, img):
        assert self.param_file and self.model
        assert img.shape[2] == 3 and img.shape[0:2] == self.image_size
        data = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        data = np.transpose(data, (2, 0, 1))
        data = np.expand_dims(data, axis=0)
        data = mx.nd.array(data)
        db = mx.io.DataBatch(data=(data,))
        self.model.forward(db, is_train=False)
        embedding = self.model.get_outputs()[0].asnumpy()
        return embedding

    def get_embeddings_list(self, image_list, batch_size=1):
        assert self.param_file and self.model
        data_list = []
        for image in image_list:
            img = cv2.resize(deepcopy(image), (112, 112))
            data = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            data = np.transpose(data, (2, 0, 1))
            data_list.append(data)

        if not data_list: return []

        embedding_list = []
        num_of_iter = math.ceil(len(data_list) / batch_size)
        for i in range(num_of_iter):
            tdata = np.array(data_list[i * batch_size:(i + 1) * batch_size])
            tdata = mx.nd.array(tdata)
            db = mx.io.DataBatch(data=(tdata,))
            self.model.forward(db, is_train=False)
            embedding = self.model.get_outputs()[0].asnumpy()
            embedding = preprocessing.normalize(embedding).tolist()
            embedding_list += embedding

        return embedding_list

    def compute_sim(self, img1, img2):
        emb1 = self.get_embedding(img1).flatten()
        emb2 = self.get_embedding(img2).flatten()
        from numpy.linalg import norm
        sim = np.dot(emb1, emb2) / (norm(emb1) * norm(emb2))
        return sim


def get_arcface(name, download=True,
                root='resources/models', **kwargs):
    model_path = kwargs.get('model_path')
    if model_path is not None:
        return FaceRecognition(name, True, model_path)

    if not download:
        return FaceRecognition(name, False, None)
    else:
        from .model_store import get_model_file
        _file = get_model_file("arcface_%s" % name, root=root)
        return FaceRecognition(name, True, _file)


def arcface_r100_v1(**kwargs):
    return get_arcface("r100_v1", download=False, **kwargs)


def arcface_mfn_v1(**kwargs):
    return get_arcface("mfn_v1", download=True, **kwargs)


def arcface_outofreach_v1(**kwargs):
    return get_arcface("outofreach_v1", download=False, **kwargs)
