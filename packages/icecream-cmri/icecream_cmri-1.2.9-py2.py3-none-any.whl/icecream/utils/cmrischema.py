"""
@author:cmcc
@file: cmrischema.py
@time: 2021-05-20 14:29
"""
import copy
import jsonpath
import re
import ast
import random
from datetime import datetime

__all__ = ["validate"]


class TypeMapping(object):
    type_transfer = {
        "string": str,
        "boolean": bool,
        "integer": int,
        "float": float,
        "json": dict,
        "array": list,
        "number": [int, float],
        "null": type(None)
    }

    @classmethod
    def get_mapping_type(cls, str_type):
        if type(str_type) == list:
            return [cls.type_transfer.get(x) for x in str_type]
        else:
            sys_type = cls.type_transfer.get(str_type)
            if sys_type:
                if type(sys_type) == list:
                    return sys_type
                return [cls.type_transfer.get(str_type)]

    @classmethod
    def get_mapping_str_type(cls, raw_type):
        for key, value in cls.type_transfer.items():
            if type(value) == list:
                if raw_type in value:
                    return key
            else:
                if value == raw_type:
                    return key


class ExpressionDepend(object):
    """operation str mapping > to >"""

    def __init__(self, node, instance, depend):
        self.current_node = node[0:node.rfind(".")]
        self.expression = eval(depend)
        self.instance = instance

    def check(self):
        path = self.expression[0]
        if path.startswith("$"):
            value = jsonpath.jsonpath(self.instance, path)
            self.expression[0] = path[path.rfind(".") + 1:-1]
        else:
            value = jsonpath.jsonpath(self.instance, self.current_node + "." + path)
        if value:
            locals()[self.expression[0]] = value[0]
            if len(self.expression) == 1:
                return True
            if eval(self.__format_str()):
                return True
        return False

    def __format_str(self):
        if len(self.expression) == 3:
            if isinstance(self.expression[2], str):
                return self.expression[0] + " " + self.expression[1] + " " + f'"{self.expression[2]}"'
        return " ".join(map(str, self.expression))


class LimitRulerCheck(object):
    """数据检查类型
    "name||string||M||limit["len", ">=", 5]||depend['test', '==', '2']"
     limit: ["reg", "\d{5}"]
          ["and",["len", ">=", 5],["reg", "\d{5}"]]
          ["or",["len", ">=", 5],["reg", "\d{5}"]]
          ["in", ["1","2","3"]]
    """

    def __init__(self, ruler, value):
        self.expressions = eval(ruler)
        self.value = value

    def check(self) -> bool:
        if self.expressions[0] == "and":
            results = self._check_list(self.expressions[1:])
            return all(results)
        if self.expressions[0] == "or":
            results = self._check_list(self.expressions[1:])
            return any(results)
        if self.expressions[0] == "len":
            return self._check_len(self.expressions)
        if self.expressions[0] == "reg":
            return self._check_reg(self.expressions)
        return self._check_common(self.expressions)

    def _check_list(self, expressions):
        result = []
        for expression in expressions:
            if expression[0] == "len":
                result.append(self._check_len(expression))
            elif expression[0] == "reg":
                result.append(self._check_reg(expression))
            else:
                result.append(self._check_common(expression))
        return result

    def _check_reg(self, expression) -> bool:
        match = re.match(expression[1], self.value)
        if match:
            return True
        return False

    def _check_len(self, expression) -> bool:
        if expression[0] == "len":
            value = f'len("{self.value}")'
            expression[0] = value
        else:
            expression[0] = self.value
        if eval(" ".join(map(str, expression))):
            return True
        return False

    def _check_common(self, expression) -> bool:
        common_expression = self.value
        expression.insert(0, "common_expression")
        if isinstance(expression[2], str):
            format_str = expression[0] + " " + expression[1] + " " + f'"{expression[2]}"'
        else:
            format_str = " ".join(map(str, expression))
        if eval(format_str):
            return True
        return False


class CmriError(object):
    def __init__(self, path, msg):
        self.path = path
        self.msg = msg

    def __str__(self):
        return f'path: {self.path} {self.msg}'


