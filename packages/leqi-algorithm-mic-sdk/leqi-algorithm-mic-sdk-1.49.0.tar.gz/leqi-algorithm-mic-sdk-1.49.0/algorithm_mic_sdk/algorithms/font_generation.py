from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class FontGeneration(AlgoBase):
    __algo_name__ = 'font_generation'

    def __init__(self,
                 auth_info: AuthInfo,
                 oss_file: FileInfo,
                 process=None,
                 custom_data=None,
                 **kwargs
                 ):
        """
        字体生成算法
            文档见 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/va9f8v0dk7nw3l8e
        @param auth_info:个人权限配置参数
        @param oss_file: 带有文字的图片
        @param process: 缩放规则
        @param custom_data: 自定义参数
        @param kwargs: 补充参数
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request.update(kwargs)
