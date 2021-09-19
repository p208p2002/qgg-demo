# QGG Demo
## 開發
```
export REACT_APP_DEV_API_URI=http://140.120.13.253:16004/generate
pip install -r  requirements.txt
python -c"import stanza;stanza.download('en')"
uvicorn server:app --reload --host=0.0.0.0 --port=16004
```
## 部署
```
docker-compose up -d --build
```