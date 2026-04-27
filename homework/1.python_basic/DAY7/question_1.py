# 导入 os 模块，用于文件和目录操作
import os
# 导入 shutil 模块，用于删除非空目录
import shutil

# ========== 第一步：创建 backup/ 目录并写入配置文件 ==========

# 定义一个字典，key 是文件名，value 是文件内容
files = {
    # R1 的配置：G0/0 是 shutdown，G0/1 是 no shutdown
    'R1_config.txt': 'hostname R1\ninterface GigabitEthernet0/0\n shutdown\ninterface GigabitEthernet0/1\n no shutdown\n',
    # R2 的配置：两个接口都是 no shutdown
    'R2_config.txt': 'hostname R2\ninterface GigabitEthernet0/0\n no shutdown\ninterface GigabitEthernet0/1\n no shutdown\n',
    # R3 的配置：两个接口都是 no shutdown
    'R3_config.txt': 'hostname R3\ninterface GigabitEthernet0/0\n no shutdown\ninterface GigabitEthernet0/1\n no shutdown\n',
    # SW1 的配置：Vlan1 是 shutdown，G0/1 是 no shutdown
    'SW1_config.txt': 'hostname SW1\ninterface Vlan1\n shutdown\ninterface GigabitEthernet0/1\n no shutdown\n',
}

# 创建 backup/ 目录
# exist_ok=True：如果目录已经存在，也不会报错，继续执行
os.makedirs('backup', exist_ok=True)

# 遍历 files 字典，把每个配置文件写入 backup/ 目录
# filename 取字典的 key（文件名），content 取字典的 value（文件内容）
for filename, content in files.items():
    # 拼接完整的文件路径：backup/文件名
    # os.path.join 是安全拼接路径的方法，Windows/Linux 都能用
    file_path = os.path.join('backup', filename)
    
    # 打开文件，'w' 表示写入模式（如果文件不存在会创建，存在会覆盖）
    with open(file_path, 'w') as f:
        # 把内容写入文件
        f.write(content)

# ========== 第二步：遍历目录，找出含 shutdown（排除 no shutdown）的文件 ==========

# 打印提示信息
print("发现包含 shutdown 接口的设备配置文件:")

# 获取 backup/ 目录下所有的文件名，存成一个列表
all_files = os.listdir('backup')

# 遍历 backup/ 目录下的每一个文件
for filename in all_files:
    # 拼接完整的文件路径
    file_path = os.path.join('backup', filename)
    
    # 打开文件，'r' 表示读取模式
    with open(file_path, 'r') as f:
        # 读取文件的全部内容，存成一个字符串
        content = f.read()
    
    # 定义一个标记变量，用来记录这个文件是否包含单独的 shutdown
    has_shutdown = False
    
    # 把文件内容按行切开，逐行检查
    for line in content.splitlines():
        # strip() 去掉行首尾的空格和换行符
        # 如果这一行纯纯就是 'shutdown'（不是 'no shutdown'）
        if line.strip() == 'shutdown':
            # 标记为 True
            has_shutdown = True
            # 找到了就不用继续往下看了，跳出循环
            break
    
    # 如果标记是 True，说明这个文件包含 shutdown 接口
    if has_shutdown:
        # 打印文件名
        print(filename)

# ========== 第三步：删除 backup/ 目录及其所有文件 ==========

# shutil.rmtree 是强制删除非空目录的方法
# 会把 backup/ 目录和里面所有的文件一起删掉
shutil.rmtree('backup')

# 打印清理完成的提示
print("backup/ 目录已清理")