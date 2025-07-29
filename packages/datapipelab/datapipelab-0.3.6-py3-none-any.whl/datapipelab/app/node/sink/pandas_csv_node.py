from datapipelab.app.node.tnode import TNode


class PandasCSVSinkNode(TNode):
    def __init__(self, spark, tnode_config, t_df):
        from pyspark.sql import DataFrame
        super().__init__(spark=spark)
        self.mode = tnode_config['options'].get('mode', 'w')
        # self.stream = tnode_config['stream']
        self.output_path = tnode_config['options']['path']
        self.overwrite = tnode_config['options'].get('overwrite', False)
        self.header = tnode_config['options'].get('header', True)
        self.df = t_df[tnode_config['options']['parents'][0]]

    def __write_csv(self):
        import pandas as pd
        pandas_df = self.df.toPandas()
        write_mode = "w" if self.overwrite else "x"

        pandas_df.to_csv(self.output_path, mode=write_mode, header=self.header, index=False)

    def _process(self):
        self.__write_csv()