FROM python:3.7

WORKDIR /streamlitResume

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8501

COPY . /streamlitResume

ENTRYPOINT ["streamlit","run"]

CMD ["resumeParserStreamlit.py"]