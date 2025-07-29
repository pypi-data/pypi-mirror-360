from datapipelab.app.node.tnode import TNode


class DeltaSourceNode(TNode):
    def __init__(self, spark, tnode_config):
        super().__init__(spark=spark)
        self.delta_table_path = tnode_config['options']['path']
        self.node_name = tnode_config['name']

    def __sql_query(self, delta_table_path):
        self.node = self.spark.read.format("delta").load(delta_table_path)

    def _process(self):
        self.__sql_query(self.delta_table_path)
        self._createOrReplaceTempView()
        return self.node
