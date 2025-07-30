import logging
import re

logger = logging.getLogger(__name__)

supportType = ['string', 'int', 'float', 'dict', 'list', 'bool', 'none']
schema = {"$schema": "http://json-schema.org/draft-07/schema#"}
SEPARATORS = "||"
CHILD_HEADER = ">"
KEY_WORD_JSON = "json"
KEY_WORD_RAW = "raw"
KEY_WORD_FORM_DATA = "form-data"
KEY_WORD_JSON_PATH = "jsonpath"
KEY_WORD_JSON_OBJECT = "object"
KEY_WORD_JSON_ARRAY_NEW = "array of json"
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
KEY_WORD_STRING_AND_INTEGER = "string/integer"
KEY_WORD_STRING_AND_BOOLEAN = "string/boolean"
KEY_WORD_NoneType = "null"
KEY_WORD_MAX = 20
BOOLEAN_VALUE = [True, False]

def loop_json_children(child_list):
    tmp_content = []
    for i, v in enumerate(child_list):
        if isinstance(v, dict):
            my_types = v.get("type").lower() if v.get("type") != "" else "string"
            if my_types in [KEY_WORD_JSON, KEY_WORD_JSON_ARRAY]:
                t_dict = {}
                if "name" in v:
                    t_dict["name"] = v.get("name")
                if "type" in v:
                    t_dict["type"] = v.get("type")
                if "detail" in v:
                    t_dict["detail"] = v.get("detail")
                if "examples" in v:
                    t_dict["examples"] = v.get("examples")
                if "required" in v:
                    t_dict["required"] = v.get("required")
                if "more" in v:
                    t_dict["more"] = v.get("more")
                if "description" in v:
                    t_dict["description"] = v.get("description")
                my_children = v.get("children", [])
                tmp_inner_data = loop_json_children(my_children)
                t_dict["children"] = tmp_inner_data
                tmp_content.append(t_dict)
            elif my_types in [KEY_WORD_STRING, KEY_WORD_INT, KEY_WORD_DATE, KEY_WORD_DATETIME,
                              KEY_WORD_BOOLEAN, KEY_WORD_SHORT, KEY_WORD_LONG, KEY_WORD_FLOAT,
                              KEY_WORD_DOUBLE, KEY_WORD_NoneType] and "$ref" not in v:
                tmp_content.append(v)
            # elif "$ref" in v:
            #     ref_id = v.get("$ref")
            #     ref_json_result = ProjectDataStructModel.objects.filter(id=ref_id).values("data")
            #     ref_result = json.loads(ref_json_result, ensure_ascii=False).get("content", [])
            #     tmp_content.extend(ref_result)
            else:
                tmp_content.append(v)
        else:
            return False
    return tmp_content
