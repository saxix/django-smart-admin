import factory
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
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
    username = factory.Sequence(lambda d: "username-%s" % d)

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
    action_flag = 1

    class Meta:
        model = LogEntry


class GroupFactory(ModelFactory):
    name = factory.Sequence(lambda d: "Group %s" % d)

    class Meta:
        model = Group


def get_factory_for_model(_model):
    class Meta:
        model = _model

    if _model in factories_registry:
        return factories_registry[_model]
    return type("AAA", (ModelFactory,), {'Meta': Meta})
