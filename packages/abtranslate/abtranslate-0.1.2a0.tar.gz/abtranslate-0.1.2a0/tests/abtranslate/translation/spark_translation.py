import os
import shutil

from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf
from pyspark import SparkFiles
from pyspark.sql.types import StringType
from pyspark.sql import dataframe as spark_df
import pandas as pd 
from zipfile import ZipFile

from abtranslate.translator.package import ArgosPackage, load_argostranslate_model
from abtranslate.utils.file_manager import extract_package

from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
from pyspark import SparkFiles

PACKAGES_PATH = "/tmp/abtranslate/packages/"
MODELS_PATH = "/tmp/abtranslate/model/"

# Pandas UDF
@pandas_udf(StringType())
def translate_column(column: pd.Series) -> pd.Series:
    package_path = SparkFiles.get("model.zip")  # pastikan yang ditambahkan namanya "model.zip"
    
    if not os.path.exists("/tmp/model_extracted"):
        import zipfile
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            zip_ref.extractall("/tmp/model_extracted")
    
    package = load_argostranslate_model(package_path)
    translator = package.load_translator(optimized_config=True)
    
    return pd.Series(translator.translate_batch(column.tolist()))


def translate_with_udf(model_path: str, spark_df: SparkDataFrame, input_column_name: str, output_column_name: str) -> SparkDataFrame:
    # Salin model zip ke lokasi kerja Spark
    if not os.path.exists(PACKAGES_PATH):
        os.makedirs(PACKAGES_PATH, exist_ok=True)
    
    dst_model_path = os.path.join(PACKAGES_PATH, "model.zip")
    shutil.copy(model_path, dst_model_path)

    spark = SparkSession.builder.getOrCreate()
    spark.sparkContext.addFile(dst_model_path)

    # Tambahkan kolom hasil translate
    df_translated = spark_df.withColumn(output_column_name, translate_column(input_column_name))
    return df_translated
