def smart_register(*models, site=None, force=True):
    from django.contrib.admin import ModelAdmin
    from django.contrib.admin.sites import AdminSite, site as default_site

    def _model_admin_wrapper(admin_class):
        if not models:
            raise ValueError('At least one model must be passed to register.')

        admin_site = site or default_site

        if not isinstance(admin_site, AdminSite):
            raise ValueError('site must subclass AdminSite')

        if not issubclass(admin_class, ModelAdmin):
            raise ValueError('Wrapped class must subclass ModelAdmin.')
        for model in models:
            if model in admin_site._registry and force:
                admin_site.unregister(model)
            admin_site.register(model, admin_class=admin_class)

        return admin_class

    return _model_admin_wrapper
