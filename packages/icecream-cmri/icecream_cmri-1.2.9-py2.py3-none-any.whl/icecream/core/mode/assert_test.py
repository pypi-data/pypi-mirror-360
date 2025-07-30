import traceback
import logging
from jsonschema import validate as jsonvalidate, ValidationError
from jsonschema._format import draft7_format_checker
from jsonschema.exceptions import SchemaError

from icecream.core.test_result import AssertResult
from icecream.core.exceptions import AssertException
from icecream.utils.cmrischema import validate

logger = logging.getLogger(__name__)


class Test(object):
    """测试相关断言"""
    def __init__(self):
        self.__test_calc = []

    def eq(self, first, second, msg, detail=None):
        """first==second"""
        if first == second:
            self.__test_calc.append(AssertResult("pass", msg))
        else:
            self.__test_calc.append(AssertResult("failure", msg, detail))

    def less(self, a, b, msg, detail=None):
        """a<b"""
        if a < b:
            self.__test_calc.append(AssertResult("pass", msg))
        else:
            self.__test_calc.append(AssertResult("failure", msg, detail))

    def greater(self, a, b, msg, detail=None):
        """a>b"""
        if a > b:
            self.__test_calc.append(AssertResult("pass", msg))
        else:
            self.__test_calc.append(AssertResult("failure", msg, detail))

    def in_(self, container, member, msg, detail=None):
        """检查数据是否在continer中"""
        if member in container:
            self.__test_calc.append(AssertResult("pass", msg))
        else:
            self.__test_calc.append(AssertResult("failure", msg, detail))

    def expr(self, expr, msg, detail=None):
        """检查表达式"""
        if expr:
            self.__test_calc.append(AssertResult("pass", msg))
        else:
            self.__test_calc.append(AssertResult("failure", msg, detail))

    def cmri_schema(self, response, cmri_schema, msg):
        """
        验证cmri_shcema
        :param response:
        :param cmri_schema:
        :param msg:
        :return:
        """

        try:
            detail = validate(response, cmri_schema)
            if detail:
                self.__test_calc.append(AssertResult("failure", msg, error=detail))
            else:
                self.__test_calc.append(AssertResult("pass", msg))
        except Exception:
            error_msg = traceback.format_exc()
            logger.warning(error_msg)
            self.__test_calc.append(AssertResult("error", msg, error=error_msg))

    def json_schema(self, response, json_schema, msg):
        """
        验证JSON schema
        :param response: 待验证的响应
        :param json_schema: JSON schema定义
        :param msg: 断言消息
        :return:
        """
        try:
            jsonvalidate(instance=response, schema=json_schema, format_checker=draft7_format_checker)
            self.__test_calc.append(AssertResult("pass", msg))
        except ValidationError as e:
            detail = str(e)
            self.__test_calc.append(AssertResult("failure", msg, error=detail))
        except Exception:
            error_msg = traceback.format_exc()
            logger.warning(error_msg)
            self.__test_calc.append(AssertResult("error", msg, error=error_msg))

    def commit(self):
        """统一提交，进行验证"""
        flag = 0
        result = {0: "pass", 1: "failure", 2: "unknown"}
        try:
            if len(self.__test_calc) == 0:
                flag = 2  # 未写断言，不知道的结果
            for test in self.__test_calc:
                if test.result == "failure":
                    flag = 1
                    break
            if flag == 1:
                raise AssertException([tmp_test.to_json() for tmp_test in self.__test_calc])
        finally:
            r = {"result": result.get(flag), "detail": [tmp_test.to_json() for tmp_test in self.__test_calc]}
            self.__test_calc = []
            return r
