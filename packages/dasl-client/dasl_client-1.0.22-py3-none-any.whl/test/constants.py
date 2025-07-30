import os
from urllib.parse import urlparse

dasl_host = os.environ["DASL_API_URL"]
databricks_host = os.environ["DASL_DATABRICKS_HOST"]
databricks_client_id = os.environ["DASL_DATABRICKS_CLIENT_ID"]
databricks_client_secret = os.environ["DASL_DATABRICKS_CLIENT_SECRET"]
workspace = urlparse(databricks_host).hostname
app_client_id = "22853b93-68ba-4ae2-8e41-976417f501dd"
alternate_app_client_id = "335ac0d3-e0ea-4732-ba93-0277423b5029"
