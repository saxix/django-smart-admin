from django.apps import AppConfig


class Config(AppConfig):
    name = "demo"

    def ready(self):
        super().ready()
        from django.contrib.admin import site  # noqa

        from smart_admin.console import (  # noqa
            panel_email,
            panel_error_page,
            panel_migrations,
            panel_redis,
            panel_sentry,
            panel_sysinfo,
        )

        site.register_panel(panel_migrations)
        site.register_panel(panel_sysinfo)
        site.register_panel(panel_sentry)
        site.register_panel(panel_redis)
        site.register_panel(panel_email)
        site.register_panel(panel_error_page)
