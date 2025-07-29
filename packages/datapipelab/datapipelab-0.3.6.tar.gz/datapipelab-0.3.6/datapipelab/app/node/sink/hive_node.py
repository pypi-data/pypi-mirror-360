from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger

class HiveSinkNode(TNode):
    def __init__(self, spark, tnode_config, df):
        from pyspark.sql import DataFrame
        super().__init__(spark=spark)
        self.mode = tnode_config.get('mode', None)
        self.stream = tnode_config.get('stream', None)
        self.database_name = tnode_config['options']['database']
        self.table_name = tnode_config['options']['table']
        self.partition_by = tnode_config['options'].get('partition_by', None)
        self.partition_count = tnode_config['options'].get('partition_count', None)
        self.overwrite = tnode_config['options']['overwrite']
        self.df = df

    def __write_dynamic_partition(self):
        if self.partition_count:
            if self.partition_by:
                self.df = self.df.repartition(int(self.partition_count))
            else:
                self.df = self.df.repartition(int(self.partition_count), self.partition_by)
        logger.info("Start writing to Hive")
        self.df.write.insertInto(f'{self.database_name}.{self.table_name}', overwrite=self.overwrite)

    def _process(self):
        self.__write_dynamic_partition()
