import csv
from abc import ABC
from collections.abc import Sequence
from csv import DictWriter
from functools import singledispatchmethod
from pathlib import Path
from typing import Self

from flatten_dict import flatten
from yaml import safe_dump_all

from bauklotz.reporting.fact import ItemFactStore
from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.report import ReportConfiguration
from bauklotz.reporting.report.buffered import BufferedReport


class FilesystemWriterConfiguration(ReportConfiguration):
    """
    Represents a configuration for a filesystem writer.

    This class is used to store configuration details for writing reports to a
    filesystem. It allows specification of the output file path and encoding,
    and provides functionality for deserializing configuration data from a
    dictionary.

    Attributes:
        path (Path): The file path where the report will be written.
        encoding (str): The encoding format to use for writing the file.
    """
    def __init__(self, path: Path, encoding: str = 'utf-8'):
        """
        Initializes a new instance of the class with the specified file path and encoding.

        The class is designed to manage file-related operations, requiring the file path
        and encoding to set up the initial state. The path should be a valid Path object,
        representing the location of the file to be accessed or modified. The encoding
        specification determines the character encoding to be used for operations involving
        text data, defaulting to UTF-8.

        Args:
            path: The Path object representing the file's location.
            encoding: The string specifying the file encoding to be used. Defaults to 'utf-8'.
        """
        self._path = path
        self._encoding = encoding

    @property
    def path(self) -> Path:
        """
        Gets the file system path associated with the instance.

        This property provides access to the file or directory path
        managed by the instance. The path is expected to be an object
        of type `Path` and represents the file system location being
        managed.

        Returns:
            Path: The file system path managed by the instance.
        """
        return self._path

    @property
    def encoding(self) -> str:
        """
        Returns the character encoding used by the object.

        This property retrieves the value of the `_encoding` attribute, which
        specifies the character encoding format associated with the object.

        Returns:
            str: The character encoding format.
        """
        return self._encoding

    @classmethod
    def deserialize(cls, data: dict[str, JSONType]) -> Self:
        """
        Deserializes a dictionary into an instance of the class. The method creates
        a class instance using the provided data dictionary, extracting required
        and optional values.

        Args:
            data (dict[str, JSONType]): A dictionary containing required key
                'path' and an optional key 'encoding'. These keys are used for
                initializing the class attributes.

        Returns:
            Self: An instance of the class initialized with data from the
                dictionary.
        """
        return cls(Path(data['path']), data.get('encoding', 'utf-8'))


class FilesystemWriterReport[I: Item](BufferedReport[I, FilesystemWriterConfiguration], ABC):
    """FilesystemWriterReport class.

    Represents a report that combines functionalities of a buffered report and
    a filesystem writer configuration. This class serves as a base class for
    handling filesystem-related reporting with specific configurations. It
    inherits from BufferedReport with a specified filesystem writer
    configuration and utilizes abstract base class functionalities.

    Attributes:
        name (str): The name associated with the report instance.
        config (FilesystemWriterConfiguration): The configuration object
            containing settings for the filesystem writer.
    """
    def __init__(self, name: str, config: FilesystemWriterConfiguration):
        """
        FilesystemWriter is responsible for writing data to a filesystem
        using the specified configuration.

        Attributes:
            name (str): The name assigned to the writer.
            config (FilesystemWriterConfiguration): Configuration object to
                control the writer's behavior.
        """
        super().__init__(name, config)


