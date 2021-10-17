from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import from_json, struct, to_json, lit, udf
from pyspark.mllib.clustering import KMeansModel
import numpy as np

# **********************************************************************
# **********************************************************************
# **********************************************************************

def get_spark_session(app_name: str) -> SparkSession:
    return SparkSession\
        .builder\
        .appName(app_name)\
        .master("spark://spark-master:7077")\
        .config("spark.executor.memory", "512m")\
        .config("spark.cassandra.connection.host", "cassandra")\
        .getOrCreate()

def loadModel(spark: SparkSession) -> KMeansModel:
    sc = spark.sparkContext
    hdfsUri = "hdfs://namenode:8020"
    hdfsModelPath = "/user/model/kmeans"
    return KMeansModel.load(sc, hdfsUri + hdfsModelPath)

def getJsonSchema() -> StructType:
    return StructType(
        [StructField("coordinates", ArrayType(DoubleType()), True),
        StructField("country", StringType(), True),
        StructField("key", IntegerType(), True),
        StructField("region", StringType(), True),
        StructField("timestamp", TimestampType(), True)])

spark = get_spark_session("stream-kafka-cassandra")
jsonSchema = getJsonSchema()
model = loadModel(spark)
udfModelPredict = udf(lambda x: model.predict(np.array(x).flatten()), returnType=IntegerType())


# Kafka Connection information
bootstrap_servers = "broker:29092"
# Topic we will consume from
topic = "raiderLocation"
# Topic we will write to
topic_to = "raiderLocation-clustered"


# **********************************************************************
# **********************************************************************
# **********************************************************************

def readDataFromKafka(spark: SparkSession):
    return spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrap_servers) \
        .option("subscribe", topic) \
        .option("kafka.request.timeout.ms", "60000") \
        .option("kafka.session.timeout.ms", "30000") \
        .option("failOnDataLoss", "true") \
        .option("startingOffsets", "latest") \
        .load()

def writeDataToKafka(df):
    dfwrite = df.select(to_json(struct("*")).alias("value")).withColumn("key",lit(None).cast(StringType()))
    dfwrite.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .write \
        .format("kafka") \
        .option("topic", topic_to) \
        .option("kafka.bootstrap.servers", bootstrap_servers) \
        .save()

def writeDataToCassandra(df):
    keys_space_name = "sparkstreaming"
    table_name = "raiders"
    dfwrite = df.withColumnRenamed("key","identifier") \
                .withColumnRenamed("timestamp","coordinatestime")
    dfwrite.write\
        .format("org.apache.spark.sql.cassandra")\
        .mode('append')\
        .options(table=table_name, keyspace=keys_space_name)\
        .save()

def foreach_batch_function(df, epoch_id):
    # Transform and write batchDF
    if df.count() <= 0:
        None
    else:
        # https://spark.apache.org/docs/3.1.1/structured-streaming-programming-guide.html#foreachbatch
        # Using Foreach and ForeachBatch
        # Write to multiple locations - If you want to write the output of a streaming query to multiple locations, 
        # then you can simply write the output DataFrame/Dataset multiple times. 
        # However, each attempt to write can cause the output data to be recomputed 
        # (including possible re-reading of the input data). To avoid recomputations, 
        # you should cache the output DataFrame/Dataset, write it to multiple locations, 
        # and then uncache it. Here is an outline.
        df.persist()
        # Select columns
        df = df.selectExpr('CAST(value AS STRING)') \
            .select(from_json("value", jsonSchema).alias("value")) \
            .select("value.*")
        # Train data whit kmeans model from hdfs
        df = df.withColumn("prediction", udfModelPredict("coordinates"))
        # Save data into Cassandra
        writeDataToCassandra(df)
        # Send data to kafka
        writeDataToKafka(df)
        df.unpersist()

if __name__ == "__main__":
    streamData = readDataFromKafka(spark)
    streamData.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()
    spark.stop()
