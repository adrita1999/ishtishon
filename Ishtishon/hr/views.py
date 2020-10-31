

# Create your views here.
from django.shortcuts import render
from .models import Job
from django.db import connection


# Create your views here.
def list_jobs(request):
    # cursor = connection.cursor()
    # sql = "INSERT INTO JOBS VALUES(%s,%s,%s,%s)"
    # cursor.execute(sql,['NEW_JOB','Something New',4000,8000])
    # connection.commit()
    # cursor.close()

    cursor = connection.cursor()
    sql = "SELECT * FROM JOBS"
    cursor.execute(sql)
    result = cursor.fetchall()

    # cursor = connection.cursor()
    # sql = "SELECT * FROM JOBS WHERE MIN_SALARY=%s"
    # cursor.execute(sql,[4000])
    # result = cursor.fetchall()

    cursor.close()
    dict_result = []

    for r in result:
        job_id = r[0]
        job_title = r[1]
        min_salary = r[2]
        max_salary = r[3]
        row = {'job_id': job_id, 'job_title': job_title, 'min_salary': min_salary, 'max_salary': max_salary}
        dict_result.append(row)

    # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    return render(request, 'list_jobs.html', {'jobs': dict_result})
