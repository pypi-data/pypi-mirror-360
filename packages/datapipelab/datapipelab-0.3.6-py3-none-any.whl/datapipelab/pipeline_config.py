import json5


class PipelineConfig:
    def __init__(self, config_file, params):
        print(config_file)
        self.params = params
        self.config_file = config_file
        # If the config file is an instance of string, it is a path to the config file
        self.config_file = config_file
        if isinstance(self.config_file, str):
            self.load_json_config_file()
        elif isinstance(self.config_file, list):
            self.pipeline_settings = config_file
        else:
            raise ValueError("Invalid config file type. Must be a string or a list.")
        self.sources = {}
        self.processors = {}
        self.sinks = {}

    def load_json_config_file(self):
        with open(self.config_file, 'r') as f:
            # Read the file as a text file
            json_config_file = f.read()
            # Replace the placeholders with the actual values
            for key, value in self.params.items():
                json_config_file = json_config_file.replace(f"{{{key}}}", value)
            # Convert to JSON file
            self.pipeline_settings = json5.loads(json_config_file)
        if len(self.pipeline_settings) > 0 and self.pipeline_settings[0]['type'] == 'import':
            self.import_json_config_file()

    def import_json_config_file(self):
        import_pipeline_settings = []
        for import_component in self.pipeline_settings:
            if import_component['type'] == '': # Maybe someone wants to use import in the middle of his config?
                pass

    def create_pipeline_nodes(self):
        for component in self.pipeline_settings:
            if component['type'] == 'source':
                source = {
                    'input_format': component['format'],
                    'name': component['name'],
                    'input_type': component['source'],
                    'options': component['options']
                }
                self.sources[component['name']] = source
            elif component['type'] == 'processor':
                processor = {
                    'format': component['format'],
                    'name': component['name'],
                    'options': component['options']
                }
                parents = component['options'].get('parents', [])
                parent_sources = []
                for parent in parents:
                    parent_source = self.sources.get(parent)
                    if not parent_source:
                        parent_processor = self.processors.get(parent)
                        if not parent_processor:
                            raise ValueError(f"Parent '{parent}' not found")
                        parent_source = parent_processor['source']
                    parent_sources.append(parent_source)
                processor['source'] = parent_sources
                self.processors[component['name']] = processor
            elif component['type'] == 'sink':
                sink = {
                    'output_format': component['format'],
                    'name': component['name'],
                    'output_type': component['sink'],
                    'options': component['options']
                }
                parent = component['options']['parents'][0]
                parent_source = self.sources.get(parent)
                if not parent_source:
                    parent_processor = self.processors.get(parent)
                    if not parent_processor:
                        raise ValueError(f"Parent '{parent}' not found")
                    parent_source = parent_processor['source']
                sink['source'] = parent_source
                self.sinks[component['name']] = sink
            else:
                raise ValueError(f"Invalid component type '{component['type']}'")


