import gensim
from gensim.models import word2vec
from pymorphy2 import MorphAnalyzer
from textblob import TextBlob
import nltk
from langdetect import detect
from nltk import pos_tag


nltk.download('averaged_perceptron_tagger')
nltk.download('tagsets')


# соотносим части речи
def map_parts_of_speech(tag):
    if tag.startswith('VB'):
        return "VERB"
    mapper = {
        "ADJF": "ADJ",
        "ADJS": "ADJ",
        "INFN": "VERB",
        "CC": 'CONJ',
        "NN": 'NOUN',
        "JJ": "ADJ"
    }

    if tag in mapper:
        return mapper[tag]
    return tag


# добавляем к слову часть речи
def word_add_part_of_speech(target_word, lang='en'):
    if lang == 'en':
        tag = pos_tag([target_word])
        return target_word + "_" + map_parts_of_speech(tag[0][1])

    morph = MorphAnalyzer()
    return target_word + "_" + map_parts_of_speech(morph.parse(target_word)[0].tag.POS)


# определяем язык
def detect_language(raw_text):
    return detect(raw_text)


# удаляем части речи, которые мы использовали в модели, для того, чтобы пользователь не видел служебные надписи с
# частями речи
def get_human_readable_form(res):
    return list(map(lambda word: word.split("_", 1)[0], res))


def start(word_to_decode):
    """
    Коды ответа для сервера:
    всё успешно, синонимы найдены = 1
    язык не поддерживается = -1
    слово не найдено в используемой модели = -2
    """
    # определяем язык для того, чтобы загрузить правильную модель
    language = detect_language(word_to_decode)
    print('language: ', language)
    # если язык русский, грузим русскую модель
    if language == 'ru':
        path = 'models/russian_model.bin'
    # если английский язык
    elif language == 'en':
        path = 'models/english_model.bin'
    else:
        # если неподдерживаемый язык
        return {
            "code": -1,
            "message": "This language is not supported"
        }

    # подготавливаем слово для модели, добавляя часть речи
    word_to_decode = word_add_part_of_speech(word_to_decode.lower(), language)

    # загружаем модель
    model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=True)

    result = []
    # ищем синонимы
    if word_to_decode in model:
        for res in model.most_similar(positive=[word_to_decode], topn=10):
            print(f"{res[0]}: {res[1]}")
            # собираем синонимы в одной переменной
            result.append(res[0])
        return {
            "code": 1,
            "result": get_human_readable_form(result),
            "language": language
        }
    else:
        # если слова нет в нашей модели
        return {
            "code": -2,
            "message": "No such word in out dictionary"
        }
