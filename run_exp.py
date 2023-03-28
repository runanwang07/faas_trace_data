import os
import subprocess
import time
import signal
import threading
import logging
import paramiko
from datetime import datetime
import pytz

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为 DEBUG
    # 设置日志格式
    format='[%(levelname)s]%(asctime)s %(filename)s:%(lineno)d: %(message)s',
    handlers=[
        logging.FileHandler("log.txt"),  # 将日志记录保存到文件
        logging.StreamHandler()  # 将日志记录输出到控制台
    ],
)


def run_remote_command(path, timeout, command_type, hostname="33.33.33.18", port=22, username="root"):
    # 创建 SSH 客户端
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 连接到远程服务器
    ssh_client.connect(hostname, port, username)

    if command_type == "collect":
        command = "cd /mnt/query-multimodel-data&&/usr/local/go/bin/go run main.go"
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # command = "/usr/local/go/bin/go run main.go"
        # stdin, stdout, stderr = ssh_client.exec_command(command)

        # 获取命令执行结果
        output = stdout.read().decode()
        error = stderr.read().decode()

        print(output)
        print(error)

        time.sleep(timeout*60)

    elif command_type == "preserve":
        utc_time = datetime.now(pytz.utc).date  # 获取当前 UTC 时间

        command = "mv /mnt/query-multimodel-data/" + utc_time + "/trace " + path
        stdin, stdout, stderr = ssh_client.exec_command(command)

        command = "rm -r /mnt/query-multimodel-data/" + utc_time + "/traceid"
        stdin, stdout, stderr = ssh_client.exec_command(command)

    # 关闭连接
    ssh_client.close()


def run_command_background(command, timeout):
    process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
    time.sleep(timeout*60)
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)


def run_command(working_directory, timeout):
    prev_working_directory = os.getcwd()  # 保存当前工作目录

    if working_directory:
        os.chdir(working_directory)  # 切换到指定的工作目录

    command = "faas-cli up -f resize.yml"

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    time.sleep(30)

    while True:
        command = "kubectl get pod -n openfaas-fn |grep resize"

        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if "Running" in str(result.stdout):
            break
        time.sleep(30)

    os.chdir(prev_working_directory)  # 切换回之前的工作目录

    local_timezone = pytz.timezone("Asia/Shanghai")  # 用您所需的时区替换
    logging.info("----------------------------------------")
    logging.info("working_directory: %s", working_directory)
    logging.info("Start Local time: %s", datetime.now(local_timezone))
    logging.info("Start UTC time: %s", datetime.now(pytz.utc))

    command = "locust -f locust_file.py --host=http://33.33.33.223:31112/function/ --headless -u 5 -r 1"
    t1 = threading.Thread(target=run_command_background,
                          args=(command, timeout+1))

    t1.start()
    t1.join()

    logging.info("End Local time: %s", datetime.now(local_timezone))
    logging.info("End UTC time: %s", datetime.now(pytz.utc))
    logging.info(" ")


if __name__ == "__main__":
    folder_path_list = [
        # "/mnt/resize_trace/resize_statement_trace_all",
        # "/mnt/resize_trace/resize_statement_trace_42",
        # "/mnt/resize_trace/resize_statement_trace_47",
        # "/mnt/resize_trace/resize_statement_trace_60",
        # "/mnt/resize_trace/resize_statement_trace_61",
        # "/mnt/resize_trace/resize_statement_trace_63",
        # "/mnt/resize_trace/resize_statement_trace_65",
        # "/mnt/resize_trace/resize_statement_trace_71",
        # "/mnt/resize_trace/resize_statement_trace_75",
        # "/mnt/resize_trace/resize_statement_trace_83",
        # "/mnt/resize_trace/resize_statement_trace_85",
        # "/mnt/resize_trace/resize_statement_trace_88",
        # "/mnt/resize_trace/fault1_resize_statement_trace_all",
        # "/mnt/resize_trace/fault1_resize_statement_trace_42",
        # "/mnt/resize_trace/fault1_resize_statement_trace_47",
        # "/mnt/resize_trace/fault1_resize_statement_trace_60",
        # "/mnt/resize_trace/fault1_resize_statement_trace_61",
        # "/mnt/resize_trace/fault1_resize_statement_trace_63",
        # "/mnt/resize_trace/fault1_resize_statement_trace_65",
        # "/mnt/resize_trace/fault1_resize_statement_trace_71",
        # "/mnt/resize_trace/fault1_resize_statement_trace_75",
        # "/mnt/resize_trace/fault1_resize_statement_trace_83",
        # "/mnt/resize_trace/fault1_resize_statement_trace_85",
        # "/mnt/resize_trace/fault1_resize_statement_trace_88",
        "/mnt/resize_trace/fault2_resize_statement_trace_all",
        "/mnt/resize_trace/fault2_resize_statement_trace_42",
        "/mnt/resize_trace/fault2_resize_statement_trace_47",
        "/mnt/resize_trace/fault2_resize_statement_trace_60",
        "/mnt/resize_trace/fault2_resize_statement_trace_61",
        "/mnt/resize_trace/fault2_resize_statement_trace_63",
        "/mnt/resize_trace/fault2_resize_statement_trace_65",
        "/mnt/resize_trace/fault2_resize_statement_trace_71",
        "/mnt/resize_trace/fault2_resize_statement_trace_75",
        "/mnt/resize_trace/fault2_resize_statement_trace_83",
        "/mnt/resize_trace/fault2_resize_statement_trace_85",
        "/mnt/resize_trace/fault2_resize_statement_trace_88",
        "/mnt/resize_trace/fault2_resize_statement_trace_all",
        "/mnt/resize_trace/fault3_resize_statement_trace_42",
        "/mnt/resize_trace/fault3_resize_statement_trace_47",
        "/mnt/resize_trace/fault3_resize_statement_trace_60",
        "/mnt/resize_trace/fault3_resize_statement_trace_61",
        "/mnt/resize_trace/fault3_resize_statement_trace_63",
        "/mnt/resize_trace/fault3_resize_statement_trace_65",
        "/mnt/resize_trace/fault3_resize_statement_trace_71",
        "/mnt/resize_trace/fault3_resize_statement_trace_75",
        "/mnt/resize_trace/fault3_resize_statement_trace_83",
        "/mnt/resize_trace/fault3_resize_statement_trace_85",
        "/mnt/resize_trace/fault3_resize_statement_trace_88",
    ]

    for path in folder_path_list:
        run_command(working_directory=path, timeout=20)
