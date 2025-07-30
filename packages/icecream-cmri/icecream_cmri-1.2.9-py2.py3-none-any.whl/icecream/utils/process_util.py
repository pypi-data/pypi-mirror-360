"""
@author:cmcc
@file: process_util.py
@time: 2022/8/30 14:39
"""
import os
import psutil


class ProcessUtil:

    @classmethod
    def get_process(cls, pid):
        return psutil.Process(pid)

    @classmethod
    def get_iter_process(cls, name):
        p_list = []
        prefix = ""
        if os.name == "nt":
            prefix = ".exe"
        for process in psutil.process_iter():
            if process.name().endswith(name + prefix):
                p_list.append(process)
        return p_list

    @classmethod
    def clear_history_process(cls, name):
        p_list = ProcessUtil.get_iter_process(name)
        for p in p_list:
            if os.name == "nt":
                if len(p.parents()) == 0:
                    p.kill()
            else:
                if len(p.parents()) == 1:
                    p.kill()


if __name__ == '__main__':
    ProcessUtil.clear_history_process("xray")
