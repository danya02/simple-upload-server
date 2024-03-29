FROM python:3.9.2
COPY requirements.txt /
RUN pip3 install --no-cache -r /requirements.txt
RUN wget https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css


WORKDIR /
COPY templates/ /templates
ENTRYPOINT ["gunicorn", "main:app"]
COPY main.py /
