"""
企业微信API接口

网址：https://developer.work.weixin.qq.com

注：上传文件需要 requests-toolbelt
"""

import os
import json
import time
import datetime
import hashlib
import random
from pathlib import Path
from pprint import pprint as pp

import requests

from requests import Response
# from requests_toolbelt import MultipartEncoder
from urllib.parse import urlparse, unquote

from .utils import BaseClient

HEADERS_JSON = {
    'authorization': '',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'content-type': 'application/json;charset=UTF-8',
    'accept-language': 'zh-CN,zh;q=0.9'
}


class QYWeiXin(BaseClient):
    access_token: str = None
    access_token_expires_time: datetime.datetime = None
    token_file_path: str = 'access_token.json'

    def __init__(self, appid: str = '', corpid: str = '', corpsecret: str = '', base_url: str = 'https://qyapi.weixin.qq.com', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        """
        初始化接口
        """
        self.corpid = corpid  # 企业 ID
        self.appid = appid  # 应用程序 ID (企业微信网页后台应用管理界面的 AgentId)
        self.corpsecret = corpsecret  # 应用 Secret (企业微信网页后台应用管理界面的 Secret)
        self.base_url = base_url
        self.access_token = None
        self.set_headers(HEADERS_JSON)
        self.data = {}
        self.load_access_token_from_file()

    def load_access_token_from_file(self):
        if os.path.exists(self.token_file_path):
            with open(self.token_file_path, 'r') as f:
                data = json.load(f)
                expires_time = datetime.datetime.strptime(data['expires_time'], "%Y-%m-%d %H:%M:%S")
                if datetime.datetime.now() < expires_time:
                    self.access_token = data['access_token']
                    self.access_token_expires_time = expires_time

    def save_access_token_to_file(self, access_token: str, expires_time: datetime.datetime):
        data = {
            'access_token': access_token,
            'expires_time': expires_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(self.token_file_path, 'w') as f:
            json.dump(data, f)

    def get_access_token(self) -> str:
        """
        获取企业微信应用 token

        Returns
        -------
        str
            企业微信程序 token

        Raises
        ------
        Exception
            当无法获取 token 时

        """
        if self.access_token_expires_time and self.access_token and datetime.datetime.now() < self.access_token_expires_time:
            return self.access_token

        params = {
            'corpid': self.corpid,
            'corpsecret': self.corpsecret

        }
        url = f'{self.base_url}/cgi-bin/gettoken'
        response = self._session.get(url, params=params)
        r: dict = response.json()
        access_token = r.get('access_token')
        if access_token is None:
            raise Exception('获取 token 失败 请确保相关信息填写的正确性')

        expires_in = r.get('expires_in')
        expires_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in - 60)
        self.access_token = access_token
        self.access_token_expires_time = expires_time

        # 保存 access_token 和过期时间到文件
        self.save_access_token_to_file(access_token, expires_time)
        return access_token

    def get_response_data(self, resp):
        """
        解析接口返回的数据
        """
        try:
            self.data = resp.json()
        except Exception as e:
            return {
                "code": 88888888,
                "data": {
                    "description": f"转换json数据失败：{e}",
                    "error_code": 88888888,
                }
            }

        # 我们不检查信息是否错误，在获取信息的时候在检查
        # if self.data['code'] != 200:
        #     raise ValueError(f'{self.data}')

        return self.data

    def get_template_detail(self, template_id: str) -> dict:
        """
        获取审批模板详情

        请求方式：POST（HTTPS）
        请求地址：https://qyapi.weixin.qq.com/cgi-bin/oa/gettemplatedetail?access_token=ACCESS_TOKEN
        文档地址：https://developer.work.weixin.qq.com/document/path/91982
        """
        params = {
            'template_id': template_id,
        }
        url = f'{self.base_url}/cgi-bin/oa/gettemplatedetail?access_token={self.access_token}'
        r = self._session.post(url, json=params)
        return self.get_response_data(r)

    def get_approval_info(self, starttime: str, endtime: str, new_cursor: str = '', size: int = 100, filters: list = None, ) -> dict:
        """
        批量获取审批单号

        通过本接口可以获取企业一段时间内企业微信“审批应用”单据的审批编号，支持按模板类型、申请人、部门、申请单审批状态等条件筛选。
        自建应用调用此接口，需在“管理后台-应用管理-审批-API-审批数据权限”中，授权应用允许提交审批单据。

        一次拉取调用最多拉取100个审批记录，可以通过多次拉取的方式来满足需求，但调用频率不可超过600次/分。

        # 筛选条件，可对批量拉取的审批申请设置约束条件，支持设置多个条件
        # 注意:
        # 1、仅“部门”支持同时配置多个筛选条件。
        # 2、不同类型的筛选条件之间为“与”的关系，同类型筛选条件之间为“或”的关系
        # 3、record_type筛选类型仅支持2021/05/31以后新提交的审批单，历史单不支持表单类型属性过滤
        "filters": [
            {
                "key": "template_id",  # 模板id
                "value": "ZLqk8pcsAoaXZ1eY56vpAgfX28MPdYU3ayMaSPHaaa"
            },
            {
                "key": "creator",  # 申请人userid
                "value": "WuJunJie"
            },
            {
                "key": "department",  # 所在部门id
                "value": "1"
            },
            {
                "key": "sp_status",  # 审批单状态（1-审批中；2-已通过；3-已驳回；4-已撤销；6-通过后撤销；7-已删除；10-已支付）
                "value": "1"
            },
            {
                "key": "record_type",  # 审批单类型属性，1-请假；2-打卡补卡；3-出差；4-外出；5-加班； 6- 调班；7-会议室预定；8-退款审批；9-红包报销审批
                "value": "1"
            },
        ]

        请求方式：POST（HTTPS）
        请求地址：https://qyapi.weixin.qq.com/cgi-bin/oa/getapprovalinfo?access_token=ACCESS_TOKEN
        文档地址：https://developer.work.weixin.qq.com/document/path/91816
        """
        params = {
            'starttime': starttime,  # 必填 审批单提交的时间范围，开始时间，UNix时间戳
            'endtime': endtime,  # 必填 审批单提交的时间范围，结束时间，Unix时间戳
            'new_cursor': new_cursor,  # 必填 分页查询游标，默认为空串，后续使用返回的new_next_cursor进行分页拉取
            'size': size,  # 一次请求拉取审批单数量，默认值为100，上限值为100。若accesstoken为自建应用，仅允许获取在应用可见范围内申请人提交的表单，返回的sp_no_list个数可能和size不一致，开发者需用next_cursor判断表单记录是否拉取完
        }
        if filters:
            params['filters'] = filters
        url = f'{self.base_url}/cgi-bin/oa/getapprovalinfo?access_token={self.access_token}'
        r = self._session.post(url, json=params)
        return self.get_response_data(r)

    def get_approval_detail(self, sp_no: str) -> dict:
        """
        获取审批申请详情

        请求方式：POST（HTTPS）
        请求地址： https://qyapi.weixin.qq.com/cgi-bin/oa/getapprovaldetail?access_token=ACCESS_TOKEN
        文档地址：https://developer.work.weixin.qq.com/document/path/91983
        """
        params = {
            'sp_no': sp_no  # 审批单编号
        }
        url = f'{self.base_url}/cgi-bin/oa/getapprovaldetail?access_token={self.access_token}'
        r = self._session.post(url, json=params)
        return self.get_response_data(r)

    def get_user_vacation_quota(self, userid: str) -> dict:
        """
        获取成员假期余额

        通过本接口可获取应用可见范围内各个员工的假期余额数据

        请求方式：POST(HTTPS)
        请求地址：https://qyapi.weixin.qq.com/cgi-bin/oa/vacation/getuservacationquota?access_token=ACCESS_TOKEN
        文档地址：https://developer.work.weixin.qq.com/document/path/93376
        """
        params = {
            'userid': userid  # 需要获取假期余额的成员的userid
        }
        url = f'{self.base_url}/cgi-bin/oa/vacation/getuservacationquota?access_token={self.access_token}'
        r = self._session.post(url, json=params)
        return self.get_response_data(r)

    def set_one_user_quota(self, userid: str, vacation_id: int, leftduration: int, time_attr: int = 1, remarks: str = '') -> dict:
        """
        修改成员假期余额

        通过本接口可以修改可见范围内员工的“假期余额”

        请求方式：POST(HTTPS)
        请求地址：https://qyapi.weixin.qq.com/cgi-bin/oa/vacation/setoneuserquota?access_token=ACCESS_TOKEN
        文档地址：https://developer.work.weixin.qq.com/document/path/93377
        """
        # raise ValueError('因为我们使用了正式环境，暂时禁用修改操作！')
        params = {
            'userid': userid,  # 必填 需要修改假期余额的成员的userid
            'vacation_id': vacation_id,  # 必填 假期id
            'leftduration': leftduration,  # 必填 设置的假期余额,单位为秒。不能大于1000天或24000小时，当假期时间刻度为按小时请假时，必须为360整倍数，即0.1小时整倍数，按天请假时，必须为8640整倍数，即0.1天整倍数
            'time_attr': time_attr,  # 必填 假期时间刻度：0-按天请假；1-按小时请假，主要用于校验，必须等于企业假期管理配置中设置的假期时间刻度类型
            'remarks': remarks  # 修改备注，用于显示在假期余额的修改记录当中，可对修改行为作说明，不超过200字符
        }
        url = f'{self.base_url}/cgi-bin/oa/vacation/setoneuserquota?access_token={self.access_token}'
        r = self._session.post(url, json=params)
        return self.get_response_data(r)
