# -*- coding:utf-8 -*-

# MJU LMS Crawling
# timetree@kakao.com
# 2020.08.29
# 2021.09.03 chagne class

import datetime as dt
import requests as r
from bs4 import BeautifulSoup as BS4


class mjuLmsCrawler:
    def __init__(self):
        self.s = r.Session()
        self.userData = {}

    def login(self, id: str, pw: str):  # 로그인 처리
        userCheckURL = "https://sso1.mju.ac.kr/mju/userCheck.do"  # 사용자가 존재하는지 검사하는 URL
        self.userData = {"id": id, "passwrd": pw}
        userCheckRes = self.s.post(userCheckURL, data=self.userData)
        userCheckResJson = userCheckRes.json()
        if userCheckResJson["error"] != "0000" and userCheckResJson["error"] != "VL-3130":  # 로그인 여부 처리
            raise Exception(userCheckResJson)

        loginData = {"user_id": id, "user_pwd": pw, "redirect_uri": "http://lms.mju.ac.kr/ilos/bandi/sso/index.jsp"}

        loginURL = "https://sso1.mju.ac.kr/login/ajaxActionLogin2.do"  # 세션 로그인 인식 처리 위한 URL
        self.s.post(loginURL, data=loginData)

        token2URL = "https://sso1.mju.ac.kr/oauth2/token2.do"  # 세션 로그인 인식 처리 위한 URL
        self.s.post(token2URL, data=loginData)

        loginBandiURL = "https://lms.mju.ac.kr/ilos/lo/login_bandi_sso.acl"  # 세션 로그인 인식 처리 위한 URL
        loginBandiRes = self.s.get(loginBandiURL)
        if "로그인 정보가 일치하지 않습니다." in loginBandiRes.text:
            raise Exception("login_bandi_sso.acl 통과 실패")

        result = {}

        for cookie in self.s.cookies.items():
            if cookie[0] == "JSESSIONID" and "." in cookie[1]:
                continue
            result[cookie[0]] = cookie[1]

        return result

    def getSubjectList(self, year: int, term: int, JSESSIONID: str = "") -> list:  # year, term 기반 과목 데이터
        if JSESSIONID:
            self.s.cookies.set("JSESSIONID", JSESSIONID, domain="lms.mju.ac.kr", path="/ilos")
        elif not self.s.cookies:
            raise Exception("JSESSIONID 값이 없습니다.")

        subjectList = []

        subjectURL = "https://lms.mju.ac.kr/ilos/mp/course_register_list.acl"  # 수강 과목 조회 URL
        subjectData = {"YEAR": year, "TERM": term, "encoding": "utf-8"}
        subjectRes = self.s.post(subjectURL, data=subjectData)
        subjectHtml = BS4(subjectRes.text, "html.parser")
        subjectHtmlList = subjectHtml.select("div > div > div > a")
        subjectInfoList = subjectHtml.select("div > ul")

        for sjIdx, sj in enumerate(subjectHtmlList):
            sjInfoList = subjectInfoList[sjIdx].select("span")
            sjName = sj.text  # 과목 이름
            sjProfessor = sjInfoList[0].text  # 교수 이름
            sjTime = sjInfoList[1].text.replace("\xa0", "")  # 강의 시간
            sjCode = sjName.split("-")[1].split(")")[0]  # 과목 코드
            KJKEY = sj["onclick"].split("'")[1]  # URL 접속 처리용 키
            subjectList.append({"name": sjName, "professor": sjProfessor, "time": sjTime, "code": sjCode, "KJKEY": KJKEY})

        return subjectList

    def getSubjectInfo(self, id: str, KJKEY: str, JSESSIONID: str = "") -> list:  # year, term 기반 과목 데이터
        if JSESSIONID:
            self.s.cookies.set("JSESSIONID", JSESSIONID, domain="lms.mju.ac.kr", path="/ilos")
        elif not self.s.cookies:
            raise Exception("JSESSIONID 값이 없습니다.")

        subjectRoomURL = "https://lms.mju.ac.kr/ilos/st/course/eclass_room2.acl"  # 강의실 POST URL
        subjectRoomData = {
            "KJKEY": KJKEY,
            "FLAG": "mp",
            "returnURI": "/ilos/st/course/submain_form.acl",
            "encoding": "utf-8",
        }
        self.s.post(subjectRoomURL, data=subjectRoomData)  # 강의실 URL 입장 POST 처리

        subjectRoomURL = "https://lms.mju.ac.kr/ilos/st/course/submain_form.acl"
        subjectRoomRes = self.s.get(subjectRoomURL)

        attendanceListURL = "https://lms.mju.ac.kr/ilos/st/course/attendance_list.acl"  # 출석율 POST URL
        attendanceListData = {"ud": id, "ky": KJKEY, "encoding": "utf-8"}
        attendanceListRes = self.s.post(attendanceListURL, data=attendanceListData)
        attendanceListHtml = BS4(attendanceListRes.text, "html.parser")

        if "선택하세요." in attendanceListHtml:
            raise Exception("출석 및 과제가 없는 과목입니다.")

        # 출석 데이터
        attData = []
        attStat = attendanceListHtml.select("div > div")[0].text.replace("\n", "")  # 전체 출석율
        attWeek = attendanceListHtml.select("div > div > div > p")  # 출석 주 리스트
        attList = attendanceListHtml.select("div > div > div > ul")  # 출석 차시 리스트
        for awIdx, AW in enumerate(attWeek):  # 출석 주 반복
            attSubList = attList[awIdx].select("li")  # 출석 차시 리스트 > 출석 주 인덱스 값을 바탕으로 세부 리스트화
            attPer = []  # 출석율 표시 용도 [ 100, 57 ]
            week = AW.text  # 출석 주
            for aslIdx, ASL in enumerate(attSubList):
                attPer.append(int(ASL.text.split("(")[1].split(")")[0].replace("%", "")))
            attData.append({"week": week, "attendance": attPer})

        # 과제 데이터
        reportData = []
        reportListURL = "https://lms.mju.ac.kr/ilos/st/course/report_list.acl"
        reportListData = {"start": "", "display": "1", "SCH_VALUE": "", "ud": id, "ky": KJKEY, "encoding": "utf-8"}
        reportListRes = self.s.post(reportListURL, data=reportListData)
        reportListHtml = BS4(reportListRes.text, "html.parser")
        reportList = reportListHtml.select("table > tbody > tr")
        for RL in reportList:
            nb = RL.select("td")[0].text
            if "없습니다" in nb:
                break
            title = RL.select("td")[2].select_one(".subjt_top").text  # 과제 이름
            progress = RL.select("td")[4].select_one("img")["title"]  # 과제 현황 > 공백 및 개행 제거 처리 필요

            deadLine = RL("td")[7].text  # 제출 기한
            dLSplit = deadLine.split(" ")
            dLSdate = dLSplit[0].split(".")
            dLStime = dLSplit[2].split(":")
            dLdate = [int(dLSdate[0]), int(dLSdate[1]), int(dLSdate[2])]
            dLtime = [int(dLStime[0]), int(dLStime[1])]
            if " 오후 " in deadLine:
                dLtime[0] = dLtime[0] + 12
            deadLineDateTime = dt.datetime(dLdate[0], dLdate[1], dLdate[2], dLtime[0], dLtime[1], 0)

            reportData.append({"title": title, "progress": progress, "deadLine": deadLineDateTime})

        return {"attData": attData, "reportData": reportData}
