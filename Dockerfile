FROM iskoldt/aeneas:latest

COPY ./ /app/
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gawk bsdmainutils wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir -r /app/requirements.txt && python download_punkt.py 
    && wget git.io/trans -O /app/trans && chmod +x /app/trans \
    && mkdir /data

WORKDIR /app
ENTRYPOINT ["python3", "bifrost.py"]
