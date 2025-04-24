import re

from demo.factories import GroupFactory, UserFactory
from django.contrib.auth.models import Permission

from smart_admin.utils import MatchString, RegexString, SmartList, get_linked_objects


def test_smartlist():
    smart_list = SmartList(["abc", re.compile("x.."), RegexString("x.."), MatchString("1*")])
    assert "abc" in smart_list
    assert "xyz" in smart_list
    assert "123" in smart_list

    assert "ac" not in smart_list
    assert "xy" not in smart_list


def test_get_related(db):
    perm = Permission.objects.get(codename="add_user")
    g = GroupFactory(permissions=[perm])
    u = UserFactory(permissions=[perm], groups=[g])

    assert get_linked_objects(u) == ([], [])
    res = get_linked_objects(g)
    res[0][0].pop("data")
    assert res == (
        [
            {
                "count": 1,
                "field_name": "user",
                "filter": f"groups={g.pk}",
                "link": "auth_user_changelist",
                "owner": g,
                "related_name": "user",
                "to": "group",
            }
        ],
        [],
    )

    res = get_linked_objects(perm)
    res[0][0].pop("data")
    res[0][1].pop("data")
    assert res == (
        [
            {
                "count": 1,
                "field_name": "group",
                "filter": f"permissions={perm.pk}",
                "link": "auth_group_changelist",
                "owner": perm,
                "related_name": "group",
                "to": "permission",
            },
            {
                "count": 1,
                "field_name": "user",
                "filter": f"user_permissions={perm.pk}",
                "link": "auth_user_changelist",
                "owner": perm,
                "related_name": "user",
                "to": "permission",
            },
        ],
        [],
    )
