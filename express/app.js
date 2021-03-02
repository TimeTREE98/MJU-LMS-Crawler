const cookieParser = require('cookie-parser');
const createError = require('http-errors');
const express = require('express');
const logger = require('morgan');
const moment = require('moment');
const path = require('path');
const http = require('http');
const port = process.env.PORT || '6000';
const app = express();

const mainRouter = require('./routes/main');

app.use('/', mainRouter);

logger.token('date', () => {
  let d = new Date()
    .toString()
    .replace(/[A-Z]{3}\+/, '+')
    .split(/ /);
  return moment(new Date()).format('YYYY/MM/DD') + ' ' + d[4] + ' ' + d[5];
});
app.set('trust proxy', true); // Proxy IP Setting
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');
app.use(logger('[:date] :remote-addr :method HTTP/:http-version :status :res[content-length] :url [:user-agent]')); //logger 형식 지정
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use('/assets/bulma', express.static(path.join(__dirname, './node_modules/bulma/css'))); // npm package mount bulma
app.use('/assets/vanillatoasts', express.static(path.join(__dirname, './node_modules/vanillatoasts'))); // npm package mount vanillatoasts

app.use((req, res, next) => {
  next(createError(404));
});

app.use((err, req, res, next) => {
  const notice = { status: err.status, msg: err.message };
  // NodeJS 실행 환경에 따라 에러 메세지 노출 범위 수정 (development 일 경우 err.stack 노출)
  if (req.app.get('env') === 'development') {
    notice['stack'] = err.stack;
    console.log(err);
  }
  res.status(err.status || 500).json(notice);
});

const server = http.createServer(app);

server.listen(port);
