# ----------------------------------------------------------------------------------------
# Python-Backpack - Custom Exceptions
# Maximiliano Rocamora / maxirocamora@gmail.com
# https://github.com/MaxRocamora/python-backpack
# ----------------------------------------------------------------------------------------


class EnvironmentVariableNotFoundError(Exception):
    def __init__(self, var_name: str) -> None:
        """Error Raised when a required environment variable is missing from os.

        Args:
            var_name (str): name of the required variable missing
        """
        self.var_name = var_name
        self.message = f'Required Environment Variable [{var_name}] not found.'
        super().__init__(self.message)

    def __str__(self):
        """Return the error message."""
        return self.message


class ApplicationNotFoundError(Exception):
    def __init__(self, app_name: str) -> None:
        """Error Raised when an Application Name required is not found.

        Args:
            app_name (str): name of the required application missing
        """
        self.app_name = app_name
        self.message = f'Application ({app_name}) not found.'
        super().__init__(self.message)

    def __str__(self):
        """Return the error message."""
        return self.message
