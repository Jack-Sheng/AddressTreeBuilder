#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@project:hello
@author:JianSheng
@file:TEST.py
@ide:PyCharm
@TIME:2019-01-08
"""

from __future__ import unicode_literals  # at top of module
from __future__ import division, print_function, with_statement
import uuid
import pymysql
import datetime
import traceback


class TreeNode(object):

    """The basic node of tree structure"""
    def __init__(self, name, parent=None):
        super(TreeNode, self).__init__()
        self.name = name
        self.id = uuid.uuid1()
        self.parentid = ''
        self.parent = parent
        self.leixing = ''
        self.child = {}

    def __repr__(self) :
        return 'TreeNode(%s)' % self.name


    def __contains__(self, item):
        return item in self.child


    def __len__(self):
        """return number of children node"""
        return len(self.child)

    def __bool__(self, item):
        """always return True for exist node"""
        return True

    @property
    def path(self):
        """return path string (from root to current node)"""
        if self.parent:
            return '%s %s' % (self.parent.path.strip(), self.name)
        else:
            return self.name

    def get_child(self, name, defval=None):
        """get a child node of current node"""
        return self.child.get(name, defval)

    # add childNode by Name,return childNode
    def add_child(self, name, obj=None):
        """add a child node to current node"""
        if obj and not isinstance(obj, TreeNode):
            raise ValueError('TreeNode only add another TreeNode obj as child')
        if obj is None:
            obj = TreeNode(name)
        obj.parent = self
        obj.parentid = self.id
        self.child[name] = obj
        return obj


    def del_child(self, name):
        """remove a child node from current node"""
        if name in self.child:
            del self.child[name]

    def create_child(self, path, create=False, cursor=None, sql='', zuobiao=''):
        """find child node by path/name, return None if not found"""
        # convert path to a list if input is a string
        path = path if isinstance(path, list) else path.split()
        cur = self
        index = 0
        while '' in path:
            path.remove('')
        length = len(path)
        for sub in path:
            # search子节点
            obj = cur.get_child(sub)
            # create子节点
            if obj is None and create:
                # create new node if need
                obj = cur.add_child(sub)
                leixing = searchLeixing(index=index, length=length, nodeName=sub, parentleixing=cur.leixing)
                if int(leixing) > 50:
                    ins = sql % (obj.id, obj.parentid, sub, leixing,zuobiao)
                else:
                    ins = sql % (obj.id, obj.parentid, sub, leixing, '')
                obj.leixing = leixing
                cursor.execute(ins)
            # check if search done
            if obj is None:
                break
            cur = obj
            index += 1
        return obj


    def items(self):
        return self.child.items()

    def dump(self, indent=0):
        """dump tree to string"""
        tab = '    '*(indent-1) + ' |- ' if indent > 0 else ''
        print('%s%s' % (tab, self.name))
        for name, obj in self.items():
            obj.dump(indent+1)

def querySQL(sql = ''):
     db = pymysql.connect("localhost", "root", "123456", "test")
     try:
        cursor = db.cursor()
        cursor.execute(sql)
        resultSet = cursor.fetchall()
        db.commit()
     except Exception as e:
     # Rollback in case there is any error
        print(e)
        db.rollback()
     cursor.close()
     db.close()
     return resultSet

def searchLeixing(index, length, nodeName, parentleixing):
    if nodeName == '陕西省':
        return '0'
    elif nodeName == '铜川市':
        return '14'
    elif nodeName == '王益区' or nodeName == '耀州区' or nodeName == '宜君县' or nodeName == '印台区' or nodeName == '新区':
        return '15'
    elif '镇' in nodeName or '乡' in nodeName or '街道' in nodeName:
        return '20'
    elif '路' in nodeName or '巷' in nodeName or ('街' in nodeName and '道' not in nodeName):
        return '41'
    elif '村' in nodeName:
        return '43'
    elif '组' in nodeName:
        return '34'
    elif ('号' in nodeName or nodeName.isdigit()) and int(parentleixing)<50:
        return '100'
    elif '栋' in nodeName or '幢'in nodeName or '号楼' in nodeName or ('楼' in nodeName and index<length-1 and int(parentleixing)>50):
        return '102'
    elif '单元' in nodeName:
        return '51'
    elif ('号' in nodeName or '层' in nodeName or '楼' in nodeName or '室' in nodeName or nodeName.isdigit()) and index==length-1:
        return '53'
    else:
        return '49'


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    print('hello')
    selectSQL = 'select dongjing,beiwei,one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen from tongchuan_yaozhouqu order by dongjing DESC'
    insertSQL = """insert into sd_dz_dizhiyuansu_yz(id,shangjiyuansu,dizhiyuansumingcheng,dizhiyuansuleixing,zuobiao,zhuangtai) values('%s','%s','%s','%s','%s',2)"""

    db = pymysql.connect(host="localhost", port=3307, user="root", passwd="123456", db="tongchuan", charset='utf8')
    cursor = db.cursor()
    cursor.execute(selectSQL)
    resultSet = cursor.fetchall()

    root = TreeNode('陕西省')
    count = 0
    for addre in resultSet:
        try:
            addrList = list(addre)
            latlng = '{"lat":' + addrList[1] + ',"lng":' + addrList[0] + '}' if addrList[0] != '' else ''
            addr = addrList[2:]
            obj = root.create_child(path=addr, create=True, cursor=cursor, sql=insertSQL, zuobiao=latlng)
        except Exception as e:
            # Rollback in case there is any error
            print(e)
            db.rollback()
            f = open("log.txt", 'a')
            traceback.print_exc(file=f)
            f.flush()
            f.close()
        count += 1
        log = '第' + str(count) + '条打完了'
        print(log)
    db.commit()
    cursor.close()
    db.close()
    endtime = datetime.datetime.now()
    print(endtime - starttime)

 #       obj1 = root.find_child('a1 b1 c2 b4 ', create=True)
 #   root.dump()



