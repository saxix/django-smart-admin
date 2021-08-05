import factory
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from factory.base import FactoryMetaClass

factories_registry = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class ModelFactory(factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass


class UserFactory(ModelFactory):
    class Meta:
        model = User


class LogEntryFactory(ModelFactory):
    user = factory.SubFactory(UserFactory)
    action_flag = 1

    class Meta:
        model = LogEntry


def get_factory_for_model(_model):
    class Meta:
        model = _model

    if _model in factories_registry:
        return factories_registry[_model]
    return type("AAA", (ModelFactory,), {'Meta': Meta})
