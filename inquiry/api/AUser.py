from ..control.CUser import CUser
from ..extensions.base_resource import Resource


class AUser(Resource):
    def __init__(self):
        self.cuser = CUser()

    def get(self, user):
        apis = {
            "get_user_list": self.cuser.get_user_list,
            "get_userlevelsetting": self.cuser.get_userlevelsetting,
            'get_inforcode': self.cuser.get_inforcode,  # 获取验证码
            'useristory': self.cuser.useristory,  # 用户查询记录
            "get_admin_list": self.cuser.get_admin_list
        }
        return apis

    def post(self, user):
        apis = {
            'mp_login': self.cuser.mini_program_login,
            'bind_phone': self.cuser.bind_phone,
            'test_login': self.cuser.test_login,
            'set_userlevelsetting': self.cuser.set_userlevelsetting,
            'update_white_list': self.cuser.update_white_list,
            'update_user_level': self.cuser.update_user_level,
            'admin_login': self.cuser.admin_login,  # 管理员登录
            'add_admin_by_superadmin': self.cuser.add_admin_by_superadmin,  # 添加管理员
            'update_admin': self.cuser.update_admin,  # 更新管理员信息
            'update_admin_password': self.cuser.update_admin_password,  # 修改管理员密码
        }
        return apis
