from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class SnaptobookEnhance2(AlgoBase):
    __algo_name__ = 'snaptobook_enhance2'
    DEFAULT_TIMEOUT = 60

    def __init__(self,
                 auth_info: AuthInfo,
                 oss_file: FileInfo,
                 process=None,
                 custom_data=None,
                 callback_url=None,
                 **kwargs):
        """
        Snaptobook 用的增强算法 V2版本
        @param auth_info: 授权信息
        @param oss_file: 待处理的文件(图片或视频)
        @param process:图片缩放参数,仅在file_type为`IMAGE` 时有效
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


class SnaptobookCorrect(AlgoBase):
    __algo_name__ = 'snaptobook_correct'
    DEFAULT_TIMEOUT = 30

    def __init__(self,
                 auth_info: AuthInfo,
                 oss_file: FileInfo,
                 process=None,
                 custom_data=None,
                 callback_url=None,
                 **kwargs):
        """
        Snaptobook 用的发票矫正算法
        @param auth_info: 授权信息
        @param oss_file: 待处理的文件(图片或视频)
        @param process:图片缩放参数,仅在file_type为`IMAGE` 时有效
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