import requests
from bs4 import BeautifulSoup

def get_rating(ttid: str) -> dict:
    url = f"https://www.imdb.com/title/{ttid}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rating_tag = soup.find("span", attrs={"class": "sc-d541859f-1 imUuxf"})
    popularity_tag = soup.find("div", attrs={"data-testid": "hero-rating-bar__popularity__score"})

    if not rating_tag or not popularity_tag:
        raise ValueError(f"Rating not found for {ttid}")

    rating = float(rating_tag.get_text(strip=True).split("/")[0])
    popularity = int(popularity_tag.get_text(strip=True).replace(",", "").split()[0])

    return {"imdb rating": rating, "popularity": popularity}
