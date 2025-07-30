from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class SwapFace(AlgoBase):
    __algo_name__ = 'swap_face'

    def __init__(self,
                 auth_info: AuthInfo,
                 source_oss_file: FileInfo,
                 target_oss_file: FileInfo,
                 process=None,
                 custom_data=None,
                 **kwargs
                 ):
        """
        换脸算法
            文档见 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/yarkodidvyy19gqx
        @param auth_info:个人权限配置参数
        @param source_oss_file: 需要换脸的原始人像图片
        @param target_oss_file: 换脸的模板图片
        @param process: 缩放规则
        @param custom_data: 自定义参数
        @param kwargs: 补充参数
        """
        super().__init__(auth_info)
        self.request['source_oss_file'] = source_oss_file.get_oss_name(self)
        self.request['target_oss_file'] = target_oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request.update(kwargs)
