from app.layer_1.schemas.masmp.export_fields import MASMP_SOFTWARE_APPLICATION_EXPORT_KEYS, MASMP_SOFTWARE_SOURCE_CODE_EXPORT_KEYS
from app.layer_1.schemas.codemeta.export_fields import CODEMETA_SOFTWARE_SOURCE_CODE_EXPORT_KEYS
from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_2.extraction_plugin_manager import ExtractionPluginManager
from app.layer_3.steps.contracts.pipeline import ExtractionPipeline
from app.layer_3.composers.pipeline_composer import PipelineComposer, ExtractionContext
import app.layer_3.plugins

class PluginPipelineComposer(PipelineComposer):

    plugin_manager : ExtractionPluginManager = None

    def get_plugin_manager(self):
        if not self.plugin_manager:
            self.plugin_manager = ExtractionPluginManager()
            self.plugin_manager.discover(app.layer_3.plugins)
        return self.plugin_manager

    def compose(self, context : ExtractionContext):

        export_keys = context.schema.get_property_list()

        priority_groups : dict[int, set[ExtractionPlugin]] = dict()
        
        for key in export_keys:
            try:
                candidate_plugins = self.get_plugin_manager().select(key, context)
                for plugin in candidate_plugins:
                        group = priority_groups.get(plugin.priority_level, set())
                        group.add(plugin)
                        priority_groups[plugin.priority_level] = group
            except Exception as e:
                print(e)
        pipeline_steps = []
        for priority_level in sorted(priority_groups.keys(), reverse=True):
            pipeline_steps.extend(priority_groups[priority_level])
        
        return ExtractionPipeline(steps=pipeline_steps)