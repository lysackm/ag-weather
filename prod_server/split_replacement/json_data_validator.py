import glob
import json

from referencing import Registry, Specification
from jsonschema.validators import validator_for


# Print out some info from a validation error.
def print_validation_error(error):
    print("There was an error validating the json data.")
    print("Error Message:", error.message)
    print("Context:", error.context)
    print("Cause:", error.cause, "\n")


class JSONDataValidator:
    def __init__(self, files_to_validate_regex, schemas_path_regex, base_schema_file):
        self.files_to_validate_regex = files_to_validate_regex
        self.schemas_path_regex = schemas_path_regex # regex for glob.glob
        self.base_schema_file = base_schema_file
        self.data_to_validate = self.load_data()
        self.schemas = self.load_schemas()
        self.base_schema = self.load_base_schema()

    def load_data(self):
        data_to_validate = []

        data_to_validate_files = glob.glob(self.files_to_validate_regex)

        for file in data_to_validate_files:
            with open(file) as f:
                data_to_validate.append(json.load(f))
        return data_to_validate

    def load_schemas(self):
        # load all schemas
        schemas = []

        schema_files = glob.glob(self.schemas_path_regex)

        # create list of schemas to load
        for file in schema_files:
            with open(file) as f:
                schemas.append(json.load(f))
        return schemas

    def load_base_schema(self):
        # load base schema
        with open(self.base_schema_file) as f:
            return json.load(f)

    # throws jsonschema.exceptions.ValidationError
    def validate_data(self):
        # put in registry
        registry = Registry().with_resources(
            [
                (schema["$id"], Specification.detect(schema).create_resource(schema))
                for schema in self.schemas
            ]
        )

        # validate
        validator = validator_for(self.base_schema)(self.base_schema, registry=registry)

        for datum in self.data_to_validate:
            # If there is a validator error it throws a jsonschema.exceptions.ValidationException
            validator.validate(datum)


if __name__ == "__main__":
    data_validator = JSONDataValidator("./partner_data/*.json",
                                       "./partner_data/schemas/sub_schemas/*.json",
                                       "./partner_data/schemas/partner_file_specs_schema.json")
    data_validator.validate_data()
