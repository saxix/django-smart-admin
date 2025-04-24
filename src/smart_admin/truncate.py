from django.db import connections, models

CLAUSES = {
    "sqlite": [
        "DELETE FROM {table_name};",
        "DELETE FROM SQLITE_SEQUENCE WHERE name='{table_name}'",
    ],
    "postgresql": [
        'TRUNCATE TABLE "{table_name}" CASCADE;',
        "ALTER TABLE {table_name} ALTER COLUMN {pk_column} RESTART SET START 1;",
    ],
    "mysql": [
        'TRUNCATE TABLE "{table_name}" CASCADE;',
        'ALTER TABLE "{table_name}" AUTO_INCREMENT = 1',
    ],
}


class TruncateMixin:
    def truncate(self, reset=True):
        truncate_model_table(self.model, reset)  # type: ignore[attr-defined]


def truncate_model_table(model: models.Model, reset: bool = True) -> None:
    conn = connections[model._default_manager.db]
    info = {
        "table_name": model._meta.db_table,
        "pk_column": model._meta.pk.column,
    }
    if reset:
        sqls = CLAUSES[conn.vendor][0:2]
    else:
        sqls = CLAUSES[conn.vendor][1:1]

    with conn.cursor() as cursor:
        if conn.vendor == "sqlite":
            cursor.execute("PRAGMA foreign_keys = ON")
        for tpl in sqls:
            c = tpl.format(**info)
            cursor.execute(c)
