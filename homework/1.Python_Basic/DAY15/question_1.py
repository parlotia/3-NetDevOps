'''
SQLAlchemy ORM 练习：设备 Inventory 系统
使用 SQLAlchemy ORM 制作一个网络设备资产管理系统，将设备信息存入 SQLite 数据库，并实现交互式查询菜单。

数据库模型字段：

id：主键，自动递增
name：设备名称（如 R1、SW1），带索引
type：设备类型（如 router、switch、firewall）
version：系统版本（如 IOS XE 17.14）
location：机房位置（如 Beijing-IDC-A）
create_time：入库时间，自动填写当前时间
代码框架参考：

import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# 创建数据库引擎
engine = create_engine('sqlite:///device_inventory.db?check_same_thread=False',
                       echo=False)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Device(Base):
    __tablename__ = 'devices'

    id          = Column(Integer, primary_key=True)
    name        = Column(String(64), nullable=False, index=True)
    type        = Column(String(64), nullable=False)
    version     = Column(String(64))
    location    = Column(String(128))
    create_time = Column(DateTime(timezone='Asia/Chongqing'), default=datetime.datetime.now)

    def __repr__(self):
        return (f"{self.__class__.__name__}(设备名称: {self.name} | 类型: {self.type} | "
                f"版本: {self.version} | 位置: {self.location} | 入库时间: {self.create_time})")


if __name__ == '__main__':
    # 创建数据库表
    Base.metadata.create_all(engine, checkfirst=True)

    # 只有表为空时才插入初始数据
    if session.query(Device).count() == 0:
        device_list = [
            # ??? 自己补充至少 6 条设备数据 ???
        ]
        for device in device_list:
            session.add(Device(**device))
        session.commit()

    while True:
        print("\n请输入查询选项:")
        print("输入 1：查询所有设备")
        print("输入 2：根据设备名称查询")
        print("输入 3：根据设备类型查询")
        print("输入 4：根据机房位置查询")
        print("输入 0：退出")

        while True:
            choice = input("\n请输入查询选项：").strip()
            if choice in ('0', '1', '2', '3', '4'):
                break
            print("无效的选项，请重新输入（0-4）")

        if choice == '1':
            # ??? 查询全部设备 ???
            pass

        elif choice == '2':
            name = input("请输入设备名称：")
            # ??? 按名称精确查询 ???
            pass

        elif choice == '3':
            device_type = input("请输入设备类型（router/switch/firewall）：")
            # ??? 按类型精确查询 ???
            pass

        elif choice == '4':
            keyword = input("请输入机房位置关键词：")
            # ??? 按位置模糊查询，使用 .contains() ???
            pass

        elif choice == '0':
            break
期望输出：
[+] 初始设备数据已写入数据库

请输入查询选项:
输入 1：查询所有设备
输入 2：根据设备名称查询
输入 3：根据设备类型查询
输入 4：根据机房位置查询
输入 0：退出

请输入查询选项：1
Device(设备名称: R1 | 类型: router | 版本: IOS XE 17.14 | 位置: Beijing-IDC-A | 入库时间: 2026-03-04 11:09:48.632191)
Device(设备名称: R2 | 类型: router | 版本: IOS XE 17.14 | 位置: Shanghai-IDC-B | 入库时间: 2026-03-04 11:09:48.632450)
Device(设备名称: SW1 | 类型: switch | 版本: IOS 15.2 | 位置: Beijing-IDC-A | 入库时间: 2026-03-04 11:09:48.632514)
Device(设备名称: SW2 | 类型: switch | 版本: IOS 15.2 | 位置: Shanghai-IDC-B | 入库时间: 2026-03-04 11:09:48.632578)
Device(设备名称: FW1 | 类型: firewall | 版本: ASA 9.16 | 位置: Beijing-IDC-A | 入库时间: 2026-03-04 11:09:48.632634)
Device(设备名称: FW2 | 类型: firewall | 版本: FTD 7.2 | 位置: Shenzhen-IDC-C | 入库时间: 2026-03-04 11:09:48.632682)

请输入查询选项：2
请输入设备名称：SW1
Device(设备名称: SW1 | 类型: switch | 版本: IOS 15.2 | 位置: Beijing-IDC-A | 入库时间: 2026-03-04 11:09:48.632514)

请输入查询选项：3
请输入设备类型（router/switch/firewall）：router
Device(设备名称: R1 | 类型: router | 版本: IOS XE 17.14 | 位置: Beijing-IDC-A | 入库时间: 2026-03-04 11:09:48.632191)
Device(设备名称: R2 | 类型: router | 版本: IOS XE 17.14 | 位置: Shanghai-IDC-B | 入库时间: 2026-03-04 11:09:48.632450)

请输入查询选项：4
请输入机房位置关键词：Beijing-IDC-A
Device(设备名称: R1 | 类型: router | 版本: IOS XE 17.14 | 位置: Beijing-IDC-A | 入库时间: 2026-03-04 11:09:48.632191)
Device(设备名称: SW1 | 类型: switch | 版本: IOS 15.2 | 位置: Beijing-IDC-A | 入库时间: 2026-03-04 11:09:48.632514)
Device(设备名称: FW1 | 类型: firewall | 版本: ASA 9.16 | 位置: Beijing-IDC-A | 入库时间: 2026-03-04 11:09:48.632634)

请输入查询选项：0
'''

