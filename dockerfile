FROM python:3.9.17-slim-bullseye

RUN mkdir /app

COPY data /app/data
COPY src /app/src
COPY app.py /app/
COPY requirements.txt /app/
COPY .streamlit /app/.streamlit

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]