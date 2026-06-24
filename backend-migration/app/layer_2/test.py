from app.layer_2.extraction_plugin_manager import ExtractionPluginManager, ExtractionContext, ExtractionState
from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_1.schemas.masmp.export_fields import MASMP_SOFTWARE_SOURCE_CODE_EXPORT_KEYS
import app.layer_3.plugins
import pdb
pdb.set_trace()
m = ExtractionPluginManager()

m.discover(app.layer_3.plugins)

context = ExtractionContext(
              "https://github.com/zbmed-semtec/maSMP-metadata-extraction",
              'software',
              'maSMP',
              'github',
              None
          )
state = ExtractionState(
              data={},
              metadata=SoftwareMetadata()
          )

# for key in MASMP_SOFTWARE_SOURCE_CODE_EXPORT_KEYS:
#     try:
#         r = m.extract(key, con, state)
#     except Warning as warn:
#         print(warn)
m.extract('alternateName', context, state)
print(state)
# print(r, con, state, m.class_registry)