import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# ======================
# 1. 初始化数据库连接
# ======================
# 创建数据库引擎：连接 SQLite 数据库文件
# check_same_thread=False：允许在多线程中使用（避免报错）
# echo=False：不打印 SQL 语句（设为 True 可以看到底层执行的 SQL）
engine = create_engine('sqlite:///device_inventory.db?check_same_thread=False',
                       echo=False)

# 创建基类：所有数据库模型类都要继承这个 Base
Base = declarative_base()

# 创建会话工厂：用于生成数据库操作会话
Session = sessionmaker(bind=engine)
# 创建会话对象：我们用这个 session 来做增删改查
session = Session()


# ======================
# 2. 定义数据库模型（Device 表）
# ======================
class Device(Base):
    __tablename__ = 'devices'  # 数据库表名

    # 定义字段
    id          = Column(Integer, primary_key=True)  # 主键，自动递增
    name        = Column(String(64), nullable=False, index=True)  # 设备名称，必填，加索引
    type        = Column(String(64), nullable=False)  # 设备类型，必填
    version     = Column(String(64))  # 系统版本，可选
    location    = Column(String(128))  # 机房位置，可选
    create_time = Column(DateTime(timezone='Asia/Chongqing'), default=datetime.datetime.now)  # 入库时间，自动填当前时间

    def __repr__(self):
        """打印对象时的格式化输出"""
        return (f"{self.__class__.__name__}(设备名称: {self.name} | 类型: {self.type} | "
                f"版本: {self.version} | 位置: {self.location} | 入库时间: {self.create_time})")


if __name__ == '__main__':
    # ======================
    # 3. 创建数据库表
    # ======================
    # checkfirst=True：如果表已经存在，就不重复创建
    Base.metadata.create_all(engine, checkfirst=True)

    # ======================
    # 4. 只有表为空时才插入初始数据
    # ======================
    if session.query(Device).count() == 0:
        # ✅ 补全：至少 6 条设备数据
        device_list = [
            {"name": "R1", "type": "router", "version": "IOS XE 17.14", "location": "Beijing-IDC-A"},
            {"name": "R2", "type": "router", "version": "IOS XE 17.14", "location": "Shanghai-IDC-B"},
            {"name": "SW1", "type": "switch", "version": "IOS 15.2", "location": "Beijing-IDC-A"},
            {"name": "SW2", "type": "switch", "version": "IOS 15.2", "location": "Shanghai-IDC-B"},
            {"name": "FW1", "type": "firewall", "version": "ASA 9.16", "location": "Beijing-IDC-A"},
            {"name": "FW2", "type": "firewall", "version": "FTD 7.2", "location": "Shenzhen-IDC-C"},
        ]
        # 批量添加设备
        for device in device_list:
            session.add(Device(**device))
        # 提交事务（保存到数据库）
        session.commit()
        print("[+] 初始设备数据已写入数据库")

    # ======================
    # 5. 交互式查询菜单
    # ======================
    while True:
        print("\n请输入查询选项:")
        print("输入 1：查询所有设备")
        print("输入 2：根据设备名称查询")
        print("输入 3：根据设备类型查询")
        print("输入 4：根据机房位置查询")
        print("输入 0：退出")

        # 输入验证：只接受 0-4
        while True:
            choice = input("\n请输入查询选项：").strip()
            if choice in ('0', '1', '2', '3', '4'):
                break
            print("无效的选项，请重新输入（0-4）")

        # ======================
        # 选项 1：查询所有设备
        # ======================
        if choice == '1':
            # ✅ 补全：查询全部设备
            devices = session.query(Device).all()
            if devices:
                for d in devices:
                    print(d)
            else:
                print("[-] 数据库中没有设备")

        # ======================
        # 选项 2：根据设备名称查询
        # ======================
        elif choice == '2':
            name = input("请输入设备名称：")
            # ✅ 补全：按名称精确查询
            devices = session.query(Device).filter_by(name=name).all()
            if devices:
                for d in devices:
                    print(d)
            else:
                print(f"[-] 未找到名称为 {name} 的设备")

        # ======================
        # 选项 3：根据设备类型查询
        # ======================
        elif choice == '3':
            device_type = input("请输入设备类型（router/switch/firewall）：")
            # ✅ 补全：按类型精确查询
            devices = session.query(Device).filter_by(type=device_type).all()
            if devices:
                for d in devices:
                    print(d)
            else:
                print(f"[-] 未找到类型为 {device_type} 的设备")

        # ======================
        # 选项 4：根据机房位置查询（模糊查询）
        # ======================
        elif choice == '4':
            keyword = input("请输入机房位置关键词：")
            # ✅ 补全：按位置模糊查询，使用 .contains()
            devices = session.query(Device).filter(Device.location.contains(keyword)).all()
            if devices:
                for d in devices:
                    print(d)
            else:
                print(f"[-] 未找到位置包含 {keyword} 的设备")

        # ======================
        # 选项 0：退出
        # ======================
        elif choice == '0':
            break
