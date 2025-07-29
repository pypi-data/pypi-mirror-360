from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger


class SparkApiSourceNode(TNode):
    def __init__(self, spark, tnode_config):
        super().__init__(spark=spark)
        self.node_name = tnode_config['name']
        self.__load_options(tnode_config)


    def __load_options(self, tnode_config):
        self.spark_options = tnode_config.get('options', {})
        self.options = {}
        if 'format' in self.spark_options:
            self.format = self.spark_options.get('format')
        if 'query' in self.spark_options:
            self.query = self.spark_options.get('query')
        if 'materialization_dataset' in self.spark_options:
            self.options['materializationDataset'] = self.spark_options.get('materialization_dataset')
        if 'parent_project' in self.spark_options:
            self.options['parentProject'] = self.spark_options.get('parent_project')
        if 'table' in self.spark_options:
            self.options['table'] = self.spark_options.get('table')
        if 'path' in self.spark_options:
            self.options['path'] = self.spark_options.get('path')



    def __load_df(self):
        reader = self.spark.read
        if self.format:
            reader = reader.format(self.format)
        for key, value in self.options.items():
            if value:
                reader = reader.option(key, value)
        self.node = reader.load()

    def _process(self):
        self.__load_df()
        self._createOrReplaceTempView()
        return self.node
