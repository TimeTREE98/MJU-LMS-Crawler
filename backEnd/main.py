from fastapi import FastAPI, Header, HTTPException
from typing import Optional
from pydantic import BaseModel
import mjuCrawler

app = FastAPI()


class userData(BaseModel):
    id: str
    pw: str


@app.post("/login")
async def login(userData: userData):
    try:
        MJU = mjuCrawler.mjuLmsCrawler()
        return MJU.login(userData.id, userData.pw)
    except Exception as e:
        raise HTTPException(status_code=400)


@app.get("/subject")
async def getSubject(year: int = 2021, term: int = 3, JSESSIONID: Optional[str] = Header(None)):
    try:
        MJU = mjuCrawler.mjuLmsCrawler()
        return MJU.getSubjectList(year, term, JSESSIONID)
    except Exception as e:
        raise HTTPException(status_code=400)


@app.get("/subject/{KJKEY}")
async def getSubjectInfo(id: str, KJKEY: str, JSESSIONID: Optional[str] = Header(None)):
    try:
        MJU = mjuCrawler.mjuLmsCrawler()
        return MJU.getSubjectInfo(id, KJKEY, JSESSIONID)
    except Exception as e:
        raise HTTPException(status_code=400)


@app.post("/subject/all")
async def getSubjectAll(userData: userData):
    try:
        MJU = mjuCrawler.mjuLmsCrawler()
        MJU.login(userData.id, userData.pw)
        subjectList = MJU.getSubjectList(2021, 3)
        for subject in subjectList:
            subjectData = MJU.getSubjectInfo(userData.id, subject["KJKEY"])
            subject["attData"] = subjectData["attData"]
            subject["reportData"] = subjectData["reportData"]
        return subjectList
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400)
