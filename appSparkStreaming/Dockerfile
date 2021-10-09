FROM obiliosd/spark-python-template:3.1.1-hadoop3.2

COPY ./log/log4j.properties /spark/conf/log4j.properties

ENV SPARK_APPLICATION_PYTHON_LOCATION=/app/src/entrypoint.py
ENV SPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0 --conf spark.sql.extensions=com.datastax.spark.connector.CassandraSparkExtensions"