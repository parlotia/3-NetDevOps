from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
import subprocess
import io
import base64
from typing import Union


def system_cmd(cmd):
    # 使用 subprocess.Popen 执行命令
    # 分别获取 stdout 和 stderr
    # 返回 (标准输出, 错误输出)
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate()
    return stdout, stderr


class PostCMD(BaseModel):
    # {"cmd": "ifconfig"}
    cmd: str = Field(title='执行的命令')


class ReturnCMD(BaseModel):
    # {"cmd": "ifconfig", "cmd_result": "base64编码后的结果"}
    cmd: str = Field(title='执行的命令')
    cmd_result: str = Field(title='执行的命令返回的结果, 已经被Base64编码')


class ERROR(BaseModel):
    # {"error": "错误信息"}
    error: str = Field(title='错误消息')


app = FastAPI()


@app.post("/cmd", response_model=Union[ReturnCMD, ERROR], summary='执行系统命令', description='执行系统命令描述')
async def cmd(postcmd: PostCMD, request: Request):
    exec_cmd = postcmd.cmd

    # 1. 调用 system_cmd(exec_cmd)
    stdout, stderr = system_cmd(exec_cmd)

    # 2. 如果 stderr 有内容，返回 ERROR(error=base64编码后的错误信息)
    if stderr:
        return ERROR(error=base64.b64encode(stderr.encode()).decode())

    # 3. 如果执行成功，返回 ReturnCMD(cmd=exec_cmd, cmd_result=base64编码后的标准输出)
    return ReturnCMD(
        cmd=exec_cmd,
        cmd_result=base64.b64encode(stdout.encode()).decode()
    )
