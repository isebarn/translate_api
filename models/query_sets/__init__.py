from googletrans import Translator
from mongoengine import QuerySet
from functools import cache

translator = Translator()


@cache
def translate(text):
    return translator.translate(text, src="pt", dest="en").text


class BookQuerySet(QuerySet):
    pass


class TextQuerySet(QuerySet):
    def default(self, cls, filters):
        texts = cls.get(**filters)

        untranslated = [x for x in texts if not x.translation]
        translations = translator.translate(
            [x.text for x in untranslated], src="pt", dest="en"
        )
        [
            setattr(item, "translation", translation.text)
            for item, translation in zip(untranslated, translations)
        ]
        [x.save() for x in untranslated]

        return [x.to_json() for x in texts]

    def word(self, cls, filters):
        return [{"translation": translate(filters.pop("word"))}]
