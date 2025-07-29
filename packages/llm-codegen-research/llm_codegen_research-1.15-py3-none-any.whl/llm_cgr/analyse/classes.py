"""Classes for handling markdown responses from LLMs."""

from dataclasses import dataclass

from llm_cgr.analyse.languages import analyse_code
from llm_cgr.analyse.regexes import CODE_BLOCK_REGEX
from llm_cgr.defaults import DEFAULT_CODEBLOCK_LANGUAGE


@dataclass
class CodeBlock:
    """
    A class to represent a block of code with it's language.
    """

    language: str | None
    text: str
    valid: bool | None  # None if validity unknown, language not supported
    error: str | None  # only set if not valid
    std_libs: list[str]
    ext_libs: list[str]
    lib_usage: dict[str, list[dict]]

    def __init__(
        self,
        language: str | None,
        text: str,
        default_language: str | None = DEFAULT_CODEBLOCK_LANGUAGE,
    ):
        self.language = language.strip().lower() if language else None
        self.text = text.strip()

        code_data = analyse_code(
            code=self.text,
            language=self.language or default_language,
        )

        if self.language is None and not code_data.valid:
            # if we hit errors after defaulting the language, ignore the results!
            self.valid = None
            self.error = None
            self.std_libs = []
            self.ext_libs = []
            self.lib_usage = {}

        else:
            self.language = self.language or default_language
            self.valid = code_data.valid
            self.error = code_data.error
            self.std_libs = code_data.std_libs
            self.ext_libs = code_data.ext_libs
            self.lib_usage = code_data.lib_usage

    def __repr__(self):
        _language = f"language={self.language or 'unspecified'}"
        _lines = f"lines={len(self.text.splitlines())}"
        return f"{self.__class__.__name__}({_language}, {_lines})"

    def __str__(self):
        return self.text

    @property
    def markdown(self):
        return f"```{self.language or ''}\n{self.text}\n```"


@dataclass
class Markdown:
    """
    A class to hold a markdown response from an LLM as a series of text and code blocks.
    """

    text: str
    code_blocks: list[CodeBlock]
    code_errors: list[str]
    languages: list[str]

    def __init__(
        self,
        text: str,
        default_codeblock_language: str | None = DEFAULT_CODEBLOCK_LANGUAGE,
    ):
        """
        Initialise the MarkdownResponse object with the text and code blocks.
        Use `codeblock_language` when no language is specified for a code block.
        """
        self.text = text
        self.code_blocks = self.extract_code_blocks(
            response=text,
            default_language=default_codeblock_language,
        )
        self.code_errors = [
            f"{i}: {cb.error}" for i, cb in enumerate(self.code_blocks) if cb.error
        ]
        self.languages = sorted(
            list({bl.language for bl in self.code_blocks if bl.language})
        )

    def __repr__(self):
        _lines = f"lines={len(self.text.splitlines())}"
        _code_blocks = f"code_blocks={len(self.code_blocks)}"
        _languages = f"languages={','.join(self.languages)}"
        return f"{self.__class__.__name__}({_lines}, {_code_blocks}, {_languages})"

    def __str__(self):
        return self.text

    @staticmethod
    def extract_code_blocks(
        response: str,
        default_language: str | None = DEFAULT_CODEBLOCK_LANGUAGE,
    ) -> list[CodeBlock]:
        """
        Extract the code blocks from the markdown formatted text.
        """
        matches = CODE_BLOCK_REGEX.findall(string=response)
        blocks = []
        for match in matches:
            language, text = match
            blocks.append(
                CodeBlock(
                    language=language if language else None,
                    text=text,
                    default_language=default_language,
                )
            )
        return blocks

    def first_code_block(self, language: str) -> CodeBlock | None:
        """
        Return the first code block of a certain language in the response.
        """
        for block in self.code_blocks:
            if block.language == language:
                return block

        return None
