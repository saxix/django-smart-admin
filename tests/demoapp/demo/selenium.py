from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
from seleniumbase import BaseCase

from demo.factories import SuperUserFactory


class MaxParentsReached(NoSuchElementException):
    pass


class TestBrowser(BaseCase):
    live_server_url: str = ""

    def setUp(self, masterqa_mode=False):
        super().setUp()

        super().setUpClass()
        self.admin_user = SuperUserFactory()
        self.admin_user._password = "password"

    def tearDown(self):
        self.save_teardown_screenshot()
        super().tearDown()
        self.admin_user.delete()

    def base_method(self):
        pass

    def open(self, url: str):
        self.maximize_window()
        return super().open(f"{self.live_server_url}{url}")

    def select2_select(self, element_id: str, value: str):
        self.slow_click(f"span[aria-labelledby=select2-{element_id}-container]")
        self.wait_for_element_visible("input.select2-search__field")
        self.click(f"li.select2-results__option:contains('{value}')")
        self.wait_for_element_absent("input.select2-search__field")

    def login(self):
        url = reverse("admin:login")
        self.open(url)
        if self.get_current_url() == f"{self.live_server_url}{url}":
            self.type("input[name=username]", f"{self.admin_user.username}")
            self.type("input[name=password]", f"{self.admin_user._password}")
            self.submit('input[value="Log in"]')
            self.wait_for_ready_state_complete()
            url = reverse("admin:index")
            assert self.get_current_url() == f"{self.live_server_url}{url}", self.get_current_url()

    def is_required(self, element: str) -> bool:
        el = self.wait_for_element_visible(element)
        return el.parent.find_element("label>span").text == "(required)"

    def get_field_error(self, element: str) -> bool:
        return self.wait_for_element_visible(f"fieldset.{element} ul.errorlist").text
