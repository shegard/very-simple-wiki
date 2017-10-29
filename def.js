let b1 = document.getElementById('b1');
b1.addEventListener('click', function () {
  if (this.value != 'click to save changes!') {
    document.getElementById('t1').readOnly = false;
    this.value = 'click to save changes!';
  }
  else {
    document.getElementById('t1').readOnly = true;
    b1.disabled = true;
    s1.disabled = true;
    let req = new XMLHttpRequest();
    req.open('POST', 'secret.boo');
    req.addEventListener('loadend', function () {
      let el = document.createElement('option');
      let chlds = document.getElementById('s1').children;
      let x;
      if (chlds.length) {
        x = (parseInt(chlds[chlds.length - 1].value) + 1).toString();
        while (x.length < 3) {
          x = '0' + x;
        }
      }
      else {
        x = '001';
      }
      el.value = el.innerText = x;
      el.selected = true;
      document.getElementById('s1').appendChild(el);
      b1.disabled = false;
      s1.disabled = false;
    });
    req.setRequestHeader('Content-Type', 'application/json');
    req.setRequestHeader('Accept', 'application/json');
    req.send(JSON.stringify({ 'query': 'add_version', 'title': `${document.getElementById('srch1').value.replace(/ /g, '_')}`, 'content': `${document.getElementById('t1').value}` }));

    this.value = 'click to edit!';
  }
});

let s1 = document.getElementById('s1');
s1.addEventListener('change', function () {
  b1.disabled = true;
  s1.disabled = true;
  let req = new XMLHttpRequest();
  req.open('POST', 'secret.boo');
  req.addEventListener('loadend', function () {
    document.getElementById('t1').value = req.response;
    b1.disabled = false;
    s1.disabled = false;
  });
  req.setRequestHeader('Content-Type', 'application/json');
  req.setRequestHeader('Accept', 'application/json');
  req.send(JSON.stringify({ 'query': 'update_current_version', 'title': `${document.getElementById('srch1').value.replace(/ /g, '_')}`, 'version': `${document.getElementById('s1').value}` }));
});

let srch1 = document.getElementById('srch1');
srch1.addEventListener('change', function () {
  let c = s1.children;
  while (c.length) {
    s1.removeChild(c[0]);
  }
  document.getElementById('t1').value = '';
  let req = new XMLHttpRequest();
  req.open('POST', 'secret.boo');
  req.addEventListener('loadend', function () {
	  console.log(req.response);
    let r = JSON.parse(req.response);
    console.log(r);
    document.getElementById('t1').value = r['content'];
    for (let x of r['versions']) {
      let el = document.createElement('option');
      el.value = el.innerText = x;
      if (x == r['current_version']) {
        el.selected = true;
      }
      s1.appendChild(el);
    }
    b1.disabled = false;
    s1.disabled = false;
  });
  req.setRequestHeader('Content-Type', 'application/json');
  req.setRequestHeader('Accept', 'application/json');
  req.send(JSON.stringify({ 'query': 'get_all', 'title': `${document.getElementById('srch1').value.replace(/ /g, '_')}` }));
});

let req = new XMLHttpRequest();
req.open('POST', 'api');
req.addEventListener('loadend', function () {
	console.log(req.response);
  let res = JSON.parse(req.response);
  for (let x of res) {
    let el = document.createElement('option');
    el.value = el.innerText = x.replace(/_/g, ' ');
    document.getElementById('srch').appendChild(el);
  }
});
req.setRequestHeader('Content-Type', 'application/json');
req.setRequestHeader('Accept', 'application/json');
req.send(JSON.stringify({
  'query': 'select',
  'action': 'get_articles'
}));
