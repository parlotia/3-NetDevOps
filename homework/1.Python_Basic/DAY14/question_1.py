'''
任务一：模拟配置备份与过期清理
网络工程师经常需要定期备份设备配置，并清理过期的备份文件。请编写一个脚本，模拟这个过程：

在脚本同级目录下创建一个 backup/ 文件夹（如果不存在则创建）。
使用 while True: 循环，每隔 3秒 在 backup/ 目录下生成一个备份文件，文件名为 backup_YYYY-MM-DD_HH-MM-SS.txt。
每次生成新文件后，检查 backup/ 目录下所有的备份文件。
如果发现某个文件的生成时间距离当前时间 超过 15 秒，则将其删除（即只保留最近 15 秒内的备份，最多 5 个）。
每次循环打印出：新创建了哪个文件、删除了哪个文件（如果有）、以及当前保留的所有文件列表。
捕获 KeyboardInterrupt 异常，当用户按下 Ctrl+C 停止程序时，把 backup/ 目录下所有剩余的备份文件全部清理干净，并删除 backup/ 目录，优雅退出。
代码提示（可以参考以下框架）：

import os
import time
from datetime import datetime, timedelta

def main():
    # 1. 确定备份目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(base_dir, 'backup')
    
    # 如果目录不存在则创建
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    print(f"开始模拟备份，目录: {backup_dir}")
    print("按 Ctrl+C 停止并清理...")
    
    try:
        while True:
            # 2. 获取当前时间并生成备份文件
            now = datetime.now()
            now_str = now.strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"backup_{now_str}.txt"
            filepath = os.path.join(backup_dir, filename)
            
            # 使用 with open 写入文件
            # ??? 你的代码写在这里 ???
            
            print(f"\n[+] 创建备份: {filename}")
            
            # 3. 计算 15 秒前的时间基准
            expire_time = now - timedelta(seconds=15)
            
            # 4. 遍历备份目录，找出过期文件并删除
            current_files = []
            for file in os.listdir(backup_dir):
                if file.startswith('backup_') and file.endswith('.txt'):
                    # 从文件名提取时间字符串
                    time_str = file.replace('backup_', '').replace('.txt', '')
                    # 将字符串转换回 datetime 对象进行比较
                    file_time = datetime.strptime(time_str, '%Y-%m-%d_%H-%M-%S')
                    
                    # 比较时间，如果过期则删除，否则加入 current_files 列表
                    # ??? 你的代码写在这里 ???
            
            # 5. 打印当前保留的所有备份文件
            print(f"[*] 当前保留的备份 ({len(current_files)}个):")
            for f in sorted(current_files):
                print(f"    - {f}")
                
            # 6. 休眠 3 秒
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n收到停止信号，正在清理所有备份文件...")
        # 遍历目录，删除所有 backup_ 开头的 txt 文件
        # 最后删除 backup_dir 目录本身 (os.rmdir)
        # ??? 你的代码写在这里 ???
        print("清理完成，程序退出。")

if __name__ == '__main__':
    main()
期望输出示例：
开始模拟备份，目录: /your/path/day14/backup
按 Ctrl+C 停止并清理...

[+] 创建备份: backup_2026-03-04_10-29-23.txt
[-] 删除过期: backup_2026-03-04_10-29-06.txt
[*] 当前保留的备份 (4个):
    - backup_2026-03-04_10-29-09.txt
    - backup_2026-03-04_10-29-17.txt
    - backup_2026-03-04_10-29-20.txt
    - backup_2026-03-04_10-29-23.txt

[+] 创建备份: backup_2026-03-04_10-29-26.txt
[-] 删除过期: backup_2026-03-04_10-29-09.txt
[*] 当前保留的备份 (4个):
    - backup_2026-03-04_10-29-17.txt
    - backup_2026-03-04_10-29-20.txt
    - backup_2026-03-04_10-29-23.txt
    - backup_2026-03-04_10-29-26.txt

^C

收到停止信号，正在清理所有备份文件...
[-] 已清理: backup_2026-03-04_10-29-17.txt
[-] 已清理: backup_2026-03-04_10-29-20.txt
[-] 已清理: backup_2026-03-04_10-29-23.txt
[-] 已清理: backup_2026-03-04_10-29-26.txt
[-] 已删除 backup 目录
清理完成，程序退出。

'''

