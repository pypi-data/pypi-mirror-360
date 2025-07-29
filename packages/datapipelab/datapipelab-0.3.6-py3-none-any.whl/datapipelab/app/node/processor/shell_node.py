from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger

class ShellProcessorNode(TNode):
    def __init__(self, spark, tnode_config):

        super().__init__(spark=spark)
        self.shell_query = tnode_config['options']['query']
        self.node_name = tnode_config['name']

    def __shell_query(self):
        import subprocess
        # run the job
        result = subprocess.run(
            f"{self.shell_query}",
            shell=True, check=True, executable='/bin/bash'
        )
        logger.info(result)

    def _process(self):
        self.__shell_query()
        self._createOrReplaceTempView()
        return self.node
