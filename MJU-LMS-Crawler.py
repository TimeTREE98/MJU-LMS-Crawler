# -*- coding:utf-8 -*-

# MJU LMS Crawling
# timetree@kakao.com
# 2020.08.29

import json
import requests as r
from bs4 import BeautifulSoup as BS4

UserID = "MJU 학번"
UserPW = "MJU 비밀번호"


def main():
    try:
        Result = []
        with r.Session() as s:
            userCheckURL = "https://sso1.mju.ac.kr/mju/userCheck.do"  # 사용자가 유효한지 검사하는 URL
            userData = {"id": UserID, "passwrd": UserPW}
            LoginRes = json.loads(s.post(userCheckURL, data=userData).text)
            if LoginRes["error"] != "0000" and LoginRes["error"] != "VL-3130":  # 로그인 여부 처리
                raise Exception(LoginRes)
            AjaxActionLogin2URL = "https://sso1.mju.ac.kr/login/ajaxActionLogin2.do"
            userData = {
                "user_id": UserID,
                "user_pwd": UserPW,
                "redirect_uri": "http://lms.mju.ac.kr/ilos/bandi/sso/index.jsp",
            }
            s.post(AjaxActionLogin2URL, data=userData)
            token2URL = "https://sso1.mju.ac.kr/oauth2/token2.do"
            s.post(token2URL, data=userData)
            LoginBandiURL = "https://lms.mju.ac.kr/ilos/lo/login_bandi_sso.acl"
            s.get(LoginBandiURL).text
            SubjectURL = "https://lms.mju.ac.kr/ilos/mp/course_register_list.acl"
            SubjectData = {
                "YEAR": "2021",
                "TERM": "1",
                "encoding": "utf-8",
            }  # 이 부분 학기별로 값이 달라지는 듯. 매 학기 별 갱신 작업 필요
            SubjectRes = s.post(SubjectURL, data=SubjectData).text  # 수강 과목 목록 POST 요청
            SubjectHTML = BS4(SubjectRes, "html.parser")
            SubjectList = SubjectHTML.select("div > div > div > a")
            for Sj in SubjectList:
                Subject = Sj.text  # 과목명
                print(Subject)  # 과목명
                SjCode = Sj["onclick"].split("'")[1]  # 과목 코드 >> ['eclassRoom(', 'A20203KMA021010012', '); return false;']
                SubjectRoomURL = "https://lms.mju.ac.kr/ilos/st/course/eclass_room2.acl"  # 강의실 POST URL
                SjData = {
                    "KJKEY": SjCode,
                    "FLAG": "mp",
                    "returnURI": "/ilos/st/course/submain_form.acl",
                    "encoding": "utf-8",
                }
                SjRes = s.post(SubjectRoomURL, data=SjData)
                AttendanceURL = "https://lms.mju.ac.kr/ilos/st/course/attendance_list.acl"  # 출석율 POST URL
                AttData = {"ud": UserID, "ky": SjCode, "encoding": "utf-8"}
                AttRes = s.post(AttendanceURL, data=AttData).text
                AttHTML = BS4(AttRes, "html.parser")
                Attendance = []
                Report = []
                Online = []
                if "선택하세요." not in AttRes:  # 출석율 URL 에서 '과목을 선택하세요' 에러 나올 경우 출석 및 과제 없는 것으로 처리 (청강 과목의 경우)
                    print("--------- 출석율 -----------")
                    AttWeek = AttHTML.select("div > div > div > p")  # 출석 주
                    AttList = AttHTML.select("div > div > div > ul")  # 출석 차시
                    AttStat = AttHTML.select("div > div")[0].text.replace("\n", "")  # 전체 출석율
                    Attendance.append(AttStat)
                    print(AttStat)  # 전체 출석율
                    for ALidx, AL in enumerate(AttWeek):
                        AttSubList = AttList[ALidx].select("li")
                        AttPer = ""
                        for ASLidx, ASL in enumerate(AttSubList):
                            AttPer += ASL.text.split("(")[1].split(")")[0] + " / "
                            if ASLidx + 1 == len(AttSubList):
                                # AttPer = ASL.text.split('\r\n')[3].split('               ')[1][:-1] + ' | ' + AttPer[:-3] 마감일 나오는 부분, 추후 활용 가능성 있음
                                AttPer = AttPer[:-3]
                                # 여기서부터 동영상 링크 추출 파트. 추후 수정 가능성 있음.
                                OnlineListURL = "https://lms.mju.ac.kr/ilos/st/course/online_list.acl"  # 강의 영상 POST URL
                                OnlineListData = {
                                    "ud": UserID,
                                    "ky": SjCode,
                                    "WEEK_NO": ALidx + 1,
                                    "encoding": "utf-8",
                                }
                                OnlineListRes = s.post(OnlineListURL, data=OnlineListData).text
                                OnlineListHTML = BS4(OnlineListRes, "html.parser")
                                OnlineList = OnlineListHTML.select("li > div > div > div > div > span[onclick]")
                                for OLidx, OL in enumerate(OnlineList):
                                    OLARR = OL["onclick"].split("'")  # ['viewGo(', '1', ', ', '3', ', ', '202009062359', ', ', '202009121417', ',', '118719', ');']
                                    OnlineViewFormURL = "https://lms.mju.ac.kr/ilos/st/course/online_view_form.acl"  # 강의 영상 VIEW POST URL
                                    OnlineViewFormData = {
                                        "lecture_weeks": OLARR[3],
                                        "WEEK_NO": OLARR[1],
                                        "_KJKEY": SjCode,
                                        "kj_lect_type": 0,
                                    }
                                    OnlineViewFormRes = s.post(OnlineViewFormURL, data=OnlineViewFormData).text
                                    OnlineViewFormHTML = BS4(OnlineViewFormRes, "html.parser")
                                    OnlineViewList = OnlineViewFormHTML.select(".item-title-lesson")
                                    if len(OnlineViewList) == 1:
                                        OVLARR = OnlineViewList[0]["val"].split("^")  # ['118717', '4216', '1', '1', 'N']
                                    else:
                                        OVLARR = OnlineViewList[OLidx]["val"].split("^")  # ['118717', '4216', '1', '1', 'N']
                                    OnlineViewNaviURL = "https://lms.mju.ac.kr/ilos/st/course/online_view_navi.acl"  # 강의 영상 Navi POST URL
                                    OnlineViewNaviData = {
                                        "content_id": OVLARR[1],
                                        "organization_id": OVLARR[2],
                                        "lecture_weeks": OVLARR[3],
                                        "navi": "current",
                                        "item_id": OLARR[9],
                                        "ky": SjCode,
                                        "ud": UserID,
                                        "returnData": "json",
                                        "encoding": "utf-8",
                                    }
                                    OnlineViewNaviRes = json.loads(s.post(OnlineViewNaviURL, data=OnlineViewNaviData).text)  # Navi 영역 POST 요청, Json 형태 변환
                                    print(OnlineViewNaviRes["path"])
                                    Online.append(
                                        {
                                            "Week": ALidx + 1,
                                            "Link": OnlineViewNaviRes["path"],
                                        }
                                    )  # 주차별 동영상 링크 저장
                        Attendance.append(AL.text + " " + AttPer)  # 주마다 출석율 표시 >> 1주 100% / 100%
                        print(AL.text, AttPer)
                    ReportURL = "https://lms.mju.ac.kr/ilos/st/course/report_list.acl"  # 과제 제출 POST URL
                    ReportData = {
                        "start": "",
                        "display": "1",
                        "SCH_VALUE": "",
                        "ud": UserID,
                        "ky": SjCode,
                        "encoding": "utf-8",
                    }
                    ReportRes = s.post(ReportURL, data=ReportData).text
                    ReportHTML = BS4(ReportRes, "html.parser")
                    ReportList = ReportHTML.select("table > tbody > tr")
                    print("--------- 과제 현황 --------")
                    for RL in ReportList:
                        Nb = RL.select("td")[0].text
                        if "없습니다" in Nb:
                            print(Nb)
                            break
                        Sub = RL.select("td")[2].select_one(".subjt_top").text  # 과제 이름
                        Prg = RL.select("td")[4].select_one("img")["title"]  # 과제 현황 > 공백 및 개행 제거 처리 필요
                        DeadLine = RL("td")[7].text  # 제출 기한
                        Report.append(Nb + " | " + Prg + " | " + Sub + " | " + DeadLine)
                    Report.reverse()
                    for R in Report:
                        print(R)
                Result.append(
                    {
                        "Subject": Subject,
                        "Attendance": Attendance,
                        "Online": Online,
                        "Report": Report,
                    }
                )
                print("\n")
        return Result
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
