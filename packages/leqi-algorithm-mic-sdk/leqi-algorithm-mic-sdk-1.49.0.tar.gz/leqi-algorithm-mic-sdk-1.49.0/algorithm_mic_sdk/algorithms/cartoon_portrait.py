from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class CartoonPortrait(AlgoBase):
    __algo_name__ = 'cartoon_portrait_aigc'
    DEFAULT_TIMEOUT = 60

    def __init__(self,
                 auth_info: AuthInfo,
                 oss_file: FileInfo,
                 sex: str,
                 style: str,
                 process=None,
                 custom_data=None,
                 callback_url=None,
                 **kwargs):
        """
        头像卡通算法 (AIGC版本)
        @param auth_info: 个人权限配置参数
        @param oss_file: 用户图片
        @param sex: 性别[MALE/FEMALE]
        @param style: 风格,有 ADULT/CHILD 两种
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request['sex'] = sex
        self.request['style'] = style
        self.request['callback_url'] = callback_url
        self.request.update(kwargs)
