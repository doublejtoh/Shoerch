FROM ubuntu:latest
MAINTAINER doublejtoh "doublejtoh@naver.com"
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev locales \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
RUN locale-gen ko_KR.UTF-8
ENV LC_ALL ko_KR.UTF-8
RUN mkdir -p /Users/jeongjoonhyun/PycharmProjects/models
RUN mkdir -p /Users/jeongjoonhyun/Desktop/TIMBERLAND_data/TIMBERLAND-batches-bin/
RUN mkdir -p /Users/jeongjoonhyun/Desktop/TIMBERLAND_model
RUN mkdir -p /Users/jeongjoonhyun/PycharmProjects/shoefinder
COPY models /Users/jeongjoonhyun/PycharmProjects/models
COPY shoefinder /Users/jeongjoonhyun/PycharmProjects/shoefinder
COPY TIMBERLAND_model /Users/jeongjoonhyun/Desktop/TIMBERLAND_model
WORKDIR /Users/jeongjoonhyun/PycharmProjects/shoefinder
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["server.py"]
