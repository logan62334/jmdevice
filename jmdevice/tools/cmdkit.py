import logging
import os
import platform
import signal
import subprocess

logger = logging


class CmdKit:

    @staticmethod
    def run_sysCmd(cmd, timeout=60):
        """执行命令cmd，返回命令输出的内容。
        cmd - 要执行的命令
        timeout - 最长等待时间，单位：秒
        """
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, close_fds=True,
                             start_new_session=True)
        encoding_format = 'utf-8'
        if platform.system() == "Windows":
            encoding_format = 'gbk'
        try:
            (msg, errs) = p.communicate(timeout=timeout)
            ret_code = p.poll()
            if ret_code:
                msg = "[Error]Called Error ： " + str(msg.decode(encoding_format)) + "命令为：" + cmd
                logger.debug(msg)
            else:
                msg = str(msg.decode(encoding_format))
        except subprocess.TimeoutExpired:
            # 注意：不能只使用p.kill和p.terminate，无法杀干净所有的子进程，需要使用os.killpg
            p.kill()
            p.terminate()
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except Exception as e:
                logger.debug(e)
            # 注意：如果开启下面这两行的话，会等到执行完成才报超时错误，但是可以输出执行结果
            # (outs, errs) = p.communicate()
            # print(outs.decode('utf-8'))
            msg = "[ERROR]Timeout Error : Command '" + cmd + "' timed out after " + str(timeout) + " seconds"
            logger.debug(msg)
        except Exception as e:
            msg = "[ERROR]Unknown Error : " + str(e) + "命令为：" + cmd
            logger.debug(msg)
        return msg
