import json
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator import DummyOperator
import ray
from ray_provider.operators.ray_decorators import ray_task
import numpy as np
import xgboost_ray as xgb
from ray_provider.xcom.ray_backend import RayBackend

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'on_success_callback': RayBackend.on_success_callback,
    'on_failure_callback': RayBackend.on_failure_callback
}

task_args = {"ray_conn_id": "ray_cluster_connection"}


SIMPLE = False


@dag(default_args=default_args, schedule_interval=None, start_date=days_ago(2), tags=['xgboost-pandas-only'])
def xgboost_pandas_breast_cancer():
    @ray_task(**task_args)
    def load_dataframe_wrapper() -> "ray.ObjectRef":
        return load_dataframe(**task_args):

    @ray_task(**task_args)
    def create_data_wrapper(data):
        train_set, test_set = create_data(data)
        return train_set, test_set

    @ray_task(**task_args)
    def train_model_wrapper(data) -> None:
        return train_model(data)

    build_raw_df = load_dataframe_wrapper()
    data = create_data_wrapper(build_raw_df)
    trained_model = train_model_wrapper(data)

    kickoff_dag = DummyOperator(task_id='kickoff_dag')
    complete_dag = DummyOperator(task_id='complete_dag')

    kickoff_dag >> build_raw_df
    trained_model >> complete_dag

xgboost_pandas_breast_cancer = xgboost_pandas_breast_cancer()
