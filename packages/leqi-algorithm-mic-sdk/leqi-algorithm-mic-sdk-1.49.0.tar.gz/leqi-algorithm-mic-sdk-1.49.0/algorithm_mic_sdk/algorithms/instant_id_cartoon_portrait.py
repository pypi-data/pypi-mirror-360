from typing import List

from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class InstantIDBatchCartoonPortrait(AlgoBase):
    __algo_name__ = 'batch_cartoon_portrait_v2'
    DEFAULT_TIMEOUT = 300

    def __init__(self,
                 auth_info: AuthInfo,
                 oss_file: FileInfo,
                 styles: List[dict],
                 process=None,
                 custom_data=None,
                 callback_url=None,
                 **kwargs):
        """
        基于InstantID的批量头像卡通算法 (AIGC版本)
        @param auth_info: 个人权限配置参数
        @param oss_file: 用户图片
        @param sex: 性别[MALE/FEMALE]
        @param style: 风格,有 ADULT/CHILD 两种
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request['styles'] = styles
        self.request['callback_url'] = callback_url
        self.request.update(kwargs)


class InstantIDCartoonPortrait(AlgoBase):
    __algo_name__ = 'cartoon_portrait_v2'
    DEFAULT_TIMEOUT = 300

    def __init__(self,
                 auth_info: AuthInfo,
                 oss_file: FileInfo,
                 prompt: str,
                 negative_prompt: str,
                 process=None,
                 custom_data=None,
                 callback_url=None,
                 **kwargs):
        """
        基于InstantID的头像卡通算法 (AIGC版本)
        @param auth_info: 个人权限配置参数
        @param oss_file: 用户图片
        @param sex: 性别[MALE/FEMALE]
        @param style: 风格,有 ADULT/CHILD 两种
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request['prompt'] = prompt
        self.request['negative_prompt'] = negative_prompt
        self.request['callback_url'] = callback_url
        self.request.update(kwargs)
