FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        software-properties-common \
        wget \
        gnupg \
        lsb-release \
        curl \
        tzdata \
        nano

RUN apt install python3 python3-pip -y

RUN pip install urllib3 dnspython requests requests_toolbelt --break-system-packages
      
RUN add-apt-repository ppa:ubuntuhandbook1/ffmpeg7 && \
    apt-get update

RUN apt install ffmpeg -y
    
WORKDIR /home/

COPY files/ /home/

RUN chmod 755 /home/o11_v22b1-DRMStuffdocker push pigscanflyyy/o11-ott-streamer:latest
RUN chmod 755 /home/run.sh

CMD ["/home/run.sh"]
