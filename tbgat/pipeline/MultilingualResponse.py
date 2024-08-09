from typing import Iterable, Literal, Mapping, TypeVar

_P_cov = TypeVar("_P_cov", covariant=True)


class MultilingualResponse(Mapping[Literal["en", "ru", "uk"], _P_cov]):
    """MultilingualResponse class. A mapping of language codes to responses.
    Responses can be of any type.

    """

    def __init__(self, *, en: _P_cov, ru: _P_cov, uk: _P_cov):
        self._data = {"en": en, "ru": ru, "uk": uk}

    def __getitem__(self, key: Literal["en", "ru", "uk"]) -> _P_cov:
        return self._data[key]

    def __iter__(self) -> Iterable[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)
