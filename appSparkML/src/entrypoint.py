#Need numpy install -> Use containers obiliosd/spark-python-template, obiliosd/spark-worker
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col, udf
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

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

if __name__ == "__main__":
    spark = get_spark_session("ml-kmeans")
    # Load data from hdfs
    df = getDataFromHdfs()

    # Split data into train/test
    splits = df.randomSplit([0.67, 0.33])
    df_spark_sql_train = splits[0]
    df_spark_sql_test = splits[1]
    print(df_spark_sql_train.count())
    print(df_spark_sql_test.count())

    # VectorAssembler -> We use UDF instead because array<double> is not supported
    list_to_vector_udf = udf(lambda vs: Vectors.dense(vs), VectorUDT())
    df_KMeans_train = df_spark_sql_train.select(list_to_vector_udf(col("coordinates")).alias("features"))
    df_KMeans_test = df_spark_sql_test.select(list_to_vector_udf(col("coordinates")).alias("features"))

   # Trains a k-means model.
    kmeans = KMeans().setK(5).setSeed(1)
    kmeans_model = kmeans.fit(df_KMeans_train.select("features"))

    # Make predictions
    predictions = kmeans_model.transform(df_KMeans_test)

    # Evaluate clustering by computing Silhouette score
    evaluator = ClusteringEvaluator()

    silhouette = evaluator.evaluate(predictions)
    print("Silhouette with squared euclidean distance = " + str(silhouette))

    # Shows the result.
    centers = kmeans_model.clusterCenters()
    print("Cluster Centers: ")
    for center in centers:
        print(center)
    
    

    # Save model into hdfs
    """
    dir = "hdfs://namenode:8020//user/model/model1"
    print("Save model in hdfs: " + dir)
    model.write().overwrite().save(dir)
    """

    spark.stop()