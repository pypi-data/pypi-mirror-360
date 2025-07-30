import pandas as pd
import pytest

from pyspark.sql import SparkSession 

from abtranslate.translator.package import load_argostranslate_model
from abtranslate.translator.argos_translator import ArgosTranslator
from abtranslate.translation.spark_translation import translate_with_udf

model_path = "./tests/example/model_data.argosmodel"
package = load_argostranslate_model(model_path)
sample_dataset_path = "./tests/example/aircraft_defects_chinese.csv"
test_df = pd.read_csv(sample_dataset_path) 
translator = package.load_translator(optimized_config=True)

sample_text_zh = """发动机左侧在飞行前检查中发现有轻微的机油渗漏。技术人员确认渗漏区域位于涡轮壳体附近，并进行了初步清洁。随后安排进一步的检查以确定是否需要更换密封件。

在机务人员建议下，更换了左侧发动机的油封并重新紧固相关组件。完成维护后进行了地面试车，未再发现新的渗漏现象。飞机恢复运行状态，记录保留供后续检查使用。"""

# @pytest.fixture
# def argos_translator() -> ArgosTranslator:
#     package = load_argostranslate_model("./model_sample/model_data.argosmodel")
#     return package.load_translator()

def test_translation():
    translation = translator.translate(sample_text_zh)
    print("Translation result: ", translation)

def test_batch_translation():
    input_column = test_df["input-text"]
    translated_column = translator.translate_batch(input_column)
    print("Df translaton results: ", translated_column)

def test_udf_translation():
    spark = SparkSession.builder.getOrCreate()
    df = spark.read.csv(sample_dataset_path, header=True)
    df_translated = translate_with_udf(model_path, df, input_column_name="input-text", output_column_name="translated_text")
    df_translated.select("translated_text").show(truncate=False)
