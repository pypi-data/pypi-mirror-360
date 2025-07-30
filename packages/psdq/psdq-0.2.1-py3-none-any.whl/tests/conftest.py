import pytest
from pyspark.sql import SparkSession
import pyspark.sql.functions as f

@pytest.fixture(scope="session")
def spark_session_fixture():
    spark = SparkSession.builder.appName("Testing PySpark Example").getOrCreate()
    yield spark

@pytest.fixture(scope="session")
def sample_data_name_age(spark_session_fixture):
    return spark_session_fixture.createDataFrame([
                    {"name": "John", "age": 30},
                    {"name": "Alice", "age": 25},
                    {"name": "Bob", "age": 35},
                    {"name": "Eve", "age": 28}])

@pytest.fixture(scope="session")
def sample_data_name_date(spark_session_fixture):
    return spark_session_fixture.createDataFrame([
                    {"name": "Alex", "birthday": '1992-03-31'},
                    {"name": "Alice", "birthday": '1990-12-15'},
                    {"name": "Bob", "birthday": '1985-06-12'},
                    {"name": "Eve", "birthday": '1964-07-22'}]) \
                    .withColumn('birthday', f.col('birthday').cast('date'))