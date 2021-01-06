import psycopg2 as dbapi2
import os
import sys
from flask import Flask, render_template, request, redirect, flash

url = os.getenv("DATABASE_URL")


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
               
def getAllCities():
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.city")
        cities = cursor.fetchall()
        cursor.close()
        city = []
        for ct in cities:
            dc = {}
            dc['id'] = ct[0]
            dc['name'] = ct[1]
            city.append(dc)
        
        return city

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