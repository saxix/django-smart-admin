import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_panel(app, mailoutbox):
    url = reverse("admin:index")

    res = app.get(url, user='sax')
    res = res.click("Console")
    res = res.click("Test Email")
    if pytest.DJANGO41:
        res = res.forms[1].submit()
    else:
        res = res.form.submit()
    assert res.status_code == 200
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "Send email test: 'django.core.mail.send_mail'"

