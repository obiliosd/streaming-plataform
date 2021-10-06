# streaming-plataform
## Stack
Docker Nifi Kafka Hadoop Spark Cassandra

## Configure nifi-hadoop
### cd path to hadoop\hdfs project folder
cd D:\Trabajo\Workspace\Master\streaming-plataform\hadoop

### find container id namenode and nifi
docker ps

### copy namenode configuration to local
docker cp d172cbfb0b4b:etc/hadoop/hdfs-site.xml ./hdfs
docker cp d172cbfb0b4b:etc/hadoop/core-site.xml ./hdfs

### copy namenode configuration from local to nifi
docker cp ./hdfs b48acb33335f:/opt/nifi/nifi-current/conf

### create directory hadoop
hdfs dfs -mkdir /user
hdfs dfs -mkdir /user/data
hdfs dfs -mkdir /user/model

hadoop fs -chmod 777 /user
hadoop fs -chmod 777 /user/data
hadoop fs -chmod 777 /user/model

Borrar archivos:
hdfs dfs -rm -r /user/data/*