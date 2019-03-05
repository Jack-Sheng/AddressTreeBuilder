# -*- coding: utf-8 -*-
"""
@project: AddressTreeBuilder
@author: Jian Sheng
@file: Example.py
@ide: PyCharm
@TIME: 2019-02-22 18:03:20
"""
import os
import sys
from PropertiesUtils import PropertiesUtils
from PyQt5.QtWidgets import QWidget, QMessageBox, QDesktopWidget, QAction, qApp, QFileDialog, QApplication
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
import xlrd
import pymysql
import time

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.cwd = os.getcwd()
        self.initUI()



    def initUI(self):

        self.setObjectName("Form")
        self.resize(771, 558)
        #self.setFixedsize(771, 558)
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(640, 510, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QtCore.QRect(550, 510, 75, 23))
        self.pushButton_3.setObjectName("pushButton_3")
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(50, 510, 461, 20))
        self.lineEdit.setObjectName("lineEdit")
        # self.widget = QtWidgets.QWidget(self)
        # self.widget.setGeometry(QtCore.QRect(9, 49, 751, 441))
        # self.widget.setObjectName("widget")
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setGeometry(QtCore.QRect(10, 50, 731, 450))
        self.textEdit.setObjectName("textEdit")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(50, 10, 81, 21))
        self.label.setObjectName("label")
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(130, 10, 341, 22))
        self.comboBox.setObjectName("comboBox")

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "文件导入"))
        self.pushButton_2.setText(_translate("Form", "开始导入"))
        self.pushButton_3.setText(_translate("Form", "选择文件"))
        self.label.setText(_translate("Form", "选择数据库："))
        dictProperties = PropertiesUtils("数据库配置.properties").getProperties()
        self.properties = dictProperties
        server = ''
        for key in dictProperties:
            if key != 'user' and key != 'passwd':
                server = server + dictProperties[key] + '/' if key != 'db' else server + dictProperties[key]
        self.comboBox.addItem(_translate("Form", server))

        QtCore.QMetaObject.connectSlotsByName(self)
        self.pushButton_3.clicked.connect(self.slot_btn_chooseFile)
        self.pushButton_2.clicked.connect(self.startInsert)






    def startInsert(self):

        path = self.lineEdit.text()
        filepath = path.replace('/','\\')
        files = os.listdir(filepath)
        for cfile in files:
            child = os.path.join('%s%s%s' % (filepath, '\\', cfile))
            #        print child.decode('utf-8')
            self.insert(path=child)
        end = '共' + str(len(files)) + '个Excel导入成功，请注意查看！'
        self.textEdit.append(end)

    def insert(self,path):

        shujuku = self.properties
        print(path)
        readbook = xlrd.open_workbook(path)
        sheet = readbook.sheet_by_index(0)  # 名字的方式
        nrows = sheet.nrows  # 最大行
        ncols = sheet.ncols  # 最大列
        # print nrows
        # print ncols
        # print type(sheet)
        ziduanming = sheet.row_values(0)
        createSQL = "CREATE TABLE " + path.split('\\')[-1].replace('.xls', '') + "("
        insertSQL = "insert into " + path.split('\\')[-1].replace('.xls', '') + "("
        zhanweifu = " values("
        for z in ziduanming:
            createSQL = createSQL + "`" + z + "` longtext DEFAULT NULL,"
            insertSQL = insertSQL + "`" + z + "`,"
            zhanweifu = zhanweifu + '"%s",'
        createSQL = createSQL[:-1] + ')'
        insertSQL = insertSQL[:-1] + ")" + zhanweifu[:-1] + ')'
        host = shujuku.get('host')
        port = int(shujuku.get('port'))
        user = shujuku.get('user')
        passwd = shujuku.get('passwd')
        db = shujuku.get('db')
        conn = pymysql.connect(host='localhost', port=3307, user='root', passwd='123456', db='test', charset='utf8')
        cursor = conn.cursor()
        try:
            cursor.execute(createSQL)
            conn.commit()
            i = 1
            while i < nrows:
                curRow = sheet.row_values(i)
                colIndex = 0
                # print len(curRow)
                while colIndex < len(curRow):
                    curRow[colIndex] = pymysql.escape_string(curRow[colIndex])
                    colIndex += 1
                if curRow[0] == '':
                    break
                cursor.execute(insertSQL % tuple(curRow))
                # print i
                #  print insertSQL % tuple(curRow)
                i += 1
            conn.commit()
            log = path + "---------------导入完毕，共导入" + str(i - 1) + "行数据\n"
            print(log)
            self.textEdit.append(log)
            QApplication.processEvents()
            time.sleep(1)


        except Exception as e:
            # Rollback in case there is any error
            print(e)
            self.textEdit.append(e)
            conn.rollback()
            err = path + "---------------导入有误，请查看!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print(err)
            self.textEdit.append(err)
            QApplication.processEvents()
            time.sleep(1)
        cursor.close()
        conn.close()




    def slot_btn_chooseFile(self):
        # fileName_choose, filetype = QFileDialog.getOpenFileName(self,"选择文件", self.cwd, "All Files (*);;Text Files (*.txt)")  # 设置文件扩展名过滤,用双分号间隔
        # if fileName_choose == "":
        #     print("\n取消选择")
        #     return
        # print("你选择的文件为:")
        # # print(fileName_choose)
        # print("文件筛选器类型: ", filetype)
        # self.lineEdit.setText(fileName_choose)
        # self.str2.append(fileName_choose)
        directory1 = QFileDialog.getExistingDirectory(self,"选择文件",self.cwd)  # 起始路径
        self.lineEdit.setText(directory1)
        self.textEdit.append(directory1+'              开始导入')

        print(directory1)







    def center(self):
            qr = self.frameGeometry()
            cp = QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())



    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    print('1111111111')
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
