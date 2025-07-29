from datapipelab.app.node.custom_node import CustomNode
from datapipelab.app.node.processor.shell_node import ShellProcessorNode
from datapipelab.app.node.source.hive_node import HiveSourceNode
from datapipelab.app.node.source.spark_node import SparkSourceNode
from datapipelab.app.node.source.delta_node import DeltaSourceNode
from datapipelab.app.node.source.spark_api_node import SparkApiSourceNode
from datapipelab.app.node.processor.spark_node import SparkProcessorNode
from datapipelab.app.node.sink.delta_node import DeltaSinkNode
from datapipelab.app.node.sink.csv_node import CSVSinkNode
from datapipelab.app.node.sink.pandas_csv_node import PandasCSVSinkNode
from datapipelab.app.node.sink.teams_notification_node import TeamsNotificationSinkNode
from datapipelab.app.node.processor.bigquery_spark_node import BigQuerySparkProcessorNode
from datapipelab.app.node.processor.bigquery_api_node import BigQueryAPIProcessorNode
from datapipelab.app.node.processor.gcp_bucket_node import GCPBucketAPINode


class PipelineHandler:
    def __init__(self, spark=None):
        self.spark = spark

    def create_source_node(self, tnode_name, tnode_config):
        input_type = tnode_config['input_type']
        input_format = tnode_config['input_format']
        print(tnode_name, input_type, input_format, tnode_config)

        source_df = None
        if input_type == 'SharedDrive':
            if input_format == 'excel':
                source_df = CTCSMBReaderSourceNode(tnode_config).run()
        if input_type == "Oracle":
            if input_format == "query":
                source_df = OracleSourceNode(tnode_config).run()
        if input_type == "SharePoint":
            if input_format == "csv":
                source_df = SharePointSourceNode(tnode_config).run()
        if input_type == 'spark':
            if input_format == 'spark':
                source_df = SparkSourceNode(self.spark, tnode_config).run()
        if input_type == 'hive':
            if input_format == 'hive':
                source_df = HiveSourceNode(self.spark, tnode_config).run()
        if input_type == 'adls_path':
            if input_format == 'delta':
                source_df = DeltaSourceNode(self.spark, tnode_config).run()
        if input_type == 'custom':
            source_df = CustomNode(self.spark, tnode_config).run()
        if input_type == 'spark':
            if input_format == 'api':
                source_df = SparkApiSourceNode(self.spark, tnode_config).run()

        return source_df

    def create_processor_node(self, tnode_name, tnode_config, t_df):
        tnode_format = tnode_config['format']
        print(tnode_name, tnode_format, tnode_config)
        processor_df = None
        if tnode_format == 'custom':
            processor_df = CustomNode(self.spark, tnode_config).run()
        if tnode_format == 'query':
            processor_df = SparkProcessorNode(self.spark, tnode_config).run()
        if tnode_format == 'bigquery_api':
            processor_df = BigQueryAPIProcessorNode(self.spark, tnode_config).run()
        if tnode_format == 'bigquery_spark':
            processor_df = BigQuerySparkProcessorNode(self.spark, tnode_config).run()
        if tnode_format == 'shell':
            processor_df = ShellProcessorNode(self.spark, tnode_config).run()
        if tnode_format == 'gcp_bucket_api':
            processor_df = GCPBucketAPINode(self.spark, tnode_config).run()
        return processor_df

    def write_sink_node(self, tnode_config, t_df):
        tnode_type = tnode_config['output_type']
        tnode_format = tnode_config['output_format']
        tnode_name_df = tnode_config['options'].get('parents', [None])[0]
        print(tnode_type, tnode_format, tnode_name_df)

        if tnode_type == 'SharePoint':
            if tnode_format == 'csv':
                sharepoint_sink = SharePointSinkNode(tnode_config, t_df).run()
                print(sharepoint_sink)
                # HiveSinkNode(self.spark, tnode_config, tnode_df[tnode_name_df]).run()
        if tnode_type == "teams":
            if tnode_format == "channel_notification":
                TeamsNotificationSinkNode(self.spark, tnode_config, t_df).run() # TODO: Spark can be set to None
        if tnode_type == "adls_path":
            if tnode_format == "delta":
                DeltaSinkNode(self.spark, tnode_config, t_df).run()
            if tnode_format == "csv":
                CSVSinkNode(self.spark, tnode_config, t_df).run()
        if tnode_type == "local":
            if tnode_format == "csv":
                PandasCSVSinkNode(self.spark, tnode_config, t_df).run()
        if tnode_type == 'custom':
            CustomNode(self.spark, tnode_config).run()
        if tnode_type == 'spark':
            if tnode_format == 'hive':
                from datapipelab.app.node.sink import hive_node
                processor_df = hive_node.HiveSinkNode(self.spark, tnode_config, t_df[tnode_name_df]).run()
        if tnode_type == 'spark':
            if tnode_format == 'spark':
                from datapipelab.app.node.sink import spark_node
                processor_df = spark_node.SparkSinkNode(self.spark, tnode_config, t_df[tnode_name_df]).run()
        if tnode_type == 'spark':
            if tnode_format == 'api':
                from datapipelab.app.node.sink import spark_api_node
                processor_df = spark_api_node.SparkApiSourceNode(self.spark, tnode_config, t_df[tnode_name_df]).run()



