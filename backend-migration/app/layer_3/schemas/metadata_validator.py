from layer_1.schemas.metadata_record import MetadataRecord
from layer_1.schemas.validation_result import ValidationResult
from linkml.validator import JsonschemaValidationPlugin, Validator

class MetadataValidator:
    def __init__(self, registry):
        self.registry = registry

    def validate(self, record: MetadataRecord) -> ValidationResult:
        view = self.registry.get(record.schema_name)
        try:
            validator = Validator(
                schema=view.schema,
                validation_plugins=[JsonschemaValidationPlugin(closed=True)],
            )
            errors = [
                str(r.message)
                for r in validator.iter_results(
                    record.data, target_class=record.class_name
                )
            ]
            return ValidationResult(valid=len(errors) == 0, errors=errors)
        except Exception as e:
            return ValidationResult(valid=False, errors=[str(e)])