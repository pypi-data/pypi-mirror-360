import ast
import builtins
import re
import logging
import types
from typing import List, Dict, Any, Callable, Text, Set
from icecream.core import exceptions
from icecream.utils.common import Utils

logger = logging.getLogger(__name__)

VariablesMapping = Dict[Text, Any]
FunctionsMapping = Dict[Text, Callable]


class ParseParams:
    # variable mapping, e.g. ${var} or $var or {{var}} => {${var}:var, $var:var, {{var}}:var}
    variables_regex_compile = re.compile(r"(\$\{[\w-]\})|(\$\w+)|(\{\{[\w-]\}\})")
    # function notation, e.g. ${func1($var_1, $var_3)}
    function_regex_compile = re.compile(r"(\$\{\w+\([\$\w\.\-/\s=,]*\)\})")
    # function notation, e.g. ${func1($var_1, $var_3)}
    function_detail_regex_compile = re.compile(r"\$\{(\w+)\(([\$\w\.\-/\s=,]*)\)\}")

    @classmethod
    def regex_findall_variables(cls, raw_string: Text) -> Dict:
        """
        变量转化为映射字典
        :param raw_string:
        :return:
        Examples:
            >>> regex_findall_variables('$var')
            {'$var': 'var'}
             >>> regex_findall_variables('${max($test,2)}')
            {'{{mm}}': 'mm'}
             >>> regex_findall_variables('${tt}')
            {'${tt}': 'tt'}
        """
        result = {}
        matches = cls.variables_regex_compile.findall(raw_string)
        for match in matches:
            for m in match:
                if m:
                    var_name = m.strip('$').strip('{}')
                    result[m] = var_name
        return result

    @classmethod
    def regex_findall_functions(cls, raw_string: Text) -> Dict:
        """
        函数转换成映射的字典
        :param raw_string:
        :return:
        Examples:
            >>> regex_findall_functions('${gen_app_version()}')
            {'${gen_app_version()}': [('gen_app_version', '')]}
             >>> regex_findall_functions('${max($test,2)}')
            {'${max($test,2)}': [('max', '$test,2')]}
        """
        result = {}
        matches = cls.function_regex_compile.findall(raw_string)
        for match in matches:
            if match:
                details = cls.function_detail_regex_compile.findall(match)
                if details:
                    result[match] = details[0]
                else:
                    result[match] = match
        return result

    @classmethod
    def get_target_sub_position(cls, target: Text, start_position: int = 0) -> int:
        """ get target sub position

        Args:
            target (str): target
            start_position(int): start position
        Returns:
            int: target sub position
        """
        position_1 = target.find("$", start_position)
        position_2 = target.find("{{", start_position)
        if position_1 >= 0 and position_2 >= 0:
            return min(position_1, position_2)
        return max(position_1, position_2)

    @classmethod
    def get_mapping_variable(cls, variable_name: Text, variables_mapping: VariablesMapping) -> Any:
        try:
            return variables_mapping[variable_name]
        except KeyError:
            raise exceptions.VariableNotFound(
                f"{variable_name} not found in {variables_mapping}"
            )

    @classmethod
    def parse_string_value(cls, str_value: Text) -> Any:
        """ parse string to number if possible
        e.g. "123" => 123
             "12.2" => 12.3
             "abc" => "abc"
             "$var" => "$var"
        """
        try:
            return ast.literal_eval(str_value)
        except ValueError:
            return str_value
        except SyntaxError:
            # e.g. $var, ${func}
            return str_value

    @classmethod
    def parse_function_params(cls, params: Text) -> Dict:
        """ parse function params to args and kwargs.

        Args:
            params (str): function param in string

        Returns:
            dict: function meta dict

                {
                    "args": [],
                    "kwargs": {}
                }

        Examples:
            >>> parse_function_params("")
            {'args': [], 'kwargs': {}}

            >>> parse_function_params("5")
            {'args': [5], 'kwargs': {}}

            >>> parse_function_params("1, 2")
            {'args': [1, 2], 'kwargs': {}}

            >>> parse_function_params("a=1, b=2")
            {'args': [], 'kwargs': {'a': 1, 'b': 2}}

            >>> parse_function_params("1, 2, a=3, b=4")
            {'args': [1, 2], 'kwargs': {'a':3, 'b':4}}

        """
        function_meta = {"args": [], "kwargs": {}}

        params_str = params.strip()
        if params_str == "":
            return function_meta

        args_list = params_str.split(",")
        for arg in args_list:
            arg = arg.strip()
            if "=" in arg:
                key, value = arg.split("=")
                function_meta["kwargs"][key.strip()] = cls.parse_string_value(value.strip())
            else:
                function_meta["args"].append(cls.parse_string_value(arg))

        return function_meta

    @classmethod
    def get_mapping_function(cls, function_name: Text, functions_mapping: FunctionsMapping) -> Callable:
        """ get function from functions_mapping,
            if not found, then try to check if builtin function.

        Args:
            function_name (str): function name
            functions_mapping (dict): functions mapping

        Returns:
            mapping function object.

        Raises:
            exceptions.FunctionNotFound: function is neither defined in debugtalk.py nor builtin.

        """
        if function_name in functions_mapping:
            return functions_mapping[function_name] if functions_mapping[function_name] else None

        try:
            built_in_functions = Utils.load_builtin_functions()
            return built_in_functions[function_name] if built_in_functions[function_name] else None
        except KeyError:
            pass

        try:
            # check if Python builtin functions
            return getattr(builtins, function_name)
        except AttributeError:
            pass

        raise exceptions.FunctionNotFound(f"{function_name} is not found.")

    @classmethod
    def parse_string(cls,
                     raw_string: Text,
                     variables_mapping: VariablesMapping,
                     functions_mapping: FunctionsMapping,
    ) -> Any:

        position = cls.get_target_sub_position(raw_string)
        if position < 0:
            return raw_string

        # 处理函数 search function like ${func($a, $b)}
        functions = {}
        for key, value in cls.regex_findall_functions(raw_string).items():
            func_name, func_params = value[0], value[1]
            func = cls.get_mapping_function(func_name, functions_mapping)
            function_meta = cls.parse_function_params(value[1])
            args = function_meta["args"]
            kwargs = function_meta["kwargs"]
            parsed_args = cls.parse_data(args, variables_mapping, functions_mapping)
            parsed_kwargs = cls.parse_data(kwargs, variables_mapping, functions_mapping)
            try:
                func_eval_value = func(*parsed_args, **parsed_kwargs)
            except Exception as ex:
                logger.error(
                    f"call function error:\n"
                    f"func_name: {func_name}\n"
                    f"args: {parsed_args}\n"
                    f"kwargs: {parsed_kwargs}\n"
                    f"{type(ex).__name__}: {ex}"
                )
                raise
            functions[key] = func_eval_value
        for key, value in functions.items():
            raw_string = raw_string.replace(key, str(value))

        # 处理变量 search variable like ${var} or $var or {{var}}
        variables = {}
        for key, value in cls.regex_findall_variables(raw_string).items():
            variables[key] = cls.get_mapping_variable(value, variables_mapping)
        for key, value in variables.items():
            raw_string = raw_string.replace(key, str(value))
        return raw_string

    @classmethod
    def parse_data(cls,
            raw_data: Any,
            variables_mapping: VariablesMapping = None,
            functions_mapping: FunctionsMapping = None
    ) -> Any:

        if isinstance(raw_data, str):
            # content in string format may contains variables and functions
            variables_mapping = variables_mapping or {}
            functions_mapping = functions_mapping or {}
            # only strip whitespaces and tabs, \n\r is left because they maybe used in changeset
            raw_data = raw_data.strip(" \t")
            return cls.parse_string(raw_data, variables_mapping, functions_mapping)

        elif isinstance(raw_data, (list, set, tuple)):
            return [
                cls.parse_data(item, variables_mapping, functions_mapping) for item in raw_data
            ]

        elif isinstance(raw_data, dict):
            parsed_data = {}
            for key, value in raw_data.items():
                parsed_key = cls.parse_data(key, variables_mapping, functions_mapping)
                parsed_value = cls.parse_data(value, variables_mapping, functions_mapping)
                parsed_data[parsed_key] = parsed_value

            return parsed_data

        else:
            # other types, e.g. None, int, float, bool
            return raw_data


