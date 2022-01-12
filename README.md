# QGG Demo
The demo system of [EQGG](https://github.com/p208p2002/Neural-Question-Group-Generation)

[Live Demo](https://qgg-demo.nlpnchu.org)
## Develop
### Front-End
```sh
# npm install
export REACT_APP_DEV_API_URI=http://127.0.0.1:16004
PORT=16005 npm start
```
### Back-End
```sh
# pip install -r  requirements.txt
# python -c"import stanza;stanza.download('en')"
uvicorn server:app --reload --host=0.0.0.0 --port=16004
```
## Deploy
```
docker-compose up --build
```