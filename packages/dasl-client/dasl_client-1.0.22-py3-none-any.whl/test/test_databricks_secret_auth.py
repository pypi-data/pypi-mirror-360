import base64
import datetime
import os
import time

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs, workspace as dbworkspace

from .constants import *

pylib_volume_path = os.environ["PYLIB_VOLUME_PATH"]
pylib_wheel_path = os.environ["PYLIB_WHEEL_PATH"]


def test_secret_auth(api_client):
    # making sure it's even possible to get a config
    api_client.get_config()

    # need to do an API operation using databricks secret auth.
    notebook_data = f"""
    %pip install {pylib_wheel_path}
    dbutils.library.restartPython()
    # COMMAND ----------
    from dasl_client.client import Client

    Client.for_workspace(
        workspace_url="{databricks_host}",
        dasl_host="{dasl_host}",
    ).get_config()
    # COMMAND ----------
    dbutils.notebook.exit("SUCCESS")
    """
    print(f"notebook_data={notebook_data}")

    wsc = WorkspaceClient()
    wsc.workspace.mkdirs(path=pylib_volume_path)

    notebook_path = f"{pylib_volume_path}/test_secret_auth_notebook"
    wsc.workspace.import_(
        path=notebook_path,
        format=dbworkspace.ImportFormat.SOURCE,
        language=dbworkspace.Language.PYTHON,
        content=base64.b64encode(notebook_data.encode("utf-8")).decode("utf-8"),
        overwrite=True,
    )

    job_id = None
    try:
        job_id = wsc.jobs.create(
            name="run test_secret_auth notebook",
            tasks=[
                jobs.Task(
                    task_key="run_notebook",
                    notebook_task=jobs.NotebookTask(notebook_path=notebook_path),
                ),
            ],
        ).job_id

        wsc.jobs.run_now(job_id=job_id)

        logs = []
        start = datetime.datetime.now()
        complete = False
        while not complete:
            elapsed = datetime.datetime.now() - start
            if elapsed > datetime.timedelta(seconds=300):
                raise Exception(f"timed out waiting for job")

            time.sleep(5)

            status, logs = fetch_latest_run_status_and_logs(wsc, job_id)
            print(f"logs={logs}")

            if status == jobs.TerminationCodeCode.RUN_EXECUTION_ERROR:
                raise Exception(f"job terminated with error")

            complete = status == jobs.TerminationCodeCode.SUCCESS

        print(logs)
        assert len(logs) == 1
        assert logs[0] == "SUCCESS"
    finally:
        wsc.workspace.delete(pylib_volume_path, recursive=True)
        if job_id is not None:
            wsc.jobs.delete(job_id=job_id)


def fetch_latest_run_status_and_logs(
    wsc: WorkspaceClient,
    job_id: str,
):
    runs = list(wsc.jobs.list_runs(job_id=job_id, expand_tasks=True))
    if not runs:
        return "No runs found", None

    # Find the latest run based on the start time
    latest_run = max(runs, key=lambda r: r.start_time)
    if latest_run.status.termination_details is None:
        return "No runs found", None
    status = latest_run.status.termination_details.code
    logs = []
    for task in latest_run.tasks:
        output = wsc.jobs.get_run_output(task.run_id)
        if output.error is not None:
            logs.append(output.error)
        elif output.logs is not None:
            logs.append(output.logs)
        elif output.notebook_output is not None:
            logs.append(output.notebook_output.result)
        elif output.run_job_output is not None:
            raise Exception("Nested jobs are not supported")
        elif output.sql_output is not None:
            raise Exception("SQL jobs are unsupported")
        else:
            logs.append("")
    return status, logs
