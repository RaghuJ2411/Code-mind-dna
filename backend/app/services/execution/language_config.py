from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageConfig:
    name: str
    provider_name: str
    extension: str
    source_file_name: str
    compile_command: tuple[str, ...] | None = None
    run_command: tuple[str, ...] | None = None


SUPPORTED_LANGUAGES: dict[str, LanguageConfig] = {
    "python": LanguageConfig(name="python", provider_name="python", extension="py", source_file_name="main.py"),
    "javascript": LanguageConfig(name="javascript", provider_name="node", extension="js", source_file_name="main.js"),
    "java": LanguageConfig(
        name="java",
        provider_name="java",
        extension="java",
        source_file_name="Main.java",
        compile_command=("javac",),
        run_command=("java",),
    ),
}


def get_language_config(language: str) -> LanguageConfig:
    key = (language or "").strip().lower()
    if key not in SUPPORTED_LANGUAGES:
        raise ValueError("Unsupported language")
    return SUPPORTED_LANGUAGES[key]


def validate_language(language: str) -> str:
    return get_language_config(language).name
