class TNode:
    def __init__(self, spark, node_type='SparkDataFrame'):
        self.node_type = node_type
        self.node = None
        self.spark = spark

    def _process(self):
        raise NotImplementedError("Subclasses must implement _process method")

    # Source and Processor nodes
    def _createOrReplaceTempView(self):
        if self.node is not None:
            self.node.createOrReplaceTempView(self.node_name)

    def run(self):
        return self._process()
