from ..control.CProduct import CProduct
from ..extensions.base_resource import Resource


class AProduct(Resource):
    def __init__(self):
        self.cproduct = CProduct()

    def get(self, product):
        apis = {
            "list": self.cproduct.list,
            "list_pc": self.cproduct.list_pc,
            "list_pp": self.cproduct.list_pp,
            "list_uc": self.cproduct.list_uc,
            "get_uc": self.cproduct.get_uc,
            "download": self.cproduct.download,
            "get": self.cproduct.get
        }
        return apis

    def post(self, product):
        apis = {
            'set_proudct': self.cproduct.set_proudct,
            'set_pc': self.cproduct.set_pc,
            'set_pp': self.cproduct.set_pp,
            'set_uc': self.cproduct.set_uc,
            'set_un': self.cproduct.set_un,
            'calculation': self.cproduct.calculation,
        }
        return apis
