
from django.shortcuts import render
from .models import Trains
from django.db import connection


def list_trains(request):
    # cursor = connection.cursor()
    # sql = "INSERT INTO JOBS VALUES(%s,%s,%s,%s)"
    # cursor.execute(sql,['NEW_JOB','Something New',4000,8000])
    # connection.commit()
    # cursor.close()

    cursor = connection.cursor()
    sql = "SELECT * FROM TRAIN"
    cursor.execute(sql)
    result = cursor.fetchall()

    # cursor = connection.cursor()
    # sql = "SELECT * FROM JOBS WHERE MIN_SALARY=%s"
    # cursor.execute(sql,[4000])
    # result = cursor.fetchall()

    cursor.close()
    dict_result = []

    for r in result:
        TRAIN_ID = r[0]
        NAME = r[1]
        TOTAL_SEAT_SNIGDHA = r[2]
        TOTAL_SEAT_SCHAIR = r[3]
        TOTAL_SEAT_SHOVAN = r[4]
        row = {'TRAIN_ID': TRAIN_ID, 'NAME': NAME, 'TOTAL_SEAT_SNIGDHA': TOTAL_SEAT_SNIGDHA,
               'TOTAL_SEAT_SCHAIR': TOTAL_SEAT_SCHAIR,
               'TOTAL_SEAT_SHOVAN': TOTAL_SEAT_SHOVAN}
        dict_result.append(row)

    # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    return render(request, 'list_trains.html', {'trains': dict_result})

def list_stations(request):
    # cursor = connection.cursor()
    # sql = "INSERT INTO JOBS VALUES(%s,%s,%s,%s)"
    # cursor.execute(sql,['NEW_JOB','Something New',4000,8000])
    # connection.commit()
    # cursor.close()

    cursor = connection.cursor()
    sql = "SELECT * FROM STATION ORDER BY STATION_ID"
    cursor.execute(sql)
    result = cursor.fetchall()

    # cursor = connection.cursor()
    # sql = "SELECT * FROM JOBS WHERE MIN_SALARY=%s"
    # cursor.execute(sql,[4000])
    # result = cursor.fetchall()

    cursor.close()
    dict_result = []

    for r in result:
        STATION_ID = r[0]
        NAME = r[1]

        row = {'STATION_ID': STATION_ID, 'NAME': NAME}
        dict_result.append(row)

    # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    return render(request, 'list_stations.html', {'stations': dict_result})
