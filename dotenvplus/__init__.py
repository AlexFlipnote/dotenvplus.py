import os
import re

from typing import Any, Iterator, Optional, Tuple, List, Dict

__version__ = "0.0.4"


class ParsingError(Exception):
    pass


class DotEnv:
    """
    DotEnv is a dotenv parser for Python with additional type support.

    It supports parsing of string, integer, float, and boolean values.

    Arguments
    ---------
    path: `str` | `None`
        The path to the .env file.
        If none are provided, it defaults to `./.env`
    update_system_env: `bool`
        If True, it will load the values to the instance's environment variables.
        Be warned that this will only support string values.
    handle_key_not_found: `bool`
        If True, it will make the object return `None` for any key that is not found.
        Essentially simulating `dict().get("Key", None)`

    Raises
    ------
    `FileNotFoundError`
        If the file_path is not a valid path.
    `ParsingError`
        If one of the values cannot be parsed.
    """
    def __init__(
        self,
        path: Optional[str] = None,
        *,
        update_system_env: bool = False,
        handle_key_not_found: bool = False,
    ):
        # General values
        self.__env: dict[str, Any] = {}
        self.__frozen: bool = False

        # Defined values
        self.__quotes: Tuple[str, ...] = ('"', "'")
        self.__bools: Tuple[str, ...] = ("true", "false")
        self.__none: Tuple[str, ...] = ("null", "none", "nil", "undefined")

        # RegEx patterns
        self.__re_keyvar = re.compile(r"^\s*([a-zA-Z0-9_]*)\s*=\s*(.+)$")
        self.__re_isdigit = re.compile(r"^(?:-)?\d+$")
        self.__re_isfloat = re.compile(r"^(?:-)?\d+\.\d+$")
        self.__re_var_call = re.compile(r"\$\{([a-zA-Z0-9_]*)\}")

        # Config for the parser
        self.__path: str = path or ".env"
        self.__handle_key_not_found: bool = handle_key_not_found

        # Finally, the parser
        self.__parser()

        if update_system_env:
            os.environ.update({
                key: str(value)
                for key, value in self.__env.items()
            })

    def __repr__(self) -> str:
        return f"<DotEnv data={self.__env}>"

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        if self.__handle_key_not_found:
            return self.__env.get(key, None)
        return self.__env[key]

    def __str__(self) -> str:
        return str(self.__env)

    def __int__(self) -> int:
        return len(self.__env)

    def __len__(self) -> int:
        return len(self.__env)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter(self.__env.items())

    def __contains__(self, key: str) -> bool:
        return key in self.__env

    def __setitem__(self, key: str, value: Any) -> None:  # noqa: ANN401
        if self.__frozen:
            raise AttributeError("This DotEnv object is read-only.")
        self.__env[key] = value

    def __delitem__(self, key: str) -> None:
        if self.__frozen:
            raise AttributeError("This DotEnv object is read-only.")
        del self.__env[key]

    @property
    def keys(self) -> List[str]:
        """ `list[str]`: Returns a list of the keys. """
        return list(self.__env.keys())

    @property
    def values(self) -> List[Any]:
        """ `list[Any]`: Returns a list of the values. """
        return list(self.__env.values())

    def get(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
        """ `Any`: Return the value for key if key is in the dictionary, else default. """
        return self.__env.get(key, default)

    def items(self) -> List[Tuple[str, Any]]:
        """ `list[tuple[str, Any]]`: Returns a list of the key-value pairs. """
        return list(self.__env.items())

    def copy(self) -> Dict[str, Any]:
        """ `dict[str, Any]`: Returns a shallow copy of the parsed values. """
        return self.__env.copy()

    def to_dict(self) -> Dict[str, Any]:
        """ `dict`: Returns a dictionary of the parsed values. """
        return self.__env

    def __parser(self) -> None:
        """
        Parse the .env file and store the values in a dictionary.

        The keys are accessible later by using the square bracket notation
        directly on the DotEnv object.

        Raises
        ------
        `FileNotFoundError`
            If the file_path is not a valid path.
        `ParsingError`
            If one of the values cannot be parsed.
        """
        with open(self.__path, encoding="utf-8") as f:
            data: list[str] = f.readlines()

        for line_no, line in enumerate(data, start=1):
            line = line.strip()

            if line.startswith("#") or line == "":
                # Ignore comment or empty line
                continue

            find_kv = self.__re_keyvar.search(line)
            if not find_kv:
                raise ParsingError(
                    f"Error at line {line_no}: "
                    f"Expected key=value format, got '{line}'"
                )

            key, value = find_kv.groups()

            # Replace any variables in the value
            value = self.__re_var_call.sub(
                lambda m: str(self.__env.get(m.group(1), "undefined")),
                str(value)
            )

            # Remove comment on the value itself too (if any)
            value = value.split("#")[0].strip()

            if (
                value.startswith(self.__quotes) and
                value.endswith(self.__quotes)
            ):
                # Remove quotes and skip the parsing step
                value = value[1:-1]

            else:
                # String is not forced, go ahead and parse it
                if self.__re_isdigit.search(value):
                    value = int(value)

                elif self.__re_isfloat.search(value):
                    value = float(value)

                elif value.lower() in self.__bools:
                    value = value.lower() == "true"

                elif value.lower() in self.__none:
                    value = None

            self.__env[key] = value

        self.__frozen = True
