# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 企微通知封装
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
from json import JSONDecodeError

import requests

from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0018, ERROR_MSG_0014
from ..models import WeChatNoticeModel, TestReportModel


class WeChatSend:
    def __init__(self,
                 notice_config: WeChatNoticeModel,
                 test_report: TestReportModel | None = None,
                 domain_name: str = None,
                 content: str = None):
        self.notice_config = notice_config
        self.test_report = test_report
        self.domain_name = domain_name
        self.content = content
        self.headers = {"Content-Type": "application/json"}

    def send_wechat_notification(self):
        if self.test_report.test_suite_id:
            text = f"""【芒果测试平台通知】
                        >测试项目：<font color=\"info\">{self.test_report.project_name}</font>
                        >测试环境：{self.test_report.test_environment}
                        >测试套ID：{self.test_report.test_suite_id}
                        >
                        > **执行结果**
                        ><font color=\"info\">成  功  率  : {self.test_report.success_rate}%</font>
                        >执行用例数：<font color=\"info\">{self.test_report.case_sum}</font>                                    
                        >成功用例数：<font color=\"info\">{self.test_report.success}</font>
                        >失败用例数：`{self.test_report.fail}个`
                        >异常用例数：`0 个`
                        >跳过用例数：<font color=\"warning\">0</font>
                        >用例执行时长：<font color=\"warning\">{self.test_report.execution_duration} s</font>
                        >测试时间：<font color=\"comment\">{self.test_report.test_time}</font>
                        >
                        >非相关负责人员可忽略此消息。
                        >测试报告，点击查看>>[测试报告入口]({self.domain_name})
                   """
        else:
            text = f"""【芒果测试平台通知】
                        >测试项目：<font color=\"info\">{self.test_report.project_name}</font>
                        >测试环境：{self.test_report.test_environment}
                        >
                        > **执行结果**
                        ><font color=\"info\">成  功  率  : {self.test_report.success_rate}%</font>
                        >执行用例数：<font color=\"info\">{self.test_report.case_sum}</font>                                    
                        >成功用例数：<font color=\"info\">{self.test_report.success}</font>
                        >失败用例数：`{self.test_report.fail}个`
                        >异常用例数：`0 个`
                        >跳过用例数：<font color=\"warning\">0</font>
                        >用例执行时长：<font color=\"warning\">{self.test_report.execution_duration} s</font>
                        >测试时间：<font color=\"comment\">{self.test_report.test_time}</font>
                        >
                        >非相关负责人员可忽略此消息。
                        >测试报告，点击查看>>[测试报告入口]({self.domain_name})
                   """
        self.send_markdown(text)

    def send_markdown(self, content):
        res = requests.post(
            url=self.notice_config.webhook,
            json={"msgtype": "markdown", "markdown": {"content": self.content if self.content else content}},
            headers=self.headers,
            proxies={'http': None, 'https': None}
        )
        try:
            if res.json()['errcode'] != 0:
                raise MangoToolsError(*ERROR_MSG_0018)
        except JSONDecodeError:
            raise MangoToolsError(*ERROR_MSG_0018)

    def send_file_msg(self, file):
        res = requests.post(
            url=self.notice_config.webhook,
            json={"msgtype": "file", "file": {"media_id": self.__upload_file(file)}},
            headers=self.headers,
            proxies={'http': None, 'https': None}
        )
        if res.json()['errcode'] != 0:
            raise MangoToolsError(*ERROR_MSG_0014)

    def __upload_file(self, file):
        data = {"file": open(file, "rb")}
        res = requests.post(
            url=self.notice_config.webhook,
            files=data,
            proxies={'http': None, 'https': None}
        ).json()
        return res['media_id']

    def send_text(self, content, mentioned_mobile_list=None):
        if mentioned_mobile_list is None or isinstance(mentioned_mobile_list, list):
            if len(mentioned_mobile_list) >= 1:
                for i in mentioned_mobile_list:
                    if isinstance(i, str):
                        res = requests.post(
                            url=self.notice_config.webhook,
                            json={
                                "msgtype": "text",
                                "text": {
                                    "content": self.content if self.content else content,
                                    "mentioned_list": None,
                                    "mentioned_mobile_list": mentioned_mobile_list
                                }
                            },
                            headers=self.headers,
                            proxies={'http': None, 'https': None}
                        )
                        if res.json()['errcode'] != 0:
                            raise MangoToolsError(*ERROR_MSG_0014)

                    else:
                        raise MangoToolsError(*ERROR_MSG_0014)
        else:
            raise MangoToolsError(*ERROR_MSG_0014)
