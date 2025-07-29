from llm_cgr.analyse.languages.code_data import CodeData
from llm_cgr.analyse.languages.python import analyse_python_code


def analyse_code(code: str, language: str | None) -> CodeData:
    """
    Analyse code based on the language.
    """
    try:
        if language == "python":
            return analyse_python_code(code=code)
    except Exception as exc:
        return CodeData(
            valid=False,
            error=str(exc),
        )

    return CodeData()


__all__ = [
    "analyse_code",
    "CodeData",
]