class SchemaUnit(object):
    """schema min unit"""

    def __init__(self, schema_unit):
        self.path = schema_unit['path']
        self.type = schema_unit['type'].lower()
        self.required = schema_unit['required']
        self.ruler = schema_unit['ruler']
        self.depend = schema_unit['depend']
        self.description = schema_unit.get("desc")
        self.detail = schema_unit.get("detail")

    def error(self, instance):
        node = jsonpath.jsonpath(instance, self.path)
        if self.required.upper() == "M":
            return self._diff_m(node)
        if self.required.upper() == "O":
            return self._diff_o(node)
        if self.required.upper() == "C":
            return self._diff_c(node)

    def is_basic_type(self):
        """检查是否基本类型"""
        return "json" not in self.type

    def is_c_verify(self, instance):
        """检查条件可选参数是否需要验证"""
        if self.required == "C":
            return ExpressionDepend(self.path, instance, self.depend).check()
        return False

    def is_exist_path(self, instance):
        """检查路径是否存在"""
        node = jsonpath.jsonpath(instance, self.path)
        if node is False:
            return False
        return True

    def _check_type(self, node):
        """检查节点数据类型"""
        raw_type = type(node[0])
        if "array of " in self.type:
            if raw_type != list:
                return CmriError(self.path, f'类型不匹配，需要{self.type}, 实际为{raw_type}')
            else:
                if len(node[0]) >= 1:
                    transfer_type = TypeMapping.get_mapping_type(self.type.split("of")[1].strip())
                    if type(node[0][0]) not in transfer_type:
                        return CmriError(self.path,
                                         f'类型不匹配，需要{self.type}, 实际为array of {TypeMapping.get_mapping_str_type(type(node[0][0]))}')
        else:
            transfer_type = TypeMapping.get_mapping_type(self.type.split("/"))
            if raw_type not in transfer_type:
                return CmriError(self.path, f'类型不匹配，需要{self.type}, 实际为{raw_type}')

    def _diff_m(self, node):
        """required M diff"""
        if not node:
            return CmriError(self.path, "节点不存在")
        msg = self._check_type(node)
        if msg:
            return msg
        if self.ruler:
            if not self._check_ruler(node[0]):
                return CmriError(self.path, f'取值异常，需要{self.ruler}, 实际为{node[0]}')

    def _diff_c(self, node):
        """required C diff"""
        if node:
            msg = self._check_type(node)
            if msg:
                return msg
            if self.ruler:
                if not self._check_ruler(node[0]):
                    return CmriError(self.path, f'取值异常，需要{self.ruler}, 实际为{node[0]}')
        else:
            return CmriError(self.path, f'节点缺失')

    def _diff_o(self, node):
        """required O diff"""
        if node:
            msg = self._check_type(node)
            if msg:
                return msg
            if self.ruler:
                if not self._check_ruler(node[0]):
                    return CmriError(self.path, f'取值异常，需要{self.ruler}, 实际为{node[0]}')

    def _check_ruler(self, value):
        """检查变量值是否在限制范围"""
        if self.ruler:
            return LimitRulerCheck(self.ruler, value).check()


class CmriSchema(object):
    """
       数据检查格式:
       字段名 类型 条件必选 字段限制 依赖字段
       "name||string||M||limit["len", ">=", 5]||depend['test', '==', '2']"
       limit: ["reg", "\d{5}"]
              ["and",["len", ">=", 5],["reg", "\d{5}"]]
              ["or",["len", ">=", 5],["reg", "\d{5}"]]
    """

    def __init__(self, schema):
        self.schema = schema

    def get_format_schema(self):
        collect = []
        self._deal_schema2json(collect, self.schema)
        return collect

    def _transfor_type(self, data_type):
        result = data_type.lower()
        if result == "datetime":
            return "string"
        if result == "date":
            return "string"
        return result

    def _deal_schema2json(self, node, lines):
        record_json_path = {}
        if lines:
            for line in lines:
                current_depth = len(re.findall(">", line[0:line.find("||")]))
                prefix = record_json_path.get(current_depth)
                if prefix is None:
                    record_json_path[current_depth] = "$"
                    prefix = "$"
                single_info = line.split("||")
                tmp = {
                    "path": prefix + "." + single_info[0].replace(">", ""),
                    "type": self._transfor_type(single_info[1]),
                    "required": single_info[2].upper(),
                    "ruler": None,
                    "depend": None
                }
                if len(single_info) == 4:  # 只有限制
                    self._set_depend_limit(single_info[3], tmp)
                elif len(single_info) == 5:  # 存在依赖，限制
                    self._set_depend_limit(single_info[4], tmp)
                if tmp['type'].lower() in ["json", "array of json"]:
                    if tmp['type'] == "json":
                        prefix = tmp['path']
                    elif tmp['type'] == "array of json":
                        prefix = tmp['path'] + ".[*]"
                    record_json_path[current_depth + 1] = prefix
                node.append(tmp)

    def _set_depend_limit(self, data, info):
        """deal depend or limit info"""
        if data.startswith("limit"):
            info['ruler'] = data[5:]
        elif data.startswith('depend'):
            info['depend'] = data[6:]


