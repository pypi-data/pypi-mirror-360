from typing import Dict

from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class ReplaceHair(AlgoBase):
    __algo_name__ = 'replace_hair'

    def __init__(self, auth_info: AuthInfo, oss_file: FileInfo, styles, process=None, need_cache=True,
                 custom_data=None, **kwargs):
        """
        换发算法
            文档见 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/rwibgpgc8d7k6584
        @param auth_info:个人权限配置参数
        @param oss_file:文件对象,FileInfo对象
        @param process:图片缩放参数
        @param need_cache:是否使用缓存
        @param styles:风格类型列表
        @param custom_data:自定义参数,将会随着响应参数原样返回
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request['need_cache'] = need_cache
        self.request['styles'] = styles
        self.request.update(kwargs)


class SeniorBeautyAIGC(AlgoBase):
    __algo_name__ = 'senior_beauty_aigc'
    DEFAULT_TIMEOUT = 180

    def __init__(self, auth_info: AuthInfo, oss_file: FileInfo, specific, clothes: Dict = None, process=None,
                 need_cache=True,
                 custom_data=None, **kwargs):
        """
        基于AIGC的人像高级精修算法
            文档见 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/yb4kvgzpp2fh6qtm
        @param auth_info:个人权限配置参数
        @param oss_file:文件对象,FileInfo对象
        @param process:图片缩放参数
        @param need_cache:是否使用缓存
        @param specific:美颜类型
        @param clothes:服装
        @param custom_data:自定义参数,将会随着响应参数原样返回
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request['need_cache'] = need_cache
        self.request['specific'] = specific
        self.request['clothes'] = clothes
        self.request.update(kwargs)


class SeniorBeautyAIGCDress(AlgoBase):
    __algo_name__ = 'senior_beauty_aigc_dress'
    DEFAULT_TIMEOUT = 180

    def __init__(self,
                 auth_info: AuthInfo,
                 cache0_im_oss_name: FileInfo,
                 cache1_im_oss_name: FileInfo,
                 clothes: Dict,
                 specific=None,
                 process=None,
                 need_cache=True,
                 custom_data=None,
                 **kwargs
                 ):
        """
        基于AIGC的人像换装算法,需要依据senior_beauty_aigc算法的结果
            文档见 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/yb4kvgzpp2fh6qtm
        @param auth_info:个人权限配置参数
        @param cache0_im_oss_name:文件对象,FileInfo对象
        @param cache1_im_oss_name:文件对象,FileInfo对象
        @param process:图片缩放参数
        @param need_cache:是否使用缓存
        @param specific:美颜类型
        @param clothes:服装
        @param custom_data:自定义参数,将会随着响应参数原样返回
        """
        super().__init__(auth_info)
        self.request['cache0_im_oss_name'] = cache0_im_oss_name.get_oss_name(self)
        self.request['cache1_im_oss_name'] = cache1_im_oss_name.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request['need_cache'] = need_cache
        self.request['specific'] = specific
        self.request['clothes'] = clothes
        self.request.update(kwargs)


class PhotoTransferHair(AlgoBase):
    __algo_name__ = 'photo_transfer_hair'

    def __init__(self, auth_info: AuthInfo, oss_file: FileInfo, hair_style, process=None, need_cache=True,
                 custom_data=None, **kwargs):
        """
        发型转换算法
            文档见 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/wcpdb5g8vzto2vct
        @param auth_info:个人权限配置参数
        @param oss_file:文件对象,FileInfo对象
        @param process:图片缩放参数
        @param need_cache:是否使用缓存
        @param hair_style:发型名称
        @param custom_data:自定义参数,将会随着响应参数原样返回
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request['need_cache'] = need_cache
        self.request['hair_style'] = hair_style
        self.request.update(kwargs)
