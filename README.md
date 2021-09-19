# QGG Demo
## 開發
### 前端
```sh
# npm install
export REACT_APP_DEV_API_URI=http://140.120.13.253:16004
PORT=16005 npm start
```
### 後端
```sh
# pip install -r  requirements.txt
# python -c"import stanza;stanza.download('en')"
uvicorn server:app --reload --host=0.0.0.0 --port=16004
```
## 部署
```
docker-compose up -d --build
```