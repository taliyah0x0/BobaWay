let intervalId;

const input_area = document.getElementById("input-area");
input_area.addEventListener("focus", () => {
    intervalId = setInterval(initiate, 200); // Run every 200ms
});

// Stop the loop when the textarea loses focus
input_area.addEventListener("blur", () => {
    clearInterval(intervalId); // Stop the interval
});

let save = [];
let old = "";
let lastWord = "";
let last_index = 0;

function initiate() {
    let rawText = document.getElementById("input-area").innerText || "";
    let output = document.getElementById("output-area");
    let options = document.getElementsByClassName("options");

    // Parse text into tokens and get current word index
    const tokens = parseTextIntoTokens(rawText);
    const index = getCurrentWordIndex();
    
    // Update input display with spans
    updateInputDisplay(tokens);
    
    let word = "";
    if (index >= 0 && index < tokens.length) {
        word = tokens[index].toLowerCase();
    }

    // Handle deletions
    const originalTokens = parseTextIntoTokens(old);
    let deleted = findDeletedTokenIndex(originalTokens, tokens);

    const all = document.getElementsByClassName("output_div");
    let all_inners = [];
    for (var i = 0; i < all.length; i++) {
        all_inners.push(all[i].innerHTML);
    }

    if (deleted != -1) {
        output.innerHTML = "";
        for (var i = 0; i < all_inners.length; i++) {
            if (i != deleted) {
                output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
            }
        }
        all_inners.pop(deleted);
    }

    let temp = [];
    if (jsonData && word in jsonData) {
        for (var i = 0; i < 4; i++) {
            if (languages_included[i] && jsonData[word][i]) {
                temp = temp.concat(jsonData[word][i]);
            }
        }
    }
    if (jsonData && word in jsonData && temp.length > 0) {
        if (index >= all_inners.length) {
            const optionsWrapper = document.getElementById("options-wrapper");
            if (optionsWrapper) {
                optionsWrapper.innerHTML += `<div class="options" style="display: flex; flex-direction: column"></div>`;
            }
            if (options[index]) {
                options[index].innerHTML = "";
                for (var i = 0; i < temp.length; i++) {
                    options[index].innerHTML += `<label><input name="${word}_${index}" type="radio" class="${index}" value="${temp[i]}" onclick="editOutput(${index}, '${word}', ${i})">${temp[i]}</label>`;
                }
                const radioButtons = document.getElementsByClassName(`${index}`);
                if (radioButtons.length > 0) {
                    radioButtons[0].checked = true;
                }
            }
            output.innerHTML += `<div class="output_div">${temp[0]}</div>`;
            save.push(0);
        } else {

        for (var i = 0; i < options.length; i++) {
            options[i].style.display = "none";
        }
        const boxTitle = document.getElementsByClassName("box-title3")[0];
        if (boxTitle) {
            boxTitle.style.display = "flex";
        }
        if (options[index]) {
            options[index].style.display = "flex";
        }
        if (last_index != index) {
            let radios = document.getElementsByClassName(`${index}`);
            if (radios.length > 0 && save[index] !== undefined && radios[save[index]]) {
                let m = radios[save[index]].value;
                radios[save[index]].checked = true;

                output.innerHTML = "";
                for (var i = 0; i < index; i++) {
                    output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
                }
                output.innerHTML += `<div class="output_div">${m}</div>`;
                for (var i = index + 1; i < all_inners.length; i++) {
                    output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
                }
            }
        } else if (options[index] && options[index].innerHTML == "") {
            options[index].innerHTML = "";
            for (var i = 0; i < temp.length; i++) {
                options[index].innerHTML += `<label><input name="${word}_${index}" type="radio" class="${index}" value="${temp[i]}" onclick="editOutput(${index}, '${word}', ${i})">${temp[i]}</label>`;
            }
            save[index] = 0;
            const radioButtons = document.getElementsByClassName(`${index}`);
            if (radioButtons.length > 0) {
                radioButtons[0].checked = true;
            }

            output.innerHTML = "";
            for (var i = 0; i < index; i++) {
                output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
            }
            if (jsonData[word] && jsonData[word][0] && jsonData[word][0][0]) {
                output.innerHTML += `<div class="output_div">${jsonData[word][0][0]}</div>`;
            }
            for (var i = index + 1; i < all_inners.length; i++) {
                output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
            }
        }
    }
    } else if (/^[a-zA-Z\s]+$/.test(word) && old != rawText) {
        for (var i = 0; i < options.length; i++) {
            options[i].style.display = "none";
        }
        const boxTitle = document.getElementsByClassName("box-title3")[0];
        if (boxTitle) {
            boxTitle.style.display = "none";
        }
        output.innerHTML = "";
        for (var i = 0; i < index; i++) {
            output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
        }
        output.innerHTML += `<div class="output_div">${word}</div>`;
        for (var i = index + 1; i < all_inners.length; i++) {
            output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
        }
    } else {
        for (var i = 0; i < options.length; i++) {
            options[i].style.display = "none";
        }
        const boxTitle = document.getElementsByClassName("box-title3")[0];
        if (boxTitle) {
            boxTitle.style.display = "none";
        }
    }
    old = rawText;
    lastWord = word;
    last_index = index;
}