class CSVWriterConfiguration(FilesystemWriterConfiguration):
    """Represents a configuration for writing data to a CSV file.

    This class extends `FilesystemWriterConfiguration` to provide additional
    configuration options specifically for CSV file writing, such as the CSV
    delimiter. It manages encoding, file path, and delimiter settings for
    writing to CSV files.

    Attributes:
        path (Path): The file path to write the CSV data.
        encoding (str): The encoding used for writing the CSV file.
        delimiter (str): The character used to separate fields in the CSV file.
    """
    def __init__(self, path: Path, encoding: str = 'utf-8', delimiter: str = ','):
        """
        Initializes an instance of the class with the provided path, encoding,
        and delimiter. It sets up the necessary attributes for working with
        file operations.

        Args:
            path (Path): The file path indicating the location of the file to be managed.
            encoding (str): The character encoding used for reading and writing the file. Defaults to 'utf-8'.
            delimiter (str): The delimiter used in the file, commonly for CSV files. Defaults to ','.
        """
        super().__init__(path, encoding)
        self._delimiter = delimiter

    @property
    def delimiter(self) -> str:
        """
        Gets the delimiter used for separating elements in a sequence.

        The delimiter defines how data elements in a sequence are separated,
        and it is often used when dealing with parsing or formatting strings
        to enforce specific delimitations.

        Returns:
            str: The delimiter value that is currently set.
        """
        return self._delimiter

    @classmethod
    def deserialize(cls, data: dict[str, JSONType]) -> Self:
        """
        Deserializes a dictionary containing JSONType data into an instance of the class.

        This method transforms the input dictionary into an object of the class using
        specific keys within the dictionary. The input dictionary must have a 'path'
        key, while 'encoding' and 'delimiter' keys are optional with default fallback
        values if not provided.

        Args:
            data (dict[str, JSONType]): Input dictionary containing the serialized data
                to deserialize. The dictionary must include a 'path' key of type str
                and optionally include 'encoding' and 'delimiter' keys.

        Returns:
            Self: An instance of the class created using the deserialized data.
        """
        return cls(Path(data['path']), data.get('encoding', 'utf-8'), data.get('delimiter', ','))


class CSVWriterReport[I: Item](FilesystemWriterReport[I]):
    """
    Handles writing data to a CSV file while normalizing and flattening the input structure.

    This class provides functionality to serialize and write structured data to a CSV file. Each entry
    is normalized to a flat dictionary format to simplify the CSV structure. It supports multiple data
    types, including custom items and their associated metadata.

    Attributes:
        name (str): The name of the CSV writer instance.
        config (CSVWriterConfiguration): Configuration for CSV writer, including encoding, file path,
            and delimiter settings.
    """
    def __init__(self, name: str, config: CSVWriterConfiguration):
        """
        Represents a CSV writer for managing data export to CSV format leveraging the associated
        configuration. Provides initialization with the given name and configuration for setting
        up the writer properties.

        Attributes:
            name: The name to uniquely identify the CSV writer instance.
            config: Configuration object specifying settings such as file path, delimiter,
                quoting options, and others required for CSV writing.
        """
        super().__init__(name, config)

    def close(self):
        """
        Closes the writer and writes data to a file in a tabular format.

        This method normalizes the given entries, extracts unique header keys, and writes
        the data into a file with these headers. The file is written in a delimited text
        format as specified in the configuration.

        Args:
            None

        Raises:
            None
        """
        entries: Sequence[dict[str, str]] = self._normalize_entries()
        header: Sequence[str] = sorted({key for entry in entries for key in entry})
        with open(self.config.path, encoding=self.config.encoding, mode='w', newline='') as out:
            writer: DictWriter = DictWriter(out, header, delimiter=self.config.delimiter)
            writer.writeheader()
            writer.writerows(entries)

    def _normalize_entries(self) -> Sequence[dict[str, str]]:
        """
        Normalizes entries and their associated facts.

        This method processes a collection of entries by normalizing their attributes
        and associated facts using the `_normalize` method. The resulting sequence
        contains dictionaries that combine the normalized item attributes and facts.

        Returns:
            Sequence[dict[str, str]]: A sequence of dictionaries containing normalized
            attributes and facts for each entry.
        """
        return tuple(
            dict(self._normalize(item), **self._normalize(item.facts)) for item in self._get_entries()
        )

    @singledispatchmethod
    def _normalize(self, item) -> dict[str, str]:
        """
        Normalize an input item and return its representation as a dictionary.

        This is a generic method that handles different types of input items and
        normalizes them into a consistent dictionary-based format. The method
        dispatches to specific implementations based on the type of the provided
        item. If the type of the input item is not supported, a `TypeError` is raised.

        Args:
            item: The input item to normalize. The type-specific implementation is
                determined by the input's type.

        Returns:
            dict[str, str]: A dictionary representing the normalized form of the input item.
        """
        raise TypeError(f"Unsupported type: {type(item)}")

    @_normalize.register
    def _(self, item: Item):
        return self._normalize_entry(dict(item=item.serialize(), _labels=','.join(sorted(item.labels))))

    @_normalize.register
    def _(self, item: ItemFactStore):
        return self._normalize_entry(dict(item.items()))

    @singledispatchmethod
    def _normalize_entry(self, entry) -> JSONType:
        """
        Normalizes a given entry to JSONType.

        This method dispatches to specific implementations based on the type of
        the input entry, allowing polymorphic behavior for normalization. If no
        specific implementation exists, the default implementation will be used.

        Args:
            entry: The input entry to be normalized.

        Returns:
            JSONType: The normalized entry as a JSON-compatible type.
        """
        return entry

    @_normalize_entry.register
    def _(self, entry: dict) -> JSONType:
        return flatten(
            dict((k, self._normalize_entry(v)) for k, v in entry.items()),
            reducer='dot'
        )

    @_normalize_entry.register
    def _(self, entry: list) -> JSONType:
        return flatten(
            dict(
                (str(i), self._normalize_entry(value))
                for i, value in enumerate(entry)
            ),
            reducer='dot'
        )