class CmriCheck(object):

    def __init__(self, schema, strict):
        self.schema = schema
        self.strict = strict
        self.records = []
        self.available_rulers = []

    def iter_errors(self, instance):
        if self.schema:
            schema_rulers = CmriSchema(self.schema).get_format_schema()
            if type(instance) == dict or type(instance) == list:
                self.collect_available_rulers(schema_rulers, instance)
                self.collect_exist_path_rulers(schema_rulers, instance)
                return self.check_params(instance)
            else:
                return {"msg": "data is not json"}
        return None

    def collect_exist_path_rulers(self, schema_rulers, instance):
        """检查所有存在路径的规则"""
        for schema_unit in schema_rulers:
            su = SchemaUnit(schema_unit)
            if su.is_exist_path(instance):
                self.available_rulers.append(su)

    def collect_available_rulers(self, schema_rulers, instance):
        """
        收集可以检查的规则
        """
        prefix_c = ""
        prefix_o = ""
        rulers_c = []
        rulers_o = []
        flag_c = False
        flag_o = False
        for schema_unit in schema_rulers:
            su = SchemaUnit(schema_unit)
            if len(prefix_c) > 1 and su.path.startswith(prefix_c):  # 收集条件必选相关检查数据
                rulers_c.append(schema_unit)
                continue
            else:
                if flag_c and len(rulers_c) > 0:
                    self.collect_available_rulers(rulers_c, instance)
                rulers_c = []
                prefix_c = ""
            if len(prefix_o) > 1 and su.path.startswith(prefix_o):  # 收集可选相关检查数据
                rulers_o.append(schema_unit)
                continue
            else:
                if flag_o and len(rulers_o) > 0:
                    self.collect_available_rulers(rulers_o, instance)
                rulers_o = []
                prefix_o = ""
            if su.required == "C":  # 条件开关，收集需要检查项
                prefix_c = su.path
                flag_c = su.is_c_verify(instance)
                if flag_c:
                    self.available_rulers.append(su)
                if not su.is_basic_type():
                    continue
            elif su.required == "O":  # 可选开关，收集需要检查项
                prefix_o = su.path
                flag_o = su.is_exist_path(instance)
                if flag_o:
                    self.available_rulers.append(su)
                if not su.is_basic_type():
                    continue
            else:
                self.available_rulers.append(su)
        if flag_c and len(rulers_c) > 0:
            self.collect_available_rulers(rulers_c, instance)
        if flag_o and len(rulers_o) > 0:
            self.collect_available_rulers(rulers_o, instance)

    def check_params(self, instance):
        """检查路径参数是否符合规则"""
        json_path = []
        rulers = []
        for ruler in self.available_rulers:
            if ruler.path not in json_path:
                rulers.append(ruler)
                json_path.append(ruler.path)
        for ruler in rulers:
            tmp = ruler.error(instance)
            if tmp:
                self.records.append(tmp)
        return "\n".join([str(record) for record in self.records])


def validate(instance, schema, strict=False):
    """Validate an instance under the given cmri schema."""
    cmri = CmriCheck(schema, strict)
    error = cmri.iter_errors(instance)
    if error is not None:
        return error


def main():
    schema = [
        "currPage||string/null||M",
        "pageSize||string||M",
        "eqpType||string||M||limit['in',['PTN','POS','OLT','OTN','SPN','ONU','路由器','BRAS']]",
        "neType||string||C||depend['eqpType','==', '路由器']",
        "olt_uuid||string||C||depend['eqpType','in', ['POS','ONU']]",
        "oltPortId||string||C||depend['eqpType','in', ['POS','ONU']]"
    ]
    instance = {
        "currPage": None,
        "eqpType": "PTN",
        "pageSize": "20",
        "siteId": "xxxxx"
    }
    print(validate(instance, schema))


if __name__ == '__main__':
    main()
