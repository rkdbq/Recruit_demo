## [Deploy Link](http://113.198.66.75:10164/)
- [API Docs](http://113.198.66.75:10164/apidocs/)

## 프로젝트 설치 및 실행 방법

Python Version: 3.12.7

### 패키지 설치
```
pip install requirements.txt
```

### 환경변수 설정

.env.example 참고

```
export SECRET_KEY=<YOUR SECRET KEY TO JWT ENCODE>
export DB_USER=<DB USER>
export DB_PASSWORD=<DB PASSWORD>
```

### 실행
```
python app.py
```

## API 엔드포인트 목록 및 설명

### Application

| Method | Endpoint               | Description          |
|--------|------------------------|----------------------|
| GET    | `/applications/`       | 회원의 지원 내역 조회     |
| POST   | `/applications/`       | 채용 공고에 지원      |
| DELETE | `/applications/{id}`   | 지원 취소            |

### Auth

| Method | Endpoint               | Description          |
|--------|------------------------|----------------------|
| DELETE | `/auth/`               | 사용자 삭제         |
| POST   | `/auth/login`          | 사용자 로그인       |
| GET    | `/auth/profile`        | 사용자 프로필 조회  |
| PUT    | `/auth/profile`        | 사용자 프로필 수정  |
| POST   | `/auth/refresh`        | 액세스 토큰 갱신  |
| POST   | `/auth/register`       | 사용자 등록         |

### Bookmark

| Method | Endpoint               | Description          |
|--------|------------------------|----------------------|
| GET    | `/bookmarks/`          | 북마크 목록 조회   |
| POST   | `/bookmarks/`          | 채용 공고 북마크 추가/제거 |

### Company

| Method | Endpoint               | Description          |
|--------|------------------------|----------------------|
| GET    | `/companies/`          | 모든 회사 목록 조회  |
| POST   | `/companies/`          | 새로운 회사 정보 추가 |
| DELETE | `/companies/{id}`      | 회사 삭제            |

### Job Posting

| Method | Endpoint               | Description          |
|--------|------------------------|----------------------|
| GET    | `/jobs/`               | 채용 공고 목록 조회   |
| POST   | `/jobs/`               | 채용 공고 추가       |
| DELETE | `/jobs/{id}`           | 채용 공고 삭제     |
| PUT    | `/jobs/{id}`           | 채용 공고 수정     |
| GET    | `/jobs/{job_id}`       | 특정 채용 공고 상세 정보 조회 |