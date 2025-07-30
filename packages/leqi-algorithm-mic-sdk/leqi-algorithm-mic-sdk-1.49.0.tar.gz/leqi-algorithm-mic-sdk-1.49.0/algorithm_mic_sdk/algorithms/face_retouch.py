from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class FaceRetouch(AlgoBase):
    __algo_name__ = 'face_retouch'
    DEFAULT_TIMEOUT = 120

    def __init__(self,
                 auth_info: AuthInfo,
                 oss_file: FileInfo,
                 process=None,
                 custom_data=None,
                 callback_url=None,
                 **kwargs):
        """
        用于证件照的美肤算法
        @param auth_info: 授权信息
        @param oss_file: 文件
        @param process:图片缩放参数
        @param custom_data:
        @param callback_url:
        @param kwargs:
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request['callback_url'] = callback_url
        self.request.update(kwargs)
