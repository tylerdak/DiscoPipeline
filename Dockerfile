FROM python:3.10

ENV HOME /root
WORKDIR /root
COPY . .

# if you ever end up adding extra dependencies that aren't installed put them here i suppose
RUN pip install -r requirements.txt

EXPOSE 8081

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD python -u main.py