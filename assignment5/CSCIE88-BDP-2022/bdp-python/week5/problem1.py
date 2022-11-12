from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

ss = SparkSession.builder.appName("problem1").getOrCreate()

# Read avro files
df = ss.read.format("avro").load("logs_avro")

# Get the counts
counts = df.rdd\
    .map(lambda s: (s[1][0:13], s[2]))\
    .groupByKey()\
    .mapValues(lambda vals: len(set(vals)))\
    # .sortByKey()

print(counts.toDebugString().decode("utf-8"))

counts.saveAsTextFile("outputlab5p1")
