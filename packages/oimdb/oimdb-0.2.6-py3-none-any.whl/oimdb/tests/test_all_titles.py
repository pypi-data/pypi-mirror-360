
from oimdb import get_alternate_titles

def test_get_alternate_titles_real():
    """
    Интеграционный тест: проверяет, что get_alternate_titles возвращает валидные данные с IMDb.
    """
    imdb_id = "tt1375666"
    results = get_alternate_titles(imdb_id)

    assert isinstance(results, list)
    assert len(results) > 0

    for item in results:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert isinstance(item[0], str)
        assert isinstance(item[1], str)

    # Примерно проверим наличие "original" названия среди результатов
    originals = [title for code, title in results if code == "original"]
    assert len(originals) > 0