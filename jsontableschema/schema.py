# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import json
from copy import deepcopy
from .field import Field
from .validate import validate
from . import compat
from . import helpers
from . import exceptions


# Module API

class Schema(object):
    """JSON Table Schema schema representation.

    Raises:
        exceptions.InvalidJSONError
        exceptions.SchemaValidationError

    Args:
        descriptor (dict/str): schema descriptor/path/url

    """

    # Public

    def __init__(self, descriptor):

        # Set attributes
        self.__descriptor = deepcopy(helpers.load_json_source(descriptor))
        self.__fields = None

        # Validate
        validate(self.__descriptor)

    @property
    def descriptor(self):
        """dict: schema descriptor
        """
        return self.__descriptor

    def convert_row(self, row, no_fail_fast=False):
        """Convert row to schema types.

        Args:
            row (mixed[]): array of values
            no_fail_fast (bool): collect all error

        Raises:
            exceptions.InvalidCastError
            exceptions.MultipleInvalid (no_fail_fast=True)

        Returns:
            mixed[]: converted row tuple

        """

        # Prepare
        errors = []

        # Check row length
        if len(row) != len(self.fields):
            message = 'Row length (%s) doesn\'t match fields count (%s)'
            message = message % (len(row), len(self.fields))
            exception = exceptions.InvalidCastError(message)
            if not no_fail_fast:
                raise exception
            errors.append(exception)

        # Convert
        result = []
        if not errors:
            for field, value in zip(self.fields, row):
                try:
                    result.append(field.convert_value(value))
                except exceptions.InvalidCastError as exception:
                    if not no_fail_fast:
                        raise
                    errors.append(exception)

        # Raise
        if errors:
            raise exceptions.MultipleInvalid(errors=errors)

        return tuple(result)

    @property
    def fields(self):
        """Field[]: field instances
        """
        if self.__fields is None:
            self.__fields = [Field(fd) for fd in self.__descriptor['fields']]
        return self.__fields

    def get_field(self, name):
        """Return field by name.

        Args:
            name (str): field name

        Returns:
            None/Field: return field instance or
                None if field with name doesn't exist

        """
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def has_field(self, name):
        """Check if field exists.

        Args:
            name (str): field name

        Returns:
            bool: existence of field

        """
        return self.get_field(name) is not None

    @property
    def headers(self):
        """str[]: field names (headers)
        """
        return [field.name for field in self.fields]

    @property
    def primary_key(self):
        """str[]: primary key
        """
        primary_key = self.__descriptor.get('primaryKey', [])
        if isinstance(primary_key, compat.str):
            primary_key = [primary_key]
        return primary_key

    @property
    def foreign_keys(self):
        """dict[]: foreign keys
        """
        return self.__descriptor.get('foreignKeys', [])

    def save(self, target):
        """Save schema descriptor.

        Args:
            target (str): file path

        """
        mode = 'w'
        encoding = 'utf-8'
        if compat.is_py2:
            mode = 'wb'
            encoding = None
        helpers.ensure_dir(target)
        with io.open(target, mode=mode, encoding=encoding) as file:
            json.dump(self.__descriptor, file, indent=4)
