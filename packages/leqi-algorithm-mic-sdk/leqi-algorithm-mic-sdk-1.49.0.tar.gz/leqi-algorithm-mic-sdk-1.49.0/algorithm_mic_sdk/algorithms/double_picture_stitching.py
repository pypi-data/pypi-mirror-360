from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class DoublePictureStitchingMic(AlgoBase):
    __algo_name__ = 'double_picture_stitching'

    def __init__(self, auth_info: AuthInfo, oss_file_female: FileInfo, oss_file_male: FileInfo, spec_info: dict,
                 feature_points: dict, process=None, **kwargs):
        """
        双人图像拼合 Mic部署方案
            文档地址: https://www.yuque.com/fenfendeyouzhiqingnian/algo/ym4h9n
        @param auth_info:
        @param oss_file_female: 女性图片
        @param oss_file_male: 男性图片
        @param spec_info: 规格信息
        @param feature_points: 人脸特征参数
        @param process: 缩放参数
        @param kwargs: 附加信息
        """
        super().__init__(auth_info)
        self.request['oss_file_female'] = oss_file_female
        self.request['process'] = process
        self.request['oss_file_male'] = oss_file_male
        self.request['spec_info'] = spec_info
        self.request['feature_points'] = feature_points
        self.request.update(kwargs)


class DoublePictureStitching(DoublePictureStitchingMic):
    """
    双人图像拼合 经典服务器部署方案
    """
    _has_classic = True
