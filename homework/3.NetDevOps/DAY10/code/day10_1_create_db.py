#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""
DAY10 - 数据库模型创建脚本
创建 pyats_ospf 表用于存储 OSPF 状态和路由表信息
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import declarative_base

# 当前文件目录
current_dir = os.path.dirname(os.path.realpath(__file__))

# 固定数据库文件位置，与当前文件相同目录
db_file_name = f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}sqlalchemy_pyats.db'

# 创建数据库引擎
engine = create_engine(f'sqlite:///{db_file_name}?check_same_thread=False')

# 创建基类
Base = declarative_base()


# 记录OSPF和路由状态
class PyatsOSPF(Base):
    __tablename__ = 'pyats_ospf'

    id = Column(Integer, primary_key=True)                    # 唯一ID，主键
    device_name = Column(String(64), nullable=False)          # 设备名称
    device_ip = Column(String(64), nullable=False)            # 设备IP地址
    ospf_status = Column(JSON, nullable=False)                # OSPF状态
    route_table_status = Column(JSON, nullable=False)         # 路由表状态
    # 记录时间
    record_datetime = Column(DateTime(timezone='Asia/Chongqing'), default=datetime.now)

    def __repr__(self):
        return f"{self.__class__.__name__}(Device_Name: {self.device_name} " \
               f"| Device_IP: {self.device_ip} " \
               f"| Datetime: {self.record_datetime})"


if __name__ == '__main__':
    # 如果老数据库文件存在就删除
    if os.path.exists(db_file_name):
        os.remove(db_file_name)
        print(f'[!] 已删除旧数据库文件: {db_file_name}')
    
    # checkfirst=True, 表示创建表前先检查该表是否存在，如同名表已存在则不再创建。其实默认就是True
    Base.metadata.create_all(engine, checkfirst=True)
    print(f'[+] 数据库表 pyats_ospf 创建成功: {db_file_name}')
