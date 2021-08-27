from django.db import connections

CLAUSES = {
    'sqlite': "DELETE FROM {0};",
    'postgresql': 'TRUNCATE TABLE "{0}" {1} CASCADE;',
    'mysql': 'TRUNCATE TABLE "{0}" {1} CASCADE;',
}


class TruncateMixin:
    def truncate(self, reset=True):
        truncate_model_table(self.model, reset)


def truncate_model_table(model, reset=True):
    conn = connections[model._default_manager.db]
    if reset and conn.vendor == "postgresql":
        restart = 'RESTART IDENTITY'
    else:
        restart = ''
    with conn.cursor() as cursor:
        cursor.execute(CLAUSES[conn.vendor].format(model._meta.db_table,
                                                   restart))
