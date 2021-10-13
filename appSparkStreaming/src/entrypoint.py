from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import from_json 

def get_spark_session(app_name: str) -> SparkSession:
    spark = SparkSession\
        .builder\
        .appName(app_name)\
        .master("spark://spark-master:7077")\
        .config("spark.executor.memory", "512m")\
        .getOrCreate()
    return spark

def run_spark_kafka_structure_stream(spark: SparkSession) -> None:
    jsonSchema = StructType(
        [StructField("coordinates", ArrayType(DoubleType()), True),
        StructField("country", StringType(), True),
        StructField("key", IntegerType(), True),
        StructField("region", StringType(), True),
        StructField("timestamp", TimestampType(), True)])
    #Kafka conexion
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "broker:29092") \
        .option("subscribe", "raiderLocation") \
        .option("kafka.request.timeout.ms", "60000") \
        .option("kafka.session.timeout.ms", "30000") \
        .option("failOnDataLoss", "true") \
        .option("startingOffsets", "latest") \
        .load()
    words = df.selectExpr('CAST(value AS STRING)') \
        .select(from_json("value", jsonSchema).alias("value")) \
        .select("value.country")
    
    # Generate running word count
    wordCounts = words.groupBy("country").count()

     # Start running the query that prints the running counts to the console
    query = wordCounts \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

    query.awaitTermination()

    # run
    #writer = df.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()

if __name__ == "__main__":
    spark = get_spark_session("Stream-kafka")
    print("test")
    run_spark_kafka_structure_stream(spark)
    spark.stop()