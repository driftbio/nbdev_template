FROM quay.io/astronomer/ap-airflow:2.0.2-1-buster
USER root
COPY requirements.txt .
COPY providers/ providers/
RUN pip install -r ./providers/requirements.txt
RUN pip install -e ./providers
RUN pip uninstall astronomer-airflow-version-check -y
USER astro
ENV AIRFLOW__CORE__XCOM_BACKEND=ray_provider.xcom.ray_backend.RayBackend