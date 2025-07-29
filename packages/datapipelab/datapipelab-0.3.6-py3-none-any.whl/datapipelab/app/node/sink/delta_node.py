from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger

class DeltaSinkNode(TNode):
    def __init__(self, spark, tnode_config, t_df):
        from delta.tables import DeltaTable
        from pyspark.sql import DataFrame
        super().__init__(spark=spark)
        self.mode = tnode_config['options']['mode']  # Can be 'append', 'overwrite', or 'upsert'
        self.partition_by = tnode_config['options'].get('partition_by')
        self.partition_count = tnode_config['options'].get('partition_count')
        self.df = t_df[tnode_config['options']['parents'][0]]
        self.delta_table_path = tnode_config['options']['path']  # Path to the Delta table
        self.primary_key = tnode_config['options'].get('primary_key', None)

    def __write_append(self):
        if self.partition_count:
            self.df = self.df.repartition(int(self.partition_count), self.partition_by)
        self.df.write.format("delta").mode("append").save(self.delta_table_path)

    def __write_overwrite(self):
        if self.partition_count:
            self.df = self.df.repartition(int(self.partition_count), self.partition_by)
        self.df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(self.delta_table_path)

    def __write_upsert(self):
        delta_table = DeltaTable.forPath(self.spark, self.delta_table_path)
        primary_key = self.primary_key
        if primary_key is None:
            raise ValueError("Primary key must be provided for upsert mode")
        delta_table.alias("target").merge(
            self.df.alias("source"),
            " AND ".join([f"target.{key} = source.{key}" for key in primary_key])
        ).whenMatchedUpdateAll(
        ).whenNotMatchedInsertAll(
        ).execute()

    def _process(self):
        if self.mode == 'append':
            self.__write_append()
        elif self.mode == 'overwrite':
            self.__write_overwrite()
        elif self.mode == 'upsert':
            self.__write_upsert()
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
