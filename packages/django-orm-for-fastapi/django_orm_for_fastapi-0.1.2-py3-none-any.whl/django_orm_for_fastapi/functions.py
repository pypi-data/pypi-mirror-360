from django.db import connections

from .consts import DEFAULT_CONNECTION_ID

def create_db_tables():
    with connections[DEFAULT_CONNECTION_ID].schema_editor() as schema_editor:
        introspection = connections[DEFAULT_CONNECTION_ID].introspection

        for model in introspection.get_migratable_models():
            if (
                model._meta.db_table
                not in introspection.table_names()
            ):
                schema_editor.create_model(model)


def drop_db_tables():
    with connections[DEFAULT_CONNECTION_ID].schema_editor() as schema_editor:
        for model in connections[DEFAULT_CONNECTION_ID].introspection.get_migratable_models():
            schema_editor.delete_model(model)

