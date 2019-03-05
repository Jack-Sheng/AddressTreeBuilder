#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@project: AddressTreeBuilder
@author: Jian Sheng
@file: BuildTreeByID.py
@ide: PyCharm
@TIME: 2019-01-10 11:18:19
"""

from __future__ import unicode_literals  # at top of module
from __future__ import division, print_function, with_statement
import uuid
import pymysql
import datetime
import traceback
from binarySearching import binary_Searching


class TreeNode(object):

    """The basic node of tree structure"""
    def __init__(self, name, parent=None):
        super(TreeNode, self).__init__()
        self.name = name
        self.parent = parent
        self.id = ''
        self.parentID = ''
        self.type = ''
        self.child = {}

    def __repr__(self):
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
    def add_child(self, name, id, obj=None):
        """add a child node to current node"""
        if obj and not isinstance(obj, TreeNode):
            raise ValueError('TreeNode only add another TreeNode obj as child')
        if obj is None:
            obj = TreeNode(name)
        obj.parent = self
        obj.parentID = self.id
        obj.id = id
        self.child[name] = obj
        return obj


    def del_child(self, name):
        """remove a child node from current node"""
        if name in self:
            del self.child[name]

    def create_child(self, path, create=False, cursor=None, sql='', zuobiao=''):
        """find child node by path/name, return None if not found"""
        # convert path to a list if input is a string
        path = path if isinstance(path, list) else path.split()
        cur = self
        index = 0
        while '' in path or ' ' in path:
            path.remove('')
            path.remove(' ')
        length = len(path)
        for sub in path:
            # search子节点
            if sub == '镇江市':
                obj = self
            else:
                obj = cur.get_child(sub)
            # create子节点
            if obj is None and create:
                # create new node if need
                obj = cur.add_child(name=sub, id=uuid.uuid1())
                #type = searchType(index=index, length=length, nodeName=sub, parentType=cur.type)
                type = searchType(index=index,  nodeName=sub)
                # if int(type) > 50:
                #     ins = sql % (obj.id, obj.parentID, sub, type, zuobiao)
                # else:
                #     ins = sql % (obj.id, obj.parentID, sub, type, '')
                if type == '19d219f15efe4408892c2f955e439489':
                    ins = sql % (obj.id, obj.parentID, sub, type, zuobiao)
                else:
                    ins = sql % (obj.id, obj.parentID, sub, type, '')
                obj.type = type
                cursor.execute(ins)
            # check if search done
            if obj is None:
                break
            cur = obj
            index += 1
        return obj




    def build_tree_by_id(self,resultList):
        """通过地址元素树将地址挂到内存"""
        root = self
        if root is not None:
            while True:
                index = binary_Searching(alist=resultList, data=root.id)
                if resultList[index][1] == root.id:
                    cur = root.add_child(name=resultList[index][2], id=resultList[index][0])
                    resultList.pop(index)
                    cur.build_tree_by_id(resultList)
                else:
                    break
        return resultList


    def numberOfLeafs(self):
        """查找某节点下叶子节点的个数"""
        root = self
        nodes = 0
        if root == None:
            return 0
        elif root.child == {}:
            return 1
        else:
            for key in root.child:
                nodes = nodes + root.child[key].numberOfLeafs()
        return nodes


    def items(self):
        return self.child.items()

    def dump_tree_on_txt(self, fw, indent=0):
        """在文件中打印形象树"""
        tab = '    '*(indent-1) + ' |- ' if indent > 0 else ''
        print('%s%s' % (tab, self.name))
        tree = '%s%s' % (tab, self.name) + '\n'
        fw.write(tree)
        for name, obj in self.items():
            obj.dump(fw=fw, indent=indent+1)

    def dump_tree_on_console(self, indent=0):
        """控制台打印形象树"""
        tab = '    '*(indent-1) + ' |- ' if indent > 0 else ''
        print('%s%s' % (tab, self.name))
        for name, obj in self.items():
            obj.dump_tree_on_console(indent+1)

    def build_path(self, fw, parentTree=''):
        """打印地址树，校验用"""
        #print('%s' % (self.name))
        treeNodeName = '%s' % (self.name)
        if self.name != '陕西省':
            _tree = parentTree + treeNodeName
        else:
            _tree = '陕西省'
        if self.child == {}:
            _tree += '\n'
            fw.write(_tree)
        for name, obj in self.items():
            obj.build_path(fw=fw, parentTree=_tree)

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

def searchType1(index, length, nodeName, parentType):
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
    elif '号' in nodeName and int(parentType)<50:
        return '100'
    elif '栋' in nodeName or '幢'in nodeName or ('楼' in nodeName and index<length-1 and int(parentType)>50):
        return '102'
    elif '单元' in nodeName:
        return '51'
    elif ('号' in nodeName or '层' in nodeName or '楼' in nodeName) and index == length-1:
        return '53'
    else:
        return '41'

def searchType(index, nodeName):
    if index == 1 and '区' in nodeName:
        return '19d201f15efe4408892c2f955e439489'
    if index == 1 and '县' in nodeName:
        return '19d202f15efe4408892c2f955e439489'
    if index== 2 and '街道'in nodeName:
        return '19d206f15efe4408892c2f955e439489'
    if index == 2 and '镇' in nodeName:
        return  '19d205f15efe4408892c2f955e439489'
    if index == 2 and '乡' in nodeName:
        return '19d204f15efe4408892c2f955e439489'
    if index== 3:
        return '19d213f15efe4408892c2f955e439489'
    if index == 4:
        return '19d219f15efe4408892c2f955e439489'
    if index == 5:
        return '19d221f15efe4408892c2f955e439489'


"""制定排序规则"""
def orderByIndex(elem):
    return elem[1]


if __name__ == '__main__':
    startTime = datetime.datetime.now()
    print('-----------------Start build tree from dzys-------------------------------')

    selectSQL = 'select id,shangjiyuansu,dizhiyuansumingcheng from sd_dz_dizhiyuansu order by shangjiyuansu asc'
    db = pymysql.connect(host="localhost", port=3307, user="root", passwd="123456", db="sd_dmdzk_zjmz", charset='utf8')
    cursor = db.cursor()
    cursor.execute(selectSQL)

    resultSet = cursor.fetchall()
    resultList = list(resultSet)
    resultList.sort(key=orderByIndex)

    root = TreeNode(name='镇江市')
    root.id = '73B091DD20C149D780326C5695519897'
    print('正在加载...')
    root.build_tree_by_id(resultList)
    print('----------------End build tree!-------------------------------------------\r\n')
    f = open("镇江纸质地址树.txt", "a", encoding="utf-8")
    print('----------------Start build path!------------------------------------------')
    print('正在创建...')
    root.build_path(fw=f)
    print('----------------End build path!-------------------------------------------')
    f.flush()
    f.close()
    endTime = datetime.datetime.now()
    print(endTime - startTime)
    print(resultList)


    # starttime = datetime.datetime.now()
    # print('hello')
    # selectSQL = 'select * from ruku order by lat DESC'
    # insertSQL = """insert into sd_dz_dizhiyuansu_0225(id,shangjiyuansu,dizhiyuansumingcheng,dizhiyuansuleixing,zuobiao,zhuangtai) values('%s','%s','%s','%s','%s',2)"""
    # sel = 'select id,shangjiyuansu,dizhiyuansumingcheng from sd_dz_dizhiyuansu_0225 order by shangjiyuansu '
    #
    # db = pymysql.connect(host="localhost", port=3307, user="root", passwd="123456", db="sd_dmdzk_zjmz", charset='utf8')
    # cursor = db.cursor()
    # cursor.execute(sel)
    # result = cursor.fetchall()
    # resList = list(result)
    # root = TreeNode(name='镇江市')
    # root.id = '73B091DD20C149D780326C5695519897'
    # root.build_tree_by_id(resList)
    # #root.dump_tree_on_console()
    #
    # cursor.execute(selectSQL)
    # resultSet = cursor.fetchall()
    #
    #
    # count = 0
    # for addre in resultSet:
    #     try:
    #         addrList = list(addre)
    #         latlng = '{"lat":' + addrList[0] + ',"lng":' + addrList[1] + '}' if addrList[0] != '' else ''
    #         addr = addrList[2:]
    #         obj = root.create_child(path=addr, create=True, cursor=cursor, sql=insertSQL, zuobiao=latlng)
    #     except Exception as e:
    #         # Rollback in case there is any error
    #         print(e)
    #         db.rollback()
    #         f = open("log.txt", 'a')
    #         traceback.print_exc(file=f)
    #         f.flush()
    #         f.close()
    #     count += 1
    #     log = '第' + str(count) + '条打完了'
    #     print(log)
    # db.commit()
    # cursor.close()
    # db.close()
    # endtime = datetime.datetime.now()
    # print(endtime - starttime)