class ParseParamsOlder:
    """
    解析特殊处理文本参数
    """
    # use $$ to escape $ notation
    dolloar_regex_compile = re.compile(r"\$\$")
    # variable notation, e.g. ${var} or $var or {{var}}
    variable_regex_compile = re.compile(r"\$\{(@?\w+)\}|\$(@?\w+)|\{\{(@?[\w-]+)\}\}")
    # variable mapping, e.g. ${var} or $var or {{var}} => {${var}:var, $var:var, {{var}}:var}
    variable_regex_mapping = re.compile(r"(\$\{\w+\})|(\$\w+)|(\{\{\w+\}\})")
    # function notation, e.g. ${func1($var_1, $var_3)}
    function_regex_compile = re.compile(r"\$\{(\w+)\(([\$\w\.\-/\s=,]*)\)\}")

    @classmethod
    def regex_findall_variables(cls, raw_string: Text) -> List[Text]:
        """extract all variable names from content, which is in format $variable

            Args:
                raw_string (str): string content

            Returns:
                list: variables list extracted from string content

            Examples:
                >>> regex_findall_variables("$variable")
                ["variable"]

                >>> regex_findall_variables("/blog/$postid")
                ["postid"]

                >>> regex_findall_variables("/$var1/$var2")
                ["var1", "var2"]

                >>> regex_findall_variables("abc")
                []

            """
        vars_list = []
        try:
            var_match = cls.variable_regex_compile.findall(raw_string)
            for item in var_match:
                var_name = [item for item in item if len(item.strip()) > 0][0]
                vars_list.append(var_name)
            return vars_list
        except ValueError:
            return []

    @classmethod
    def regex_findall_functions(cls, content: Text) -> List[Text]:
        """ extract all functions from string content, which are in format ${fun()}

        Args:
            content (str): string content

        Returns:
            list: functions list extracted from string content

        Examples:
            >>> regex_findall_functions("${func(5)}")
            ["func(5)"]

            >>> regex_findall_functions("${func(a=1, b=2)}")
            ["func(a=1, b=2)"]

            >>> regex_findall_functions("/api/1000?_t=${get_timestamp()}")
            ["get_timestamp()"]

            >>> regex_findall_functions("/api/${add(1, 2)}")
            ["add(1, 2)"]

            >>> regex_findall_functions("/api/${add(1, 2)}?_t=${get_timestamp()}")
            ["add(1, 2)", "get_timestamp()"]

        """
        try:
            return cls.function_regex_compile.findall(content)
        except TypeError as ex:
            return []

    @classmethod
    def extract_variables(cls, content: Any) -> Set:
        """ extract all variables in content recursively.
        """
        if isinstance(content, (list, set, tuple)):
            variables = set()
            for item in content:
                variables = variables | cls.extract_variables(item)
            return variables

        elif isinstance(content, dict):
            variables = set()
            for key, value in content.items():
                variables = variables | cls.extract_variables(value)
            return variables

        elif isinstance(content, str):
            return set(cls.regex_findall_variables(content))

        return set()

    @classmethod
    def parse_string_value(cls, str_value: Text) -> Any:
        """ parse string to number if possible
        e.g. "123" => 123
             "12.2" => 12.3
             "abc" => "abc"
             "$var" => "$var"
        """
        try:
            return ast.literal_eval(str_value)
        except ValueError:
            return str_value
        except SyntaxError:
            # e.g. $var, ${func}
            return str_value

    @classmethod
    def parse_function_params(cls, params: Text) -> Dict:
        """ parse function params to args and kwargs.

        Args:
            params (str): function param in string

        Returns:
            dict: function meta dict

                {
                    "args": [],
                    "kwargs": {}
                }

        Examples:
            >>> parse_function_params("")
            {'args': [], 'kwargs': {}}

            >>> parse_function_params("5")
            {'args': [5], 'kwargs': {}}

            >>> parse_function_params("1, 2")
            {'args': [1, 2], 'kwargs': {}}

            >>> parse_function_params("a=1, b=2")
            {'args': [], 'kwargs': {'a': 1, 'b': 2}}

            >>> parse_function_params("1, 2, a=3, b=4")
            {'args': [1, 2], 'kwargs': {'a':3, 'b':4}}

        """
        function_meta = {"args": [], "kwargs": {}}

        params_str = params.strip()
        if params_str == "":
            return function_meta

        args_list = params_str.split(",")
        for arg in args_list:
            arg = arg.strip()
            if "=" in arg:
                key, value = arg.split("=")
                function_meta["kwargs"][key.strip()] = cls.parse_string_value(value.strip())
            else:
                function_meta["args"].append(cls.parse_string_value(arg))

        return function_meta

    @classmethod
    def get_mapping_variable(cls, variable_name: Text, variables_mapping: VariablesMapping) -> Any:
        """ get variable from variables_mapping.

        Args:
            variable_name (str): variable name
            variables_mapping (dict): variables mapping

        Returns:
            mapping variable value.

        Raises:
            exceptions.VariableNotFound: variable is not found.

        """
        # TODO: get variable from debugtalk module and environ
        value = variables_mapping.get(variable_name)
        return value


    @classmethod
    def get_mapping_function(cls, function_name: Text, functions_mapping: FunctionsMapping) -> Callable:
        """ get function from functions_mapping,
            if not found, then try to check if builtin function.

        Args:
            function_name (str): function name
            functions_mapping (dict): functions mapping

        Returns:
            mapping function object.

        Raises:
            exceptions.FunctionNotFound: function is neither defined in debugtalk.py nor builtin.

        """
        if function_name in functions_mapping:
            return functions_mapping.get(function_name) if functions_mapping.get(function_name) else None

        try:
            built_in_functions = Utils.load_builtin_functions()
            return built_in_functions.get(function_name) if built_in_functions.get(function_name) else None
        except KeyError:
            pass

        try:
            # check if Python builtin functions
            return getattr(builtins, function_name) if getattr(builtins, function_name) else None
        except AttributeError:
            pass
        return function_name

    @classmethod
    def get_target_sub_position(cls, target: Text, start_position: int = 0) -> int:
        """ get target sub position

        Args:
            target (str): target
            start_position(int): start position
        Returns:
            int: target sub position
        """
        position_1 = target.find("$", start_position)
        position_2 = target.find("{{", start_position)
        if position_1 >= 0 and position_2 >= 0:
            return min(position_1, position_2)
        return max(position_1, position_2)

    @classmethod
    def parse_string(cls,
            raw_string: Text,
            variables_mapping: VariablesMapping,
            functions_mapping: FunctionsMapping,
    ) -> Any:
        """ parse string content with variables and functions mapping.

        Args:
            raw_string: raw string content to be parsed.
            variables_mapping: variables mapping.
            functions_mapping: functions mapping.

        Returns:
            str: parsed string content.

        Examples:
            >>> raw_string = "abc${add_one($num)}def"
            >>> variables_mapping = {"num": 3}
            >>> functions_mapping = {"add_one": lambda x: x + 1}
            >>> parse_string(raw_string, variables_mapping, functions_mapping)
                "abc4def"

        """
        match_start_position = cls.get_target_sub_position(raw_string, 0)
        if match_start_position >= 0:
            parsed_string = raw_string[0:match_start_position]
        else:
            parsed_string = raw_string
            return parsed_string

        while match_start_position < len(raw_string):

            # Notice: notation priority
            # $$ > ${func($a, $b)} > $var

            # search $$
            dollar_match = cls.dolloar_regex_compile.match(raw_string, match_start_position)
            if dollar_match:
                match_start_position = dollar_match.end()
                parsed_string += "$"
                continue

            # search function like ${func($a, $b)}
            func_match = cls.function_regex_compile.match(raw_string, match_start_position)
            if func_match:
                func_name = func_match.group(1)
                func_expression = "${" + func_name + "()}"
                func_value = cls.get_mapping_function(func_name, functions_mapping)
                func = func_value if func_value else func_expression

                func_params_str = func_match.group(2)

                function_meta = cls.parse_function_params(func_params_str)
                args = function_meta["args"]
                kwargs = function_meta["kwargs"]
                parsed_args = cls.parse_data(args, variables_mapping, functions_mapping)
                parsed_kwargs = cls.parse_data(kwargs, variables_mapping, functions_mapping)
                if isinstance(func, types.FunctionType):
                    func_eval_value = func(*parsed_args, **parsed_kwargs)
                else:
                    func_eval_value = func_expression

                func_raw_str = "${" + func_name + f"({func_params_str})" + "}"
                if func_raw_str == raw_string:
                    # raw_string is a function, e.g. "${add_one(3)}", return its eval value directly
                    return func_eval_value

                # raw_string contains one or many functions, e.g. "abc${add_one(3)}def"
                parsed_string += str(func_eval_value)
                match_start_position = func_match.end()
                continue

            # search variable like ${var} or $var or {{var}}
            var_match = cls.variable_regex_compile.match(raw_string, match_start_position)
            if var_match:
                var_name = var_match.group(1) or var_match.group(2) or var_match.group(3)
                var_expression = "${" + var_name + "}" if var_match.group(1) else (
                    "$" + var_name if var_match.group(2) else "{{" + var_name + "}}")
                var_value = cls.get_mapping_variable(var_name, variables_mapping)
                # var_value = var_value if var_value else var_expression
                if f"${var_name}" == raw_string or "${" + var_name + "}" == raw_string \
                        or "{{" + var_name + "}}" == raw_string:
                    # raw_string is a variable, $var or ${var}, return its value directly
                    return var_value

                # raw_string contains one or many variables, e.g. "abc${var}def"

                parsed_string += str(var_value)
                match_start_position = var_match.end()
                continue

            curr_position = match_start_position

            match_start_position = cls.get_target_sub_position(raw_string, curr_position + 1)
            if match_start_position >= 0:
                remain_string = raw_string[curr_position:match_start_position]
            else:
                remain_string = raw_string[curr_position:]
                # break while loop
                match_start_position = len(raw_string)

            parsed_string += remain_string

        return parsed_string

    @classmethod
    def parse_data(cls,
            raw_data: Any,
            variables_mapping: VariablesMapping = None,
            functions_mapping: FunctionsMapping = None,
    ) -> Any:
        """ parse raw data with evaluated variables mapping.
            Notice: variables_mapping should not contain any variable or function.
        """
        if isinstance(raw_data, str):
            # content in string format may contains variables and functions
            variables_mapping = variables_mapping or {}
            functions_mapping = functions_mapping or {}
            # only strip whitespaces and tabs, \n\r is left because they maybe used in changeset
            raw_data = raw_data.strip(" \t")
            return cls.parse_string(raw_data, variables_mapping, functions_mapping)

        elif isinstance(raw_data, (list, set, tuple)):
            return [
                cls.parse_data(item, variables_mapping, functions_mapping) for item in raw_data
            ]

        elif isinstance(raw_data, dict):
            parsed_data = {}
            for key, value in raw_data.items():
                parsed_key = cls.parse_data(key, variables_mapping, functions_mapping)
                parsed_value = cls.parse_data(value, variables_mapping, functions_mapping)
                parsed_data[parsed_key] = parsed_value

            return parsed_data

        else:
            # other types, e.g. None, int, float, bool
            return raw_data

    @classmethod
    def parse_variables_mapping(cls,
            variables_mapping: VariablesMapping, functions_mapping: FunctionsMapping = None
    ) -> VariablesMapping:

        parsed_variables: VariablesMapping = {}

        while len(parsed_variables) != len(variables_mapping):
            for var_name in variables_mapping:

                if var_name in parsed_variables:
                    continue

                var_value = variables_mapping[var_name]
                variables = cls.extract_variables(var_value)

                # check if reference variable itself
                if var_name in variables:
                    # e.g.
                    # variables_mapping = {"token": "abc$token"}
                    # variables_mapping = {"key": ["$key", 2]}
                    raise exceptions.VariableNotFound(var_name)

                # check if reference variable not in variables_mapping
                not_defined_variables = [
                    v_name for v_name in variables if v_name not in variables_mapping
                ]
                if not_defined_variables:
                    # e.g. {"varA": "123$varB", "varB": "456$varC"}
                    # e.g. {"varC": "${sum_two($a, $b)}"}
                    raise exceptions.VariableNotFound(not_defined_variables)

                try:
                    parsed_value = cls.parse_data(
                        var_value, parsed_variables, functions_mapping
                    )
                except exceptions.VariableNotFound:
                    continue

                parsed_variables[var_name] = parsed_value

        return parsed_variables

if __name__ == '__main__':
    variables = {
        "var": "1000",
        "mm": "A2dEx",
        "a": 5,
        # "tang": "123",
        # "jian": "yang"
    }
    functions = {
        "add_two_nums": lambda a, b=1: a,
        "gen_app_version": lambda: "m666",
        "max": lambda x, y: min(x, y)
    }
    str_text = "hahahah: $var ${tang},  ${mm} ${add_two_nums($a)} ${max($a,2)} ${lambda666}，{{jian}},${max(${a},2)}"
    print(ParseParamsOlder.parse_data(str_text, variables, functions))