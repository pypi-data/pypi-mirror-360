from datapipelab.pipeline_config import PipelineConfig
from datapipelab.pipeline_handler import PipelineHandler
from datapipelab.logger import logger

class Pipeline:
    def __init__(self, pipeline_config_path, spark, config_params=None):
        self.pipeline_config = None
        self.pipeline_config_path = pipeline_config_path
        self.params = config_params
        self.__load_config()
        self.spark = spark

    def __load_config(self):
        self.pipeline_config = PipelineConfig(self.pipeline_config_path, self.params)
        self.pipeline_config.create_pipeline_nodes()

    def __process(self):
        logger.info('Fetch sources...')
        print(self.pipeline_config.sources)
        tnode = PipelineHandler(self.spark)
        self.t_df = {}
        for source in self.pipeline_config.sources:
            self.t_df[source] = tnode.create_source_node(source, self.pipeline_config.sources[source])

        logger.info('Running Processors...')
        print(self.pipeline_config.processors)
        for processor in self.pipeline_config.processors:
            self.t_df[processor] = tnode.create_processor_node(processor, self.pipeline_config.processors[processor], self.t_df)

        logger.info('Write into sinks...')
        print(self.pipeline_config.sinks)
        for sink in self.pipeline_config.sinks:
            tnode.write_sink_node(self.pipeline_config.sinks[sink], self.t_df)

    def run(self):
        self.__process()
