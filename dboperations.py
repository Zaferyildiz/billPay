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

def updateConsumer(consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "INSERT INTO BILL (INVOICEDATE, DEADLINE, COMPANYID, SERVICETYPEID, CONSUMERID, CHARGE) VALUES(%s,%s,%s,%s,%s,%s);"
        cursor.execute(query, (invoiceDate, deadline, companyId, serviceTypeId, consumerId, charge))
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
        query = """SELECT * FROM public.bill WHERE consumerid = %s"""
        cursor.execute(query, (consumerId, ))
        bills = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        for row in bills:
            data.append(dict(zip(columns, row)))
        return data

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

def getCompany(username):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "SELECT * FROM public.company WHERE username=%s;"
        cursor.execute(query, (username, ))
        company = cursor.fetchone()
        columns = list(cursor.description[i][0] for i in range(0, len(cursor.description)))
        cursor.close()
        data = dict(zip(columns, company))
        return data

def deleteCon(consumerId):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM public.consumer WHERE id=%s;"
        cursor.execute(query, (consumerId, ))
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