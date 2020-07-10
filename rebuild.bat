docker build -t audiotest:latest .
docker tag audiotest:latest audiotoolstest.azurecr.io/audiotest:latest
docker push audiotoolstest.azurecr.io/audiotest:latest