import os
import time
from datetime import datetime, timedelta

def main():
    # ======================
    # 1. 确定并创建备份目录
    # ======================
    # 获取当前脚本所在的绝对路径（__file__ 是当前脚本的文件名）
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接路径：在脚本同级目录下创建 backup 文件夹
    backup_dir = os.path.join(base_dir, 'backup')
    
    # 如果 backup 目录不存在，就创建它
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    print(f"开始模拟备份，目录: {backup_dir}")
    print("按 Ctrl+C 停止并清理...")
    
    try:
        # ======================
        # 2. 无限循环：每3秒备份一次
        # ======================
        while True:
            # 获取当前时间
            now = datetime.now()
            # 把时间格式化成字符串：YYYY-MM-DD_HH-MM-SS
            now_str = now.strftime('%Y-%m-%d_%H-%M-%S')
            # 拼接文件名：backup_时间.txt
            filename = f"backup_{now_str}.txt"
            # 拼接完整文件路径
            filepath = os.path.join(backup_dir, filename)
            
            # ✅ 写入备份文件（模拟配置内容）
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"这是模拟的设备配置备份，生成时间：{now_str}")
            
            print(f"\n[+] 创建备份: {filename}")
            
            # ======================
            # 3. 计算过期时间基准
            # ======================
            # 15秒前的时间点，超过这个时间的文件就是过期文件
            expire_time = now - timedelta(seconds=15)
            
            # ======================
            # 4. 遍历目录，删除过期文件
            # ======================
            current_files = []  # 用来存没过期的文件
            for file in os.listdir(backup_dir):
                # 只处理 backup_ 开头且 .txt 结尾的文件
                if file.startswith('backup_') and file.endswith('.txt'):
                    # 从文件名里把时间抠出来
                    # 例如：backup_2026-04-08_12-00-00.txt → 2026-04-08_12-00-00
                    time_str = file.replace('backup_', '').replace('.txt', '')
                    # 把时间字符串转回 datetime 对象，才能比较大小
                    file_time = datetime.strptime(time_str, '%Y-%m-%d_%H-%M-%S')
                    
                    # ✅ 判断是否过期
                    if file_time < expire_time:
                        # 过期了：删除文件
                        os.remove(os.path.join(backup_dir, file))
                        print(f"[-] 删除过期: {file}")
                    else:
                        # 没过期：加入保留列表
                        current_files.append(file)
            
            # ======================
            # 5. 打印当前保留的文件
            # ======================
            print(f"[*] 当前保留的备份 ({len(current_files)}个):")
            # 按文件名排序（也就是按时间排序）
            for f in sorted(current_files):
                print(f"    - {f}")
                
            # ======================
            # 6. 等待3秒
            # ======================
            time.sleep(3)
            
    except KeyboardInterrupt:
        # ======================
        # 7. 用户按 Ctrl+C 时的清理逻辑
        # ======================
        print("\n\n收到停止信号，正在清理所有备份文件...")
        
        # 遍历目录，删除所有 backup_ 开头的 txt 文件
        for file in os.listdir(backup_dir):
            if file.startswith('backup_') and file.endswith('.txt'):
                file_path = os.path.join(backup_dir, file)
                os.remove(file_path)
                print(f"[-] 已清理: {file}")
        
        # 删除空的 backup 目录
        os.rmdir(backup_dir)
        print("[-] 已删除 backup 目录")
        print("清理完成，程序退出。")

if __name__ == '__main__':
    main()