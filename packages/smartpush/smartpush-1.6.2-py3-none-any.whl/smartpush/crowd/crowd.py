from smartpush.base.request_base import CrowdRequestBase
from smartpush.base.url_enum import URL


class Crowd(CrowdRequestBase):

    def callEditCrowdPackage(self, crowdName="", groupRules=None, groupRelation="$AND",
                             triggerStock=False):
        """
        更新群组条件id
        :param triggerStock:
        :param crowdName:
        :param groupRules:
        :param groupRelation:
        :return:
        """
        requestParam = {"id": self.crowd_id, "crowdName": crowdName, "groupRelation": groupRelation,
                        "groupRules": groupRules, "triggerStock": triggerStock}
        result = self.request(method=URL.editCrowdPackage.method, path=URL.editCrowdPackage.url, data=requestParam)
        return result['resultData']

    def callCrowdPersonList(self, page=1, pageSize=20, filter_type=None, filter_value=None):
        """
        获取群组联系人列表
        :param page:
        :param pageSize:
        :param filter_type:
        :param filter_value:
        :return:
        """
        requestParam = {"id": self.crowd_id, "page": page, "pageSize": pageSize}
        if filter_value is not None:
            requestParam["filter"] = {filter_type: {"in": filter_value}}
        result = self.request(method=URL.crowdPersonList.method, path=URL.crowdPersonList.url, data=requestParam)
        resultData = result['resultData']
        return resultData

    def callCrowdPackageDetail(self, page=1, pageSize=20, filter_type=None, filter_value=None):
        """
        获取群组详情
        :param page:
        :param pageSize:
        :param filter_type:
        :param filter_value:
        :return:
        """
        requestParam = {"id": self.crowd_id, "page": page, "pageSize": pageSize, "filter": {}}
        if filter_value is not None:
            requestParam["filter"] = {filter_type: {"in": filter_value}}
        result = self.request(method=URL.crowdPersonList.method, path=URL.crowdPackageDetail.url, data=requestParam)
        resultData = result['resultData']
        return resultData