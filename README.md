# MJU-LMS-Crawler
명지대학교 LMS 출석, 과제 조회

https://mju.timetree.me

Python 3.8.2 에서 작업.
requests, BeautifulSoup 라이브러리 사용 (pip 설치 필요!!)

MJU-LMS-Crawler.py 파일을 텍스트 편집기로 열어 UserID, UserPw 항목을 학번, 비밀번호로 채워넣고 실행.

Change Log
- 20201016 정보 요청 flask API 주소로 변경 HTTPS 적용, CORS 설정 추가 (현재 mju.timetree.me 만 허용)
- 20201015 express, flask 서버 파일 추가
- 20200902 청강 과목이 들어가 있을 경우 list index out of range 에러 발생 FIX
- 20200830 학번만 있어도 조회되는 현상 수정 (userCheck.do 검증 소스)
- 20200829 출석율 전체 수집 수정
- 20200829 조회할 과제가 없는 경우 IndexError 발생 #1 Issue FIX
