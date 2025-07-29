from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger

class CustomNode(TNode):
    def __init__(self, spark, tnode_config):
        super().__init__(spark=spark)
        self.tnode_config = tnode_config
        self.spark = spark
        module_name = tnode_config['options']['module_name']
        module_path = tnode_config['options']['module_path']
        class_name = tnode_config['options']['class_name']
        self.custom_processor = self.import_module(module_name, module_path, class_name)

    def import_module(self, module_name, module_path, class_name):
        custom_module = __import__(module_path, fromlist=[module_name])
        custom_class = getattr(custom_module, class_name)
        return custom_class(self.spark, self.tnode_config)  # .create_instance(self.t_df)

    def _process(self):
        logger.info("Custom node process")
        return self.custom_processor.process()
