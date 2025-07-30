# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 邮箱通知封装
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from socket import gaierror

from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0016
from ..models import EmailNoticeModel, TestReportModel


class EmailSend:

    def __init__(self, notice_config: EmailNoticeModel, test_report: TestReportModel = None, domain_name: str = None,
                 content: str = None):
        self.test_report = test_report
        self.notice_config = notice_config
        self.domain_name = domain_name
        self.content = content

    def send_main(self) -> None:
        if self.test_report.test_suite_id:
            content = f"""
            各位同事, 大家好:
                测试套ID：{self.test_report.test_suite_id}任务执行完成，执行结果如下:
                用例运行总数: {self.test_report.case_sum} 个
                通过用例个数: {self.test_report.success} 个
                失败用例个数: {self.test_report.fail} 个
                异常用例个数: {self.test_report.warning} 个
                跳过用例个数: 暂不统计 个
                成  功   率: {self.test_report.success_rate} %
    
    
            **********************************
            芒果自动化平台地址：{self.domain_name}
            详细情况可前往芒果自动化平台查看，非相关负责人员可忽略此消息。谢谢！
            """
        else:
            content = f"""
            各位同事, 大家好:
                用例运行总数: {self.test_report.case_sum} 个
                通过用例个数: {self.test_report.success} 个
                失败用例个数: {self.test_report.fail} 个
                异常用例个数: {self.test_report.warning} 个
                跳过用例个数: 暂不统计 个
                成  功   率: {self.test_report.success_rate} %


            **********************************
            芒果自动化平台地址：{self.domain_name}
            详细情况可前往芒果自动化平台查看，非相关负责人员可忽略此消息。谢谢！
            """
        self.send_mail(self.notice_config.send_list, f'【芒果测试平台通知】', content)

    def send_mail(self, user_list: list, sub: str, content: str, ) -> None:
        try:
            user = f"MangoTestPlatform <{self.notice_config.send_user}>"
            msg = MIMEMultipart()
            msg['From'] = user
            msg['To'] = ";".join(user_list)
            msg['Subject'] = sub
            msg.attach(MIMEText(self.content if self.content else content, 'plain'))
            with smtplib.SMTP(self.notice_config.email_host, ) as server:
                server.starttls()
                server.login(self.notice_config.send_user, self.notice_config.stamp_key)
                server.sendmail(user, user_list, msg.as_string())
                server.quit()
        except (gaierror, smtplib.SMTPServerDisconnected):
            raise MangoToolsError(*ERROR_MSG_0016)
