import pandas as pd
import os
from io import BytesIO, StringIO
from base.utils.exceptions import CustomValidationError


class FileParser:
    """Parser for CSV and Excel files (.csv, .xls, .xlsx) with validation and normalization."""

    VALID_EXTENSIONS = {".csv", ".xls", ".xlsx"}

    def __init__(self, file_obj, mandatory_fields=None, readable_field_map=None, field_validators=None):
        """
        :param file_obj: Either a file path (str) or InMemoryUploadedFile (from request.FILES)
        :param mandatory_fields: List of internal field names required in the file (e.g. ['missioner_email', 'first_name'])
        :param readable_field_map: Optional dict mapping internal field names to user-friendly display names
                                   e.g. {'missioner_email': 'Missioner Email', 'first_name': 'First Name'}
        """
        self.file_obj = file_obj
        self.extension = self._get_extension()
        self.mandatory_fields = mandatory_fields or []
        self.readable_field_map = readable_field_map or {}
        self.field_validators = field_validators or {}

    def _get_extension(self):
        """Detect file extension from name or path."""
        if hasattr(self.file_obj, "name"):
            return os.path.splitext(self.file_obj.name)[1].lower()
        elif isinstance(self.file_obj, str):
            return os.path.splitext(self.file_obj)[1].lower()
        else:
            raise CustomValidationError("Invalid file input type.")

    def validate_file_type(self):
        """Ensure the file has a supported extension."""
        if self.extension not in self.VALID_EXTENSIONS:
            raise CustomValidationError(
                f"Invalid file format: {self.extension}. "
                f"Allowed formats: {', '.join(self.VALID_EXTENSIONS)}"
            )

    def read_file(self) -> pd.DataFrame:
        """Read the uploaded file into a pandas DataFrame."""
        if self.extension == ".csv":
            if hasattr(self.file_obj, "read"):
                self.file_obj.seek(0)
                df = pd.read_csv(StringIO(self.file_obj.read().decode("utf-8")))
            else:
                df = pd.read_csv(self.file_obj)
        else:
            if hasattr(self.file_obj, "read"):
                self.file_obj.seek(0)
                df = pd.read_excel(BytesIO(self.file_obj.read()))
            else:
                df = pd.read_excel(self.file_obj)

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        df = df.where(pd.notnull(df), None)

        return df

    def validate_data(self, df: pd.DataFrame):
        """Ensure headers, data, and mandatory fields are valid."""

        if df.columns.isnull().any():
            raise CustomValidationError("File contains missing or invalid column headers.")

        if df.dropna(how="all").empty:
            raise CustomValidationError("File appears to be empty or contains only blank rows.")

        missing_columns = [col for col in self.mandatory_fields if col not in df.columns]
        if missing_columns:
            readable_missing = [
                self.readable_field_map.get(col, col.replace("_", " ").title())
                for col in missing_columns
            ]
            raise CustomValidationError(
                f"Missing mandatory columns: {', '.join(readable_missing)}"
            )

        for field in self.mandatory_fields:
            missing_rows = df[df[field].isnull()]
            if not missing_rows.empty:
                row_numbers = ", ".join(str(i + 2) for i in missing_rows.index.tolist())  # +2 to account for header row
                readable_name = self.readable_field_map.get(field, field.replace("_", " ").title())
                raise CustomValidationError(
                    f"Field '{readable_name}' contains missing values in rows: {row_numbers}"
                )

        # TODO: Find a better refactoring approach that does not compromise on functiontionality, perfomance and error handling
        for field, validator in self.field_validators.items():
            if field not in df.columns:
                continue
            for i, value in enumerate(df[field]):
                try:
                    new_value = validator(value, i + 2)
                    # If validator returns a normalized value, replace it
                    if new_value is not None:
                        df.at[i, field] = new_value
                except CustomValidationError as e:
                    raise CustomValidationError(str(e))

    def to_dict(self):
        """Validate and convert file into list of dictionaries."""
        self.validate_file_type()
        df = self.read_file()
        self.validate_data(df)
        return df.to_dict(orient="records")
