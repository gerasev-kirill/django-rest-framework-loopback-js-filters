from django.db import models




class TestModel(models.Model):
    string_field = models.CharField(max_length=30)
    int_field = models.IntegerField(null=True, blank=True)
    float_field = models.FloatField(null=True)
    date_field = models.DateField(null=True)
    datetime_field = models.DateTimeField(null=True)
