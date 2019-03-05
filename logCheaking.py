import pymysql

def logCheaking(resultList):
    i = 0
    indexMemory = []
    while i < len(resultList)-2:
        if resultList[i][0] in resultList[i+1][0]:
            indexMemory.append(resultList[i][0])
        i += 1
    newList = []
    for addre in resultList:
        if addre[0] not in indexMemory:
            newList.append(addre[0])
    return newList


def querySQL(sql=''):
    db = db = pymysql.connect(host="localhost",port=3307, user="root", passwd="123456", db="tongchuan",charset='utf8')
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

if __name__ == '__main__':
    selSQL = 'select distinct dzqc from tongchuan_yintaiqu order by dzqc'
    resultSet = querySQL(selSQL)
    resultList = list(resultSet)
    result = logCheaking(resultList)
    f = open("原始.txt", "a", encoding="utf-8")
    for r in result:
        f.write(r +'\n')
    f.flush()
    f.close()