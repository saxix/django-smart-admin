from django.contrib.auth.models import User
from django.db import models


class DemoModel1(models.Model):
    name = models.CharField(max_length=255)
    char = models.CharField('Chäř', max_length=255)
    integer = models.IntegerField(null=True, blank=True)
    logic = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    decimal = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    email = models.EmailField()
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)


class DemoModel2(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "DemoModel2 #%s" % self.pk


class DemoModel3(models.Model):
    name = models.CharField(max_length=255)


class DemoModel4(models.Model):
    name = models.CharField(max_length=255)
