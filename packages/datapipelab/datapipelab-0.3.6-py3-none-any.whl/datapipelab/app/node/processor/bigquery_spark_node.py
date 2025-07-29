# This node should be merged with source/spark_api_node.py

from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger


class BigQuerySparkProcessorNode(TNode):
    def __init__(self, spark, tnode_config):
        super().__init__(spark=spark)
        self.sql_query = tnode_config['options']['query']
        self.node_name = tnode_config['name']
        self.materialization_dataset = tnode_config['options']['materialization_dataset']  # materializationDataset
        self.parent_project = tnode_config['options']['parent_project']  # parentProject

    def __sql_query(self):
        self.node = self.spark.read.format("bigquery").option("materializationDataset",
                                                              self.materialization_dataset).option("query",
                                                                                                   self.sql_query).option(
            "parentProject", self.parent_project).load()

    def _process(self):
        self.__sql_query()
        self._createOrReplaceTempView()
        return self.node
