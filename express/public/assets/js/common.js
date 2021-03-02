document.addEventListener('DOMContentLoaded', function () {
  const pathname = window.location.pathname.split('/')[1];
  if (pathname !== '') {
    const nav_menu = document.getElementById('nav_' + pathname);
    nav_menu.classList.add('is-active');
  }
  const menus = document.querySelectorAll('.navbar-burger');
  const dropdowns = document.querySelectorAll('.navbar-menu');
  if (menus.length && dropdowns.length) {
    for (var i = 0; i < menus.length; i++) {
      menus[i].addEventListener('click', function () {
        for (var j = 0; j < dropdowns.length; j++) {
          dropdowns[j].classList.toggle('is-active');
        }
      });
    }
  }
  const modal_bg = document.querySelectorAll('.modal-background');
  for (var i = 0; i < modal_bg.length; i++) {
    modal_bg[i].addEventListener('click', function () {
      hide_modal();
    });
  }
});

function login_submit() {
  var loginBtn = document.getElementById('loginBtn');
  loginBtn.classList.add('is-loading');
  axios
    .post('https://mju-api.timetree.me/get/all', serialize(document.getElementById('login_form')))
    .then(function (response) {
      let data = response.data;
      if (data.length == 0) {
        alert('로그인 실패 혹은 에러!\n다시 시도해주세요.');
      } else {
        let SubmitCnt = 0;
        let UnSubmitCnt = 0;
        let listhtml = '';
        data.forEach(function (d) {
          listhtml += '<div class="column is-6-tablet is-3-widescreen"><div class="card" style="height: 100%"><div class="card-content"><h5 class="title is-6">';
          listhtml += d['Subject'];
          listhtml += '</h5><h5 class="title is-6">출석율</h5>';
          d['Attendance'].forEach(function (a, aidx) {
            if (aidx == 0) {
              listhtml += '<p>';
            } else {
              let DOWN_URL = '';
              d['Online'].forEach(function (o, oidx) {
                let aweek = a.split('주')[0];
                if (o['Week'] == parseInt(aweek)) {
                  DOWN_URL += o['Link'] + '^';
                }
              });
              if (DOWN_URL != '') {
                DOWN_URL = DOWN_URL.substr(0, DOWN_URL.length - 1);
              }
              if (a.indexOf('주 100%') == -1) {
                listhtml += `<p style='color: red;' onclick='download("${DOWN_URL}");'>`;
              } else {
                listhtml += `<p style='color: green;' onclick='download("${DOWN_URL}");'>`;
              }
            }
            listhtml += a;
            listhtml += '</p>';
          });
          listhtml += '</br><h5 class="title is-6">과제 현황</h5>';
          d['Report'].forEach(function (r) {
            rArr = r.split(' | ');
            if (r.indexOf('미제출') == -1 && r.indexOf('없습니다') == -1) {
              listhtml += '<p style="color: green;">';
              listhtml += rArr[0] + ' | ' + rArr[2];
              SubmitCnt += 1;
            } else {
              listhtml += '<p style="color: red;">';
              listhtml += rArr[0] + ' | ' + rArr[2] + ' | ' + rArr[3];
              UnSubmitCnt += 1;
            }
            listhtml += '</p>';
          });
          listhtml += '</div></div></div>';
        });
        let SubmitSum = SubmitCnt + UnSubmitCnt;
        let subjecthtml =
          '<div class="column is-6-tablet is-3-widescreen"><div class="card" style="height: 100%"><div class="card-content"><h5 class="title is-6">전체 과제 제출 현황</h5><div style="display : inline-block;">';
        subjecthtml +=
          '<p style="color: green; float: left;">👍 : ' +
          String(SubmitCnt) +
          '건</p><p style="float: left;">&nbsp;&nbsp;|&nbsp;&nbsp;</p><p style="color: red;">👎 : ' +
          String(UnSubmitCnt) +
          '건</p>';
        subjecthtml += '<p>당신은 지금까지 총 ' + String(SubmitSum) + '개의 과제를 받았으며</p><p>이 중 완료율은 ' + percentage(SubmitCnt, SubmitSum) + ' 입니다!</p></div></div></div></div>';
        hide_modal();
        let VL = document.getElementById('ViewList');
        VL.innerHTML = subjecthtml + listhtml;
      }
      loginBtn.classList.remove('is-loading');
    })
    .catch(function (error) {
      console.log(error);
    });
}

function download(URL_ARR) {
  if (!URL_ARR) {
    alert('영상이 없거나, 에러가 있습니다.\n문의 부탁드립니다.');
  } else {
    let URL = URL_ARR.split('^');
    let downloadhtml = '';
    URL.forEach(function (UA, UAIDX) {
      downloadhtml += '<a href="' + UA + '" target="_blank">' + (UAIDX + 1) + '</a><br><br>';
    });
    let DU = document.getElementById('download_url');
    DU.innerHTML = downloadhtml;
    show_modal('download_notice_modal');
  }
}

function percentage(partialValue, totalValue) {
  return String(((100 * partialValue) / totalValue).toFixed(2)) + ' %';
}

function hide_modal() {
  const modals = document.querySelectorAll('.modal');
  for (var i = 0; i < modals.length; i++) {
    modals[i].classList.remove('is-active');
  }
}

function show_modal(ID) {
  const modal = document.getElementById(ID);
  modal.classList.add('is-active');
}

/*
 * jQuery 사용 안함으로써 serialize 함수 작성
 */
const serialize = function (form) {
  var arr = [];
  Array.prototype.slice.call(form.elements).forEach(function (field) {
    if (!field.name || field.disabled || ['file', 'reset', 'submit', 'button'].indexOf(field.type) > -1) return;
    if (field.type === 'select-multiple') {
      Array.prototype.slice.call(field.options).forEach(function (option) {
        if (!option.selected) return;
        arr.push(encodeURIComponent(field.name) + '=' + encodeURIComponent(option.value));
      });
      return;
    }
    if (['checkbox', 'radio'].indexOf(field.type) > -1 && !field.checked) return;
    arr.push(encodeURIComponent(field.name) + '=' + encodeURIComponent(field.value));
  });
  return arr.join('&');
};
