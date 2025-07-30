from ..auth import AuthInfo
from ..base import AlgoBase
from ..tools import FileInfo


class ExtractFaceFeatureV2Mic(AlgoBase):
    __algo_name__ = 'extract_face_feature_v2'

    def __init__(self, auth_info: AuthInfo, oss_file: FileInfo, process=None, liveness_threshold=None, **kwargs):
        """
        人脸特征提取V2(用于考勤项目)
            文档地址: https://www.yuque.com/fenfendeyouzhiqingnian/algo/cbmiiz
        @param auth_info:
        @param oss_file: 文件名
        @param process:缩放参数
        @param liveness_threshold:活体检测阈值
        @param kwargs:
        """
        super().__init__(auth_info)
        self.request['oss_file'] = oss_file
        self.request['process'] = process
        self.request['liveness_threshold'] = liveness_threshold
        self.request.update(kwargs)


class ExtractFaceFeatureV2(ExtractFaceFeatureV2Mic):
    """
    人脸特征提取V2(经典服务器部署方案)
    """
    _has_classic = True
