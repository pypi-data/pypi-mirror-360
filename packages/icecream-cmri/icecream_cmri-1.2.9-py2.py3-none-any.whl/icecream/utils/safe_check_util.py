"""
@author:cmcc
@file: safe_check_util.py
@time: 2024/7/21 23:10
"""
import json
import logging
import traceback

logger = logging.getLogger(__name__)


def safe_output(collect_info: list, environment):
    if collect_info:
        try:
            tmp = json.dumps(collect_info, ensure_ascii=False)
            for key, value in environment.get_all().items():
                if key.startswith("@icepwd_"):
                    tmp = tmp.replace(str(value), "sensitive_info_xxxxxxxxxxxxxxxxxxxxx")
            return json.loads(tmp)
        except Exception:
            logger.warning(traceback.format_exc())
    return []