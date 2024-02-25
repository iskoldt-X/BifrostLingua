FROM iskoldt/aeneas:latest

COPY ./ /app/

RUN apt-get update && apt-get install -y \
    gawk bsdmainutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir -r /app/requirements.txt && python download_punkt.py \
    && mkdir /data

WORKDIR /app
ENTRYPOINT ["python3", "bifrost.py"]
CMD ["/data/audio.mp3", "/data/text.txt"]
