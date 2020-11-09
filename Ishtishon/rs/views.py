from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
#from hashutils import make_pw_hash,check_pw_hash
import hashlib

from .models import Trains
from django.db import connection

global is_logged_in
global details
is_logged_in=0
details={}

def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_pw_hash(password,hash):
    if make_pw_hash(password)==hash:
        return True
    return False

def list_trains(request):
    if request.method == "POST":
        if is_logged_in==0:
            return redirect("/" + "?not_logged_in=" + str(is_logged_in))


        fro = request.POST["from"]
        to = request.POST["to"]
        date = request.POST["date"]
        adult = request.POST["adult"]
        child = request.POST["child"]
        clas=request.POST["class"]
        global details
        details={'from':fro,'to':to,'date':date,'adult':adult,'child':child,'class':clas}
        cursor = connection.cursor()
        sql = "SELECT TT1.TRAIN_ID,(SELECT NAME FROM TRAIN T1 WHERE T1.TRAIN_ID=TT1.TRAIN_ID) NAME1,TT1.DEPARTURE_TIME,TT2.DEPARTURE_TIME FROM TRAIN_TIMETABLE TT1,TRAIN_TIMETABLE TT2 WHERE (TT1.DIRECTION='FROM' AND TT1.STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s)) AND (TT2.DIRECTION='TO' AND TT2.STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s)) AND (TT1.TRAIN_ID=TT2.TRAIN_ID) ORDER BY TO_TIMESTAMP(LPAD(TT1.DEPARTURE_TIME,4,'0'), 'HH24:MI');"
        cursor.execute(sql, [fro, to])
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
        request.session['trains']=dict_result
        request.session['cost']=st
        return render(request, 'list_trains.html', {'trains': dict_result, 'cost': str(st) + '' + ' BDT', 'details': details})
    else:
        dict_result=request.session.get('trains')
        st=request.session.get('cost')
        name=request.GET.get('name')
        name=name[1:]

        return render(request, 'list_trains.html',
                      {'trains': dict_result, 'cost': str(st) + '' + ' BDT', 'details': details})






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
    if request.method=="GET":
        return render(request, 'search.html', {'names': dict})
        #print("data= ",request.POST)
    else:
        return render(request,'search.html',{'names':dict})

def registration(request):
    if is_logged_in == 1:
        return redirect("/" + "?already_logged_in=" + str(is_logged_in))
    if request.method == "POST":
        print(request.POST)
        first = request.POST["frst"]
        last= request.POST["last"]
        dob=request.POST["dob"]
        gender=request.POST["gender"]
        mail=request.POST["email"]
        nid = request.POST["nid"]
        house = request.POST["houseno"]
        road = request.POST["roadno"]
        city = request.POST["city"]
        zip = request.POST["zip"]
        contact = request.POST["contact"]
        ps = request.POST["password"]

        cursor1 = connection.cursor()
        sql1 = "SELECT EMAIL_ADD FROM R_USER WHERE EMAIL_ADD=%s;"
        cursor1.execute(sql1, [mail])
        result1 = cursor1.fetchall()
        cursor1.close()

        if (result1):
            print('1')
            msg="This E-mail ID is already registered."
            return render(request,'registration.html',{"status":msg})
        else:
            print('2')
            cursor2 = connection.cursor()
            sql2 = "SELECT NID_NO FROM R_USER WHERE NID_NO=%s;"
            cursor2.execute(sql2, [nid])
            result2 = cursor2.fetchall()
            cursor2.close()

            if(result2):
                print('3')
                msg = "This NID number is already registered."
                return render(request, 'registration.html', {"status": msg})
            else:
                print('4')
                cursor3 = connection.cursor()
                sql3 = "SELECT CONTACT_NO FROM R_USER WHERE CONTACT_NO='+880'||%s;"
                cursor3.execute(sql3, [contact])
                result3 = cursor3.fetchall()
                cursor3.close()

                if(result3):
                    print('5')
                    msg = "This contact number is already registered."
                    return render(request, 'registration.html', {"status": msg})
                else:
                    print('6')
                    pw_hash=make_pw_hash(ps)
                    print(pw_hash)

                    f = open("info.txt", "a+")
                    f.write(mail+" "+ps)
                    f.write("\n")
                    f.close()

                    cursor = connection.cursor()
                    sql = "INSERT INTO R_USER VALUES(NVL((SELECT MAX(USER_ID)+1 FROM R_USER),1),%s,UPPER(%s),UPPER(%s),TO_DATE(%s,'YYYY-MM-DD'),'+880'||%s,UPPER(%s),%s,%s,UPPER(%s),UPPER(%s),UPPER(%s),UPPER(%s));"
                    cursor.execute(sql, [pw_hash, first, last, dob, contact, gender, mail, nid, house, road, zip, city])
                    # result = cursor.fetchall()
                    cursor.close()
                    fullname=first+" "+last
                    return redirect("/login" + "?user=" + fullname)
                    #return render(request, 'login.html')
    return render(request,'registration.html')

def login(request):
    if request.method == "POST":
        global is_logged_in
        print(request.POST)
        if is_logged_in==1:
            print('already logged in')
            return redirect("/" + "?logged_in=" + str(is_logged_in))
        mail = request.POST["email"]
        ps = request.POST["password"]



        cursor = connection.cursor()
        sql = "SELECT PASSWORD FROM R_USER WHERE EMAIL_ADD=%s;"
        cursor.execute(sql,[mail])
        result = cursor.fetchall()
        cursor.close()


        if(result):

            for r in result:
                hash=r[0]
            if(check_pw_hash(ps,hash)):

                is_logged_in=1;
                #user = authenticate(request, username=username, password=password)

                cursor1 = connection.cursor()
                sql1 = "SELECT FIRST_NAME||' '||LAST_NAME FROM R_USER WHERE EMAIL_ADD=%s;"
                cursor1.execute(sql1, [mail])
                result1 = cursor1.fetchall()
                cursor1.close()

                fullname=""
                for r in result1:
                    fullname=r[0]


                return redirect("/"+"?user="+fullname)
            else:
                response = "Login Denied. Wrong Password."
                return render(request, "login.html", {"status": response})
        else:
            response = "Login Denied. Invalid E-mail."
            return render(request, "login.html", {"status": response})

    else :
        if (request.GET.get('logged_out')):
            if(is_logged_in==0):
                response="You are not logged in yet.Please log in first"#if (request.GET.logged_out == '1'):
            else:
                is_logged_in = 0
                response="You are logged out."
            return render(request, 'login.html', {"status": response})
        else:
            return render(request, 'login.html')

def seatselection(request):
    id=request.GET.get('id')

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

