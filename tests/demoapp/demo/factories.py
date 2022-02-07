import random

import factory.fuzzy
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from factory.base import FactoryMetaClass

from . import models

factories_registry = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class ModelFactory(factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass


class UserFactory(ModelFactory):
    username = factory.Sequence(lambda d: "username-%s" % d)
    email = factory.Faker('email')
    first_name = factory.Faker('name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = User
        django_get_or_create = ('username',)


class ContentTypeFactory(ModelFactory):
    class Meta:
        model = ContentType


class PermissionFactory(ModelFactory):
    content_type = factory.SubFactory(ContentTypeFactory)
    codename = 'perm1'

    class Meta:
        model = Permission
        django_get_or_create = ('codename',)


class LogEntryFactory(ModelFactory):
    user = factory.SubFactory(UserFactory)
    content_type = factory.Iterator(ContentType.objects.all())
    action_flag = 1

    class Meta:
        model = LogEntry


class GroupFactory(ModelFactory):
    name = factory.Sequence(lambda d: "Group %s" % d)

    class Meta:
        model = Group


class CustomerFactory(ModelFactory):
    name = factory.Faker('name')
    email = factory.Faker('email')
    user = factory.SubFactory(UserFactory)
    active = True
    registration_date = factory.LazyFunction(timezone.now)

    class Meta:
        model = models.Customer

    @factory.lazy_attribute
    def flags(self):
        # Convert to plain ascii text
        f = lambda: random.choice([
            ("int", random.randint(1, 100)),
            ("chr", chr(random.randrange(65, 90))),
            ("int", '__'),
            ("chr", ""),
            ("chr", None),
            ("int", None),
            ("chr", '__'),
        ])
        value = f()
        if value[1] == '__':
            base = {}
        else:
            base = dict([value])
        value = f()
        if value[1] != '__':
            base.update(dict([value]))
        return base


class ProductFamilyFactory(ModelFactory):
    name = factory.LazyFunction(lambda: 'Family %s' % random.choice([0, 1, 3]))

    class Meta:
        model = models.ProductFamily
        django_get_or_create = ('name',)


class ProductFactory(ModelFactory):
    name = factory.LazyFunction(lambda: random.choice(['Brooks Ghost 13',
                                                       'ASICS Gel-Trabuco 9',
                                                       'New Balance']))
    price = factory.fuzzy.FuzzyDecimal(100, 10000)
    family = factory.SubFactory(ProductFamilyFactory)

    class Meta:
        model = models.Product
        django_get_or_create = ('name',)


class InvoiceFactory(ModelFactory):
    customer = factory.SubFactory(CustomerFactory)
    number = factory.LazyFunction(lambda: random.choice(range(100)))
    date = factory.LazyFunction(timezone.now)

    class Meta:
        model = models.Invoice
        django_get_or_create = ('number',)


class InvoiceItemFactory(ModelFactory):
    invoice = factory.SubFactory(InvoiceFactory)
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = models.InvoiceItem


def get_factory_for_model(_model):
    class Meta:
        model = _model

    if _model in factories_registry:
        return factories_registry[_model]
    return type("AAA", (ModelFactory,), {'Meta': Meta})
