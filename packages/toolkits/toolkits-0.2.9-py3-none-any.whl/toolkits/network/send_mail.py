#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import pprint
import traceback
from os.path import basename
from exchangelib import Configuration, Account, Credentials, DELEGATE, Message, Mailbox, FileAttachment
from log4python.Log4python import log
import importlib

logger = log("SendMail")
importlib.reload(sys)


class SendMail:
    def __init__(self, username, password, ews_url, primary_smtp_address):
        self.username = username
        self.password = password
        self.ews_url = ews_url
        self.primary_smtp_address = primary_smtp_address
        self.attach_file_list = []
        self.to_recipients = []
        self.cc_recipients = []
        self.bcc_recipients = []
        self.subject = None
        self.body = None
        self.ews_account = self.connect_mail_server()

    def connect_mail_server(self):
        credentials = Credentials(username=self.username, password=self.password)
        config = Configuration(service_endpoint=self.ews_url, credentials=credentials)
        account = Account(primary_smtp_address=self.primary_smtp_address, config=config,
                          autodiscover=False, access_type=DELEGATE)
        return account

    @staticmethod
    def read_file_content(file_path):
        fp = open(file_path, "r+")
        lines = fp.readlines()
        return "".join(lines)

    @staticmethod
    def list_update(list_container, new_data):
        if new_data is not None:
            if type(new_data).__name__ in ["str", "unicode"]:
                list_container.append(new_data)
            else:
                list_container.extend(new_data)
        return list_container

    def mail_receiver(self, to_recipients, cc_recipients=None, bcc_recipients=None):
        self.list_update(self.to_recipients, to_recipients)
        self.list_update(self.cc_recipients, cc_recipients)
        self.list_update(self.bcc_recipients, bcc_recipients)

    def mail_assemble(self, subject, body, attach_file_list=None):
        self.list_update(self.attach_file_list, attach_file_list)
        logger.debug("attach_files:%s" % json.dumps(self.attach_file_list))
        self.subject = subject
        self.body = body

    def mail_send(self, receive_mailer, subject, mail_body, attach_file=None):
        if self.to_recipients is None:
            return False

        self.mail_receiver(receive_mailer)
        if attach_file:
            self.mail_assemble(subject, mail_body, attach_file)
        else:
            self.mail_assemble(subject, mail_body)

        m = Message(
                account=self.ews_account,
                subject=self.subject,
                body=self.body,
                to_recipients=list(set(self.to_recipients)),
                cc_recipients=list(set(self.cc_recipients)),
                bcc_recipients=list(set(self.bcc_recipients))
        )

        for item in self.attach_file_list:
            logger.debug("attach_file:%s" % str(item))
            m.attach(FileAttachment(name=basename(item), content=self.read_file_content(item)))
        m.send()
        return True


if __name__ == '__main__':
    try:
        username = "lijiayue"
        password = "please change to your mail info"
        ews_url = "https://mail.qq.com/EWS/Exchange.asmx"
        receive_mail = "lijiayue@qq.com"
        primary_smtp_address = "lijiayue@qq.com"

        csv_file = "%s/%s" % ("/var/log/", "访问.csv")
        csv_detail_file = "/var/log/test.txt"

        mail = SendMail(username, password, ews_url, primary_smtp_address)
        mail.mail_send(receive_mail, "发现违规访问用户", "\n日期：%s; 人员数量：%s；\n访问，见附件：%s\n详细访问信息，见附件：%s\n\n",
                       [csv_file, csv_detail_file])
    except Exception as ex:
        pprint.pprint("Error: %s" % ex)
        pprint.pprint(traceback.format_exc())
