from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
import functools
import re
import logging
from logging import Logger
from unittest.mock import Mock
import copy

class DataTest:
    def __init__(self, colname, test, scope, partial, tolerance=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
        assert tolerance >= 0.0 and tolerance <= 1.0, f"tolerance must be between 0.0 and 1.0 inclusive. Current value is {tolerance}"
        assert over_under_tolerance in ['over','under'], f"over_under_tolerance not in ['over','under']. Current value is {over_under_tolerance}"
        assert inclusive_exclusive in ['inclusive', 'exclusive'], f"inclusive_exclusive must be in ['inclusive', 'exclusive']. Current value is {inclusive_exclusive}"
        self._colname = colname
        self._test = test
        self._scope = str(scope)
        self._partial = partial
        self._tolerance = float(tolerance)
        self._over_under_tolerance = over_under_tolerance
        self._inclusive_exclusive = inclusive_exclusive

    def get_pyspark_row_struct(self):
        return f.struct(f.lit(self.colname).alias('colname'),
                        f.lit(self.test).alias('test'),
                        f.lit(self.scope).alias('scope'),
                        self.partial.alias('pass'),
                        )
    def __eq__(self, other: object) -> bool:
        return (
            self.colname == other.colname and
            self.test == other.test and
            self.scope == other.scope and
            str(self.partial) == str(other.partial) and
            self.tolerance == other.tolerance and
            self.over_under_tolerance == other.over_under_tolerance and
            self.inclusive_exclusive == other.inclusive_exclusive
        )
    
    def __repr__(self):
        return f"""{{ test: {self._test}, col: {self._colname}, partial: {self._partial}, 
        tolerance: {self._tolerance}, over_under_tolerance: {self._over_under_tolerance}, 
        inclusive_exclusive: {self._inclusive_exclusive} }} """
    
    @property
    def colname(self):
        return self._colname
    @property
    def test(self):
        return self._test
    @property
    def scope(self):
        return self._scope
    @property
    def partial(self):
        return self._partial
    @property
    def tolerance(self):
        return self._tolerance
    @property
    def over_under_tolerance(self):
        return self._over_under_tolerance
    @property
    def inclusive_exclusive(self):
        return self._inclusive_exclusive
    
class PySparkDQ:
  
  class PysparkDQFailedTestException(Exception):
        def __init__(self, message):
            super().__init__(message)
            
  def __init__(self, spark_session:SparkSession, df:SparkDataFrame, warning_rows:int=1_000_000, logger:Logger=None, df_test_results=None, data_tests=None):
    """
    spark_session : SparkSession
        Spark session to be used
    df : SparkDataFrame
        Spark Dataframe to evaluate
    warning_rows (optional): int
        Class will display a warning log if class has more than this amount of rows.
    logger (optional): None | Logger
        Whether to use logging library of print statements. Defaults to None.
    """
    self._spark_session = spark_session

    self._logging = Mock() if logger is None else logger # Mock the logger if none is supplied
    self._warning_rows = warning_rows
    self._df = df
    self._df_count = None
    self._result_schema = 'colname:string,test:string,scope:string,found:int,total:int,found_percentage:double,tolerance:double,over_under_tolerance:string,inclusive_exclusive:string,pass:boolean'
    self._df_test_results = self._spark_session.createDataFrame([], self._result_schema)
    self._data_tests = [] if data_tests is None else data_tests
    self._df_test_results = self._spark_session.createDataFrame(data=[], schema=self._result_schema) if df_test_results is None else df_test_results

  ## ---------------- Native dq evaluations --------------------- ##

  def values_in_list(self, colname:str, val_list:list, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values in list, same as c.isIn(val_list). Defaults to all values must satisfy the condition inclusive on tolerance. 
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    val_list : list(any)
        List of values to check. Must match column datatype. 
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_in_list(colname="my_col",
    |                      value_list=[1,2,3,4],
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_in_list"
    scope = val_list
    partial = f.col(colname).isin(val_list)
    
    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)

  def values_not_in_list(self, colname:str, val_list:list, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values not in list, same as ~c.isIn(val_list). Defaults to all values must satisfy the condition inclusive on tolerance. 
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    value_list : list(any)
        List of values to check. Must match column datatype. 
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_not_in_list(colname="my_col",
    |                      value_list=[1,2,3,4],
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_not_in_list"
    scope = val_list
    partial = ~f.col(colname).isin(val_list)

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)
    
    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)
  
  def values_null(self, colname:str, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for Null values, same as c.isNull(). Defaults to all values must satisfy the conditioninclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_null(colname="my_col",
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_null"
    scope = 'null'
    partial = f.col(colname).isNull()

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)
  
  def values_not_null(self, colname:str, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for Not Null values, same as c.isNotNull(). Defaults to all values must satisfy the condition inclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'
  
    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_not_null(colname="my_col",
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_not_null"
    scope = 'null'
    partial = f.col(colname).isNotNull()

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)

  def values_equal(self, colname:str, value, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values equal to value, same as c == value. Defaults to all values must satisfy the condition inclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    value: string, int, float, column
        Reference value to compare
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_equal(colname="my_col",
    |                      value=10,
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_equal"
    scope = value
    partial = f.col(colname)==scope

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)
  
  def values_not_equal(self, colname:str, value, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values equal to value, same as c == value. Defaults to all values must satisfy the condition inclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    value: string, int, float, column
        Reference value to compare
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_not_equal(colname="my_col",
    |                      value=10,
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_not_equal"
    scope = value
    partial = f.col(colname)!=scope

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)

  def values_between(self, colname:str, lower_value, upper_value, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values between boundaries, same as c.between(lower, upper). Defaults to all values must satisfy the condition inclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    lower_value: string, int, float, column
        Lower reference to compare
    upper_value: string, int, float, column
        Upper reference to compare
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_between(colname="my_col",
    |                      lower_value=10,
    |                      upper_value=20,
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_between"
    scope = f"{lower_value} - {upper_value}"
    partial = f.col(colname).between(lower_value,upper_value)
    
    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)

  def values_greater_equal_than(self, colname:str, value, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values greater equal than the reference value, same as c >= value. Defaults to all values must satisfy the condition inclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    value: string, int, float, column
        Reference value to compare
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_lower_equal_than(colname="my_col",
    |                      value=10,
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_greater_equal_than"
    scope = value
    partial = f.col(colname) >= value

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)

  def values_lower_equal_than(self, colname:str, value, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values lower equal than the reference value, same as c <= value. Defaults to all values must satisfy the condition inclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    value: string, int, float, column
        Reference value to compare
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_lower_equal_than(colname="my_col",
    |                      value=10,
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_lower_equal_than"
    scope = value
    partial = f.col(colname) <= value

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)

  def values_greater_than(self, colname:str, value, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values greater than the reference value, same as c <= value. Defaults to all values must satisfy the condition inclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    value: string, int, float, column
        Reference value to compare
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_greater_than(colname="my_col",
    |                      value=10,
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()
  
    Returns
    -------
    None
    """
    test = "values_greater_than"
    scope = value
    partial = f.col(colname) > value

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)
  
  def values_lower_than(self, colname:str, value, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Test column for values lower than the reference value, same as c <= value. Defaults to all values must satisfy the condition inclusive on tolerance.
    If there's a different tolerance that the default one, adjust the parameters: tolerance, over_under_tolerance, inclusive_exclusive

    Parameters
    ----------
    colname : string
        Column name to evaluate.
    value: string, int, float, column
        Reference value to compare
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_lower_than(colname="my_col",
    |                      value=10,
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    test = "values_lower_than"
    scope = value
    partial = f.col(colname) > value

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)
  
  def values_custom_dq(self, test, partial, scope=None, tolerance:float=1.0, over_under_tolerance='over', inclusive_exclusive='inclusive'):
    """
    Adds a custom data quality check. The only requiremets for the partial argument expressions is that it's written in terms of
    pyspark columns or spark sql expressions and resolves into a boolean column

    Parameters
    ----------
    test : string
        Test name to use. 
    partial: column
        Column expression that defines the test.
    scope (optional): string
        If you want to manually add your scope to identify this test feel free to do so. Defaults to the partial used on the test.
    tolerance (optional): float
        Tolerance threshold for test evaluation. ranges from 0.0 to 1.0. Defaults to 1.0.
    over_under_tolerance (optional): string
        Evaluates threshold success checking if matching records are over or under it. Options are 'over', 'under'. Defaults to 'over'.
    inclusive_exclusive (optional): string
        Whether it should consider results inclusive or exclusive on the threshold. Options are 'inclusive', 'exclusive'. Defaults to 'inclusive'

    Examples
    -------
    |  dq = PySparkDQ(...) 
    |  dq.values_custom_dq(test="My Custom Test",
    |                      partial=expr("my_date_col = '2024-12-01' and my_numeric_col between 10 and 50"),
    |                      tolerance=0.8,
    |                      over_under_tolerance='under',
    |                      inclusive_exclusive='inclusive')
    |            .evaluate()

    Returns
    -------
    None
    """
    scope = scope if scope is not None else str(partial)
    colname = "N/A"

    data_test = DataTest(colname, test, scope, partial, tolerance, over_under_tolerance, inclusive_exclusive)

    new_test_list = []
    new_test_list.extend(self._data_tests)
    new_test_list.append(data_test)
    self._add_to_summary_report(data_test)

    return PySparkDQ(spark_session=self._spark_session,df=self._df,logger=self._logging,df_test_results=self._df_test_results,data_tests=new_test_list, warning_rows=self._warning_rows)
  
  ## ----------------------- User Main Functions ----------------------- ##

  def get_summary(self, cache_result=True) -> SparkDataFrame:
    """
    Evaluates all tests and returns a SparkDataFrame with the test summaries.

    Parameters
    ----------
    cache_result (optional): boolean
        Option to cache the result or not. Defaults to True.

    Examples
    -------
    |  dq = PySparkDQ(...)
    |  
    |  df_summary=dq.values_custom_dq(test="My Custom Test 2",
    |  partial=( (col('my_float_col') >= 250.9) & (col('my_bool_col') == False))
    |  .get_summary()

    Returns
    -------
    SparkDataFrame
    """
    self._calculate_test_results()

    if cache_result:
        self._df_test_results = self._df_test_results.cache()
    
    return self._df_test_results

  def get_row_level_qa(self) -> SparkDataFrame:
    """
    Evaluates all tests row-by-row and returns the initial dataframe with extra columns for test results.

    Parameters
    ----------
    None

    Examples
    -------
    |  dq = PySparkDQ(...)
    |  dq.custom_dq(test="My Custom Test",
    |                      partial=expr("my_date_col = '2024-12-01 and my_numeric_col between 10 and 50")
    |                      tolerance=0.8,
    |                      over_under_tolerance='under'
    |                      inclusive_exclusive='inclusive') \
    |            .custom_dq(test="My Custom Test 2", 
    |                      partial=( (col('my_float_col') >= 250.9) & (col('my_bool_col') == False)
    |                      )
    |            .get_row_level_qa()

    Returns
    -------
    SparkDataFrame
    """
    assert len(self._data_tests) > 0, "No tests to run. Make sure to add qa tests before calling this function."
    self._df_row_level_qa = self._df.withColumn(f"pysparkdq", f.array([x.get_pyspark_row_struct() for x in self._data_tests]))\
                .withColumn('pysparkdq_fail_count', f.size(
                    f.filter('pysparkdq', lambda x: x.getField('pass')==False))) \
                .withColumn('pysparkdq_failed_tests', f.transform(
                    f.filter('pysparkdq', lambda x: x.getField('pass')==False), 
                    lambda y: y.dropFields('pass')
                )).drop('pysparkdq')
    return self._df_row_level_qa
      
  def evaluate(self) -> None:
    """
    Evaluates the test summary and throws an exception if anything fails.

    Parameters
    ----------
    None

    Examples
    -------
    |  dq = PySparkDQ(...)
    |  dq.custom_dq(test="My Custom Test",
    |                      partial=expr("my_date_col = '2024-12-01 and my_numeric_col between 10 and 50")
    |                      tolerance=0.8,
    |                      over_under_tolerance='under'
    |                      inclusive_exclusive='inclusive') \
    |            .custom_dq(test="My Custom Test 2", 
    |                      partial=( (col('my_float_col') >= 250.9) & (col('my_bool_col') == False)
    |                      )
    |            .evaluate()

    Returns
    -------
    SparkDataFrame
    """
    self._calculate_test_results()
    if self._df_test_results.isEmpty():
        self._logging.info("No test summary found. Make sure to run X function to generate the summary")
        return
    elif not self._df_test_results.filter('pass = false').isEmpty():
        failed_tests=self._df_test_results.filter('pass = false')
        cnt = failed_tests.count()
        which = [{'colname': x['colname'], 'test': x['test'], 'scope': x['scope']} for x in failed_tests.select('colname','test','scope').collect()]
        if not self._df_test_results.filter('pass = false').isEmpty(): raise self.PysparkDQFailedTestException(f"Detected failed tests. Count: {cnt}, Tests: {which}")
    else:
        self._logging.info("All tests passed")

  ## ------------------------------ Internal functions ---------------------- ##

  def _calculate_test_results(self) -> None:
    self._count_records() # As this function depends on total record count we have to add this at the beginning.
    
    percentage_tolerance = f.when(f.col('over_under_tolerance') == 'over', 
                                    f.when(f.col('inclusive_exclusive') == 'inclusive', f.col('found_percentage')>=f.col('tolerance')).otherwise(f.col('found_percentage')>f.col('tolerance'))
                                  ).otherwise(
                                     f.when(f.col('inclusive_exclusive') == 'inclusive', f.col('found_percentage')<=f.lit(f.col('tolerance'))).otherwise(f.col('found_percentage')<f.lit(f.col('tolerance')))
                                  )
    
    self._df_test_results = self._df_test_results.withColumn('total', f.when(f.col('total').isNull(),f.lit(self._df_count)).otherwise(f.col('total')))\
                            .withColumn('found_percentage', f.round(f.col('found')/f.lit(self._df_count),8).alias('found_percentage')) \
                            .withColumn('pass',percentage_tolerance)

  def _count_records(self):
    if self._df_count == None:
      self._logging.info("Counting total records for evaluation...")
      self._df_count = self._df.count()

    if int(self._df_count) > self._warning_rows:
      self._logging.warning(f"Large number of rows detected ({self._df_count}), be aware that large datasets will take longer to compute. Consider sampling the dataframe before initializing this class")

  def _add_test_to_queue(self, data_test) -> bool:
    try:
        over_under_str = 'at least' if data_test.over_under_tolerance == 'over' else 'up until'
        self._logging.info(f"Checking {data_test.test} for {data_test.colname} - {over_under_str} {round(100*data_test.tolerance,4)}% of total rows")
        self._data_tests.append(data_test)
        return True
    except Exception as e:
       self._logging.error(f"Error adding test: {data_test}, error: {e}")
       return False
                                  
  def _add_to_summary_report(self, data_test:DataTest):
    # Setting summary report row for this test
    self._df_test_results = self._df_test_results.unionByName(
                            self._df.filter(data_test.partial).select(
                            f.lit(data_test.colname).alias('colname'),
                            f.lit(data_test.test).alias('test'),
                            f.lit(data_test.scope).alias('scope'),
                            f.sum(f.when(data_test.partial,1).otherwise(0)).alias("found"),
                            f.lit(self._df_count).alias("total"),
                            f.round(f.col('found')/f.lit(self._df_count),8).alias('found_percentage'),
                            f.lit(data_test.tolerance).alias('tolerance'),
                            f.lit(data_test.over_under_tolerance).alias('over_under_tolerance'),
                            f.lit(data_test.inclusive_exclusive).alias('inclusive_exclusive'),
                            f.lit(None).alias("pass")
                            ))
    
  def __repr__(self):
    return f"PysparkDQ Test Suite - {self._data_tests}"
  
  def __str__(self):
    return f"Spark Data Quality Tool - Checks for enhanced data quality !"