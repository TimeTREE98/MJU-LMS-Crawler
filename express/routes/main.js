const express = require('express');
const router = express.Router();

router.get('/', function (req, res, next) {
  res.render('main', { title: 'MJU 조회' });
});

module.exports = router;
