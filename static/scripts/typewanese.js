//Watermelon, Strawberry, Thai, Mango, Honeydew Melon, Butterfly Pea, Taro, Sesame, Brown Sugar
const flavColors = [
  [[255, 130, 130], [255, 170, 170], "Watermelon"],
  [[255, 183, 212], [252, 219, 232], "Strawberry"],
  [[252, 163, 116], [255, 196, 165], "Thai"],
  [[255, 222, 109], [255, 241, 175], "Mango"],
  [[176, 224, 99], [218, 255, 159], "Honeydew Melon"],
  [[127, 225, 255], [191, 240, 255], "Butterfly Pea"],
  [[239, 178, 255], [247, 216, 255], "Taro"],
  [[150, 150, 150], [200, 200, 200], "Sesame"],
  [[226, 199, 140], [250, 230, 170], "Brown Sugar"],
];

let letter_map = [];
let numbers = ['2','3','4','5','7','8']
let consonants = ['p','ts','t','ph','tsh','th','k','ch','s','kh','chh','j','b','l','d','g','h','n']
vowels = ['a','e','i','o','u','ng']
let all_options = [];
let all_tai = [];
let audio_files = [];

function changePath() {
  document.getElementById("path").value = 11;
}

function enterTerm(word) {
  document.getElementById("path").value = '12';
  document.getElementById("black").innerHTML += " " + all_options[word];
  document.getElementById("ogg").value += " " + all_options[word];
  document.getElementById("red").style.display = "none";
  document.mainform.submit();
}

function loadOptions() {
  let device = window.screen.height / window.screen.width;
  
  let options = document.getElementById("options").value;
  let option_string = "";
  for (let i = 0; i < options.length; i++){
    if (options[i] != '[' && options[i] != "'" && options[i] != ']' && options[i] != ' '){
      option_string += options[i];
    }
  }
  all_options = option_string.split(',');

  let tai = document.getElementById("tai").value;
  let tai_string = "";
  for (let i = 0; i < tai.length; i++){
    if (tai[i] != '[' && tai[i] != "'" && tai[i] != ']' && tai[i] != ' '){
      tai_string += tai[i];
    }
  }
  all_tai = tai_string.split(',');

  if (all_options[0].length > 1) {
    for (let i = 0; i < all_options.length; i++) {
      if (device < 1) {
        document.getElementById("options-container").innerHTML += `
          <pre class="option-button" onmouseover="playOption(${i})" onmouseout="stopOption(${i})" onclick="enterTerm(${i})">${all_options[i]}\t\t\t\t${all_tai[i]}</pre>
        `
      } else {
        document.getElementById("options-container").innerHTML += `
          <pre class="option-button" onclick="mobileOption(${i})">${all_options[i]}\t\t\t\t${all_tai[i]}</pre>
        `
      }
    }
  }

  let removal = document.getElementById("black").innerHTML.length * 2;
  if (device < 1) {
    document.getElementById("red").style.width =  `${100-removal*2}%`
  } else {
    document.getElementById("red").style.width =  `${100-removal*2}%`
  }
}

function mobileOption(word) {
  var options = document.getElementsByClassName("option-button");
  for (var i = 0; i < options.length; i++) {
    options[i].style.border = 'none';
  }
  if (audio_files.length > 0) {
    stopOption(selected_option);
  }
  if (selected_option == word) {
    enterTerm(word);
  } else {
    playOption(word);
  }
}

function playOption(word) {
  selected_option = word;
  let hour = document.getElementById("hour").value;
  audio_files[word] = new Audio(`./static/sounds/${hour}_${all_options[word]}.wav`);
  audio_files[word].load();
  audio_files[word].play();
  var options = document.getElementsByClassName("option-button");
  for (var i = 0; i < options.length; i++) {
    options[i].style.border = 'none';
  }
  options[word].style.border = '4px solid rgb(60, 20, 0)';
}

function stopOption(word) {
  audio_files[word].pause();
  audio_files[word].currentTime = 0;
  var options = document.getElementsByClassName("option-button");
  options[word].style.border = 'none';
}

function copyTextToClipboard() {
          document.getElementsByClassName("copy")[0].src = "./static/img/light-copy.png";
  let ogg = document.getElementById("ogg").innerHTML;
  let text = ogg.split(" ");

  if (!navigator.clipboard) {
    fallbackCopyTextToClipboard(ogg);
    return;
  }
  navigator.clipboard.writeText(ogg).then(function() {
    console.log('Async: Copying to clipboard was successful!');
  }, function(err) {
    console.error('Async: Could not copy text: ', err);
  });

  let cleaned_text = [];
  for (let i = 0; i < text.length; i++) {
    if (text[i] != '') {
      cleaned_text.push(text[i]);
    }
  }

  let hour = document.getElementById("hour").innerHTML;
  playSound(hour, 0, cleaned_text.length, cleaned_text);
  
  setTimeout(() => {
            document.getElementsByClassName("copy")[0].src = "./static/img/copy.png";
  },200);
}

function rgb(values) {
  return 'rgb(' + values.join(", ") + ')';
}

function playSound(hour, file, file_count, cleaned_text) {
  if (file < file_count) {
    var sentence = new Audio(`./static/sounds/${hour}_${cleaned_text[file]}.wav`)
    sentence.load();
    sentence.play();
  
    sentence.onended = () => {
      playSound(hour, file + 1, file_count, cleaned_text)
    }
  }
}

var selected_option = -1;

document.addEventListener('keydown', function(event) {
  if (event.keyCode == 13) { //Enter
      if (selected_option == -1) {
      var textarea = document.getElementById("red");
      textarea.blur();
      var updatedValue = textarea.value.replace(/(\r\n|\n|\r)/gm, "");
      textarea.value = updatedValue;
      document.mainform.submit();
    } else {
        enterTerm(selected_option);
    }
  }

  if (event.keyCode == 40) { //Down Arrow
    console.log(selected_option)
    var options = document.getElementsByClassName("option-button");
    for (var i = 0; i < options.length; i++) {
      options[i].style.border = 'none';
    }
    if (selected_option != -1) {
      stopOption(selected_option);
    }
    selected_option += 1;
    if (selected_option == options.length) {
      selected_option = 0;
    }
    options[selected_option].style.border = '4px solid rgb(60, 20, 0)';
    playOption(selected_option);
  }

  if (event.keyCode == 38) { //Up Arrow
    var options = document.getElementsByClassName("option-button");
    for (var i = 0; i < options.length; i++) {
      options[i].style.border = 'none';
    }
    if (selected_option != -1) {
      stopOption(selected_option);
    }
    selected_option -= 1;
    if (selected_option <= -1) {
      selected_option = options.length - 1;
    }
    options[selected_option].style.border = '4px solid rgb(60, 20, 0)';
    playOption(selected_option);
  }
});

function menuMOU() {
  menus = document.getElementsByClassName("menu-button");
  for (var i = 0; i < menus.length; i++) {
    menus[i].style.backgroundColor = rgb(flavColors[8][0]);
  }
}

function menuMOV(select) {
  menus = document.getElementsByClassName("menu-button");
  menus[select].style.backgroundColor = rgb(flavColors[8][1]);
}