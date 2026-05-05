from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, BigInteger
import datetime
import os

db_file_name = f'{os.path.dirname(os.path.realpath(__file__))}{os.path.sep}sqlalchemy_interface_sqlite3.db'

engine = create_engine(f'sqlite:///{db_file_name}?check_same_thread=False')

Base = declarative_base()


# 记录路由器接口信息数据库表
class InternfaceMonitor(Base):
    __tablename__ = 'interface_monitor'

    id              = Column(Integer, primary_key=True)
    device_ip       = Column(String(64), nullable=False)         # 设备IP地址
    interface_name  = Column(String(64), nullable=False)         # 接口名称
    in_bytes        = Column(BigInteger, nullable=False)         # 入向字节数
    out_bytes       = Column(BigInteger, nullable=False)         # 出向字节数
    record_datetime = Column(DateTime(timezone='Asia/Chongqing'), default=datetime.datetime.now)

    def __repr__(self):
        return f"{self.__class__.__name__}(路由器IP: {self.device_ip} " \
               f"| 时间: {self.record_datetime} " \
               f"| 接口名称: {self.interface_name} " \
               f"| 入向字节数: {self.in_bytes} " \
               f"| 出向字节数: {self.out_bytes})"


if __name__ == '__main__':
    if os.path.exists(db_file_name):
        os.remove(db_file_name)
    Base.metadata.create_all(engine, checkfirst=True)
    print(f"[+] 数据库创建成功: {db_file_name}")
