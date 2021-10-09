from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

#Need numpy
def get_spark_session(app_name: str) -> SparkSession:
    spark = SparkSession\
        .builder\
        .appName(app_name)\
        .master("spark://spark-master:7077")\
        .config("spark.executor.memory", "512m")\
        .getOrCreate()
    return spark

if __name__ == "__main__":
    spark = get_spark_session("kmeans")
    # $example on$
    # Loads data.
    dataset = spark.read.format("libsvm").load("spark/data/mllib/sample_kmeans_data.txt")

    # Trains a k-means model.
    kmeans = KMeans().setK(2).setSeed(1)
    model = kmeans.fit(dataset)

    # Make predictions
    predictions = model.transform(dataset)

    # Evaluate clustering by computing Silhouette score
    evaluator = ClusteringEvaluator()

    silhouette = evaluator.evaluate(predictions)
    print("Silhouette with squared euclidean distance = " + str(silhouette))

    # Shows the result.
    centers = model.clusterCenters()
    print("Cluster Centers: ")
    for center in centers:
        print(center)
    # $example off$

    dir = "hdfs://namenode:8020//user/model/model1"
    print("Save model in hdfs: " + dir)
    model.write().overwrite().save(dir)

    spark.stop()