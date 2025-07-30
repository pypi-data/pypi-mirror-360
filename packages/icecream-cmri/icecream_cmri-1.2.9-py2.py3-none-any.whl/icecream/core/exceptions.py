"""
@author:cmcc
@file: exceptions.py
@time: 2022/11/30 14:48
"""


class IceBaseException(Exception):
    pass


class ValidationFailure(IceBaseException):
    pass


class FunctionNotFound(IceBaseException):
    pass


class VariableNotFound(IceBaseException):
    pass


class ParamsError(IceBaseException):
    pass


class RunnerException(Exception):
    """
    Base driver exception.
    """
    pass


class FileNotFoundException(RunnerException):
    pass


class YamlFormatException(RunnerException):
    pass


class AssertException(AssertionError):
    pass


class AttrException(RunnerException):
    pass


class ExecCaseException(RunnerException):
    pass

