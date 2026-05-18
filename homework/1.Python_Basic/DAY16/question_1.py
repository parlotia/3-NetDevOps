'''
路由器配置变更监控 + ORM 存储
综合运用 paramiko、hashlib、SQLAlchemy ORM，每隔 5 秒从路由器采集一次 show running-config， 计算配置的 SHA256 哈希值并存入 SQLite 数据库，与上一次哈希比较，若发现配置变化则打印告警。

数据库模型字段：

id：主键，自动递增
router_ip：路由器 IP（带索引）
router_config：完整配置文本
config_hash：SHA256 哈希值（64位十六进制字符串）
record_time：采集时间，自动填写当前时间
代码框架参考（使用你自己的设备 IP / 账户填入）：

import sys, os, hashlib, time, datetime, re

# ---- 1. 复用第12天的 qytang_multicmd ----
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from day12.day12_task01_multicmd import qytang_multicmd  # noqa: E402

# ---- 2. SQLAlchemy ORM ----
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///router_config.db',
                       connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)


class RouterConfig(Base):
    """路由器配置备份模型"""
    __tablename__ = 'router_config'
    id            = Column(Integer, primary_key=True)
    router_ip     = Column(String(64),    nullable=False, index=True)
    router_config = Column(String(99999), nullable=False)
    config_hash   = Column(String(500),   nullable=False)
    record_time   = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"路由器IP地址: {self.router_ip} | "
                f"配置Hash: {self.config_hash} | "
                f"记录时间: {self.record_time})")


Base.metadata.create_all(engine, checkfirst=True)


# ---- 3. 工具函数 ----
def get_show_run(host, username, password):
    """获取配置并计算 hash"""
    raw = qytang_multicmd(host, username, password,
                          ['terminal length 0', 'show running-config'],
                          verbose=False)
    match = re.search(r'(hostname[\s\S]+end)', raw)
    config = ???                       # 从 match 中取出配置文本
    config_hash = hashlib.sha256(???).hexdigest()   # 对配置文本做 SHA256
    return config, config_hash


def save_config(host, config, config_hash):
    """写入数据库（使用独立 session，避免事务残留）"""
    with Session() as session:
        record = RouterConfig(router_ip=???, router_config=???, config_hash=???)
        session.add(record)
        session.commit()


def get_latest_two_hashes(host):
    """查询最近两条记录"""
    with Session() as session:
        results = (session.query(RouterConfig)
                   .filter(???)            # 按 router_ip 过滤
                   .order_by(RouterConfig.id.desc())
                   .limit(2)
                   .all())
        return results


# ---- 4. 主循环 ----
if __name__ == '__main__':
    host     = '192.168.1.1'       # 换成自己的路由器
    username = 'admin'
    password = 'your_password'

    print(f"[*] 开始监控 {host} 的配置变化，每 5 秒采集一次...\n")
    while True:
        config, config_hash = get_show_run(host, username, password)
        save_config(host, config, config_hash)
        records = get_latest_two_hashes(host)

        if len(records) < 2:
            print(f"本次采集的HASH:{config_hash}")
        elif records[0].config_hash == records[1].config_hash:
            ???    # 配置无变化，打印本次 hash
        else:
            ???    # 配置有变化，打印告警及前后两次 hash
        time.sleep(5)
期望输出（完整测试，包含配置变化检测）：

[*] 开始监控 192.168.1.1 的配置变化，每 5 秒采集一次...

本次采集的HASH:536069dceadf7e32ba15a7c5ea715b30b09b2ae177e477a6378491853ce8dfb7
本次采集的HASH:536069dceadf7e32ba15a7c5ea715b30b09b2ae177e477a6378491853ce8dfb7
==========配置发生变化==========
  THE MOST RECENT HASH  c10b9fc96f2409317dcc13c089f914193a9710e270ac39cbe5f00ad39b840658
  THE LAST HASH         536069dceadf7e32ba15a7c5ea715b30b09b2ae177e477a6378491853ce8dfb7
本次采集的HASH:c10b9fc96f2409317dcc13c089f914193a9710e270ac39cbe5f00ad39b840658
==========配置发生变化==========
  THE MOST RECENT HASH  c0c87167b2ef1c2cbad27ab532d2ba7325a8a645bd6662a836475762a906bf18
  THE LAST HASH         c10b9fc96f2409317dcc13c089f914193a9710e270ac39cbe5f00ad39b840658
==========配置发生变化==========
  THE MOST RECENT HASH  536069dceadf7e32ba15a7c5ea715b30b09b2ae177e477a6378491853ce8dfb7
  THE LAST HASH         c0c87167b2ef1c2cbad27ab532d2ba7325a8a645bd6662a836475762a906bf18
本次采集的HASH:536069dceadf7e32ba15a7c5ea715b30b09b2ae177e477a6378491853ce8dfb7
本次采集的HASH:536069dceadf7e32ba15a7c5ea715b30b09b2ae177e477a6378491853ce8dfb7
提示：

需要先安装 SQLAlchemy：pip install sqlalchemy
第12天的 qytang_multicmd 需要能返回命令输出，确认该函数有 return all_output
使用 re.search(r'(hostname[\s\S]+end)', raw) 提取有效配置段
hashlib.sha256(text.encode('utf-8')).hexdigest() 计算哈希
每次操作数据库使用独立的 with Session() as session:，避免事务残留导致写入失败
'''

import sys, os, hashlib, time, datetime, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DAY12.question_1 import qytang_multicmd  # noqa: E402

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///router_config.db',
                       connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)


class RouterConfig(Base):
    __tablename__ = 'router_config'
    id            = Column(Integer, primary_key=True)
    router_ip     = Column(String(64),    nullable=False, index=True)
    router_config = Column(String(99999), nullable=False)
    config_hash   = Column(String(500),   nullable=False)
    record_time   = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"路由器IP地址: {self.router_ip} | "
                f"配置Hash: {self.config_hash} | "
                f"记录时间: {self.record_time})")


Base.metadata.create_all(engine, checkfirst=True)


def get_show_run(host, username, password):
    raw = qytang_multicmd(host, username, password,
                          ['terminal length 0', 'show running-config'],
                          verbose=False)
    match = re.search(r'(hostname[\s\S]+end)', raw)
    config = match.group(1) if match else raw
    config_hash = hashlib.sha256(config.encode('utf-8')).hexdigest()
    return config, config_hash


def save_config(host, config, config_hash):
    with Session() as session:
        record = RouterConfig(
            router_ip=host,
            router_config=config,
            config_hash=config_hash
        )
        session.add(record)
        session.commit()


def get_latest_two_hashes(host):
    with Session() as session:
        results = (session.query(RouterConfig)
                   .filter(RouterConfig.router_ip == host)
                   .order_by(RouterConfig.id.desc())
                   .limit(2)
                   .all())
        return results


if __name__ == '__main__':
    host     = '10.10.1.200'
    username = 'admin'
    password = 'Cisc0123'

    print(f"[*] 开始监控 {host} 的配置变化，每 5 秒采集一次...\n")
    while True:
        config, config_hash = get_show_run(host, username, password)
        save_config(host, config, config_hash)
        records = get_latest_two_hashes(host)

        if len(records) < 2:
            print(f"本次采集的HASH:{config_hash}")
        elif records[0].config_hash == records[1].config_hash:
            print(f"本次采集的HASH:{config_hash}")
        else:
            print("==========配置发生变化==========")
            print(f"  THE MOST RECENT HASH  {records[0].config_hash}")
            print(f"  THE LAST HASH         {records[1].config_hash}")
        
        time.sleep(5)