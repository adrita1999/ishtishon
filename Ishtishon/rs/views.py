import decimal
import os
import sys
import twilio
import random
from twilio.rest import Client
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
#from hashutils import make_pw_hash,check_pw_hash
import hashlib
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

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
        temp=int(child)+int(adult)
        request.session["total_seats"]=str(temp)
        request.session["doj"]=str(date)
        request.session["class"] = clas
        request.session["from"] = fro
        request.session["to"] = to
        global details
        details={'from':fro,'to':to,'date':date,'adult':adult,'child':child,'class':clas}
        cursor = connection.cursor()
        sql = "SELECT TT1.TRAIN_ID,(SELECT NAME FROM TRAIN T1 WHERE T1.TRAIN_ID=TT1.TRAIN_ID) NAME1,TT1.DEPARTURE_TIME,TT2.DEPARTURE_TIME FROM TRAIN_TIMETABLE TT1,TRAIN_TIMETABLE TT2 WHERE (TT1.DIRECTION='FROM' AND TT1.STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s)) AND (TT2.DIRECTION='TO' AND TT2.STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s)) AND (TT1.TRAIN_ID=TT2.TRAIN_ID) ORDER BY TO_TIMESTAMP(LPAD(TT1.DEPARTURE_TIME,4,'0'), 'HH24:MI');"
        cursor.execute(sql, [fro, to])
        result = cursor.fetchall()
        cursor.close()

        cursor1 = connection.cursor()
        sql1 = "select (COST*%s+COST*%s*0.5) FROM COST WHERE STATION_ID=(SELECT STATION_ID from STATION where NAME=%s) AND TO_STATION_ID=(SELECT STATION_ID from STATION where NAME=%s)"
        cursor1.execute(sql1, [adult,child,fro, to])
        result1 = cursor1.fetchall()
        cursor1.close()
        cursor2 = connection.cursor()
        sql2 = "select COST FROM COST WHERE STATION_ID=(SELECT STATION_ID from STATION where NAME=%s) AND TO_STATION_ID=(SELECT STATION_ID from STATION where NAME=%s)"
        cursor2.execute(sql2, [fro,to])
        result2 = cursor2.fetchall()
        cursor2.close()
        st1=""
        st2=""
        st3=""
        st4=""
        st5=""
        st6=""
        for re2 in result2:
            st1=int(re2[0])
            st2=int(re2[0]*decimal.Decimal('0.5'))
            st3=int(re2[0]*decimal.Decimal('0.8'))
            st4 = int(re2[0]*decimal.Decimal('0.8')*decimal.Decimal('0.5'))
            st5= int(re2[0]*decimal.Decimal('0.6'))
            st6 = int(re2[0]*decimal.Decimal('0.6')*decimal.Decimal('0.5'))
        fare_list=[]
        fare_list.append(str(st1))
        fare_list.append(str(st2))
        fare_list.append(str(st3))
        fare_list.append(str(st4))
        fare_list.append(str(st5))
        fare_list.append(str(st6))
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
        request.session['snigdha_fare'] = fare_list
        return render(request, 'list_trains.html', {'trains': dict_result, 'cost': str(st) + '' + ' BDT', 'details': details})
    else:
        dict_result=request.session.get('trains')
        st=request.session.get('cost')
        name=request.GET.get('name')
        snigdha_fare=request.session.get('snigdha_fare')
        id=name[1:4]
        print(id);
        snigdha=""
        s_chair=""
        shovan=""
        available_seats=[]
        cursor=connection.cursor()
        sql="SELECT 78-COUNT(*) FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND CLASS='SNIGDHA' AND DATE_OF_JOURNEY= TO_DATE('15-11-2020','DD-MM-YYYY');"
        cursor.execute(sql,[id])
        result=cursor.fetchall()
        for r in result:
            snigdha=r[0];

        cursor1 = connection.cursor()
        sql1 = "SELECT 78-COUNT(*) FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND CLASS='S_CHAIR' AND DATE_OF_JOURNEY= TO_DATE('15-11-2020','DD-MM-YYYY');"
        cursor1.execute(sql1, [id])
        result1 = cursor1.fetchall()
        for r1 in result1:
            s_chair=r1[0];
        cursor2 = connection.cursor()
        sql2 = "SELECT 78-COUNT(*) FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND CLASS='SHOVAN' AND DATE_OF_JOURNEY= TO_DATE('15-11-2020','DD-MM-YYYY');"
        cursor2.execute(sql2, [id])
        result2 = cursor2.fetchall()
        for r2 in result2:
            shovan=r2[0];


        row={'snigdha':snigdha,'s_chair':s_chair,'shovan':shovan}
        available_seats.append(row)
        print(available_seats)
        return render(request, 'list_trains.html',
                      {'trains': dict_result, 'cost': str(st) + '' + ' BDT', 'details': details,'available_seats':available_seats,'snigdha_fare':snigdha_fare})






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

    """email=EmailMessage(
        'subject',
        'body',
        settings.EMAIL_HOST_USER,
        ['adrita_99@yahoo.com'],
    )
    email.fail_silently=False
    email.send()"""
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
        #print(request.POST)
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

                is_logged_in=1
                request.session['usermail']=mail
                #user = authenticate(request, username=username, password=password)

                cursor1 = connection.cursor()
                sql1 = "SELECT FIRST_NAME,LAST_NAME,DOB,GENDER,NID_NO,HOUSE_NO,ROAD_NO,ZIP_CODE,CITY,CONTACT_NO,USER_ID FROM R_USER WHERE EMAIL_ADD=%s;"
                cursor1.execute(sql1, [mail])
                result1 = cursor1.fetchall()
                cursor1.close()

                fullname=""
                for r in result1:
                    fullname=r[0]
                    request.session['first'] = r[0]
                    request.session['last'] = r[1]
                    request.session['dob'] = str(r[2])
                    request.session['gender'] = r[3]
                    request.session['nid'] =r[4]
                    request.session['house'] = r[5]
                    request.session['road'] = r[6]
                    request.session['zip'] = r[7]
                    request.session['city'] = r[8]
                    request.session['contact'] = r[9]
                    request.session['user_id'] = r[10]

                #request.session['fullname']=fullname;
                return redirect("/"+"?user="+fullname)
            else:
                print(make_pw_hash(ps))
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
                request.session.flush()
                response="You are logged out."
            return render(request, 'login.html', {"status": response})
        else:
            return render(request, 'login.html')

