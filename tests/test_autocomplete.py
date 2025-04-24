from django.urls import reverse


def test_autocomplete(app):
    base_url = reverse("admin:autocomplete")
    url = base_url + "?app_label=auth&model_name=user&field_name=username"
    res = app.get(url, user=app._user)
    assert res.json == {
        "results": [{"id": str(app._user.pk), "text": app._user.username}],
        "pagination": {"more": False},
    }
