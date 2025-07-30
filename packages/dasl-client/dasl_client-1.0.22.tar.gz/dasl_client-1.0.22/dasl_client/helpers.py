from urllib.parse import urlparse
import os


class Helpers:
    default_dasl_host = "https://api.prod.sl.antimatter.io"

    @staticmethod
    def ensure_databricks():
        if "DATABRICKS_RUNTIME_VERSION" not in os.environ:
            raise Exception(
                "attempted to access databricks context outside "
                + "of databricks notebook"
            )

    @staticmethod
    def databricks_context():
        # This import raises an exception if outside a notebook context, so only
        # import if this method is called
        Helpers.ensure_databricks()
        from databricks.sdk.runtime import dbutils

        return dbutils.notebook.entry_point.getDbutils().notebook().getContext()

    @staticmethod
    def current_workspace_url() -> str:
        base_url = Helpers.databricks_context().browserHostName().get()
        return f"https://{base_url}"

    @staticmethod
    def api_token() -> str:
        return Helpers.databricks_context().apiToken().get()

    @staticmethod
    def workspace_name_from_url(url: str) -> str:
        u = urlparse(url)
        return u.hostname
