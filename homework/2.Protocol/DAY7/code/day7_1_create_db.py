#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

tzutc_8 = datetime.timezone(datetime.timedelta(hours=8))  # 设置时区为东八区

# -------------------------psql-------------------------
# psycopg2 (yum install postgresql-devel;pip3 install psycopg2-binary)

engine = create_engine('postgresql+psycopg2://qytangdbuser:Cisc0123@localhost/qytangdb')

Base = declarative_base()


class Router(Base):
    __tablename__ = 'router'

    id = Column(Integer, primary_key=True)
    router_name = Column(String(64), nullable=False, index=True)
    ip = Column(String(64), nullable=False, index=True)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)

    # ----------接口------------
    interface = relationship('Interface', back_populates="router", passive_deletes=True)

    # ----------OSPF------------
    # uselist=False表示onetoone
    ospf_process = relationship('OSPFProcess', back_populates="router", uselist=False, passive_deletes=True)

    # --------CPU利用率----------
    cpu_usage = relationship('CPUUsage', back_populates="router", passive_deletes=True)

    # --------设备配置-----------
    device_config = relationship('DeviceConfig', back_populates="router", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.router_name})"


class DeviceConfig(Base):
    __tablename__ = 'device_config'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey("router.id", ondelete='CASCADE'), nullable=False)
    device_config = Column(String(99999), nullable=False)
    config_md5 = Column(String(100), nullable=False)
    router = relationship('Router', back_populates="device_config", passive_deletes=True)
    record_time = Column(DateTime(timezone='Asia/Chongqing'), default=datetime.datetime.now)

    def __repr__(self):
        return f"{self.__class__.__name__}(Device IP: {self.router.ip} " \
               f"| Datetime: {self.record_time} " \
               f"| Config MD5: {self.config_md5})"


class Interface(Base):
    __tablename__ = 'interface'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey("router.id", ondelete='CASCADE'), nullable=False)
    interface_name = Column(String(64), nullable=False)
    ip = Column(String(64), nullable=False)
    mask = Column(String(64), nullable=False)
    router = relationship('Router', back_populates="interface", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.router.router_name} "\
               f"| Interface_name: {self.interface_name} " \
               f"| IP: {self.ip} / {self.mask})"


class OSPFProcess(Base):
    __tablename__ = 'ospf_process'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey("router.id", ondelete='CASCADE'), nullable=False)
    processid = Column(Integer, nullable=False)
    routerid = Column(String(64), nullable=False)
    router = relationship('Router', back_populates="ospf_process", passive_deletes=True)
    area = relationship('Area', back_populates="ospf_process", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.router.router_name} " \
               f"| Process: {self.processid})"


class Area(Base):
    __tablename__ = 'area'

    id = Column(Integer, primary_key=True)
    ospfprocess_id = Column(Integer, ForeignKey("ospf_process.id", ondelete='CASCADE'), nullable=False)
    area_id = Column(Integer, nullable=False)
    ospf_process = relationship('OSPFProcess', back_populates="area", passive_deletes=True)
    ospf_network = relationship('OSPFNetwork', back_populates="area", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.ospf_process.router.router_name} " \
               f"| Process: {self.ospf_process.processid} " \
               f"| Area: {self.area_id})"


class OSPFNetwork(Base):
    __tablename__ = 'ospf_network'

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey("area.id", ondelete='CASCADE'), nullable=False)
    network = Column(String(64), nullable=False)
    wildmask = Column(String(64), nullable=False)
    area = relationship('Area', back_populates="ospf_network", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.area.ospf_process.router.router_name} " \
               f"| Process: {self.area.ospf_process.processid} " \
               f"| Area: {self.area.area_id} " \
               f"| Network: {self.network}/{self.wildmask})"


class CPUUsage(Base):
    __tablename__ = 'cpu_usage'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey("router.id", ondelete='CASCADE'), nullable=False)
    cpu_useage_percent = Column(Integer, nullable=False)
    cpu_useage_datetime = Column(DateTime(timezone='Asia/Chongqing'), default=datetime.datetime.now)
    router = relationship('Router', back_populates="cpu_usage", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.router.router_name} " \
               f"| Datetime: {self.cpu_useage_datetime} " \
               f"| Percent: {self.cpu_useage_percent})"


if __name__ == '__main__':
    # checkfirst=True，表示创建表前先检查该表是否存在，如同名表已存在则不再创建。其实默认就是True
    Base.metadata.create_all(engine, checkfirst=True)
