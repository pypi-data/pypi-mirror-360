import subprocess
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError


class IMDbScraperError(Exception):
    pass


class IMDbNotAvailableError(IMDbScraperError):
    pass


class IMDbNotFoundError(IMDbScraperError):
    pass


class IMDbStructureChangedError(IMDbScraperError):
    pass


class IMDbAlternateTitlesNotFoundError(IMDbScraperError):
    pass


def ensure_playwright_browser_installed():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        raise RuntimeError(
            "Не удалось установить браузер для Playwright. Установи вручную: `playwright install chromium`") from e


def _get_alternate_titles_sync(imdb_id: str) -> list[tuple[str, str]]:
    """
    Внутренняя функция для синхронного получения альтернативных названий.
    Запускается в отдельном потоке, чтобы избежать конфликтов с event loop.
    """
    url = f"https://www.imdb.com/title/{imdb_id}/releaseinfo/"

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except PlaywrightError as e:
                raise IMDbScraperError(f"Не удалось запустить браузер Playwright: {e}")

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()

            try:
                response = page.goto(url, wait_until="networkidle", timeout=10000)
                if response is None or response.status >= 500:
                    raise IMDbNotAvailableError(
                        f"IMDb сейчас недоступен (status: {response.status if response else 'No Response'})")
                if response.status == 404:
                    raise IMDbNotFoundError(f"Фильм с IMDb ID '{imdb_id}' не найден (404 Not Found)")
            except PlaywrightTimeoutError:
                raise IMDbNotAvailableError("Таймаут при загрузке IMDb страницы")

            all_buttons = page.locator("button.ipc-see-more__button:has(span:text('All'))")
            try:
                all_buttons.nth(1).wait_for(timeout=5000)
            except PlaywrightTimeoutError:
                raise IMDbAlternateTitlesNotFoundError(
                    "Кнопка 'All' для альтернативных названий не найдена. Возможно, нет альтернативных названий.")

            before_count = page.locator("li.ipc-metadata-list__item").count()
            all_buttons.nth(1).click()

            try:
                page.wait_for_function(
                    f"() => document.querySelectorAll('li.ipc-metadata-list__item').length > {before_count}",
                    timeout=5000
                )
            except PlaywrightTimeoutError:
                raise IMDbStructureChangedError(
                    "После клика по кнопке список названий не увеличился. Возможно, изменилась структура IMDb страницы.")

            try:
                page.locator("li.ipc-metadata-list__item").first.wait_for(timeout=5000)
            except PlaywrightTimeoutError:
                raise IMDbStructureChangedError(
                    "Не удалось найти элементы списка названий. Вероятно, изменился HTML IMDb.")

            items = page.locator("li.ipc-metadata-list__item")
            results = []

            for i in range(items.count()):
                item = items.nth(i)
                try:
                    label = item.locator("span.ipc-metadata-list-item__label").inner_text(timeout=100)
                    title = item.locator("span.ipc-metadata-list-item__list-content-item").inner_text(timeout=100)

                    label = "original" if "(original title)" in label.lower() else label.strip().lower()
                    results.append((label, title.strip()))
                except PlaywrightTimeoutError:
                    continue

            browser.close()

            if not results:
                raise IMDbAlternateTitlesNotFoundError("Не найдено ни одного альтернативного названия.")

            return results

    except IMDbScraperError as e:
        raise
    except PlaywrightError as e:
        raise IMDbScraperError(f"Внутренняя ошибка Playwright: {e}")
    except Exception as e:
        raise IMDbScraperError(f"Неизвестная ошибка при парсинге IMDb: {e}")


def get_alternate_titles(imdb_id: str) -> list[tuple[str, str]]:
    """
    Получает альтернативные названия фильма по IMDb ID (например: "tt1375666").
    Возвращает список кортежей (код страны или "original", название).

    Эта функция автоматически определяет, находится ли она в asyncio event loop,
    и запускает Playwright в отдельном потоке при необходимости.
    """
    try:
        # Проверяем, есть ли активный event loop
        loop = asyncio.get_running_loop()

        # Если мы в event loop, запускаем в отдельном потоке
        if loop.is_running():
            with ThreadPoolExecutor() as executor:
                future = executor.submit(_run_in_new_thread, imdb_id)
                return future.result()
        else:
            # Если нет активного event loop, запускаем напрямую
            return _get_alternate_titles_sync(imdb_id)
    except RuntimeError:
        # Нет активного event loop, запускаем напрямую
        return _get_alternate_titles_sync(imdb_id)


def _run_in_new_thread(imdb_id: str) -> list[tuple[str, str]]:
    """
    Запускает парсер в новом потоке с собственным event loop.
    Это необходимо для избежания конфликтов с основным asyncio event loop.
    """

    def thread_target():
        # Создаем новый event loop для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            return _get_alternate_titles_sync(imdb_id)
        finally:
            loop.close()

    # Запускаем в отдельном потоке
    result = []
    exception = None

    def run_target():
        nonlocal result, exception
        try:
            result = thread_target()
        except Exception as e:
            exception = e

    thread = threading.Thread(target=run_target)
    thread.start()
    thread.join()

    if exception:
        raise exception

    return result