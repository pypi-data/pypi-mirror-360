"""
@author:cmcc
@file: make_cmri_schema.py
@time: 2021-09-01 16:01
"""
import logging


supportType = ['string', 'int', 'float', 'dict', 'list', 'bool', 'none']
schema = {"$schema": "http://json-schema.org/draft-07/schema#"}
SEPARATORS = "||"
CHILD_HEADER = ">"
KEY_WORD_JSON = "json"
KEY_WORD_RAW = "raw"
KEY_WORD_FORM_DATA = "form-data"
KEY_WORD_JSON_PATH = "jsonpath"
KEY_WORD_JSON_OBJECT = "object"
KEY_WORD_JSON_ARRAY = "array"
KEY_WORD_TYPE = "type"
KEY_WORD_NAME = "name"
KEY_WORD_RULER = "ruler"
KEY_WORD_EXCEPT = "expect"
KEY_WORD_GREATER = ">"
KEY_WORD_LESSER = "<"
KEY_WORD_GREATER_EQUAL = ">="
KEY_WORD_LESSER_EQUAL = "<="
KEY_WORD_EQUAL = "=="
KEY_WORD_REG = "reg"
KEY_WORD_INCLUDE = "in"
KEY_WORD_STRING = "string"
KEY_WORD_INT = "integer"
KEY_WORD_DATE = "date"
KEY_WORD_DATETIME = "datetime"
KEY_WORD_BOOLEAN = "boolean"
KEY_WORD_SHORT = "short"
KEY_WORD_LONG = "long"
KEY_WORD_FLOAT = "float"
KEY_WORD_DOUBLE = "double"
KEY_WORD_MAX = 20

logger = logging.getLogger(__name__)


class CMRISchemaMaker:
    """生成cmri schema"""

    def __init__(self, body_data):
        self.body_data = body_data

    def get_cmri_schema_body(self):
        # mock_outer_type = self.body_data.get("content", "").get("type", "").lower()
        if isinstance(self.body_data, dict):
            inner_body = self.body_data.get("content", {}).get("content", [])
        if isinstance(self.body_data, list):
            inner_body = self.body_data
        # json_schema = {"$schema": "http://json-schema.org/schema#"}
        changed_schema = self.__loop_child(inner_body)
        logger.info(f"get_cmri_schema_body:{changed_schema}")
        return changed_schema

    def __loop_child(self, child_list, num=0):
        final_list = []
        for i, v in enumerate(child_list):
            if isinstance(v, dict):
                child_str = ""
                v_name = v.get("name", "")
                v_type = v.get("type", "")
                v_required = v.get("required", "O")
                if num > 0:
                    child_str = CHILD_HEADER * num + v_name + SEPARATORS + v_type + SEPARATORS + v_required
                else:
                    child_str = v_name + SEPARATORS + v_type + SEPARATORS + v_required
                if "more" in v:
                    v_more = v.get("more", "")
                    more_str = self.__get_msg_from_more(v.get("more", ""))  # 加过分隔符
                    child_str = child_str + more_str
                final_list.append(child_str)
                if "children" in v:
                    children_list = self.__loop_child(v.get("children", [{}]), num + 1)
                    final_list.extend(children_list)
            else:
                return False
        return final_list

    @staticmethod
    def __check_depend_on(v_depend):
        child_list_depend = []
        if "path" in v_depend:
            child_list_depend.append(v_depend.get("path"))
        if "expression" in v_depend:
            child_list_depend.append(v_depend.get("expression"))
        if "value" in v_depend:
            child_list_depend.append(v_depend.get("value"))
        return child_list_depend

    def __get_msg_from_more(self, v_dict):
        final_str = ""
        depend_str = ""
        if "depend" in v_dict:  # 是否有依赖, 如果有依赖的话，最后需要拼接一下
            v_depend = v_dict.get("depend")
            child_list_depend = []
            if isinstance(v_depend, dict):
                child_list_depend = self.__check_depend_on(v_depend)
            elif isinstance(v_depend, list):
                for num in v_depend:
                    if isinstance(num, str):
                        child_list_depend.append(num)
                    else:
                        tmp_list = self.__check_depend_on(num)
                        child_list_depend.append(tmp_list)
            depend_str = SEPARATORS + "depend" + str(child_list_depend)
        limit_list = []
        if "minLength" in v_dict:
            # child_list_minL =
            limit_list.append(["len", ">=", v_dict.get("minLength")])
        if "maxLength" in v_dict:
            # child_list_maxL = ["len", "<=", v_dict.get("maxLength")]
            limit_list.append(["len", "<=", v_dict.get("maxLength")])
        if "minimum" in v_dict:
            # child_list_minimum = [">=", v_dict.get("minimum")]
            limit_list.append([">=", v_dict.get("minimum")])
        if "maximum" in v_dict:
            # child_list_maximum = ["<=", v_dict.get("maximum")]
            limit_list.append(["<=", v_dict.get("maximum")])
        if "pattern" in v_dict:
            # child_list_reg = ["reg", v_dict.get("pattern")]
            limit_list.append(["reg", v_dict.get("pattern")])
        if "enum" in v_dict:
            enum_list = []
            for i, j in enumerate(v_dict.get("enum")):
                enum_list.append(j.get("value", ""))
            limit_list.append(["in", enum_list])
        if len(limit_list) > 1:  # 暂时不支持not in 和 or，后续再根据场景进行修改
            limit_list.insert(0, "and")
            # final_str = depend_str + SEPARATORS + "limit" + '[%s]' % ','.join(list(map(lambda x: "'%s'" % x, limit_list)))
            final_str = depend_str + SEPARATORS + "limit" + str(limit_list)
            # final_str = depend_str + SEPARATORS + "limit" + json.dumps(limit_list, ensure_ascii=False)
        elif len(limit_list) == 1:
            limit_list = limit_list[0]
            final_str = depend_str + SEPARATORS + "limit" + str(limit_list)
            # final_str = depend_str + SEPARATORS + "limit" + json.dumps(limit_list, ensure_ascii=False)
            # final_str = depend_str + SEPARATORS + "limit" + '[%s]' % ','.join(list(map(lambda x: "'%s'" % x, limit_list)))
        else:
            final_str = depend_str
        logger.info(f"wyf---{final_str}")
        return final_str

