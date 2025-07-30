from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class SupperResolution(AlgoBase):
    __algo_name__ = 'supper_resolution'

    def __init__(self,
                 auth_info: AuthInfo,
                 oss_file: FileInfo,
                 resolution=2,
                 process=None,
                 custom_data=None,
                 **kwargs
                 ):
        """
        去水印产品的图像超分算法
            文档见 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/op5vr04wd9yvvekt
        @param auth_info:个人权限配置参数
        @param oss_file: 需要处理的图片
        @param resolution: 分辨率的倍数,取值为2或4
        @param process: 缩放规则
        @param custom_data: 自定义参数
        @param kwargs: 补充参数
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['resolution'] = resolution
        self.request['process'] = process
        self.request['custom_data'] = custom_data
        self.request.update(kwargs)
