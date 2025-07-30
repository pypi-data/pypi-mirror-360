import csv
import io
from pathlib import Path
from tempfile import SpooledTemporaryFile

import pandas as pd
import tqdm

from qcogclient.httpclient import ReadableFile


class LoadedCSV:
    file: ReadableFile
    number_of_columns: int
    number_of_rows: int


def validate_csv(
    file: Path | str,
    *,
    sample_size: int = 1000,
    max_errors: int = 10,
) -> tuple[bool, list[str]]:
    """
    Validate that a file is a valid CSV by checking its structure and formatting.

    Args:
        file: Path to the CSV file to validate
        sample_size: Number of lines to sample for validation (0 for full file)
        max_errors: Maximum number of errors to collect before stopping

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if isinstance(file, str):
        file = Path(file)

    if not file.exists():
        return False, [f"File does not exist: {file}"]

    if not file.is_file():
        return False, [f"Path is not a file: {file}"]

    errors = []
    line_count = 0
    expected_columns = None

    try:
        with file.open("r", encoding="utf-8", newline="") as f:
            # Try to detect the dialect
            try:
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel  # Default to Excel dialect

            reader = csv.reader(f, dialect=dialect)

            for row in reader:
                line_count += 1

                # Check if we've reached the sample size limit
                if sample_size > 0 and line_count > sample_size:
                    break

                # Set expected columns from first non-empty row
                if expected_columns is None and row:
                    expected_columns = len(row)
                    if expected_columns == 0:
                        errors.append(f"Line {line_count}: Empty header row")
                        if len(errors) >= max_errors:
                            break
                    continue

                # Skip empty rows
                if not row or all(cell.strip() == "" for cell in row):
                    continue

                # Check column count consistency
                if expected_columns is not None and len(row) != expected_columns:
                    errors.append(
                        f"Line {line_count}: Expected {expected_columns} columns, got {len(row)}"  # noqa: E501
                    )
                    if len(errors) >= max_errors:
                        break

                # Check for common CSV issues
                for i, cell in enumerate(row):
                    # Check for unescaped quotes in the middle of fields
                    if '"' in cell and not (
                        cell.startswith('"') and cell.endswith('"')
                    ):
                        # This is a simplified check - in practice, CSV parsing
                        # handles this
                        # but we can flag potentially problematic patterns
                        pass

                    # Check for newlines in unquoted fields
                    if "\n" in cell and not (
                        cell.startswith('"') and cell.endswith('"')
                    ):
                        errors.append(
                            f"Line {line_count}, column {i + 1}: Unquoted field contains newline"  # noqa: E501
                        )
                        if len(errors) >= max_errors:
                            break

    except UnicodeDecodeError as e:
        return False, [f"File encoding error: {e}"]
    except Exception as e:
        return False, [f"Error reading file: {e}"]

    # Additional validation checks
    if line_count == 0:
        errors.append("File is empty")

    if expected_columns is None:
        errors.append("No valid CSV structure found")

    return len(errors) == 0, errors


def load_csv(
    file: Path | str,
    *,
    chunk_size: int = 1024 * 1024,
    validate: bool = False,
) -> LoadedCSV:
    """
    Load a CSV file into a file-like object and compute its dimensions.
    Returns a LoadedCSV object containing the file and its dimensions.

    Args:
        file: Path to the CSV file to load
        chunk_size: Size of chunks to read the file in
        validate: Whether to validate the CSV structure before loading
    """
    if isinstance(file, str):
        file = Path(file)

    # Validate the CSV if requested
    if validate:
        is_valid, errors = validate_csv(file)
        if not is_valid:
            raise ValueError(f"Invalid CSV file: {'; '.join(errors)}")

    retval = SpooledTemporaryFile()  # Use binary mode for pandas compatibility
    total_chunks = max(1, file.stat().st_size // chunk_size)  # Ensure at least 1 chunk
    current_chunk = 0
    percentage = 0

    # Initialize counters
    number_of_rows = 0
    number_of_columns = 0
    first_line = True

    with tqdm.tqdm(total=total_chunks, desc="Loading CSV", unit="chunk") as pbar:
        with file.open(
            "r", encoding="utf-8"
        ) as f:  # Read in text mode with UTF-8 encoding
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                # Count rows and columns in this chunk
                lines = chunk.split("\n")  # Split on string newline
                for line in lines:
                    if line.strip():  # Skip empty lines
                        if first_line:
                            number_of_columns = len(
                                line.split(",")
                            )  # Split on string comma
                            first_line = False
                        number_of_rows += 1

                # Write the chunk as UTF-8 bytes to maintain pandas compatibility
                retval.write(chunk.encode("utf-8"))
                current_chunk += 1
                percentage = round(current_chunk / total_chunks * 100)
                pbar.update(1)
                pbar.set_postfix(percentage=percentage)
                pbar.refresh()

        retval.seek(0)

        return {  # type: ignore
            "file": retval,
            "number_of_columns": number_of_columns,
            "number_of_rows": number_of_rows,
        }


def load_dataframe(
    file: pd.DataFrame,
    *,
    index: bool = False,
) -> ReadableFile:
    """
    Load a pandas DataFrame into a file-like object.
    """

    retval = io.BytesIO()
    file.to_csv(retval, index=index)
    retval.seek(0)
    return retval
