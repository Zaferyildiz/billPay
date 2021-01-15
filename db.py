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
        
        if consumer is None:
            isConsumer = False
        else:
            columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
            cnmer = dict(zip(columns, consumer))
            return "consumer", cnmer
        
        if not(isCompany or isConsumer):
            return "none"

def updateConsumer(consumerId, username, name, surname, email, cityId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
            UPDATE CONSUMER
            SET USERNAME = %s,
            NAME = %s,
            SURNAME = %s,
            EMAIL = %s,
            CITYID = %s
            WHERE CONSUMER.ID = %s;
        """
        cursor.execute(query, (username, name, surname, email, cityId, consumerId ))
        cursor.close()

def updateCompany(companyId, username, name, email, serviceTypeId, cityId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """
            UPDATE COMPANY
            SET USERNAME = %s,
            NAME = %s,
            EMAIL = %s,
            CITYID = %s,
            SERVICETYPEID = %s
            WHERE COMPANY.ID = %s;
        """
        cursor.execute(query, (username, name,  email, cityId, serviceTypeId, companyId ))
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

def saveCompany(username, name, email, password, serviceTypeId, cityId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO COMPANY (USERNAME, NAME, EMAIL, PASSWORD, SERVICETYPEID, CITYID) VALUES(%s,%s,%s,%s,%s,%s); """
        cursor.execute(query, (username, name,email,password, serviceTypeId, cityId) )
        connection.commit()
        cursor.close()

def saveConsumer(username, name, surname, email, password, cityId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO CONSUMER (USERNAME, NAME, SURNAME, EMAIL, PASSWORD, CITYID) VALUES(%s,%s,%s,%s,%s,%s); """
        cursor.execute(query, (username, name, surname, email, password, cityId) )
        connection.commit()
        cursor.close()