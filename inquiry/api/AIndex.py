from ..control.CIndex import CIndex
from ..extensions.base_resource import Resource

class AUser(Resource):
    def __init__(self):
        self.cindex = CIndex()

    def get(self, user):
        apis = {
            "list_mp_banner": self.cindex.list_mp_banner
        }
        return apis

    def post(self, user):
        apis = {
            'set_mp_banner': self.cindex.set_mp_banner,
        }
        return apis