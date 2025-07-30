import os
from datetime import datetime

import fsspec
import httpx
from jinja2 import Template

"""
    A manager to dynamically generate, save, and upload Airflow DAGs via SSH using fsspec.
    """
DAG_TEMPLATE = """
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from {{ wrapper_module_path }} import DataUpdateWrapper
{% for module_path, classes in wrapped_classes.items() %}
{% for class_name in classes %}
from {{ module_path }} import {{ class_name }}
{% endfor %}
{% endfor %}

wrapped_classes = {
    {% for group, items in wrapped_classes.items() %}
    '{{ group }}': [{% for class_name in items %}{{ class_name }}, {% endfor %}],
    {% endfor %}
}

def update_data(group_name, params):
    wrapper = DataUpdateWrapper(wrapped_classes)
    wrapper.update_data(group_name, **params)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    '{{ dag_id }}',
    default_args=default_args,
    description='{{ description }}',
    schedule_interval='{{ schedule_interval }}',
    start_date=datetime({{ start_year }}, {{ start_month }}, {{ start_day }}),
    catchup=False,
) as dag:
    {% for group in groups %}
    PythonOperator(
        task_id='{{ group }}_update',
        python_callable=update_data,
        op_kwargs={'group_name': '{{ group }}', 'params': {{ params }}},
    )
    {% endfor %}
"""


class AirflowDAGManager:

    def __init__(self, output_dir, remote_dags_path, ssh_host, ssh_user, ssh_password, url, auth, wrapper_module_path):
        """
        Initialize the Airflow DAG Manager.

        Args:
            output_dir (str): Local directory to save generated DAGs.
            remote_dags_path (str): Path to the Airflow `dags` folder on the remote server.
            ssh_host (str): Hostname or IP of the remote server.
            ssh_user (str): SSH username for the remote server.
            ssh_password (str): SSH password for the remote server.
            wrapper_module_path (str): Path to the `DataUpdateWrapper` module.
        """
        self.output_dir = output_dir
        self.remote_dags_path = remote_dags_path
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.url = url
        self.wrapper_module_path = wrapper_module_path
        self.auth = auth

        os.makedirs(self.output_dir, exist_ok=True)

    def generate_dag(self, dag_id, description, schedule_interval, wrapped_classes, groups, params):
        """
        Generate an Airflow DAG script from the provided template.

        Args:
            dag_id (str): Unique DAG ID.
            description (str): Description of the DAG.
            schedule_interval (str): Cron schedule for the DAG.
            wrapped_classes (dict): Classes grouped by functionality.
            groups (list): List of groups to include as tasks.
            params (dict): Parameters for the `update_data` function.

        Returns:
            str: Path to the generated DAG file.
        """
        module_classes = {}
        for group, classes in wrapped_classes.items():
            for cls in classes:
                module_path, class_name = cls.__module__, cls.__name__
                if module_path not in module_classes:
                    module_classes[module_path] = []
                module_classes[module_path].append(class_name)

        template = Template(DAG_TEMPLATE)
        dag_script = template.render(
            dag_id=dag_id,
            description=description,
            schedule_interval=schedule_interval,
            start_year=datetime.now().year,
            start_month=datetime.now().month,
            start_day=datetime.now().day,
            wrapper_module_path=self.wrapper_module_path,
            wrapped_classes=module_classes,
            groups=groups,
            params=params,
        )

        file_path = os.path.join(self.output_dir, f"{dag_id}.py")
        with open(file_path, "w") as f:
            f.write(dag_script)

        print(f"DAG for {dag_id} created at: {file_path}")
        return file_path

    def upload_dag(self, local_file, subdirectory=None):
        """
        Upload a DAG file to the Airflow server using SSH.

        Args:
            local_file (str): Path to the local DAG file.
            subdirectory (str, optional): Subdirectory within the Airflow `dags` folder.
        """
        try:
            # Destination path on the remote server
            remote_path = os.path.join(self.remote_dags_path, subdirectory) if subdirectory else self.remote_dags_path

            # Ensure subdirectory exists
            fs = fsspec.filesystem(
                "ssh",
                host=self.ssh_host,
                username=self.ssh_user,
                password=self.ssh_password,
            )
            fs.makedirs(remote_path, exist_ok=True)

            # Upload the DAG file
            remote_file_path = os.path.join(remote_path, os.path.basename(local_file))
            with open(local_file, "rb") as f, fs.open(remote_file_path, "wb") as remote_f:
                remote_f.write(f.read())

            print(f"Uploaded {local_file} to {remote_file_path}")
        except Exception as e:
            print(f"Failed to upload DAG: {e}")
            raise

    def manage_dags(self, wrapped_classes, schedule_interval, description, params, subdirectory=None):
        """
        Generate, upload, and manage Airflow DAGs for all groups in wrapped_classes.

        Args:
            wrapped_classes (dict): Dictionary of groups and their corresponding classes.
            schedule_interval (str): Cron schedule for the DAGs.
            description (str): Description for the DAGs.
            params (dict): Parameters for the `update_data` function.
            subdirectory (str, optional): Subdirectory within the Airflow `dags` folder.
        """
        groups = list(wrapped_classes.keys())
        dag_id = "daily_data_update"

        print("Generating DAG...")
        dag_file = self.generate_dag(
            dag_id=dag_id,
            description=description,
            schedule_interval=schedule_interval,
            wrapped_classes=wrapped_classes,
            groups=groups,
            params=params,
        )

        print("Uploading DAG to Airflow server...")
        self.upload_dag(dag_file, subdirectory)

        print("DAG management completed successfully.")

    def trigger_dag(self, dag_id, run_id=None, conf=None):
        """
        Trigger a DAG via Airflow's REST API.

        Args:
            dag_id (str): ID of the DAG to trigger.
            run_id (str, optional): Custom run ID for the DAG run.
            conf (dict, optional): Additional parameters for the DAG run.

        Returns:
            dict: Response from Airflow.
        """
        url = f"{self.url}/api/v1/dags/{dag_id}/dagRuns"
        payload = {
            "dag_run_id": run_id or f"manual_{datetime.now().isoformat()}",
            "conf": conf or {}
        }
        try:
            response = httpx.post(url, json=payload, auth=self.auth)
            response.raise_for_status()
            print(f"DAG {dag_id} triggered successfully.")
            return response.json()
        except httpx.RequestError as e:
            print(f"Failed to trigger DAG {dag_id}: {e}")
            raise
