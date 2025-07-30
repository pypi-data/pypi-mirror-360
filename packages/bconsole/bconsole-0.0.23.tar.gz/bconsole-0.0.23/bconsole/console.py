from __future__ import annotations

from functools import partial
from getpass import getpass
from os import system as execute
from sys import stdin, stdout
from typing import Any, Literal, NoReturn, Sequence, TextIO, overload

from unidecode import unidecode

from .core import Erase, Foreground, Modifier
from .utils import find_closest_match, first, format_iter, surround_with

__all__ = ["Console"]


class Console:
    """A helper class to make better looking, and more consistent console output!"""

    @overload
    def __init__(
        self,
        file_out: TextIO = stdout,
        file_in: TextIO = stdin,
        *,
        prompt_color: str,
        input_color: str,
        arrow_color: str,
        error_color: str,
        hint_color: str,
        panic_color: str,
        arrow: str,
    ) -> None: ...

    @overload
    def __init__(
        self, file_out: TextIO = stdout, file_in: TextIO = stdin, **kwargs: str
    ) -> None: ...

    def __init__(
        self, file_out: TextIO = stdout, file_in: TextIO = stdin, **kwargs: str
    ) -> None:
        """
        Initializes a new instance of the Console class.

        ### Args:
            file_out (TextIO, optional): The file to write output to. Defaults to stdout.
            file_in (TextIO, optional): The file to read input from. Defaults to stdin.

        ### **kwargs:
            prompt_color (str, optional): The color to use for prompts. Defaults to Foreground.CYAN.
            input_color (str, optional): The color to use for input. Defaults to Modifier.RESET.
            arrow_color (str, optional): The color to use for arrows. Defaults to Foreground.GREEN + Modifier.BOLD.
            error_color (str, optional): The color to use for errors. Defaults to Foreground.RED.
            hint_color (str, optional): The color to use for hints. Defaults to Foreground.YELLOW.
            panic_color (str, optional): The color to use for panics. Defaults to Foreground.RED + Modifier.BOLD.
            arrow (str, optional): The arrow to use. Defaults to ">>".
        """
        self.file_out = file_out
        self.file_in = file_in

        self.prompt_color: str = kwargs.get("prompt_color", Foreground.CYAN)
        self.input_color: str = kwargs.get("input_color", Modifier.RESET)
        self.arrow_color: str = kwargs.get(
            "arrow_color", Foreground.GREEN + Modifier.BOLD
        )
        self.error_color: str = kwargs.get("error_color", Foreground.RED)
        self.hint_color: str = kwargs.get("hint_color", Foreground.YELLOW)
        self.panic_color: str = kwargs.get(
            "panic_color", Foreground.RED + Modifier.BOLD
        )
        self.arrow_ = kwargs.get("arrow", ">> ")

        self._get_pass = partial(getpass, "")

    def print(
        self,
        text: Any,
        color: str = Modifier.RESET,
        /,
        *,
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """
        Prints the specified text to the console with the specified color.

        ### Args:
            text (Any): The text to print.
            color (str, optional): The color to use. Defaults to Modifier.RESET.
            end (str, optional): The end to use. Defaults to "\n".
            flush (bool, optional): Whether to flush the output. Defaults to False.
        """
        self.file_out.write(self.colorize(text, color) + end)
        _ = flush and self.file_out.flush()

    def input(
        self,
        prompt: str | None = None,
        /,
        *,
        invalid_values: list[str] | None = None,
        ensure_not_empty: bool = True,
        is_password: bool = False,
        allow_extras: bool = False,
    ) -> str:
        """
        Prompts the user for input with the specified prompt.

        ### Args:
            prompt (str): The prompt to display.
            invalid_values (list[str], optional): A list of invalid values. Defaults to None.
            ensure_not_empty (bool, optional): Whether to ensure the input is not empty. Defaults to True.
            is_password (bool, optional): Whether to hide the input. Defaults to False.
            allow_extras (bool, optional): Whether to allow extras, such as typing "clear" to clear the console, and "exit" to exit the program. Defaults to False.

        ### Returns:
            str: The user's input.
        """
        invalid_values = invalid_values or []

        if ensure_not_empty:
            invalid_values.append("")

        if prompt:
            self.print(prompt, self.prompt_color)
            self.arrow(flush=True)

        f = self._get_pass if is_password else self.file_in.readline

        while True:
            match res := f().strip():
                case "cls" | "clear" if allow_extras:
                    self.clear()
                case "exit" | "quit" if allow_extras:
                    exit(0)
                case _ if res in invalid_values:
                    self.error("Invalid value.", hint="Try again.")
                case _:
                    return res

    def password(self, prompt: str | None = None, /) -> str:
        """
        Prompts the user for a password.

        ### Args:
            prompt (str, optional): The prompt to display. Defaults to None.

        ### Returns:
            str: The user's password.
        """
        return self.input(prompt, is_password=True)

    def options(
        self,
        prompt: str,
        /,
        options: Sequence[str] | None = None,
        *,
        show_options: bool = True,
        allow_suggestions: bool = True,
        oxford_comma: bool = True,
        return_style: Literal["raw", "option", "simplified"] = "option",
        option_wrapper: str | None = "[]",
        options_end: str | None = "?",
        choice_end: str | None = ".",
    ) -> str:
        """
        Prompts the user to select an option from a list of options.

        ### Args:
            prompt (str): The prompt to display.
            options (Sequence[str], optional): A `Sequence` of options. Defaults to ["Yes", "No"].
            show_options (bool, optional): Whether to show the options list. Defaults to True.
            allow_suggestions (bool, optional): Whether to show suggestions for the user when they make an invalid selection. Defaults to True.
            oxford_comma (bool, optional): Whether to use the Oxford comma. Defaults to True.
            return_style (Literal["raw", "option", "simplified"], optional): The returning style to use for the selected option. Defaults to "option". Can be "raw", "option", or "simplified". "raw" returns the raw user input, "option" returns the option selected from the options list, and "simplified" returns the first character of the option selected from the options list.
            options_wrapper (str, optional): The wrapper to use around each of the options. Defaults to "[]". Example: "[x] or [y]". Can also be None or empty. Example: "x or y".
            options_end (str, optional): The end to use after the options list. Defaults to "?".
            choice_end (str, optional): The end to use after the chosen option. Defaults to ".".

        ### Examples:
            >>> console.options("Do you wish to continue?")
            Do you wish to continue? [Yes] or [No]?
            >>
            >>> console.options("Do you wish to continue?", show_options=True)  # doesn't show the options list
            Do you wish to continue?
            >>
            >>> console.options("Are you sure about that?", options=["yes", "no", "maybe"], wrapper=None, end='???')
            Are you sure about that? yes, no or maybe???
            >>
            >>> console.options("Are you sure about that?", return_style="simplified") == "y"
            Are you sure about that? [Yes] or [No]?
            >> Yes  # results in console.options returning just "y"
            True

        ### Returns:
            str: The user's selection. Selected from the options list if raw is False, otherwise returns the user's input directly.
        """
        options = options or ["Yes", "No"]
        option_wrapper = option_wrapper or ""

        simplified_options = {
            unidecode(option).casefold().strip(): option.strip() for option in options
        }

        formatted_options = format_iter(
            (surround_with(option, wrapper=option_wrapper) for option in options),
            oxford_comma=oxford_comma,
        )

        while True:
            raw = self.input(
                f"{prompt} {formatted_options}{options_end or ''}"
                if show_options
                else prompt
            )

            proper = unidecode(raw).casefold().strip()

            possible_option = first(
                filter(
                    lambda option: option.startswith(proper),
                    simplified_options.keys(),
                )
            )

            if possible_option:
                chosen_option = simplified_options[possible_option]

                self.erase_lines()
                self.arrow(
                    f"Chosen option: {Modifier.RESET}{chosen_option}{choice_end or ''}",
                    Foreground.MAGENTA,
                )

                match return_style:
                    case "raw":
                        return raw
                    case "option":
                        return chosen_option
                    case "simplified":
                        return chosen_option.lower()[0]

            closest = (
                find_closest_match(proper, simplified_options.keys())
                if allow_suggestions
                else None
            )

            self.error(
                "Invalid option.",
                hint=f"{f'Did you mean {closest}? ' if closest else ''}Choose one among the following options: {formatted_options}.",
            )

    def error(
        self, error: Exception | str, /, *, hint: str = "", same_line: bool = True
    ) -> None:
        """
        Prints an error message to the console.

        ### Args:
            error (Exception | str): The error to print.
            hint (str, optional): A hint to display. Defaults to "".
            same_line (bool, optional): Whether to print the hint on the same line as the error. Defaults to True.
        """
        self.print(error, self.error_color, end=" " if same_line else "\n")
        _ = hint and self.print(hint, self.hint_color)

    def panic(self, reason: Exception | str, /, *, code: int = -1) -> NoReturn:
        """
        Prints an error message to the console and exits the program with the specified code.

        ### Args:
            error (Exception | str): The error to print.
            code (int, optional): The exit code. Defaults to -1.
        """
        self.print(reason, self.panic_color)
        self.enter_to_continue()
        exit(code)

    def arrow(
        self, text: str = "", color: str = Modifier.RESET, /, *, flush: bool = False
    ) -> None:
        """
        Prints an arrow to the console.

        ### Args:
            text (str, optional): The text to display after the arrow. Defaults to "".
            color (str, optional): The color to use. Defaults to Modifier.RESET.
            flush (bool, optional): Whether to flush the output. Defaults to False.
        """
        self.print(self.arrow_, self.arrow_color, end="", flush=flush)
        _ = text and self.print(text, color)

    def actions(self, *args: str) -> None:
        """
        Helper method to print multiple escape codes, joined by newlines.

        ### Args:
            *args (str): The escape codes to print.

        ### Example:
            >>> console.actions(*Erase.lines(2), Cursor.UP + Cursor.LEFT)
        """
        self.print("\n".join(args), end="")

    def enter_to_continue(
        self, text: str = "Press enter to continue...", color: str | None = None
    ) -> None:
        """
        Prompts the user to press enter to continue.

        ### Args:
            text (str, optional): The text to display. Defaults to "Press enter to continue...".
            color (str, optional): The color to use. Defaults to `self.prompt_color`.
        """
        self.print(text, color or self.prompt_color, end="", flush=True)
        self._get_pass()
        self.erase_lines(2)

    def space(self, count: int = 1, /) -> None:
        """
        Skips the specified number of lines.

        ### Args:
            count (int, optional): The number of lines to skip. Defaults to 1.
        """
        self.print("\n" * count, end="")

    def erase_lines(self, count: int = 1, /) -> None:
        """
        Erases the specified number of lines.

        ### Args:
            count (int, optional): The number of lines to erase. Defaults to 1.
        """
        self.actions(*Erase.lines(count))

    def clear(self) -> None:
        """Clears the console."""
        execute("cls||clear")

    def colorize(self, text: Any, /, color: str) -> str:
        """
        Helper method to colorize text.

        ### Args:
            text (str): The text to colorize.
            color (str): The color to use.

        ### Returns:
            str: The colorized text. Simply COLOR + TEXT + RESET.
        """
        return f"{color}{str(text)}{Modifier.RESET}"