// Helper function to parse text into clean tokens
function parseTextIntoTokens(text) {
    if (!text) return [];
    return text.split(/(\s+|[^\w\s])/g).filter(token => token.trim());
}

// Helper function to find deleted token index
function findDeletedTokenIndex(originalTokens, currentTokens) {
    if (originalTokens.length <= currentTokens.length) return -1;
    
    for (let i = 0; i < originalTokens.length; i++) {
        if (i >= currentTokens.length || originalTokens[i] !== currentTokens[i]) {
            return i;
        }
    }
    return originalTokens.length - 1;
}

// Get the current word index based on cursor position or active span
function getCurrentWordIndex() {
    const selection = window.getSelection();
    if (selection.rangeCount === 0) return -1;
    
    const range = selection.getRangeAt(0);
    let node = range.startContainer;
    
    // If we're in a text node, find its parent span
    if (node.nodeType === Node.TEXT_NODE) {
        node = node.parentNode;
    }
    
    // Check if we're in a word span
    if (node.classList && node.classList.contains('word-span')) {
        return parseInt(node.dataset.index) || -1;
    }
    
    // Fallback: find closest word span
    const inputArea = document.getElementById("input-area");
    const wordSpans = inputArea.querySelectorAll('.word-span');
    
    for (let i = 0; i < wordSpans.length; i++) {
        if (wordSpans[i].contains(node) || node === wordSpans[i]) {
            return parseInt(wordSpans[i].dataset.index) || -1;
        }
    }
    
    return -1;
}

