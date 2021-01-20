import psycopg2 as dbapi2
import os
import sys
from flask import Flask, render_template, request, redirect, flash

url = "postgres://dsqcgjjeueapqd:b80fa6b9b8c36a4dae076b0b5bef40d2b978137b76ff2b2f38ee0c8eaaf7d988@ec2-52-208-138-246.eu-west-1.compute.amazonaws.com:5432/d70mv9snenlrnc"

def isLogin(username, password):
    isCompany = True
    isConsumer = True
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        queryCompany = "SELECT * FROM public.company WHERE username = %s"
        cursor.execute(queryCompany, (username, ))
        company = cursor.fetchone()
        
        if company is None:
            isCompany = False
        else:
            columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
            cmp = dict(zip(columns, company))
            return "company", cmp
        
        queryConsumer = "SELECT * FROM public.consumer WHERE username = %s"
        cursor.execute(queryConsumer, (username, ))
        consumer = cursor.fetchone()
        cursor.close()
        if consumer is None:
            isConsumer = False
        else:
            columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
            cnmer = dict(zip(columns, consumer))
            return "consumer", cnmer
        
        if not(isCompany or isConsumer):
            return "none"

def getInvoice(billId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM BILL WHERE BILL.ID = %s """
        cursor.execute(query, (billId, ))
        bill = cursor.fetchone()
        columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
        cursor.close()
        data = dict(zip(columns, bill))
        return data

def editInvoice(billId, invoiceDate, deadline, charge, taxrate):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
            UPDATE BILL
            SET INVOICEDATE = %s,
            DEADLINE = %s,
            CHARGE = %s,
            TAXRATE = %s
            WHERE BILL.ID = %s;"""
        cursor.execute(query, (invoiceDate, deadline, charge, taxrate, billId ))
        cursor.close()
        
def createBankAccount(name, iban, balance):
    try:
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO BANKACCOUNT (NAME, IBAN, BALANCE) VALUES(%s,%s,%s) RETURNING ID;"""
            cursor.execute(query, (name, iban, balance))
            bankAccountId = cursor.fetchone()[0]
            cursor.close()
            return bankAccountId
    except dbapi2.IntegrityError as e:
        return(e.diag.message_detail)

def assignBankAccounttoConsumer(bankAccountId, consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """UPDATE CONSUMER SET BANKACCOUNTID = %s WHERE CONSUMER.ID = %s"""
        cursor.execute(query, (bankAccountId, consumerId))
        cursor.close()

def assignBankAccounttoCompany(bankAccountId, companyId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """UPDATE COMPANY SET BANKACCOUNTID = %s WHERE COMPANY.ID = %s"""
        cursor.execute(query, (bankAccountId, companyId))
        cursor.close()

def getBankAccount(userId, role):
    with dbapi2.connect(url) as connection:
        bankAccountId = 0
    
        if role == "company":
            company = getCompany(userId)
            bankAccountId = company['bankaccountid']
        else:
            consumer = getConsumer(userId)
            bankAccountId = consumer['bankaccountid']
        if bankAccountId is None:
            nulldict = {}
            return nulldict
        else:
            cursor = connection.cursor()
            query = """SELECT * FROM BANKACCOUNT WHERE BANKACCOUNT.ID = %s"""
            cursor.execute(query, (bankAccountId, ))
            bankAccount = cursor.fetchone()
            columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
            cursor.close()
            data = dict(zip(columns, bankAccount))
            return data

def addOutage(startDate, endDate, companyId):
    company = getCompany(companyId)
    cityId = company['cityid']
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO OUTAGE (STARTDATE, ENDDATE, COMPANYID, CITYID) VALUES(%s,%s,%s,%s);"""
        cursor.execute(query, (startDate, endDate, companyId, cityId))
        cursor.close()

def getOutages(cityId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
            SELECT OUTAGE.ID as id, OUTAGE.STARTDATE as startDate, OUTAGE.ENDDATE as endDate, COMPANY.NAME as companyName, SERVICETYPE.NAME as serviceType, CITY.ID as cityId, CITY.NAME as city FROM OUTAGE
            INNER JOIN COMPANY ON OUTAGE.COMPANYID = COMPANY.ID
            INNER JOIN SERVICETYPE ON COMPANY.SERVICETYPEID = SERVICETYPE.ID
            INNER JOIN CITY ON COMPANY.CITYID = CITY.ID 
            WHERE OUTAGE.CITYID = %s
        """
        cursor.execute(query, (cityId, ))
        data  = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        outages = []
        for row in data:
            outages.append(dict(zip(columns, row)))
        return outages

def getInvoiceofConsumer(consumerId, companyId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
        SELECT BILL.ID as id, BILL.CHARGE as charge, BILL.INVOICEDATE as invoicedate, BILL.DEADLINE as deadline, SERVICETYPE.NAME as serviceType, CONSUMER.ID as consumerid, CONSUMER.NAME as consumerName, CONSUMER.SURNAME as consumerSurname FROM BILL 
        INNER JOIN CONSUMER ON BILL.CONSUMERID = CONSUMER.ID 
        INNER JOIN COMPANY ON BILL.COMPANYID = COMPANY.ID
        INNER JOIN SERVICETYPE ON COMPANY.SERVICETYPEID = SERVICETYPE.ID 
        WHERE BILL.CONSUMERID = %s AND BILL.COMPANYID = %s
        """
        cursor.execute(query, (consumerId, companyId))
        bills = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        for row in bills:
            data.append(dict(zip(columns, row)))
        return data

def updateConsumer(consumerId, username, name, surname, idnumber, email, cityId, address):
    try:
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            query = """
                UPDATE CONSUMER
                SET USERNAME = %s,
                NAME = %s,
                SURNAME = %s,
                IDENTITYNUM = %s,
                EMAIL = %s,
                CITYID = %s,
                ADDRESS = %s
                WHERE CONSUMER.ID = %s;
            """
            cursor.execute(query, (username, name, surname, idnumber, email, cityId, address, consumerId))
            connection.commit()
            cursor.close()
    except dbapi2.IntegrityError as e:
        return(e.diag.message_detail)

    
def updateCompany(companyId, username, name, taxnumber, email, serviceTypeId, cityId, logo):
    company = getCompany(companyId)
    logoofCompany = company['logo']
    try:
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            query = """
                UPDATE COMPANY
                SET USERNAME = %s,
                NAME = %s,
                TAXNUMBER = %s,
                EMAIL = %s,
                CITYID = %s,
                SERVICETYPEID = %s,
                LOGO = %s
                WHERE COMPANY.ID = %s;
            """
            
            if logoofCompany is not None and logo == b'':
                logo = logoofCompany
            cursor.execute(query, (username, name, taxnumber, email, cityId, serviceTypeId, logo, companyId ))
            cursor.close()
    except dbapi2.IntegrityError as e:
        return(e.diag.message_detail)

def makeInvoice(billnum, invoicedate, deadline, charge, companyId, consumerId, taxrate):
    try:
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO BILL (BILLNUM, INVOICEDATE, DEADLINE, CHARGE, TAXRATE, COMPANYID, CONSUMERID) VALUES(%s,%s,%s,%s,%s,%s,%s);"
            cursor.execute(query, (billnum, invoicedate, deadline, charge, taxrate, companyId, consumerId))
            cursor.close()
    except dbapi2.IntegrityError as e:
        return(e.diag.message_detail)

def getMyBills(consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
        SELECT BILL.ID as id, BILL.CONSUMERID, BILL.CHARGE as charge, BILL.DEADLINE as deadline, COMPANY.NAME as companyname, SERVICETYPE.NAME as serviceType FROM BILL 
        INNER JOIN COMPANY ON BILL.COMPANYID = COMPANY.ID 
        INNER JOIN SERVICETYPE ON COMPANY.SERVICETYPEID = SERVICETYPE.ID 
        WHERE BILL.CONSUMERID = %s"""
        cursor.execute(query, (consumerId, ))
        bills = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        for row in bills:
            data.append(dict(zip(columns, row)))
        return data

def getDonatedBills():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
        SELECT BILL.ID as id, BILL.CONSUMERID, BILL.CHARGE as charge, BILL.DEADLINE as deadline, COMPANY.NAME as companyname, SERVICETYPE.NAME as serviceType FROM BILL 
        INNER JOIN COMPANY ON BILL.COMPANYID = COMPANY.ID 
        INNER JOIN SERVICETYPE ON COMPANY.SERVICETYPEID = SERVICETYPE.ID 
        WHERE BILL.ISDONATED = TRUE
        """
        cursor.execute(query)
        bills = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        for row in bills:
            data.append(dict(zip(columns, row)))
        return data

def billShare(billId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
            UPDATE BILL
            SET isDonated = True
            WHERE BILL.ID = %s;
        """
        cursor.execute(query, (billId, ))
        cursor.close()

def deleteBill(billId):
    deletedBill = getInvoice(billId)
    updateBankAccount(deletedBill['companyid'], deletedBill['charge'])
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM public.bill WHERE id=%s;"
        cursor.execute(query, (billId, ))
        cursor.close()

def updateBankAccount(companyId, charge):
    bankaccount = getBankAccount(companyId, "company")
    newbalance = 0
    if bankaccount:
        newbalance = bankaccount['balance']
        newbalance += charge
        company = getCompany(companyId)
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            query = """UPDATE BANKACCOUNT
                    SET BALANCE = %s
                    WHERE BANKACCOUNT.ID = %s;"""
            cursor.execute(query, (newbalance, company['bankaccountid'] ))
            cursor.close()

def updateBankAccountofConsumer(consumerId, charge):
    bankaccount = getBankAccount(consumerId, "consumer")
    newbalance = 0
    if bankaccount:
        newbalance = bankaccount['balance']
        newbalance -= charge
        consumer = getConsumer(consumerId)
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            query = """UPDATE BANKACCOUNT
                    SET BALANCE = %s
                    WHERE BANKACCOUNT.ID = %s;"""
            cursor.execute(query, (newbalance, consumer['bankaccountid'] ))
            cursor.close()

def deleteBankAccountfromdb(bankAccountId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM BANKACCOUNT WHERE id=%s;"
        cursor.execute(query, (bankAccountId, ))
        cursor.close()

def bankAccountDrawMoney(bankAccountId, money):
    bankAccount = getBankAccountwithId(bankAccountId)
    newbalance = bankAccount['balance']
    newbalance += money
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """UPDATE BANKACCOUNT
                SET BALANCE = %s
                WHERE BANKACCOUNT.ID = %s;"""
        cursor.execute(query, (newbalance, bankAccountId ))
        cursor.close()

def getBankAccountwithId(bankAccountId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM BANKACCOUNT WHERE BANKACCOUNT.ID = %s"""
        cursor.execute(query, (bankAccountId, ))
        bankAccount = cursor.fetchone()
        columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
        cursor.close()
        data = dict(zip(columns, bankAccount))
        return data
            
        
def getAllCities():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.city")
        cities = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        for row in cities:
            data.append(dict(zip(columns, row)))
        return data

def getAllConsumer():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.consumer")
        consumers = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        for row in consumers:
            data.append(dict(zip(columns, row)))
        return data

def getCity(companyId):
    company = getCompany(companyId)
    cityId = company['cityid']
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "SELECT * FROM CITY WHERE ID = %s"
        cursor.execute(query, (cityId,))
        city = cursor.fetchone()
        columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
        cursor.close()
        data = dict(zip(columns, city))
        return data
        

def getAllConsumerinaCity(companyId):
    company = getCompany(companyId)
    cityId = company['cityid']
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "SELECT * FROM CONSUMER WHERE CITYID = %s"
        cursor.execute(query, (cityId,))
        consumers = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        for row in consumers:
            data.append(dict(zip(columns, row)))
        return data

def getConsumer(consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "SELECT * FROM public.consumer WHERE id=%s;"
        cursor.execute(query, (consumerId, ))
        consumer = cursor.fetchone()
        columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
        cursor.close()
        data = dict(zip(columns, consumer))
        return data
        
def getCompany(companyId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "SELECT * FROM public.company WHERE COMPANY.ID = %s;"
        cursor.execute(query, (companyId, ))
        company = cursor.fetchone()
        columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
        cursor.close()
        data = dict(zip(columns, company))
        return data

def deleteConsumer(consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM CONSUMER WHERE id=%s;"
        cursor.execute(query, (consumerId, ))
        cursor.close()

def deleteCompany(companyId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM COMPANY WHERE id=%s;"
        cursor.execute(query, (companyId, ))
        cursor.close()

def getAllServiceTypes():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM SERVICETYPE")
        types = cursor.fetchall()
        servicetype = []
        cursor.close()
        for ty in types:
            dc = {}
            dc['id'] = ty[0]
            dc['name'] = ty[1]
            servicetype.append(dc)
        return servicetype


def saveCompany(username, name, taxnumber, email, password, serviceTypeId, cityId, encoded):
    try:
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO COMPANY (USERNAME, NAME, TAXNUMBER, EMAIL, PASSWORD, SERVICETYPEID, CITYID, LOGO) VALUES(%s,%s,%s,%s,%s,%s,%s,%s); """
            cursor.execute(query, (username, name,taxnumber,email,password, serviceTypeId, cityId, encoded) )
            connection.commit()
            cursor.close()
    except dbapi2.IntegrityError as e:
        return(e.diag.message_detail)


def getlogo(companyId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """SELECT encode(logo::bytea, 'escape') FROM company as o where o.logo != '' AND o.id = %s """
        cursor.execute(query, (companyId, ) )
        logodata = cursor.fetchone()
        connection.commit()
        cursor.close()
        if logodata is not None:
            return logodata[0]
    

def saveConsumer(username, name, surname, identitynum, email, password, cityId, address):
    try:
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO CONSUMER (USERNAME, NAME, SURNAME, IDENTITYNUM, EMAIL, PASSWORD, CITYID, ADDRESS) VALUES(%s,%s,%s,%s,%s,%s,%s,%s); """
            cursor.execute(query, (username, name, surname, identitynum, email, password, cityId, address) )
            connection.commit()
            cursor.close()
    except dbapi2.IntegrityError as e:
        return(e.diag.message_detail)

def getNumberofConsumer():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT COUNT(*) FROM CONSUMER""")
        num = cursor.fetchone()
        cursor.close()
        return num[0]

def getNumberofCompany():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT COUNT(*) FROM COMPANY""")
        num = cursor.fetchone()
        cursor.close()
        return num[0]

def getNumberofCity():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT COUNT(*) FROM CITY""")
        num = cursor.fetchone()
        cursor.close()
        return num[0]

def getNumberofOutageofCompany(companyId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """SELECT COUNT(*) FROM OUTAGE WHERE COMPANYID = %s"""
        cursor.execute(query, (companyId, ))
        num = cursor.fetchone()
        cursor.close()
        return num[0]

def getNumberOfConsumerinCity(companyId):
    company = getCompany(companyId)
    cityId = company['cityid']
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """SELECT COUNT(*) FROM CONSUMER WHERE CITYID = %s"""
        cursor.execute(query, (cityId, ))
        num = cursor.fetchone()
        cursor.close()
        return num[0]

def getNumberofMyBills(consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """SELECT CONSUMERID, COUNT(CONSUMERID) FROM BILL GROUP BY CONSUMERID"""
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        num = {}
        for row in data:
            num[row[0]] = row[1]
        if not bool(num):
            return 0
        if consumerId in num.keys():
            return num[consumerId]
        else:
            return 0
        
def getNumberofOutagesinCity(consumerId):
    consumer = getConsumer(consumerId)
    cityId = consumer['cityid']
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """SELECT CITYID, COUNT (CITYID) FROM OUTAGE GROUP BY CITYID;"""
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        num = {}
        for row in data:
            num[row[0]] = row[1]
        if not bool(num):
            return 0
        if cityId in num.keys():
            return num[cityId]
        else:
            return 0