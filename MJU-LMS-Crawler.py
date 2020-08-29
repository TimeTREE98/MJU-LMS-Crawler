#-*- coding:utf-8 -*-

# MJU LMS Crawling
# timetree@kakao.com
# 2020.08.29

import json
import requests as r
from bs4 import BeautifulSoup as BS4

UserID = 'MJU 학번'
UserPW = 'MJU 비밀번호'

def main():
  try:
    with r.Session() as s:
      LoginURL = 'https://sso1.mju.ac.kr/mju/userCheck.do'  # 사용자가 유효한지 검사하는 URL
      LoginData = {'id' : UserID, 'passwrd' : UserPW}
      AjaxActionLoginURL = 'https://sso1.mju.ac.kr/login/ajaxActionLogin2.do'
      AjaxActionLoginData = {'user_id' : UserID, 'user_pwd' : UserPW, 'redirect_uri' : 'http://lms.mju.ac.kr/ilos/bandi/sso/index.jsp' }
      LoginBandiURL = 'http://lms.mju.ac.kr/ilos/lo/login_bandi_sso.acl'
      SubjectURL = 'http://lms.mju.ac.kr/ilos/mp/course_register_list.acl'
      SubjectRoomURL = 'http://lms.mju.ac.kr/ilos/st/course/eclass_room2.acl'  # 강의실 POST URL
      AttendanceURL = 'http://lms.mju.ac.kr/ilos/st/course/attendance_list.acl'  # 출석율 POST URL
      ReportURL = 'http://lms.mju.ac.kr/ilos/st/course/report_list.acl'  # 과제 제출 POST URL
      SubjectData = {'YEAR' : '2020', 'TERM' : '3', 'encoding' : 'utf-8'}  # 이 부분 학기별로 값이 달라지는 듯. 매 학기 별로 갱신 작업 필요
      LoginRes = json.loads(s.post(LoginURL, data = LoginData).text)
      if LoginRes['error'] != '0000' and LoginRes['error'] != 'VL-3130':  # 로그인 여부 처리
        raise Exception(LoginRes)
      s.post(AjaxActionLoginURL, data = AjaxActionLoginData)
      s.get(LoginBandiURL)
      SubjectRes = s.post(SubjectURL, data = SubjectData).text  # 수강 과목 목록 POST 요청
      SubjectHTML = BS4(SubjectRes, 'html.parser')
      SubjectList = SubjectHTML.select('div > div > div > a')
      for Sj in SubjectList:
        print(Sj.text) # 과목명
        SjCode = Sj['onclick'].split("'")[1] # 과목 코드
        SjData = {'KJKEY' : SjCode, 'FLAG' : 'mp', 'returnURI' : '/ilos/st/course/eclass_room2.acl' , 'encoding' : 'utf-8'}
        SjRes = s.post(SubjectRoomURL, data = SjData)
        AttData = {'ud' : UserID, 'ky' : SjCode, 'encoding' : 'utf-8'}
        AttRes = s.post(AttendanceURL, data = AttData).text
        AttHTML = BS4(AttRes, 'html.parser')
        print('--------- 출석율 -----------')
        AttWeek = AttHTML.select('div > div > div > p')  # 출석 주
        AttList = AttHTML.select('div > div > div > ul')  # 출석 차시
        print(AttHTML.select('div > div')[0].text.replace('\n', '')) # 전체 출석율
        for ALidx, AL in enumerate(AttWeek):
          AttSubList = AttList[ALidx].select('ul > li')
          AttPer = ''
          for ASLidx, ASL in enumerate(AttSubList):
            AttPer += ASL.text.split('(')[1].split(')')[0] + ' / '
            if ASLidx + 1 == len(AttSubList):
              AttPer = ASL.text.split('\r\n')[3].split('               ')[1][:-1] + ' | ' + AttPer[:-3]
          print(AL.text, AttPer)
        ReportData = {'start' : '' , 'display' : '1', 'SCH_VALUE' : '', 'ud' : UserID, 'ky' : SjCode, 'encoding' : 'utf-8'}
        ReportRes = s.post(ReportURL, data = ReportData).text
        ReportHTML = BS4(ReportRes, 'html.parser')
        ReportList = ReportHTML.select('table > tbody > tr')
        print('--------- 과제 현황 --------')
        for RL in ReportList:
          Nb = RL.select('td')[0].text
          if '없습니다' in Nb:
            print(Nb)
            break
          Nm = RL.select('td')[1].select('a > div')[0].text
          Prg = RL.select('td')[2].text  # 공백 및 개행 제거 처리 필요
          Sub = RL.select('td')[3].select('img')[0]['title']
          print(Nb + ' | ' + Nm + ' | ' + Sub)
        print('\n')
  except Exception as e:
    print(e)

if __name__ == '__main__':
  main()