class JsonSchemaMaker:

    def __init__(self, body_data):
        self.body_data = body_data

    def __check_more_and_enum(self, v_dict, para_type=""):
        # para_type 用来传递type信息,依据type("integer")来做特殊处理
        check_dict = {}
        for check_key in ["maxLength", "minLength", "maximum", "minimum"]:
            check_value = v_dict.get(check_key, None)
            if check_value is None:
                # 没有设置 do nothing
                pass
            elif check_value == "":
                # "" 没有意义 直接删掉键值
                v_dict.pop(check_key)
            else:
                # 类似 "10" 才有意义 需要前端input做适当限制
                check_dict[check_key] = int(check_value)
        if "pattern" in v_dict:
            check_dict["pattern"] = v_dict.get("pattern")
        if "enum" in v_dict:
            check_dict["enum"] = []
            for i, j in enumerate(v_dict.get("enum")):
                if j.get("value", "") == "":
                    pass
                else:
                    if para_type in ["integer"]:
                        check_dict["enum"].append(int(j.get("value", "")))
                    else:
                        check_dict["enum"].append(j.get("value", ""))
            if not check_dict["enum"]:
                # check_dict["enum"] == [] 处理完还是空，就去掉这个key "enum"
                # 枚举值 没有值得话就去掉键值，防止误判
                check_dict.pop("enum")
        return check_dict

    def __loop_child_except_arr_obj(self, child_list):
        properties = {}  # check_list = [["jsonpath", "ruler", "expect"], ["wyf.aa.bb.ccc", ">=", "wyf"]] #jsonpath 可以携程jsonpath能识别的路径，然后便于检索
        required_list = []
        for i, v in enumerate(child_list):
            if isinstance(v, dict):
                # 都需要走这个步骤
                v_name = v.get("name", "")
                v_type = v.get("type") if v.get("type") and v.get("type", "") != "" else "string"
                properties[v_name] = {"type": v_type,
                                      "title": v.get("description", ""),
                                      "description": v.get("detail", "")}
                for check_key in ["maxLength", "minLength", "maximum", "minimum"]:
                    check_value = v.get(check_key, None)
                    if check_value is None:
                        # 没有设置 do nothing
                        pass
                    elif check_value == "":
                        # "" 没有意义 直接删掉键值
                        v.pop(check_key)
                    else:
                        # 类似 "10" 才有意义 需要前端input做适当限制
                        properties[v_name][check_key] = int(check_value)
                # 替换基本类型
                t = re.sub(r'float|short|long|double', "number", properties[v_name]["type"], flags=re.I)
                if "/" in t:
                    properties[v_name]["type"] = list(set(t.split("/")))
                else:
                    properties[v_name]["type"] = t
                # 转化more等数据
                if "more" in v:
                    more_and_enum = self.__check_more_and_enum(v.get("more", ""))
                    properties[v_name].update(more_and_enum)
                # 2022.11.11 对integer做特殊处理
                if "more" in v and v_type in ["integer", "number", "float"]:
                    # 数字类型转化 特殊处理
                    key_type = v_type
                    more_and_enum_1 = self.__check_more_and_enum(v.get("more", ""), para_type=key_type)
                    properties[v_name].update(more_and_enum_1)
                if properties[v_name]["type"]:
                    pass
                if v_type == "json" or v_type == "object":  # json, object
                    properties[v_name].update({"type": "object", "properties": {}})
                elif v_type == "array":  # array
                    properties[v_name].update({"type": "array", "items": {"type": "array", "properties": {}}})
                elif "array of " in v_type:  # array of int/string等
                    inner_type = str.split(v.get("type")[9:])[0]
                    if inner_type == "json":
                        properties[v_name].update({"type": "array", "items": {"type": "object", "properties": {}}})
                    else:
                        properties[v_name].update({"type": "array", "items": {"type": inner_type, "properties": {}}})
                else:
                    pass
                if v.get("required", "") == "M":
                    required_list.append(v.get("name", ""))
                if "children" in v:
                    children_properties = self.__loop_child_except_arr_obj(v.get("children", [{}]))
                    if v_type == "json" or v_type == "object":  # json
                        properties[v_name]['required'] = children_properties.pop("required")
                        properties[v_name]['properties'].update(children_properties)
                    elif v_type == "array" or ("array of " in v_type):  # array
                        properties[v_name]['required'] = children_properties.pop("required")
                        properties[v_name]['items']['properties'].update(children_properties)
                    # for i, v in enumerate(inner_list):
                    #     tmp_list = [child_list[0] + v[0], v[1], v[2]]
                    #     my_list.append(tmp_list)
                    # continue
            else:
                return {}
        properties["required"] = required_list
        return properties

    def get_json_schema(self):
        outer_content = self.body_data.get("content", {})
        if isinstance(outer_content, list) and not outer_content:
            return {}
        elif isinstance(outer_content, list) and outer_content:
            mock_outer_type = self.body_data.get("type", "").lower()
            inner_body = outer_content
            new_inner_body = loop_json_children(inner_body)
            changed_schema = self.__loop_child_except_arr_obj(new_inner_body)
        else:
            mock_outer_type = outer_content.get("type", "").lower()
            inner_body = outer_content.get("content", "")
            new_inner_body = loop_json_children(inner_body)
            changed_schema = self.__loop_child_except_arr_obj(new_inner_body)
        if mock_outer_type == "json" or mock_outer_type == "object":
            return {"type": "object", "properties": changed_schema, "required": changed_schema.pop("required")}
        elif mock_outer_type == "array":
            return {"type": "array:", "properties": changed_schema, "required": changed_schema.pop("required")}

