import pandera as pa
from pandera.typing import Series


class BrynQPanderaDataFrameModel(pa.DataFrameModel):
    """
    A custom DataFrameModel that supports relationship annotations
    via a nested Metadata class.
    """
    class _Annotation:
        """
        Annotates a pandera DataFrameSchema with PK/FK relationship metadata.

        Parameters:
            schema (DataFrameSchema): The schema to annotate.
            primary_key (str): The name of the primary key column. Must be present in the schema.
            foreign_keys (dict, optional): A dict mapping column names to foreign key details. For each foreign key, the details must be a dict with:
                - "parent_schema": a string indicating the referenced schema (or table), most often the parent.
                - "parent_column": a string indicating the referenced column.
                - "cardinality": A string describing the relationship type. Must be one of "1:1", "1:N", "N:1", or "N:N".
                  The first character points to the annotated (child) schema itself, the second to the referenced (parent) schema.

        Example:
            employee_schema = pa.DataFrameSchema({
                "id": pa.Column(int, nullable=False),
                "name": pa.Column(str, nullable=False),
                "department_id": pa.Column(int, nullable=False),
            })

            class _Annotation:
                primary_key = "id"
                foreign_keys = {
                    "department_id": {
                        "parent_schema": "department_schema",
                        "parent_column": "id",
                        "cardinality": "N:1"
                    }
                }

        Raises:
            ValueError: If:
                - The cardinality is not one of the allowed values.
                - The primary key column is not in the schema.
                - Any foreign key column is not in the schema.
                - The foreign key details do not match the expected format.
        """
        primary_key: str = None
        foreign_keys: dict = None
        cardinality: str = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        # Let the DataFrameModel create the schema as usual.
        super().__init_subclass__(**kwargs)
        schema = cls.__schema__

        # Look for an inner Annotation class and store info, but don't validate yet
        annotation_cls = getattr(cls, "_Annotation", None)
        # For backward compatibility, also check for Annotation
        if annotation_cls is None:
            annotation_cls = getattr(cls, "Annotation", None)

        if annotation_cls:
            pk = getattr(annotation_cls, "primary_key", None)
            fk = getattr(annotation_cls, "foreign_keys", None)

            # Store for deferred validation - just store, no validation during class construction
            if pk is not None or fk is not None:
                cls._deferred_annotation = {
                    'primary_key': pk,
                    'foreign_keys': fk.copy() if fk is not None else None
                }
            else:
                cls._deferred_annotation = None

            # Initialize metadata if schema exists (but no validation)
            if schema is not None:
                schema.metadata = schema.metadata or {}
                schema.metadata["primary_key"] = pk
                if fk:
                    schema.metadata["foreign_keys"] = fk

        # collect any pydantic-style field aliases into cls._alias_map
        alias_map = {}
        for attr_name, attr_value in cls.__dict__.items():
            # Many pandera Field defaults carry an .alias attribute
            alias = getattr(attr_value, "alias", None)
            if alias and alias != attr_name:
                alias_map[attr_name] = alias
        # store on class for use in validate()
        cls._alias_map = alias_map

        return schema

    @classmethod
    def to_schema(cls):
        """Override to_schema to perform deferred validation when schema is actually needed."""
        schema = super().to_schema()

        # Perform deferred annotation validation now that schema is fully built
        if hasattr(cls, '_deferred_annotation') and cls._deferred_annotation:
            pk = cls._deferred_annotation.get('primary_key')
            fk = cls._deferred_annotation.get('foreign_keys')

            if pk or fk:
                # Get the alias map to check aliased names
                alias_map = getattr(cls, "_alias_map", {})

                # Now we can safely validate since schema should be fully constructed
                if pk:
                    # Check if primary key exists either as original name or aliased name
                    pk_aliased = alias_map.get(pk, pk)  # Get alias if it exists, otherwise use original
                    if pk not in schema.columns and pk_aliased not in schema.columns:
                        raise ValueError(
                            f"Primary key '{pk}' (alias: '{pk_aliased}') is not a column in the schema. "
                            f"Available columns: {list(schema.columns.keys())}"
                        )

                # Validate the foreign keys structure.
                if fk is not None:
                    if not isinstance(fk, dict):
                        raise ValueError("foreign_keys must be a dictionary mapping column names to foreign key details.")

                    for col, details in fk.items():
                        # Check that the foreign key column exists in the schema (check both original and aliased names)
                        col_aliased = alias_map.get(col, col)  # Get alias if it exists, otherwise use original
                        if col not in schema.columns and col_aliased not in schema.columns:
                            raise ValueError(
                                f"Foreign key column '{col}' (alias: '{col_aliased}') is not a column in the schema. "
                                f"Available columns: {list(schema.columns.keys())}"
                            )
                        # Check that the details are provided as a dictionary.
                        if not isinstance(details, dict):
                            raise ValueError(f"Foreign key details for column '{col}' must be provided as a dictionary.")
                        # Check that required keys are present.
                        required_keys = {"parent_schema", "parent_column", "cardinality"}
                        missing_keys = required_keys - details.keys()
                        if missing_keys:
                            raise ValueError(
                                f"Foreign key details for column '{col}' are missing required keys: {missing_keys}"
                            )
                        # Optionally, verify that the values for required keys are strings.
                        if not isinstance(details["parent_schema"], str):
                            raise ValueError(f"The 'parent_schema' value for foreign key '{col}' must be a string.")
                        if not isinstance(details["parent_column"], str):
                            raise ValueError(f"The 'parent_column' value for foreign key '{col}' must be a string.")

                        # Enforce allowed type values.
                        allowed_relationships = {"1:1", "1:N", "N:1", "N:N"}
                        cardinality = details.get("cardinality")
                        if cardinality not in allowed_relationships:
                            raise ValueError(
                                f"Invalid relationship type '{cardinality}'. "
                                f"Allowed values are: {allowed_relationships}"
                            )

        return schema

    @classmethod
    def validate(cls, df, *args, **kwargs):
        """
        Override validate to first apply pydantic-style aliases via pa.Field(alias=...),
        then delegate to the base DataFrameModel.validate.
        """
        alias_map = getattr(cls, "_alias_map", {})
        df = super().validate(df, *args, **kwargs)
        alias_map = {v: k for k, v in alias_map.items()}
        if alias_map:
            df = df.rename(columns=alias_map)
        return df
