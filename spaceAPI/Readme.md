docker build --no-cache -t spaceapi .

docker run -p 1341:1341 -d -t spaceapi
