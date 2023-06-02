//Watermelon, Strawberry, Thai, Mango, Honeydew Melon, Butterfly Pea, Taro, Sesame, Brown Sugar
const flavColors = [
  [
    [255, 130, 130],
    [255, 170, 170], "Watermelon"
  ],
  [
    [255, 183, 212],
    [252, 219, 232], "Strawberry"
  ],
  [
    [252, 163, 116],
    [255, 196, 165], "Thai"
  ],
  [
    [255, 222, 109],
    [255, 241, 175], "Mango"
  ],
  [
    [176, 224, 99],
    [218, 255, 159], "Honeydew Melon"
  ],
  [
    [127, 225, 255],
    [191, 240, 255], "Butterfly Pea"
  ],
  [
    [239, 178, 255],
    [247, 216, 255], "Taro"
  ],
  [
    [150, 150, 150],
    [200, 200, 200], "Sesame"
  ],
  [
    [226, 199, 140],
    [250, 230, 170], "Brown Sugar"
  ],
];

var flav = 9;

var id1 = null;
var id2 = null
var id3 = null;

var play = 0;

function submitButton() {
  moveBobaBL();
}

function moveBobaTR() {
  var elem = document.getElementById("bobatr");
  var pos = 0;

  elem.style.bottom = "0.5vmax";
  elem.style.left = "12vmax";
  elem.style.opacity = 1;
  clearInterval(id1);
  id1 = setInterval(frame, 10);

  function frame() {
    if (pos < 5) {
      pos += 0.3;
      elem.style.bottom = 1 + pos + "vmax";
    } else if (pos < 7) {
      pos += 0.3;
      elem.style.bottom = 1 + pos + "vmax";
      elem.style.left = 12 - (pos - 5) + "vmax";
    } else if (pos < 15) {
      pos += 0.3;
      elem.style.left = 12 - (pos - 5) + "vmax";
    } else if (pos >= 15) {
      clearInterval(id1);
      elem.style.opacity = 0;
      setTimeout(moveBobaBL, 500);
    }
  }
}

function moveBobaBL() {
  var elem = document.getElementById("bobabl");
  var pos = 0;

  elem.style.top = "1vmax";
  elem.style.right = "12vmax";
  elem.style.opacity = 1;
  clearInterval(id2);
  id2 = setInterval(frame, 10);

  function frame() {
    if (pos < 5.5) {
      pos += 0.3;
      elem.style.top = 1 + pos + "vmax";
    } else if (pos < 7.7) {
      pos += 0.3;
      elem.style.top = 1 + pos + "vmax";
      elem.style.right = 12 - (pos - 5.5) + "vmax";
    } else if (pos < 14) {
      pos += 0.3;
      elem.style.right = 12 - (pos - 5.5) + "vmax";
    } else if (pos >= 14) {
      clearInterval(id2);
      elem.style.opacity = 0;
      moveBobaB();
    }
  }
}

function moveBobaB() {
  var elem = document.getElementById("bobab");
  var pos = 0;

  elem.style.left = "1vmax";
  elem.style.opacity = 1;
  clearInterval(id3);
  id3 = setInterval(frame, 10);

  function frame() {
    if (pos < 12) {
      pos += 0.3;
      elem.style.left = 1 + pos + "vmax";
    } else {
      clearInterval(id3);
      elem.style.opacity = 0;
      moveBobaTR();
    }
  }
}

function rgb(values) {
  return "rgb(" + values.join(", ") + ")";
}

function changeFlavor() {
  flav = document.getElementById("color").innerHTML;
  var old = flav;
  while (old == flav) {
    flav = Math.ceil(Math.random() * 9);
  }
  document.getElementById("background").style.backgroundColor = rgb(flavColors[flav - 1][0]);
  document.getElementsByClassName("flavor-text")[0].innerHTML = flavColors[flav - 1][2] + " Milk Tea";
  document.getElementsByClassName("flavor-text")[1].innerHTML = flavColors[flav - 1][2] + " Milk Tea";
  document.getElementById("color").innerHTML = flav

  var drinks = document.getElementsByClassName("drink");
  for (var i = 0; i < drinks.length; i++) {
    drinks[i].style.backgroundColor = rgb(flavColors[flav - 1][1]);
  }

  document.getElementsByClassName("drink-box")[0].style.backgroundColor = rgb(flavColors[flav - 1][0]);
  document.getElementsByClassName("drink-box")[1].style.backgroundColor = rgb(flavColors[flav - 1][0]);

  var drinkStraws = document.getElementsByClassName("drink-straw");
  for (var i = 0; i < drinkStraws.length; i++) {
    drinkStraws[i].style.backgroundColor = rgb(flavColors[flav - 1][1]);
  }

  var speechButtons = document.getElementsByClassName("speech-button");
  for (var i = 0; i < speechButtons.length; i++) {
    speechButtons[i].style.backgroundColor = rgb(flavColors[flav - 1][1]);
  }

  var straws = document.getElementsByClassName("straw");
  for (var i = 0; i < straws.length; i++) {
    straws[i].style.backgroundColor = rgb(flavColors[flav - 1][1]);
  }
  var textboxes = document.getElementsByClassName("text-box");
  for (var i = 0; i < textboxes.length; i++) {
    textboxes[i].style.backgroundColor = rgb(flavColors[flav - 1][1]);
  }

  menuMOU();
  document.getElementsByClassName("submit-button")[0].style.backgroundColor = rgb(flavColors[flav - 1][0]);

  var favicons = document.getElementsByClassName("favicon");
  for (var i = 0; i < favicons.length; i++) {
    favicons[i].href = `./static/flav_${flav - 1}.png`
  }
}

function submitMOV() {
  document.getElementById("submit-shadow").style.display = "none";
}

function submitMOU() {
  document.getElementById("submit-shadow").style.display = "block";
}

function drinkMOV() {
  let shadows = document.getElementsByClassName("drink-shadow");
  for (var i = 0; i < shadows.length; i++) {
    shadows[i].style.display = "none";
  }
}

function drinkMOU() {
  let shadows = document.getElementsByClassName("drink-shadow");
  for (var i = 0; i < shadows.length; i++) {
    shadows[i].style.display = "block";
  }
}

function speechMOV() {
  play = document.getElementById('play').innerHTML;
  if (play == 0) {
    document.getElementsByClassName("speech-shadow")[0].style.display = "none";
    document.getElementsByClassName("speech-shadow")[1].style.display = "none";
  }
}

function speechMOU() {
  play = document.getElementById('play').innerHTML;
  if (play == 0) {
    document.getElementsByClassName("speech-shadow")[0].style.display = "block";
    document.getElementsByClassName("speech-shadow")[1].style.display = "block";
  }
}

function menuMOU() {
  flav = document.getElementById("color").innerHTML;
  menus = document.getElementsByClassName("menu-button");
  for (var i = 0; i < menus.length; i++) {
    menus[i].style.backgroundColor = rgb(flavColors[flav - 1][0]);
  }
}

function menuMOV(select) {
  flav = document.getElementById("color").innerHTML;
  menus = document.getElementsByClassName("menu-button");
  menus[select].style.backgroundColor = rgb(flavColors[flav - 1][1]);
}
