# -*- coding: utf-8 -*-
from inquiry.extensions.base_resource import Resource
from inquiry.control.CFile import CFile


class AFile(Resource):
    def __init__(self):
        self.cfile = CFile()

    def post(self, file):
        apis = {
            'upload': self.cfile.upload_img,
            'batch_upload': self.cfile.batch_upload
        }
        return apis
