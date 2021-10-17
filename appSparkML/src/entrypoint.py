#Need numpy install -> Use containers obiliosd/spark-python-template, obiliosd/spark-worker
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col
from pyspark.mllib.clustering import KMeans, KMeansModel
import numpy as np

def get_spark_session(app_name: str) -> SparkSession:
    spark = SparkSession\
        .builder\
        .appName(app_name)\
        .master("spark://spark-master:7077")\
        .config("spark.executor.memory", "512m")\
        .getOrCreate()
    return spark

def getDataFromHdfs():
    print("read data..")
    hdfsPath = "hdfs://namenode:8020//user/data/location_2021_10/"
    hdfsFile = "delivery_person_06_185106.json"
    jsonSchema = StructType(
        [StructField("coordinates", ArrayType(DoubleType()), True),
        StructField("country", StringType(), True),
        StructField("key", IntegerType(), True),
        StructField("region", StringType(), True),
        StructField("timestamp", TimestampType(), True)])
    return spark.read.json(hdfsPath + hdfsFile, schema=jsonSchema)

def deleteHdfsDir(sc, hdfsUri, hdfsPath):
    #https://diogoalexandrefranco.github.io/interacting-with-hdfs-from-pyspark/
    ######
    # Get fs handler from java gateway
    ######
    URI = sc._gateway.jvm.java.net.URI
    Path = sc._gateway.jvm.org.apache.hadoop.fs.Path
    FileSystem = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
    fs = FileSystem.get(URI(hdfsUri), sc._jsc.hadoopConfiguration())
    fs.delete(Path(hdfsPath))

def saveModelHdfs(spark, model):
    sc = spark.sparkContext
    hdfsUri = "hdfs://namenode:8020"
    hdfsModelPath = "/user/model/kmeans"
    print("Save model in hdfs: " + hdfsModelPath)
    # Overwrite
    deleteHdfsDir(sc, hdfsUri, hdfsModelPath)
    model.save(sc, hdfsUri + hdfsModelPath)

if __name__ == "__main__":
    spark = get_spark_session("ml-kmeans")
    # Load data from hdfs
    df = getDataFromHdfs()
    # Convert to rdd
    rdd_data = df.select(col("coordinates")).rdd.map(lambda data: np.array(data).flatten())
    # Trains a k-means model.
    k=5
    initialModel = KMeansModel([
        (2.1893692016601562, 41.39174892980349),
        (2.167739868164062, 41.39432450769634),
        (2.1649932861328125, 41.399475357337565),
        (2.1392440795898433, 41.39664244054911),
        (2.1516036987304688, 41.390203534085344)])
    model = KMeans.train(rdd_data, k, maxIterations=0, initialModel=initialModel)
    # Result
    print("Final centers: " + str(model.clusterCenters))
    print("Total Cost: " + str(model.computeCost(rdd_data)))
    # Save model into hdfs
    saveModelHdfs(spark, model)
    spark.stop()