// Update input display with clickable word spans
function updateInputDisplay(tokens) {
    const inputArea = document.getElementById("input-area");
    let html = '';
    
    for (let i = 0; i < tokens.length; i++) {
        html += `<span class="word-span" data-index="${i}" onclick="setActiveWord(${i})">${tokens[i]}</span>`;
        if (i < tokens.length - 1) {
            html += ' ';
        }
    }
    
    // Preserve cursor position
    const selection = window.getSelection();
    const currentIndex = getCurrentWordIndex();
    
    inputArea.innerHTML = html;
    
    // Restore cursor to the same word if possible
    if (currentIndex >= 0 && currentIndex < tokens.length) {
        const targetSpan = inputArea.querySelector(`[data-index="${currentIndex}"]`);
        if (targetSpan) {
            const range = document.createRange();
            range.selectNodeContents(targetSpan);
            range.collapse(false); // Move cursor to end
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }
}

// Set active word (for click events)
function setActiveWord(index) {
    // Remove active class from all spans
    const spans = document.querySelectorAll('.word-span');
    spans.forEach(span => span.classList.remove('active-word'));
    
    // Add active class to clicked span
    const targetSpan = document.querySelector(`[data-index="${index}"]`);
    if (targetSpan) {
        targetSpan.classList.add('active-word');
    }
    
    // Trigger initiate to update options
    setTimeout(initiate, 0);
}

function editOutput(index, word, radio) {
    const all = document.getElementsByClassName("output_div");
    const all_inners = [];
    for (var i = 0; i < all.length; i++) {
        all_inners.push(all[i].innerHTML);
    }
    let output = document.getElementById("output-area");
    output.innerHTML = "";
    for (var i = 0; i < index; i++) {
        output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
    }
    let temp = [];
    if (jsonData && word in jsonData) {
        for (var i = 0; i < 4; i++) {
            if (languages_included[i] && jsonData[word][i]) {
                temp = temp.concat(jsonData[word][i]);
            }
        }
    }
    if (temp[radio]) {
        output.innerHTML += `<div class="output_div">${temp[radio]}</div>`;
    }
    for (var i = index + 1; i < all_inners.length; i++) {
        output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
    }
    save[index] = radio;
}

let languages_included = [1, 0, 0, 0];
function editLanguages(index) {
    languages_included[index] = !languages_included[index] ? 1 : 0;
}

function copy() {
    const all = document.getElementsByClassName("output_div");
    let text = "";
    for (var i = 0; i < all.length; i++) {
        text += all[i].innerHTML;
    }
    try {
        navigator.clipboard.writeText(text);
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
}

let jsonData; // Global variable to store the fetched JSON
async function loadLanguageData() {
    try {
        const response = await fetch('/api/all-languages-data');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        jsonData = await response.json();
        console.log("JSON data fetched and stored:", jsonData);
    } catch (error) {
        console.error("Error fetching language data:", error);
        // Fallback to static file if API fails
        try {
            const fallbackResponse = await fetch('./static/output.json');
            jsonData = await fallbackResponse.json();
        } catch (fallbackError) {
            console.error("Fallback also failed:", fallbackError);
        }
    }
}

// Call this function when the page loads
loadLanguageData();

// Simplified hover functionality using span-based approach
function setupHoverFunctionality() {
    const inputArea = document.getElementById("input-area");
    const outputArea = document.getElementById("output-area");
    
    // Use event delegation for dynamically created spans
    inputArea.addEventListener('mouseover', handleInputHover);
    inputArea.addEventListener('mouseout', clearHoverHighlight);
    
    outputArea.addEventListener('mouseover', handleOutputHover);
    outputArea.addEventListener('mouseout', clearHoverHighlight);
}

function handleInputHover(event) {
    if (event.target.classList.contains('word-span')) {
        const wordIndex = parseInt(event.target.dataset.index);
        const word = event.target.textContent;
        
        if (wordIndex >= 0) {
            highlightCorrespondingWords(wordIndex);
            showOptionsForWord(wordIndex, word);
        }
    }
}

function handleOutputHover(event) {
    if (event.target.classList.contains('output_div')) {
        const outputDivs = Array.from(document.getElementsByClassName('output_div'));
        const wordIndex = outputDivs.indexOf(event.target);
        
        if (wordIndex >= 0) {
            highlightCorrespondingWords(wordIndex);
            
            // Get the corresponding input word
            const inputSpan = document.querySelector(`[data-index="${wordIndex}"]`);
            if (inputSpan) {
                showOptionsForWord(wordIndex, inputSpan.textContent);
            }
        }
    }
}

function highlightCorrespondingWords(wordIndex) {
    // Clear previous highlights
    clearHoverHighlight();
    
    // Highlight input word span
    const inputSpan = document.querySelector(`[data-index="${wordIndex}"]`);
    if (inputSpan) {
        inputSpan.classList.add('hover-highlight');
    }
    
    // Highlight output word
    const outputDivs = document.getElementsByClassName('output_div');
    if (wordIndex >= 0 && wordIndex < outputDivs.length) {
        outputDivs[wordIndex].classList.add('hover-highlight');
    }
}

function showOptionsForWord(wordIndex, word) {
    const options = document.getElementsByClassName("options");
    const boxTitle = document.getElementsByClassName("box-title3")[0];
    
    // Hide all options first
    for (let i = 0; i < options.length; i++) {
        options[i].style.display = "none";
    }
    
    // Check if word has translations
    if (word && jsonData && word.toLowerCase() in jsonData) {
        const lowerWord = word.toLowerCase();
        let temp = [];
        
        for (let i = 0; i < 4; i++) {
            if (languages_included[i] && jsonData[lowerWord][i]) {
                temp = temp.concat(jsonData[lowerWord][i]);
            }
        }
        
        if (temp.length > 0 && wordIndex < options.length && boxTitle) {
            boxTitle.style.display = "flex";
            options[wordIndex].style.display = "flex";
        }
    }
}

function clearHoverHighlight() {
    // Clear input highlights
    const inputSpans = document.querySelectorAll('.word-span');
    inputSpans.forEach(span => span.classList.remove('hover-highlight'));
    
    // Clear output highlights
    const outputDivs = document.getElementsByClassName('output_div');
    for (let div of outputDivs) {
        div.classList.remove('hover-highlight');
    }
    
    // Hide options when not hovering
    const options = document.getElementsByClassName("options");
    for (let i = 0; i < options.length; i++) {
        options[i].style.display = "none";
    }
    const boxTitle = document.getElementsByClassName("box-title3")[0];
    if (boxTitle) {
        boxTitle.style.display = "none";
    }
}

// Initialize hover functionality when page loads
document.addEventListener('DOMContentLoaded', function() {
    setupHoverFunctionality();
});

function menuMOU() {
    let menus = document.getElementsByClassName("menu-button");
    for (var i = 0; i < menus.length; i++) {
        menus[i].style.backgroundColor = "rgb(226, 199, 140)";
    }
}
    
function menuMOV(select) {
    let menus = document.getElementsByClassName("menu-button");
    if (menus[select]) {
        menus[select].style.backgroundColor = "#FAE6AA";
    }
}