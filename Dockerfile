FROM python:3.7-stretch

RUN pip install pymongo Flask flask-cors pyxDamerauLevenshtein textdistance[extras]

RUN mkdir /spellchecker
WORKDIR /spellchecker

COPY dao dao
COPY suggester suggester

COPY app.py app.py

ENV MONGODB_HOST mongo
ENV MONGODB_DB default
ENV MONGODB_WORDS_BY_LENGTH_COLLECTION words_by_length

ENV MONGODB_USERNAME spellchecker_suggester
ENV MONGODB_PASSWORD spellchecker_suggester

ENV SERVER_PORT 8282

ENV DEBUG true

CMD ["python3", "-u", "app.py"]