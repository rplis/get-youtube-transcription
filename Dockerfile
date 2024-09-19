FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    python3 \
    python3-pip \
    ffmpeg \
    wget \
    tzdata

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN git clone https://github.com/ggerganov/whisper.cpp.git /whisper.cpp
WORKDIR /whisper.cpp

RUN make

# Download the model file
RUN mkdir -p /whisper.cpp/models && \
    wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin -O /whisper.cpp/models/ggml-base.en.bin

RUN pip3 install flask yt-dlp

COPY app.py /app/app.py

WORKDIR /app

# Set appropriate permissions
RUN chmod +x /whisper.cpp/main
RUN chmod 644 /whisper.cpp/models/ggml-base.en.bin
RUN chmod 777 /app

# Final check for model file and permissions
RUN ls -l /whisper.cpp/models/ggml-base.en.bin
RUN ls -l /whisper.cpp/main

CMD ["python3", "app.py"]