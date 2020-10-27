from django.db import models

# Create your models here.
class Trains(models.Model):
    train_id= models.IntegerField()
    name= models.CharField(max_length=50, null = False)
    total_seat_snigdha= models.IntegerField()
    total_seat_schair = models.IntegerField()
    total_seat_shovan = models.IntegerField()

    #train_id = models.CharField(max_length=10,primary_key=True)
    #job_title = models.CharField(max_length=50, null = True)
    #min_salary = models.IntegerField()
    #max_salary = models.IntegerField()
    class Meta:
         db_table = "train"

class Stations(models.Model):
    station_id=models.IntegerField()
    name = models.CharField(max_length=20, null=False)
    class Meta:
         db_table = "station"