def seatselection(request):
    id=request.GET.get('id');
    request.session["train_id"]=id
    clas = request.session.get('class')
    doj = request.session.get('doj')
    cursor = connection.cursor()
    sql="SELECT SEAT_NO FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND CLASS=%s AND DATE_OF_JOURNEY= TO_DATE(%s,'YYYY-MM-DD');"
    cursor.execute(sql,[id,clas,doj])
    result=cursor.fetchall();
    cursor.close()
    booked_seats=[]
    for r in result:
        seat_no=r[0]
        booked_seats.append(seat_no)

    print(booked_seats)
    return render(request, 'seat_selection.html',{'booked_seats':booked_seats})
def contactus(request):
    return render(request, 'contactus.html')

def updateinfo(request):
    if is_logged_in == 0:
        return redirect("/login" + "?notdash_logged_in=" + str(is_logged_in))

    mail = request.session.get('usermail')
    contact = request.session.get('contact')
    first=request.session.get('first')
    last=request.session.get('last')
    dob=request.session.get('dob')
    gender=request.session.get('gender')
    nid=request.session.get('nid')
    house=request.session.get('house')
    road=request.session.get('road')
    zip=request.session.get('zip')
    city=request.session.get('city')
    dob=dob[0:10]
    print(dob)

    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    #return render(request, 'updateinfo.html',{"first":first,"last":last,"dob":dob,"gender":gender,"nid":nid,"house":house,"road":road,"zip":zip,"city":city,"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr})
    if request.method == "POST":
        first=request.POST["first"]
        last=request.POST["last"]
        dob=request.POST["dob"]
        request.session["dob"]=dob
        gender=request.POST["gender"]
        request.session["gender"] = gender.upper()
        nid = request.POST["nid"]
        request.session["nid"] = nid
        house = request.POST["house"]
        request.session["house"] = house.upper()
        road = request.POST["road"]
        request.session["road"] = road.upper()
        zip = request.POST["zip"]
        request.session["zip"] = zip.upper()
        city = request.POST["city"]
        mail = request.session.get('usermail')
        print(request.POST)
        cursor = connection.cursor()
        sql = "UPDATE R_USER SET  FIRST_NAME=upper(%s),LAST_NAME=UPPER (%s),DOB=TO_DATE(%s,'YYYY-MM-DD'),GENDER=UPPER (%s),NID_NO=%s,HOUSE_NO=UPPER(%s),ROAD_NO=UPPER(%s),ZIP_CODE=UPPER(%s),CITY=UPPER(%s) WHERE EMAIL_ADD=%s;"
        cursor.execute(sql, [first,last,dob,gender,nid,house,road,zip,city,mail])
        cursor.close()
        first=first.upper()
        request.session["first"] = first
        last=last.upper()
        request.session["last"] = last
        city=city.upper()
        request.session["city"] = city
        mail = request.session.get('usermail')
        contact = request.session.get('contact')
        first = request.session.get('first')
        last = request.session.get('last')
        dob = request.session.get('dob')
        gender = request.session.get('gender')
        nid = request.session.get('nid')
        house = request.session.get('house')
        road = request.session.get('road')
        zip = request.session.get('zip')
        city = request.session.get('city')
        dob = dob[0:10]
        print(dob)

        fullname = first + " " + last
        address = ""
        if (house):
            if (road):
                if (zip):
                    address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
                else:
                    address = "House no: " + house + ", Road no: " + road + ", " + city
            else:
                if (zip):
                    address = "House no: " + house + ", " + city + "-" + zip
                else:
                    address = "House no: " + house + ", " + city
        else:
            if (road):
                if (zip):
                    address = "Road no: " + road + ", " + city + "-" + zip

                else:
                    address = "Road no: " + road + ", " + city

            else:
                if (zip):
                    address = city + "-" + zip

                else:
                    address = city
        slice_object = slice(4, 14, 1)
        pnr = contact[slice_object]
        response='Profile updated successfully'
        return render(request, 'updateinfo.html',{"status":response,"first":first,"last":last,"dob":dob,"gender":gender,"nid":nid,"house":house,"road":road,"zip":zip,"city":city,"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr})

    else:
        first=request.session.get('first')
        last=request.session.get('last')
        dob=request.session.get('dob')
        gender=request.session.get('gender')
        gender=gender.capitalize()
        nid=request.session.get('nid')
        house=request.session.get('house')
        road=request.session.get('road')
        zip=request.session.get('zip')
        city=request.session.get('city')
        dob=dob[0:10]
        print(dob)
        return render(request, 'updateinfo.html',{"first":first,"last":last,"dob":dob,"gender":gender,"nid":nid,"house":house,"road":road,"zip":zip,"city":city,"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr})

    return render(request, 'updateinfo.html',
                  {"first":first,"last":last,"dob":dob,"gender":gender,"nid":nid,"house":house,"road":road,"zip":zip,"city":city,"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr})
def changepass(request):
    first=request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact=request.session.get('contact')
    nid = request.session.get('nid')
    fullname= first + " " +last
    address=""
    if(house):
        if(road):
            if(zip):
                address= "House no: "+house+", Road no: "+road+", "+city+"-"+zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house  + ", " + city + "-" + zip
            else:
                address = "House no: " + house +  ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr=contact[slice_object]

    if request.method == "POST":
        ps = request.POST["pass"]
        newps = request.POST["newpass"]
        mail=request.session.get('usermail')
        cursor = connection.cursor()
        sql = "SELECT PASSWORD FROM R_USER WHERE EMAIL_ADD=%s;"
        cursor.execute(sql, [mail])
        result = cursor.fetchall()
        cursor.close()

        for r in result:
            dbps = r[0]
        if (check_pw_hash(ps,dbps)):
            newps_hash = make_pw_hash(newps)

            f = open("info.txt", "a+")
            f.write(mail + " " + newps)
            f.write("\n")
            f.close()
            cursor1 = connection.cursor()
            sql1 = "UPDATE R_USER SET  PASSWORD= %s WHERE EMAIL_ADD=%s;"
            cursor1.execute(sql1, [newps_hash,mail])
            cursor1.close()
            response = "Password successfully updated. "
            return render(request, "changepass.html", {"status": response, "fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr,"nid":nid})


        else:
            response = "Wrong Password."
            print(response+ fullname+mail+address+contact+pnr+nid)
            return render(request, "changepass.html", {"status": response, "fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr,"nid":nid})


    return render(request, 'changepass.html',{"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr,"nid":nid})
def changemail(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    return render(request, 'changemail.html',{"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr,"nid":nid})

def changenum(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    return render(request, 'changenum.html',{"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr,"nid":nid})
def prev(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    return render(request, 'prev.html',{"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr,"nid":nid})
def upcoming(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    return render(request, 'upcoming.html',{"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr,"nid":nid})
def successful(request):
    train_id=request.session.get('train_id')
    cursor=connection.cursor()
    sql="SELECT NAME FROM TRAIN WHERE TRAIN_ID=%s;"
    cursor.execute(sql,[train_id])
    result = cursor.fetchall()
    cursor.close()

    for r in result:
        name = r[0]

    return render(request, 'successful.html',{"name":name,"train_id":train_id,"total_seats":request.session.get('total_seats'),
                                              "amount":request.session.get('cost'),"details":details})
def payment_selection(request):
    seat_nos=request.GET.get('seat_nos')

    total_seats = request.session.get('total_seats')
    amount = request.session.get('cost')
    if(seat_nos[0]=='a'):
        clas=request.session.get('class')
        train_id=request.session.get('train_id')
        doj=request.session.get('doj')
        cursor=connection.cursor()
        out=""
        total_seats=int(total_seats)
        result=cursor.callproc('SEATNOS',[total_seats,train_id,clas,doj,out])
        print(result[4])
        request.session["seat_nos"] = result[4]
        return render(request, 'payment selection.html', {'amount': amount})
    else:

        print(total_seats)
        seat_nos=seat_nos[1:]
        print(seat_nos)
        request.session["seat_nos"] = seat_nos
        seat_list=seat_nos.split()
        print(seat_list)
        if(int(total_seats)!=len(seat_list)):
            return redirect("/seat_selection" + "?not_equal=" + str('1'))


        #print(seat_list)
        return render(request, 'payment selection.html',{'amount':amount})
def bkash(request):
    name=""
    ps=""
    vcode=""
    otp=1111
    amount = request.session.get('cost')
    if request.method == "POST"and 'btn1' in request.POST:
        # print(request.POST)
        # otp=random.randint(1000,9999)
        otp = 1111
        account_sid = 'AC12508562ed95fd8227bfb94ee4c762ae'
        auth_token = '36e0fe6c03fff9833e5f9173250e9723'

        print("otp jacche")
        # client = Client(account_sid, auth_token)
        #
        # message = client.messages \
        #     .create(
        #     body='Your OTP is '+str(otp),
        #     from_='+12543235243',
        #     to='+8801878046439'
        # )

        # print(message.sid)



    if request.method == "POST" and 'btn2' in request.POST:
        name = request.POST["name"]
        ps = request.POST["password"]
        vcode=request.POST["vcode"]
        print(request.POST)
        if vcode == str(otp):
            cursor = connection.cursor()
            sql = "INSERT INTO PAYMENT VALUES(NVL((SELECT (MAX(PAYMENT_ID)+1) FROM PAYMENT),1),%s,SYSDATE);"
            cursor.execute(sql, [amount])
            cursor.close()
            cursor1 = connection.cursor()
            print("payment e dhukse")
            sql1 = "INSERT INTO MOBILE_BANKING VALUES(NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1), TO_NUMBER(%s),TO_NUMBER(%s),TO_NUMBER(%s));"
            cursor1.execute(sql1, [name,vcode,ps])
            cursor1.close()
            print("mb e dhukse")
            return redirect("/successful")
        if vcode != "" and vcode != str(otp):
            print("otp milena")
            msg = "Wrong OTP Entered."
            return render(request, 'bkash_payment.html', {"status": msg, 'amount':amount})


    return render(request, 'bkash_payment.html',{'amount':amount})


def card(request):
    amount = request.session.get('cost')
    if request.method=="POST":

        cardnumber=request.POST["cardnumber"]
        name=request.POST["name"]
        cvv=request.POST["cvv"]
        date = request.POST["date"]
        cursor=connection.cursor()
        sql="INSERT INTO PAYMENT VALUES(NVL((SELECT MAX(PAYMENT_ID)+1 FROM PAYMENT),1),%s,SYSDATE);"
        cursor.execute(sql,[amount])
        cursor.close()

        cursor1=connection.cursor()
        sql1="INSERT INTO CARD VALUES(NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1),UPPER(%s),%s,TO_DATE(%s,'YYYY-MM-DD'),%s);"
        cursor1.execute(sql1,[name,cardnumber,date,cvv])
        cursor1.close()

        doj = request.session.get('doj')
        doj=str(doj)
        print(doj)
        tot = request.session.get('total_seats')
        cls = request.session.get('class')
        fro = request.session.get('from')
        to = request.session.get('to')
        tr = request.session.get('train_id')
        id = request.session.get('user_id')
        cursor2 = connection.cursor()
        sql2 = "INSERT INTO RESERVATION VALUES(NVL((SELECT (MAX(RESERVATION_ID)+1) FROM RESERVATION),1),SYSDATE,TO_DATE(%s,'YYYY-MM-DD'),TO_NUMBER(%s),%s,%s,%s,TO_NUMBER(%s),TO_NUMBER(%s),NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1));"
        cursor2.execute(sql2, [doj, tot, cls, fro,to,tr,id])
        cursor2.close()
        seat_nos = request.session.get('seat_nos')
        seat_list = seat_nos.split()
        cursor3 = connection.cursor()
        for s in seat_list:
            seat=str(s)
            sql3 = "INSERT INTO BOOKED_SEAT VALUES(TO_NUMBER(%s),TO_NUMBER(%s),NVL((SELECT (MAX(RESERVATION_ID)) FROM RESERVATION),1),%s,TO_DATE(%s,'YYYY-MM-DD'));"
            cursor3.execute(sql3, [tr, seat, cls, doj])
        cursor3.close()
        return  redirect("/successful")
        #print(request.POST);


    return render(request, 'card_payment.html',{'amount':amount})
def nexus(request):
    amount = request.session.get('cost')
    if request.method=="POST":

        cardnumber=request.POST["cardnumber"]
        name=request.POST["name"]
        pin=request.POST["pin"]
        cursor = connection.cursor()
        sql = "INSERT INTO PAYMENT VALUES(NVL((SELECT MAX(PAYMENT_ID)+1 FROM PAYMENT),1),%s,SYSDATE);"
        cursor.execute(sql, [amount])
        cursor.close()
        cursor1 = connection.cursor()
        sql1 = "INSERT INTO NEXUSPAY VALUES(NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1),UPPER(%s),%s,%s);"
        cursor1.execute(sql1, [name, cardnumber,pin])
        cursor1.close()
        doj = request.session.get('doj')
        doj = str(doj)
        print(doj)
        tot = request.session.get('total_seats')
        cls = request.session.get('class')
        fro = request.session.get('from')
        to = request.session.get('to')
        tr = request.session.get('train_id')
        id = request.session.get('user_id')
        cursor2 = connection.cursor()
        sql2 = "INSERT INTO RESERVATION VALUES(NVL((SELECT (MAX(RESERVATION_ID)+1) FROM RESERVATION),1),SYSDATE,TO_DATE(%s,'YYYY-MM-DD'),TO_NUMBER(%s),%s,%s,%s,TO_NUMBER(%s),TO_NUMBER(%s),NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1));"
        cursor2.execute(sql2, [doj, tot, cls, fro, to, tr, id])
        cursor2.close()
        seat_nos = request.session.get('seat_nos')
        seat_list = seat_nos.split()
        cursor3 = connection.cursor()
        for s in seat_list:
            seat = str(s)
            sql3 = "INSERT INTO BOOKED_SEAT VALUES(TO_NUMBER(%s),TO_NUMBER(%s),NVL((SELECT (MAX(RESERVATION_ID)) FROM RESERVATION),1),%s,TO_DATE(%s,'YYYY-MM-DD'));"
            cursor3.execute(sql3, [tr, seat, cls, doj])
        cursor3.close()

        return redirect("/successful")
    return render(request, 'nexus_payment.html',{'amount':amount})
def rocket(request):
    name = ""
    ps = ""
    vcode = ""
    otp = 1111
    amount = request.session.get('cost')
    if request.method == "POST" and 'btn1' in request.POST:
        # print(request.POST)
        # otp=random.randint(1000,9999)
        otp = 1111
        account_sid = 'AC12508562ed95fd8227bfb94ee4c762ae'
        auth_token = '36e0fe6c03fff9833e5f9173250e9723'

        print("otp jacche")
        # client = Client(account_sid, auth_token)
        #
        # message = client.messages \
        #     .create(
        #     body='Your OTP is '+str(otp),
        #     from_='+12543235243',
        #     to='+8801878046439'
        # )

        # print(message.sid)

    if request.method == "POST" and 'btn2' in request.POST:
        name = request.POST["name"]
        ps = request.POST["password"]
        vcode = request.POST["vcode"]

        print(request.POST)
        if vcode == str(otp):
            cursor = connection.cursor()
            sql = "INSERT INTO PAYMENT VALUES(NVL((SELECT (MAX(PAYMENT_ID)+1) FROM PAYMENT),1),%s,SYSDATE);"
            cursor.execute(sql, [amount])
            cursor.close()
            cursor1 = connection.cursor()
            print("payment e dhukse")
            sql1 = "INSERT INTO MOBILE_BANKING VALUES(NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1), TO_NUMBER(%s),TO_NUMBER(%s),TO_NUMBER(%s));"
            cursor1.execute(sql1, [name, vcode, ps])
            cursor1.close()
            print("mb e dhukse")
            return redirect("/successful")
        if vcode != "" and vcode != str(otp):
            print("otp milena")
            msg = "Wrong OTP Entered."
            return render(request, 'rocket_payment.html', {"status": msg, 'amount':amount})

    return render(request, 'rocket_payment.html',{'amount':amount})


