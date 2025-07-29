#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   dictHelper.py
@Time    :   2020/09/24 07:13:30
@Author  :   Tang Jing
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
'''

# here put the import lib

# code start


def createDictbyStr(key: str, source={}, value: any = None):
    ''' [obsolete]createDictbyStr
        (obsolete)create an dict object by formatter string. this method has obsoleted, can use appendDict method.
        - Params:
        -   key: <str>, the string that generates the dict.
        -   source: <dict>, the targte dict, default {}.
        -   value: <any>, set the value of the new dict last child node.
        - Returns: <dict>, the new dict.
    '''
    result = source
    node = ''
    total = 1
    m_source = result
    for k in key.split('.'):
        total += 1
        node += ("." if node else "") + k
        if node:
            search_count = 1
            m_m_source = m_source
            for k1 in node.split('.'):
                search_count += 1
                if search_count > len(node.split('.')):
                    if k1 not in m_m_source:
                        m_m_source.update({k1: value})
                    else:
                        m_m_source = m_m_source[k1]
                else:
                    if k1 not in m_m_source:
                        m_m_source.update({k1: {}})
                    else:
                        if not isinstance(m_m_source[k1], dict):
                            m_m_source[k1] = {}
                    m_m_source = m_m_source[k1]
    return result


def appendDict(k, v, source: 'dict'):
    k = k.split('.')
    count = 0
    instance_dict = source
    for item in k:
        count += 1
        if count == len(k):
            instance_dict.update({item: v})
        else:
            if item not in instance_dict:
                instance_dict.update({item: {}})
            instance_dict = instance_dict[item]


def findInDict(findKey, source: 'dict|type'):
    '''
        根据finkey查找dict.
        - Params:
        -   findkey: <str>, formatter("node1.node2.node3").
        -   source: <dict>, it is your search target, findkey must in it. if findkey not in it, then raise an error
        - Returns: <any>, if can't found, then return None.
    '''
    result = None
    search_node = ''
    for key in findKey.split('.'):
        search_node += ("." if search_node else "") + key
        if isinstance(source, dict):
            if key not in source:
                raise Exception("can not found key(%s)" % search_node)
            result = source[key]
            source = source[key]
        elif isinstance(source, object):
            result = getattr(source, key)
            if not result:
                raise Exception("can not found key(%s)" % search_node)
            else:
                source = result
    return result


def hitDict(k, source: "dict"):
    search_node = ''
    instace_dict = source
    keys = k.split('.')
    count = 0
    for key in keys:
        count += 1
        search_node += ("." if search_node else "") + key
        if key not in instace_dict:
            raise Exception("can not found key(%s)" % search_node)
        if count == len(keys):
            return instace_dict[key]
        else:
            instace_dict = instace_dict[key]


def setDictValue(k, v, source: 'dict|type'):
    search_node = ''
    instace_dict = source
    keys = k.split('.')
    count = 0
    for key in keys:
        count += 1
        search_node += ("." if search_node else "") + key
        if isinstance(instace_dict, dict):
            if key not in instace_dict:
                raise Exception("can not found key(%s)" % search_node)
            if count == len(keys):
                instace_dict[key] = v
            else:
                instace_dict = instace_dict[key]
        elif isinstance(instace_dict, object):
            result = getattr(instace_dict, key)
            if not result:
                raise Exception("can not found key(%s)" % search_node)
            if count == len(keys):
                setattr(instace_dict, v)
            else:
                instace_dict = result


def destoryKey(k, source: "dict"):
    search_node = ''
    instace_dict = source
    keys = k.split('.')
    count = 0
    for key in keys:
        count += 1
        search_node += ("." if search_node else "") + key
        if key not in instace_dict:
            raise Exception("can not found key(%s)" % search_node)
        if count == len(keys):
            instace_dict.pop(key)
        else:
            instace_dict = instace_dict[key]
