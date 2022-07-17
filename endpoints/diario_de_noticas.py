from requests import get

# Third party imports
from flask import request
from flask_restx import Namespace
from flask_restx import Resource
from bs4 import BeautifulSoup
from requests import get
from googletrans import Translator

translator = Translator()

api = Namespace("diario_de_noticas", description="")
base_url = "https://www.dn.pt/"


@api.route("/front_page")
class FrontPageController(Resource):
    def get(self):
        response = get(base_url)

        soup = BeautifulSoup(response.text, features="lxml")

        articles_items = soup.find_all("article")

        articles = [
            {
                "title": article.find("h2", {"class": "t-am-title"}).text,
                "picture": article.find("img").get("src")
                if article.find("img")
                else None,
                "url": base_url + article.find("a", {"class": "t-am-text"})["href"],
            }
            for article in articles_items
            if article.find("h2", {"class": "t-am-title"})
        ]

        return articles


@api.route("/article")
class ArticleController(Resource):
    def post(self):
        response = get(request.get_json()["url"])

        soup = BeautifulSoup(response.text, features="lxml")

        page = soup.find_all("p")

        untranslated = [x.text for x in page if x.text and not x.text.isspace()]
        translations = translator.translate(untranslated, src="pt", dest="en")

        return [
            {"untranslated": untranslated, "translation": translation.text}
            for untranslated, translation in zip(untranslated, translations)
        ]
