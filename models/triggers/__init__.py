from models import Book
from models import Text
from mongoengine.signals import post_save
from mongoengine.signals import pre_save
from requests import get
from requests import post
from epub2txt import epub2txt
from nltk import download
from nltk import sent_tokenize

download("book")


def download_book(sender, document, created):
    if created:
        book = epub2txt(document.to_json()["url"])
        text = ""
        for line in book:
            text += line.replace("\n", "")

        text = sent_tokenize(text)

        Text.objects.insert(
            [
                Text(**{"text": sentence, "index": index, "book": document.id})
                for index, sentence in enumerate(text)
            ]
        )

        document.length = len(text)
        document.save()


post_save.connect(download_book, sender=Book)
