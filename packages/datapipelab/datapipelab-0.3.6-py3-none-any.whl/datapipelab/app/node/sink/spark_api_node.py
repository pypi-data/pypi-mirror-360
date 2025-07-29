from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger


class SparkApiSourceNode(TNode):
    def __init__(self, spark, tnode_config, df):
        from pyspark.sql import DataFrame
        super().__init__(spark=spark)
        self.df = df
        self.__load_options(tnode_config)

    def __load_options(self, tnode_config):
        self.spark_options = tnode_config.get('options', {})
        self.options = {}
        if 'format' in self.spark_options:
            self.format = self.spark_options.get('format')
        if 'mode' in self.spark_options:
            self.mode = self.spark_options.get('mode')
        if 'parent_project' in self.spark_options:
            self.options['parentProject'] = self.spark_options.get('parent_project')
        if 'table' in self.spark_options:
            self.options['table'] = self.spark_options.get('table')
        if 'write_method' in self.spark_options:
            self.options['writeMethod'] = self.spark_options.get('write_method')
        if 'temporary_gcs_bucket' in self.spark_options:
            self.options['temporaryGcsBucket'] = self.spark_options.get('temporary_gcs_bucket')

    def __write_df(self):
        writer = self.df.write
        if self.format:
            writer = writer.format(self.format)
        for key, value in self.options.items():
            if value:
                writer = writer.option(key, value)
        if self.mode:
            writer = writer.mode(self.mode)
        writer.save()

    def _process(self):
        self.__write_df()
