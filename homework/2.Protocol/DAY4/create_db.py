from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pathlib import Path

# 数据库文件在脚本所在目录生成（确保crontab环境下路径一致）
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'sqlalchemy_syslog_sqlite3.db'

# 创建SQLite数据库引擎
# check_same_thread=False：允许多线程访问
engine = create_engine(f'sqlite:///{DB_PATH}',
                       connect_args={'check_same_thread': False})

# 创建ORM基类
Base = declarative_base()

# 创建会话工厂：用于生成数据库会话
Session = sessionmaker(bind=engine)


class RouterMonitor(Base):
    """路由器监控表：记录CPU和内存利用率"""
    # 表名
    __tablename__ = 'router_monitor'
    
    # 字段定义
    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键，自增
    device_ip = Column(String(64), nullable=False)              # 设备IP地址
    cpu_useage_percent = Column(Integer, nullable=False)        # CPU利用率百分比
    mem_use = Column(Integer, nullable=False)                    # 已用内存（字节）
    mem_free = Column(Integer, nullable=False)                   # 空闲内存（字节）
    record_datetime = Column(DateTime, default=datetime.now)    # 记录时间，自动取当前时间

    def __repr__(self):
        """打印对象时的字符串表示"""
        return (f"<RouterMonitor(device_ip='{self.device_ip}', "
                f"cpu={self.cpu_useage_percent}%, "
                f"mem_use={self.mem_use}, mem_free={self.mem_free}, "
                f"time={self.record_datetime})>")


if __name__ == '__main__':
    # 创建所有表（如果不存在）
    Base.metadata.create_all(engine, checkfirst=True)
    print(f"[*] 数据库表创建成功！")
    print(f"[*] 数据库文件路径: {DB_PATH}")