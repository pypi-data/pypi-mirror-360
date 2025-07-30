from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class ForeignMatterRemovalPro(AlgoBase):
    __algo_name__ = 'foreign_matter_removal_pro'

    def __init__(self, auth_info: AuthInfo, oss_file: FileInfo, mask: FileInfo, process=None, custom_data=None,
                 **kwargs):
        """
        杂物去除算法(升级版)
            文档见 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/irtg5i9vv8vf4fv9
        @param auth_info:个人权限配置参数
        @param oss_file:文件对象,FileInfo对象
        @param mask::文件对象,FileInfo对象
        @param process:缩放规则
        @param single:默认为False
        @param custom_data:自定义参数,将会随着响应参数原样返回
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file.get_oss_name(self)
        self.request['process'] = process
        self.request['mask'] = mask
        self.request['custom_data'] = custom_data
        self.request.update(kwargs)
