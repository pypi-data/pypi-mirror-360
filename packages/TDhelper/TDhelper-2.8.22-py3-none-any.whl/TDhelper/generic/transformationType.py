#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
"""
@File    :   transformationType.py
@Time    :   2020/07/30 23:34:47
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   类型转换
"""

# here put the import lib
import datetime
from pickle import TRUE

# code start


def transformation(value: any, transformationType, split_str=" ", default_None=""):
    """
    类型转换(目前仅只支持int,str,datetime,bool转换)
    - Params:
        - value: 需要转换的内容.
        - transformationType: 转换后的类型.
        - split_str: 字符转数组分割字符，默认一个空格, 如字符串内不包含分割字符则会直接把字符串按每个字符分割；
    """
    if not value:
        return default_None
    try:
        if not isinstance(value, transformationType):
            if transformationType == int:
                value = int(value)
            if transformationType == str:
                if isinstance(value, datetime.datetime):
                    # 日期类型转字符
                    value = datetime.datetime.strftime(value, "%Y-%m-%d %H:%M:%S")
                elif isinstance(value, datetime.date):
                    value = datetime.date.strftime(value, "%Y-%m-%d")
                else:
                    value = str(value)
            if transformationType == float:
                try:
                    if isinstance(
                        value,
                        (
                            str,
                            int,
                        ),
                    ):
                        value = float(value)
                    else:
                        raise Exception(
                            "transformation float, value type must is str. value: %s"
                            % value
                        )
                except Exception as e:
                    raise e
            if transformationType == datetime.datetime:
                if isinstance(value, str):
                    value = value.replace("/", "-")
                    if len(value) > 10:
                        value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    else:
                        value = datetime.datetime.strptime(value, "%Y-%m-%d")
                else:
                    raise Exception(
                        "transformation datetime, value type must is str. value:%s"
                        % value
                    )
            if transformationType == datetime.date:
                if isinstance(value, str):
                    value = value.replace("/", "-")
                    if len(value) > 10:
                        value = datetime.datetime.strptime(
                            value, "%Y-%m-%d %H:%M:%S"
                        ).date()
                    else:
                        value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                else:
                    raise Exception(
                        "transformation date, value type must is str. value: %s" % value
                    )
            if transformationType == bool:
                if isinstance(value, str):
                    v = value.lower()
                    if not v:
                        value = False
                    elif v == "false":
                        value = False
                    elif v == "true":
                        value = True
                    else:
                        value = True
                else:
                    value = bool(value)
            if transformationType == list:
                if isinstance(value, str):
                    if value.__contains__(split_str):
                        value= value.split(split_str)
                    else:
                        value= list(value)
    except Exception as e:
        raise e
    return value
