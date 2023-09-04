FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /app
ENV PYTHONPATH=/app:$PYTHONPATH
ENV ES_PORT 9200
ENV APP_ENV dev
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY cli_dna_seq ./app/cli_dna_seq
EXPOSE 80
EXPOSE ${ES_PORT}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]