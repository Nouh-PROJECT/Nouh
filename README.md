# Nouh LMS
<br>

### 서비스 환경 구성 가이드
- `config.py` 추가
- api키 추가 : `my api key` 수정 후 실행
<br>

 ```
 # flask/app/views/chatbot.py

 openai_api_key="my api key"
 ```

- flask/app/tmp 디렉토리 추가
- flask/app/tmp/uploads 디렉토리 추가

### 서비스 실행
```
sudo bash run_docker
```

