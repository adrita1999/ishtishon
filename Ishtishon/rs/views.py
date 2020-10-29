
from django.shortcuts import render
from .models import Trains
from django.db import connection

#welcome dristi
def list_trains(request):
    if request.method == "POST":
        fro = request.POST["from"]
        to = request.POST["to"]
        date = request.POST["date"]
        adult = request.POST["adult"]
        child = request.POST["child"]

        cursor = connection.cursor()
        sql = "SELECT TRAIN_ID,(select NAME from TRAIN t where t.TRAIN_ID=tab.TRAIN_ID),MIN(DEPARTURE_TIME),MAX(DEPARTURE_TIME)FROM (select st.NAME,t1.TRAIN_ID,t1.DEPARTURE_TIME,st.STATION_ID FROM TRAIN_TIMETABLE t1,STATION st where t1.STATION_ID=st.STATION_ID) tab where (NAME=%s OR NAME=%s) GROUP BY TRAIN_ID HAVING COUNT(*)=2 AND MAX(DEPARTURE_TIME)=ANY(SELECT DEPARTURE_TIME FROM TRAIN_TIMETABLE WHERE STATION_ID=(select STATION_ID from STATION where NAME=%s))"
        cursor.execute(sql, [fro, to, to])
        result = cursor.fetchall()
        cursor.close()

        cursor1 = connection.cursor()
        sql1 = "select (COST*%s+COST*%s*0.5) FROM COST WHERE STATION_ID=(SELECT STATION_ID from STATION where NAME=%s) AND TO_STATION_ID=(SELECT STATION_ID from STATION where NAME=%s)"
        cursor1.execute(sql1, [adult, child, fro, to])
        result1 = cursor1.fetchall()
        cursor1.close()

        st = ""
        for re in result1:
            st = re[0]
        print(st)

        dict_result = []

        for r in result:
            TRAIN_ID = r[0]
            NAME = r[1]
            departure = r[2]
            arrival = r[3]
            row = {'TRAIN_ID': TRAIN_ID, 'NAME': NAME, 'DEPARTURE_TIME': departure, 'ARRIVAL_TIME': arrival}
            dict_result.append(row)



    else:

        cursor = connection.cursor()
        sql = "SELECT * FROM TRAIN"
        cursor.execute(sql)
        result = cursor.fetchall()


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

    return render(request, 'list_trains.html', {'trains': dict_result})
    #cost add korbo

def list_stations(request):

    cursor = connection.cursor()
    sql = "SELECT * FROM STATION ORDER BY STATION_ID"
    cursor.execute(sql)
    result = cursor.fetchall()

    cursor.close()
    dict_result = []

    for r in result:
        STATION_ID = r[0]
        NAME = r[1]

        row = {'STATION_ID': STATION_ID, 'NAME': NAME}
        dict_result.append(row)

    return render(request, 'list_stations.html', {'stations': dict_result})

def homepage(request):
    #print("data= ",request.POST)
    return render(request,'search.html')

def registration(request):
    if request.method == "POST":
        print(request.POST)
        # mail = request.POST["email"]
        # ps = request.POST["password"]
        #
        #
        # cursor = connection.cursor()
        # sql = "SELECT EMAIL_ADD,PASSWORD FROM R_USER WHERE EMAIL_ADD=%s AND PASSWORD= %s;"
        # cursor.execute(sql,[mail,ps])
        # result = cursor.fetchall()
        # cursor.close()
        # if(result):
        #     print("logged in")
        #     return render(request, 'search.html')
        # else:
        #     print("log in denied")


    return render(request,'registration.html')

def login(request):
    if request.method == "POST":
        print(request.POST)
        mail = request.POST["email"]
        ps = request.POST["password"]


        cursor = connection.cursor()
        sql = "SELECT EMAIL_ADD,PASSWORD FROM R_USER WHERE EMAIL_ADD=%s AND PASSWORD= %s;"
        cursor.execute(sql,[mail,ps])
        result = cursor.fetchall()
        cursor.close()
        if(result):
            print("logged in")
            return render(request, 'search.html')
        else:
            print("log in denied")

    return render(request,'login.html')
