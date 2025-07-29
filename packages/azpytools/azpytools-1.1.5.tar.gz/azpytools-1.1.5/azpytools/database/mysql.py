import pymysql

class MySql:
    def __init__(self,host,user,password,database) -> None:
        self.db = pymysql.connect(host=host,
                        user= user , #'root',
                        password=password,
                        database=database)
    
    def disconnect(self):
        self.db.close()
        
    # sql = "SELECT * FROM justest"
    def executeSQL(self,sql):
        sqlStm = sql
        cursor = self.db.cursor()
        cursor.execute(sqlStm)
        results = cursor.fetchall()
        return results
    
    def createTable(self,tableName):
        pass
        # 使用 cursor() 方法创建一个游标对象 cursor
        # cursor = db.cursor()
        
        # # 使用 execute() 方法执行 SQL，如果表存在则删除
        # cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")
        
        # # 使用预处理语句创建表
        # sql = """CREATE TABLE EMPLOYEE (
        #         FIRST_NAME  CHAR(20) NOT NULL,
        #         LAST_NAME  CHAR(20),
        #         AGE INT,  
        #         SEX CHAR(1),
        #         INCOME FLOAT )"""
        
        # cursor.execute(sql)
 
# 关闭数据库连接
        # db.close()
    
    def getCounts(self,tableName,condString):
        
        cursor = self.db.cursor()
        
        # SQL语句 
        sqlStatement = f"SELECT COUNT(*)  from {tableName} where {condString}"
        try:
        # 使用 execute()  方法执行 SQL 
            cursor.execute(sqlStatement)
            data = cursor.fetchone()
            return int(data[0])
        except:
            return 0
    
    def insertRow(self,tableName,content:dict):
        cursor = self.db.cursor()
        # # SQL 插入语句
        try:
            cnt = content
            fields = ','.join(cnt.keys())
            values = '"' + '","'.join(cnt.values())+'"'
            sqlStatement = f"INSERT INTO {tableName} ({fields}) VALUES ({values})"
            cursor.execute(sqlStatement)
        # # 提交到数据库执行
            self.db.commit()

        except:
            self.db.rollback()
            # self.db.close()
    
    def insertRows(self,tableName,contents:list):
        cursor = self.db.cursor()
        # # SQL 插入语句
        try:
            for cnt in contents:
                fields = ','.join(cnt.keys())
                values = '"' + '","'.join(cnt.values())+'"'
                sqlStatement = f"INSERT INTO {tableName} ({fields}) VALUES ({values})"
                # print(sqlStatement)
                cursor.execute(sqlStatement)
        # # 提交到数据库执行
            self.db.commit()

        except Exception as e:
            print(str(e))
            self.db.rollback()
            # self.db.close()
            
    def deleteRows(self,tableName,condString):
        cursor = self.db.cursor()
        
        # # SQL 插入语句
        try:
            sqlStatement = f"DELETE FROM {tableName} WHERE {condString} "
            cursor.execute(sqlStatement)
    # # 提交到数据库执行
            self.db.commit()
            return cursor.rowcount

        except:
            self.db.rollback()
            return 0
    
    def selectRows(self,tableName,condString):
        cursor = self.db.cursor()
        sqlStatement = f"SELECT *  from {tableName} where {condString}"
        cursor.execute(sqlStatement)
        results = cursor.fetchall()
        return results
    


if __name__ == '__main__':
    # drop table accounts;
    # create table accounts(
    # addr char(42) not null primary key,
    # addr1 char(42) not null,
    # pk varchar(132) not null,
    # phrase varchar(152) not null,
    # index idx_addr1(addr1) );
    # create table ethaddlist(
    # addr char(42) not null,
    # index idx_addr(addr) );
            
    # rcd = [{'addr':'0x1Cbd19f2d76eFa1A9F409Bec619b47EC8Afc02eb','addr1':'0x1Cbd19f2d76eFa1A9F409Bec619b47EC8Afc02eb','pk':'NjE5YjQ3RUM4QWZjMDJlYg==ifntWO077M6n0C+WhiHaCg5CfGocWXXjTX7NgyncM5+Sl+n0UBHR7WKrbiW35YTkUjrNN9KGxa9KZX+EmbVpDrrqCFHGTTdNPb1ZCZ/mscM=','phrase':'NjE5YjQ3RUM4QWZjMDJlYg==2wF4B8LDaofJMAZBwV0AZa+yMrGEQsj80rYRHrGOBXQdy3XnwaK6fm4MEZ/mFI9SX8Jvcq8OWGI3JlQO4DkUIHWQVcC7WtrPsYf+48/AS5czBuboD6CTjKgGykSecGHO'}]
    mysql = MySql('localhost','root','abcd1234','blockchain')
    
    # # mysql.deleteRows('accounts','addr = "0x1Cbd19f2d76eFa1A9F409Bec619b47EC8Afc02eb"')
    # # mysql.insertRows('accounts',rcd)
    with open('/Users/zhuzhenhua/Desktop/richlist.tsv','r',encoding='UTF-8') as f:
        strs = f.readlines()
    import re
    cnt = 0
    inscnt = 0
    rows = 0
    records = []
    for str in strs:
        if cnt == 0:
            records.clear() 
        cnt +=1
        list = re.split('\t|\n',str)
        record = {
            'addr':list[0].upper()
            # 'qty':float(list[1])
        }
        records.append(record)
        if cnt > 200:
            inscnt+=1
            cnt = 0
            rows = inscnt * 200
            mysql.insertRows('ethaddlist',records) 
            print(f'insert {rows} rows')
    if records:
        inscnt+=1
        rows = rows  + cnt
        mysql.insertRows('ethaddlist',records)
        print(f'insert {rows} rows')   
            
      
    # cnt = mysql.getCounts('accounts',"addr = '0x1Cbd19f2d76eFa1A9F409Bec619b47EC8Afc02eb'")
    # print(cnt)
    
    # rs = mysql.selectRows('accounts',"addr = '0x1Cbd19f2d76eFa1A9F409Bec619b47EC8Afc02eb'")
    # print(rs)
    mysql.disconnect()
    
    