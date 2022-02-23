from flask import Flask
from flask import render_template, request
from net import start
import sqlite3

con = sqlite3.connect('synonyms.db', check_same_thread=False)  # подключение
cur = con.cursor()


# создаём таблицу для базы данных
def create_table():
    print("CREATING TABLE...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS SYNONYMS (
        synonym TEXT PRIMARY KEY,
        results TEXT,
        target_language TEXT
    )
    """)
    con.commit()


# проверяем, существует ли синоним в нашей базе данных
def check_if_synonym_exists(syn):
    cur.execute("""
        SELECT synonym as s FROM SYNONYMS WHERE s = ? """, (syn,))
    result = cur.fetchall()
    return result


# добавляем синоним в базу данных, если его не существует в ней
def append_new_word(syn, results, lang):
    cur.execute("""
            INSERT INTO SYNONYMS(synonym, results, target_language) VALUES (?, ?, ?)
             """, (syn, results, lang))
    con.commit()


# получаем синонимы, если они уже есть в нашей базе
def get_results_for_word(word):
    cur.execute("""
        SELECT * from SYNONYMS as s where s.synonym = ?
    """, (word, ))
    return cur.fetchall()


app = Flask(__name__)

# отправляем в браузер главную страничку
@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/process', methods=['GET'])
def process_word():
    # получаем слово из формы
    target = request.args.get('word', '')

    # отправляем ошибку, если пришло пустое слово
    if target == '':
        return render_template('error.html', message="Please, provide word")
    # проверяем, если в базе указанный синоним
    db_query_res = check_if_synonym_exists(target)

    if len(db_query_res) == 0:
        # находим синонимы
        processed = start(target)
        print('processed: ', processed)
        # если слово не поддерживается (не английский и не русский язык)
        if processed["code"] == -1:
            return render_template('error.html', message='Unfortunately, this language is not supported.')
        if processed["code"] == -2:
            # если слова нет в модели
            return render_template('error.html', message='Unfortunately, we could not find your word in out dictionary.')
        # добавляем слово в базу данных
        append_new_word(target, " ".join(processed["result"]), processed["language"])
        # отправляем html с результатом
        return render_template('result.html', language=processed["language"], words=processed["result"], word=target)
    else:
        # если в базе данных есть слово,
        res = get_results_for_word(target)
        #
        print("res", res[0][1])
        # отправляем html с результатом
        return render_template('result.html', language=res[0][2], words=res[0][1].split(), word=res[0][0])





