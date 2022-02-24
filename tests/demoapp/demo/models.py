import django
from django.contrib.auth.models import User
from django.db import models

if django.VERSION[0] == 2:
    from django.contrib.postgres.fields import JSONField
else:
    from django.db.models import JSONField


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(verbose_name='Other email')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    registration_date = models.DateField(auto_created=True)
    active = models.BooleanField()

    flags = JSONField(default=dict)

    def __str__(self):
        return self.name


class ProductFamily(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    family = models.ForeignKey(ProductFamily, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Invoice #{self.number}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    qty = models.IntegerField(default=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
