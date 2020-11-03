from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render,redirect
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
        clas=request.POST["class"]

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
            if clas=='SNIGDHA':
                st = re[0]
            elif clas=='S_CHAIR':
                st=re[0]*0.8
            else:
                st=re[0]*0.6

        dict_result = []

        for r in result:
            TRAIN_ID = r[0]
            NAME = r[1]
            departure = r[2]
            arrival = r[3]
            row = {'TRAIN_ID': TRAIN_ID, 'NAME': NAME, 'DEPARTURE_TIME': departure, 'ARRIVAL_TIME': arrival}
            dict_result.append(row)



    else:
        st=""
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

    return render(request, 'list_trains.html', {'trains': dict_result,'cost':str(st)+''+' BDT'})
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
    my_user=request.user
    #is_user_logged = my_user.is_authenticated
    #print(is_user_logged)
    cursor = connection.cursor()
    sql="SELECT NAME FROM STATION"
    cursor.execute(sql)
    result=cursor.fetchall()
    cursor.close()
    dict=[]
    for r in result:
        NAME=r[0]
        row={'NAME':NAME}
        dict.append(row)

    #print("data= ",request.POST)
    return render(request,'search.html',{'names':dict})

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

            #user = authenticate(request, username=username, password=password)

            cursor1 = connection.cursor()
            sql1 = "SELECT FIRST_NAME||' '||LAST_NAME FROM R_USER WHERE EMAIL_ADD=%s AND PASSWORD= %s;"
            cursor1.execute(sql1, [mail, ps])
            result1 = cursor1.fetchall()
            cursor1.close()

            fullname=""
            for r in result1:
                fullname=r[0]

            #print("logged in")
            response="Dear {}, you are successfully logged in.".format(fullname)
            #return render(request, "search.html",{"status":response})
            return redirect('http://127.0.0.1:8000/', {"status": response})
        else:
            #print("log in denied")
            response = "Login Denied. Invalid email or password."
            return render(request, "login.html", {"status": response})

    return render(request,'login.html')

def seatselection(request):
    return render(request, 'seat_selection.html')
def contactus(request):
    return render(request, 'contactus.html')

def updateinfo(request):
    return render(request, 'updateinfo.html')

def changepass(request):
    return render(request, 'changepass.html')
def changemail(request):
    return render(request, 'changemail.html')
def changenum(request):
    return render(request, 'changenum.html')
def prev(request):
    return render(request, 'prev.html')
def upcoming(request):
    return render(request, 'upcoming.html')
def successful(request):
    return render(request, 'successful.html')