class LabelAwareCSVWriterReport[I: Item](CSVWriterReport[I]):
    """Handles writing labeled CSV reports based on provided data.

    This class extends `CSVWriterReport` and is capable of splitting input entries
    based on their associated labels. For each unique label found in the input
    entries, a separate labeled CSV file will be created. The output will include
    only the entries containing the corresponding label, with headers derived from
    the keys in the labeled entries.

    Attributes:
        name (str): The name identifying the report or writer instance.
        config (CSVWriterConfiguration): Configuration settings for the CSV writer,
            including the output path, file encoding, and delimiter.
    """
    def __init__(self, name: str, config: CSVWriterConfiguration):
        """
        Represents a CSV file writer that extends a generic writer class.

        This class is designed to handle writing data to a CSV file, utilizing the
        configuration provided through the CSVWriterConfiguration object. It ensures
        the correct setup for the file output and inherits base functionality from
        its parent writer class.

        Args:
            name: Name of the writer instance.
            config: Configuration object specific to CSV writing.
        """
        super().__init__(name, config)

    def close(self) -> None:
        """
        Writes labeled entries from normalized data into separate CSV files.

        This method processes normalized entries by extracting unique labels from
        the '_labels' field of each entry. It groups entries by each label and writes
        them into separate CSV files. Each CSV file is named after the original file
        name suffixed with the corresponding label. The files are created using the
        configuration specified in `self.config`.

        Attributes:
            entries (Sequence[dict[str, str]]): A sequence of normalized dictionary
                entries processed for grouping and writing operations.
            labels (set[str]): A set of unique label strings extracted from the
                '_labels' field of the `entries`.
            labeled_entries (Sequence[dict[str, str]]): A group of entries associated
                with a specific label.
            header (Sequence[str]): A sorted sequence of all unique keys from the
                labeled entries, used as the CSV file header.
            writer (DictWriter): A CSV DictWriter initialized to write the header and
                rows to the file.

        """
        entries: Sequence[dict[str, str]] = self._normalize_entries()
        labels: set[str] = {label for entry in entries for label in entry.get('_labels', '').split(',')}
        for label in labels:
            labeled_entries: Sequence[dict[str, str]] = tuple(
                entry for entry in entries if label in entry.get('_labels', ''))
            header: Sequence[str] = sorted({key for entry in labeled_entries for key in entry})
            with open(self.config.path.with_name(f'{self.config.path.stem}_{label}.csv'), encoding=self.config.encoding,
                      mode='w', newline='') as out:
                writer: DictWriter = DictWriter(out, header, delimiter=self.config.delimiter, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(labeled_entries)


class YAMLWriterConfiguration(FilesystemWriterConfiguration):
    """Handles the configuration for writing YAML files to the filesystem.

    This class extends FilesystemWriterConfiguration, adding specific YAML
    configuration options, such as the default flow style for serialization.
    It is used to define the settings required for writing YAML data to a file.

    Attributes:
        path (Path): The file path where the YAML content will be written.
        encoding (str): The character encoding used when writing to the file.
        default_flow_style (bool): Indicates if the YAML should be written in default
            flow style (block or inline).
    """
    def __init__(self, path: Path, encoding: str = 'utf-8', default_flow_style: bool = False):
        """
        Represents a class to handle initialization of a path with specific encoding and default flow
        style for YAML processing.

        Attributes:
            path (Path): A path object representing the location to be processed.
            encoding (str): Text encoding to be used for file operations.
            default_flow_style (bool): Indicates whether to use default flow style for YAML output.

        Args:
            path: Path object indicating the location to work with.
            encoding: Encoding format for text processing. Defaults to 'utf-8'.
            default_flow_style: Flag indicating whether to use default flow style for
                YAML operations. Defaults to False.
        """
        super().__init__(path, encoding)
        self._default_flow_style = default_flow_style

    @property
    def default_flow_style(self) -> bool:
        """
        Gets the default flow style for YAML representation.

        The default flow style determines whether the YAML output will use a
        block or flow style for formatting. This is a read-only property.

        Returns:
            bool: The current default flow style setting.
        """
        return self._default_flow_style


class YAMLWriterReport[I: Item](FilesystemWriterReport[I]):
    """Class responsible for writing reports in YAML format.

    This class extends FilesystemWriterReport with additional functionality to
    serialize data into YAML and write it to a specified file. It employs the PyYAML
    library to handle the YAML serialization and supports customization via the
    YAMLWriterConfiguration object. The generated YAML content includes the serialized
    representation of items, their associated facts, and labels.

    Attributes:
        name (str): The name of the report writer.
        config (YAMLWriterConfiguration): Configuration for YAML serialization, such as
            file path, encoding, and formatting options.
    """
    def __init__(self, name: str, config: YAMLWriterConfiguration):
        """
        Initializes a YAMLWriter instance.

        This constructor sets up the YAMLWriter with a name and a configuration object.
        It inherits from its parent class and ensures that the necessary parameters are
        properly initialized.

        Args:
            name: The name assigned to the YAMLWriter instance.
            config: The configuration object of type YAMLWriterConfiguration
                used to initialize the instance.

        """
        super().__init__(name, config)

    def close(self) -> None:
        """
        Closes the resource by saving its current state to a YAML file.

        The method serializes the current entries of the resource and writes
        them into a YAML file specified by the configuration. This ensures
        that any changes made to entries during the execution of the program
        are persisted.

        Args:
            None

        Returns:
            None
        """
        with open(self.config.path, 'w', encoding=self.config.encoding) as out:
            safe_dump_all(
                map(self._convert_entry, self._get_entries()),
                out,
                default_flow_style=self.config.default_flow_style
            )

    def _convert_entry(self, item: I) -> dict[str, JSONType]:
        """
        Converts a given item into a dictionary representation with serialized data,
        facts, and sorted labels. The method is intended for internal use within the
        application for standardized conversion of entry objects.

        Args:
            item: Input object of type I, representing the entity to be converted. It
                must provide a `serialize` method, a `facts` attribute that includes
                key-value pairs, and a `labels` attribute containing a collection of
                labels.

        Returns:
            dict[str, JSONType]: A dictionary containing the serialized representation
            of the input item under `item`, a dictionary of key-value pairs from the
            item’s facts under `facts`, and a sorted list of the item’s labels under
            `labels`.
        """
        return dict(item=item.serialize(), facts=dict(item.facts.items()), labels=sorted(item.labels))
