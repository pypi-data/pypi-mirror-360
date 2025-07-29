from datapipelab.app.node.tnode import TNode


class HiveSourceNode(TNode):
    def __init__(self, spark, tnode_config):
        super().__init__(spark=spark)
        self.sql_query = tnode_config['options']['query']
        self.node_name = tnode_config['name']

    def __sql_query(self, sql_query):
        self.node = self.spark.sql(sql_query)

    def _process(self):
        self.__sql_query(self.sql_query)
        self._createOrReplaceTempView()
        return self.node