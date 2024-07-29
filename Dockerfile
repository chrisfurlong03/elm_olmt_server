FROM python:3.12-bookworm

WORKDIR /usr/src/elm_olmt_server
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","main.py"]
