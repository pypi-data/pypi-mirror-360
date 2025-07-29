# -*- coding: utf-8 -*-
"""
Functions:
    language:
        Set the language for the help information. Currently supports en and zh.
    upgradeLog:
        Print the upgrade log with rich.
"""



# 导入需要的对象。
from re import search as _search
from colorama import Fore as _fore, init as _colorinit
from ._text import text
from ._base import _showArgsError, _checkAndShowParamTypeError
# 设置自动重置样式。
_colorinit(autoreset=True)



def upgradeLog(*args, ver="0.0.3", lang="en"):
    """
    Print the upgrade log.
    
    Args:
        *args:
            A TypeError will be raised when too many arguments are passed.
        ver (str, optional):
            Keyword argument.
            Specify the version number for which to retrieve the log.
            The Defaults to the latest version.
        lang (str, optional):
            Keyword argument.
            Specifies the language for printing logs.
            The default is "en".
    
    Returns:
        None
    
    Raises:
        TypeError: This error is raised when too many arguments are passed.
        ValueError: This error is raised when the provided version number does not conform to the "x.y.z" format.
    """
    
    # 如果有多余参数，就抛出错误。
    if args:
        _showArgsError(args)
    _checkAndShowParamTypeError("ver", ver, str)
    _checkAndShowParamTypeError("lang", lang, str)
    
    # 如果版本号不符合x.y.z格式，就抛出ValueError。
    if not _search("^\\d+\\.\\d+\\.\\d+$", ver):
        raise ValueError(f"{text[lang]['helps.function.updateLog.versionFormatError']}{_fore.GREEN}{repr(ver)}{_fore.RESET}")
    # 把版本号中的分割点替换为下划线，然后在指定语言的文本组里寻找指定版本号的日志。
    r = text[lang].get("helps.upgradeLogs." + ver.replace(".", "_"))
    # 如果找不到，就抛出错误。
    if r is None:
        raise ValueError(f"{text[lang]['helps.function.updateLog.versionNotFound']}{_fore.GREEN}{ver}{_fore.RESET}")
    # 找到了，就打印出来。
    print(r)
