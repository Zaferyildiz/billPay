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

def editInvoice(billId, invoiceDate, deadline, charge):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
            UPDATE BILL
            SET INVOICEDATE = %s,
            DEADLINE = %s,
            CHARGE = %s
            WHERE BILL.ID = %s;"""
        cursor.execute(query, (invoiceDate, deadline, charge, billId ))
        cursor.close()
        

def createBankAccount(name, iban, balance):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO BANKACCOUNT (NAME, IBAN, BALANCE) VALUES(%s,%s,%s) RETURNING ID;"""
        cursor.execute(query, (name, iban, balance))
        bankAccountId = cursor.fetchone()[0]
        cursor.close()
        return bankAccountId

def assignBankAccounttoConsumer(bankAccountId, consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """UPDATE CONSUMER SET BANKACCOUNTID = %s WHERE CONSUMER.ID = %s"""
        cursor.execute(query, (bankAccountId, consumerId))
        cursor.close()

def getBankAccount(consumerId):
    with dbapi2.connect(url) as connection:
        consumer = getConsumer(consumerId)
        bankAccountId = consumer['bankaccountid']
        print(bankAccountId)
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
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO OUTAGE (STARTDATE, ENDDATE, COMPANYID) VALUES(%s,%s,%s);"""
        cursor.execute(query, (startDate, endDate, companyId))
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

def getInvoiceofConsumer(consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
        SELECT BILL.ID as id, BILL.CONSUMERID as consumerId, BILL.CHARGE as charge, BILL.DEADLINE as deadline, SERVICETYPE.NAME as serviceType, CONSUMER.NAME as consumerName, CONSUMER.SURNAME as consumerSurname FROM BILL 
        INNER JOIN CONSUMER ON BILL.CONSUMERID = CONSUMER.ID 
        INNER JOIN SERVICETYPE ON BILL.SERVICETYPEID = SERVICETYPE.ID 
        WHERE BILL.CONSUMERID = %s
        """
        cursor.execute(query, (consumerId, ))
        bills = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        for row in bills:
            data.append(dict(zip(columns, row)))
        return data

def updateConsumer(consumerId, username, name, surname, idnumber, email, cityId, address):
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

def updateCompany(companyId, username, name, taxnumber, email, serviceTypeId, cityId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
            UPDATE COMPANY
            SET USERNAME = %s,
            NAME = %s,
            TAXNUMBER = %s,
            EMAIL = %s,
            CITYID = %s,
            SERVICETYPEID = %s
            WHERE COMPANY.ID = %s;
        """
        cursor.execute(query, (username, name, taxnumber, email, cityId, serviceTypeId, companyId ))
        cursor.close()

def makeInvoice(invoiceDate, deadline, companyId, serviceTypeId, consumerId, charge):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "INSERT INTO BILL (INVOICEDATE, DEADLINE, COMPANYID, SERVICETYPEID, CONSUMERID, CHARGE) VALUES(%s,%s,%s,%s,%s,%s);"
        cursor.execute(query, (invoiceDate, deadline, companyId, serviceTypeId, consumerId, charge))
        cursor.close()

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
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM public.bill WHERE id=%s;"
        cursor.execute(query, (billId, ))
        cursor.close()
        
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
        query = "DELETE FROM public.consumer WHERE id=%s;"
        cursor.execute(query, (consumerId, ))
        cursor.close()

def deleteCompany(companyId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM public.company WHERE id=%s;"
        cursor.execute(query, (companyId, ))
        cursor.close()

def getAllServiceTypes():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.servicetype")
        types = cursor.fetchall()
        servicetype = []
        cursor.close()
        for ty in types:
            dc = {}
            dc['id'] = ty[0]
            dc['name'] = ty[1]
            servicetype.append(dc)
        return servicetype

def saveCompany(username, name, taxnumber, email, password, serviceTypeId, cityId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO COMPANY (USERNAME, NAME, TAXNUMBER, EMAIL, PASSWORD, SERVICETYPEID, CITYID) VALUES(%s,%s,%s,%s,%s,%s,%s); """
        cursor.execute(query, (username, name,taxnumber,email,password, serviceTypeId, cityId) )
        connection.commit()
        cursor.close()

def saveConsumer(username, name, surname, identitynum, email, password, cityId, address):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO CONSUMER (USERNAME, NAME, SURNAME, IDENTITYNUM, EMAIL, PASSWORD, CITYID, ADDRESS) VALUES(%s,%s,%s,%s,%s,%s,%s,%s); """
        cursor.execute(query, (username, name, surname, identitynum, email, password, cityId, address) )
        connection.commit()
        cursor.close()

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