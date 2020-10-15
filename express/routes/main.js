const express = require('express');
const router = express.Router();
const request = require('request');

router.get('/', function (req, res, next) {
  res.render('main', { title: 'MJU 조회' });
});

router.post('/get/all', function (req, res, next) {
  let UserID = req.body['UserID'];
  let UserPW = req.body['UserPW'];

  request.post('http://mju-api.timetree.me/get/all', { form: { UserID: UserID, UserPW: UserPW, redirect_uri: 'http://lms.mju.ac.kr/ilos/bandi/sso/index.jsp' } }, function (err, httpResponse, body) {
    if (err) {
      res.send([]);
    } else {
      res.send(body);
    }
  })
});

module.exports = router;