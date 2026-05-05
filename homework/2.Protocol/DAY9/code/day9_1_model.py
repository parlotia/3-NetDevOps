#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 9 - 配置备份数据库模型"""

import os
import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'day9_config_backup.db')
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DB_FILE}?check_same_thread=False')

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Device(Base):
    """保存 Day 9 使用的设备清单。"""

    __tablename__ = 'device'

    id = Column(String(64), primary_key=True)
    device_name = Column(String(64), nullable=False, index=True)
    ip = Column(String(64), nullable=False, unique=True, index=True)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    enable_password = Column(String(64), nullable=False)
    transport = Column(String(16), nullable=False, default='ssh')
    config_backups = relationship('ConfigBackup', back_populates='device', passive_deletes=True)

    def __repr__(self):
        return f'{self.__class__.__name__}(device_name={self.device_name}, ip={self.ip})'


class ConfigBackup(Base):
    """保存每次采集到的设备配置和 MD5 值。"""

    __tablename__ = 'config_backup'

    id = Column(String(64), primary_key=True)
    device_id = Column(String(64), ForeignKey('device.id', ondelete='CASCADE'), nullable=False, index=True)
    config_text = Column(Text, nullable=False)
    config_md5 = Column(String(64), nullable=False, index=True)
    backup_time = Column(DateTime, default=datetime.datetime.now, nullable=False, index=True)
    device = relationship('Device', back_populates='config_backups', passive_deletes=True)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(device_ip={self.device.ip}, '
            f'backup_time={self.backup_time}, config_md5={self.config_md5})'
        )
