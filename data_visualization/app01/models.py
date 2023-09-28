from django.db import models


# Create your models here.
class Admin(models.Model):
    """ User """

    username = models.CharField(verbose_name='username', max_length=32)
    password = models.CharField(verbose_name='password', max_length=64)

    def __str__(self):
        return self.username



class BodsBusAnalysis(models.Model):
    Name = models.CharField(max_length=32)
    Length = models.FloatField()
    Median = models.FloatField()
    Mean = models.FloatField()
    Mode = models.FloatField()
    Maximum = models.FloatField()
    Minimum = models.FloatField()
    Variance = models.FloatField()
    Quartile_0_25 = models.FloatField()
    Quartile_0_75 = models.FloatField()
    Skewness = models.FloatField()
    Kurtosis = models.FloatField()

    class Meta:
        db_table = 'bods_bus_analysis'
        managed = False


class BodsBusAnalysisAll(models.Model):
    OperatorRef = models.CharField(max_length=32)
    LineRef = models.CharField(max_length=32)
    DirectionRef = models.CharField(max_length=32)
    hour = models.IntegerField()
    Degree = models.FloatField()

    class Meta:
        db_table = 'bods_bus_analysis_all'
        managed = False
















