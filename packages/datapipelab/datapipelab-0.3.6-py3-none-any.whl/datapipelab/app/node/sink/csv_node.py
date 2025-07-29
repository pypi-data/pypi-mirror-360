from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger

class CSVSinkNode(TNode):
    def __init__(self, spark, tnode_config, t_df):
        from pyspark.sql import DataFrame
        super().__init__(spark=spark)
        self.output_path = tnode_config['options']['path']
        self.partition_by = tnode_config['options'].get('partition_by')
        self.partition_count = tnode_config['options'].get('partition_count', 1)
        self.overwrite = tnode_config['options'].get('overwrite', False)
        self.header = tnode_config['options'].get('header', True)
        self.df = t_df[tnode_config['options']['parents'][0]]
        self.quote_all = tnode_config['options'].get('quote_all', False)
        self.ignore_leading_white_space = tnode_config['options'].get('ignore_leading_white_space', True)
        self.ignore_trailing_white_space = tnode_config['options'].get('ignore_trailing_white_space', True)

    def __write_csv(self):
        if self.partition_count:
            if self.partition_by:
                self.df = self.df.repartition(int(self.partition_count), *self.partition_by)
            else:
                self.df = self.df.repartition(int(self.partition_count))

        write_mode = "overwrite" if self.overwrite else "errorifexists"

        (self.df.write.mode(write_mode).option("quoteAll", self.quote_all).option("ignoreLeadingWhiteSpace",
                                                                                  self.ignore_leading_white_space).option(
            "ignoreTrailingWhiteSpace", self.ignore_trailing_white_space).option("header", self.header).csv(
            self.output_path))

    def _process(self):
        self.__write_csv()
