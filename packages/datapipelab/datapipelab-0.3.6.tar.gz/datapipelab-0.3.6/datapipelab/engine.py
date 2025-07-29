from datapipelab.pipeline import Pipeline
from datapipelab.logger import logger


class Engine:
    def __init__(self, engine_config_path, spark=None, params=None):
        self.engine_config_path = engine_config_path
        self.params = params
        self.pipeline = None
        self.spark = spark

    def running_travelers(self):
        self.pipeline = Pipeline(self.engine_config_path, self.spark, self.params)
        self.pipeline.run()