# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring



# 显示多余参数的错误信息，报告了多余的参数数量和这些参数的值。
def _showArgsError(args):
    raise TypeError(f"{len(args)} extra parameters gived: {args}")

# 检查参数类型，如果类型错误，就抛出错误。
def _checkAndShowParamTypeError(varName, var, varType):
    if not isinstance(var, varType):
        s = None
        if isinstance(varType, type):
            s = varType.__name__
        elif isinstance(varType, (tuple, list, set)):
            if isinstance(varType, set):
                varType = list(varType)
            if len(varType) == 1:
                s = varType[0].__name__
            elif len(varType) == 2:
                s = varType[0].__name__ + " or " + varType[1].__name__
            elif len(varType) >= 3:
                bl = varType[:-1]
                s = ", ".join([i.__name__ for i in bl]) + " or " + varType[-1].__name__
        raise TypeError(f"The parameter \"{varName}\" must be {s}, but gived {type(var).__name__}.")
