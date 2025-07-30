import requests
from bs4 import BeautifulSoup

def get_main_title(ttid: str) -> str:
    url = f"https://www.imdb.com/title/{ttid}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("span", attrs={"data-testid": "hero__primary-text"})

    if not title_tag:
        raise ValueError(f"Title not found for {ttid}")

    return title_tag.get_text(strip=True)
