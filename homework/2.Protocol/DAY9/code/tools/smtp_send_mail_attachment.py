#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 9 - 支持附件的邮件发送工具"""

import os
import smtplib
import email.utils
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def qyt_smtp_attachment(mailserver, username, password, from_mail, to_mail, subj, main_body, files=None):
    """使用 SSL SMTP 发送带正文和附件的邮件。"""
    tos = [mail.strip() for mail in to_mail.split(';') if mail.strip()]
    date = email.utils.formatdate()
    msg = MIMEMultipart()
    msg['Subject'] = subj
    msg['From'] = from_mail
    msg['To'] = to_mail
    msg['Date'] = date

    part = MIMEText(main_body, _subtype='plain', _charset='utf-8')
    msg.attach(part)

    if files:
        for file in files:
            with open(file, 'rb') as file_obj:
                part = MIMEApplication(file_obj.read())

            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            msg.attach(part)

    server = smtplib.SMTP_SSL(mailserver, 465)
    server.login(username, password)
    failed = server.sendmail(from_mail, tos, msg.as_string())
    server.quit()

    if failed:
        print(f'[-] Falied recipients: {failed}')
    else:
        print('[+] 邮件已经成功发出！')


if __name__ == '__main__':
    print('请在主程序中调用 qyt_smtp_attachment() 发送邮件。')
