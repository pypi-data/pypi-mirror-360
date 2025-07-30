import pytest
from pyspark.testing.utils import assertDataFrameEqual
from psdq import PySparkDQ
import pyspark.sql.functions as f

def test_values_in_list(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_in_list(colname='age',val_list=[30,25,35],tolerance=0.75, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_not_in_list(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_not_in_list(colname='age',val_list=[1,2,3],tolerance=1, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_null(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_null(colname='age', tolerance=0, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_not_null(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_not_null(colname='age', tolerance=1, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_equal(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_equal(colname='age', value=30, tolerance=0.25, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_not_equal(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_not_equal(colname='age', value=28, tolerance=0.75, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_between(spark_session_fixture, sample_data_name_age, sample_data_name_date):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)
    dq.values_between(colname='age', lower_value=30, upper_value=35, tolerance=0.501, over_under_tolerance='under', inclusive_exclusive='exclusive').evaluate()
    
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_date)
    dq.values_between(colname='birthday', lower_value='1990-01-01', upper_value='1993-01-01', tolerance=0.5, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_greater_equal_than(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_greater_equal_than(colname='age', value=30, tolerance=0.501, over_under_tolerance='under', inclusive_exclusive='exclusive').evaluate()

def test_values_lower_equal_than(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_lower_equal_than(colname='age', value=30, tolerance=0.75, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_greater_than(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_greater_than(colname='age', value=30, tolerance=0.25, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_lower_than(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_lower_than(colname='age', value=30, tolerance=0.75, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_custom_dq(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_custom_dq(test='custom dq', partial=f.lower('name')=='john',
                                tolerance=0.25, over_under_tolerance='over').evaluate()

