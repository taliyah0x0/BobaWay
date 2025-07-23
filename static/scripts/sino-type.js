// GLOBAL VARIABLES
let jsonData; // Store the fetched JSON
let save = [];
let old = "";
let lastWord = "";
let last_index = 0;
let languages_included = [1, 0, 0, 0];
let wordMapping = []; // Store mapping between input words and output divs
let isProcessingInput = false; // Flag to prevent highlight interference during input processing

// FUNCTIONS
// Get the hanzi options for the word
function getHanziOptions(word) {
    let hanzi_options = [];
    if (word in jsonData) {
        for (var i = 0; i < 4; i++) {
            if (languages_included[i]) {
                hanzi_options = hanzi_options.concat(jsonData[word][i]);
            }
        }
    }
    return hanzi_options;
}

// Set the output at the given index
function setOutputAtIndex(index, hanzi) {
    // get the current output
    const all = document.getElementsByClassName("output_div");
    const all_inners = Array.from(all, el => el.innerHTML);
    let output = document.getElementById("output-area");

    // update the output at the given index
    const newHTML = all_inners.map(inner => `<div class="output_div">${inner}</div>`);
    newHTML[index] = `<div class="output_div">${hanzi}</div>`;
    output.innerHTML = newHTML.join('');
}

function initiate () {
    // Use textContent instead of innerHTML to avoid issues with highlight spans
    const inputArea = document.getElementById("input-area");
    let text = (inputArea.textContent || inputArea.innerText || "").replace(/\s+/g, " ");
    let options = document.getElementsByClassName("options");
    let output = document.getElementById("output-area");

    let index = -1;
    const selection = window.getSelection();
    let cursorPosition = 0;

    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0); // Get the first range of the selection
        const preCaretRange = range.cloneRange(); // Clone the range
        preCaretRange.selectNodeContents(document.getElementById("input-area")); // Set the cloned range to the start of the editable div
        preCaretRange.setEnd(range.startContainer, range.startOffset); // Set the end of the range to the caret
        cursorPosition = preCaretRange.toString().length; // Get the length of the text in the range
    }

    // locate the word at the cursor position
    let start = cursorPosition;
    while (start > 0 && /\S/.test(text[start - 1])) {
        start--;
    }
    let end = cursorPosition;
    while (end < text.length && /\S/.test(text[end])) {
        end++;
    }

    let word = text.slice(start, end);
    word = word.toLowerCase();

    let tokens = text.split(/(\s+|[^\w\s])/g).filter(token => token.trim());
    let charIndex = 0;

    // locate the index of the word at the cursor position
    for (let i = 0; i < tokens.length; i++) {
        const tokenStart = charIndex;
        const tokenEnd = charIndex + tokens[i].length;

        // Check if the cursor position is within the current token
        if (cursorPosition >= tokenStart && cursorPosition <= tokenEnd) {
            index = i;
            break;
        }

        // Advance the character index, accounting for spaces between tokens
        charIndex = tokenEnd + 1; // +1 for the space
    }

    // check if the word has been deleted
    const originalTokens = old.split(/(\s+|[^\w\s])/g).filter(token => token.trim());
    let deleted = -1;
    for (let i = 0; i < originalTokens.length; i++) {
        if (originalTokens[i] !== tokens[i]) {
            deleted = i; // Index of the deleted word
            break;
        }
    }

    if (originalTokens.length > tokens.length) {
        deleted = originalTokens.length - 1;
    }

    // remove the deleted element from the output
    const all = document.getElementsByClassName("output_div");
    let all_inners = Array.from(all, el => el.innerHTML);
    if (deleted !== -1) {
        all_inners.splice(deleted, 1);
        output.innerHTML = all_inners.map(inner => `<div class="output_div">${inner}</div>`).join('');
    }

    const hanzi_options = getHanziOptions(word);

    if (hanzi_options.length > 0) {
        if (index >= all_inners.length) {
            // fill in the options for the new word at end of the output
            document.getElementById("options-wrapper").innerHTML += `<div class="options" style="display: flex; flex-direction: column"></div>`;
            options[index].innerHTML = hanzi_options.map((hanzi, i) => `<label><input name="${word}_${index}" type="radio" class="${index}" value="${hanzi}" onclick="editOutput(${index}, '${word}', ${i})">${hanzi}</label>`).join('');
            document.getElementsByClassName(`${index}`)[0].checked = true;


            output.innerHTML += `<div class="output_div">${hanzi_options[0]}</div>`;
            save.push(0);
        } else {
            for (var i = 0; i < options.length; i++) {
                options[i].style.display = "none";
            }
            document.getElementsByClassName("box-title3")[0].style.display = "flex";
            options[index].style.display = "flex";
            if (last_index != index) {
                let radios = document.getElementsByClassName(`${index}`);
                let m = radios[save[index]].value;
                radios[save[index]].checked = true;

                setOutputAtIndex(index, m);
            } else if (options[index].innerHTML == "") {
                options[index].innerHTML = "";
                for (var i = 0; i < hanzi_options.length; i++) {
                    options[index].innerHTML += `<label><input name="${word}_${index}" type="radio" class="${index}" value="${hanzi_options[i]}" onclick="editOutput(${index}, '${word}', ${i})">${hanzi_options[i]}</label>`;
                }
                save[index] = 0;
                document.getElementsByClassName(`${index}`)[0].checked = true;

                setOutputAtIndex(index, hanzi_options[0]);
            }
        }
    } else if (/^[a-zA-Z\s]+$/.test(word) && old != text) {
        for (var i = 0; i < options.length; i++) {
            options[i].style.display = "none";
        }
        document.getElementsByClassName("box-title3")[0].style.display = "none";
        setOutputAtIndex(index, word);
    } else {
        for (var i = 0; i < options.length; i++) {
            options[i].style.display = "none";
        }
        document.getElementsByClassName("box-title3")[0].style.display = "none";
    }
    old = text;
    lastWord = word;
    last_index = index;
    
    setTimeout(() => {
        addOutputHoverListeners();
    }, 10);
}

function editOutput(index, word, radio) {
    clearAllHighlights();
    // update the output with the new hanzi option
    const hanzi_options = getHanziOptions(word);
    setOutputAtIndex(index, hanzi_options[radio]);
    save[index] = radio;
    
    // After updating output, highlight both the romanization and hanzi
    setTimeout(() => {
        addOutputHoverListeners();
        highlightWord(index);
    }, 10);
}

// Edit the languages included in the hanzi options
function editLanguages(index) {
    languages_included[index] = !languages_included[index] ? 1 : 0;
}

// Helper function to copy the hanzi output to the clipboard
function copy() {
    const all = document.getElementsByClassName("output_div");
    let text = "";
    for (var i = 0; i < all.length; i++) {
        text += all[i].innerHTML;
    }
    navigator.clipboard.writeText(text);
}

// Highlight functionality
function highlightWord(wordIndex) {
    // Clear all previous highlights
    clearAllHighlights();
    
    // Highlight corresponding output div
    const outputDivs = document.querySelectorAll('#output-area .output_div');
    if (outputDivs[wordIndex]) {
        outputDivs[wordIndex].classList.add('word-highlight');
    }
    
    // Highlight corresponding input word
    highlightInputWordAtIndex(wordIndex);
}

function highlightInputWordAtIndex(wordIndex) {
    const inputArea = document.getElementById('input-area');
    const text = (inputArea.textContent || inputArea.innerText).replace(/\s+/g, ' ').trim();
    const words = text.split(/\s+/).filter(word => word.length > 0);
    
    if (wordIndex >= 0 && wordIndex < words.length) {
        // Create a temporary range to find the word boundaries
        const textNodes = getTextNodes(inputArea);
        let currentPos = 0;
        let wordStart = -1;
        let wordEnd = -1;
        
        // Find the character positions of the word
        for (let i = 0; i < words.length; i++) {
            if (i === wordIndex) {
                wordStart = currentPos;
                wordEnd = currentPos + words[i].length;
                break;
            }
            currentPos += words[i].length + 1; // +1 for space
        }
        
        if (wordStart >= 0 && wordEnd >= 0) {
            // Find the text node and offset for the word boundaries
            const startInfo = findTextNodeAndOffset(textNodes, wordStart);
            const endInfo = findTextNodeAndOffset(textNodes, wordEnd);
            
            if (startInfo && endInfo) {
                // Create a range and wrap it with a highlight span
                const range = document.createRange();
                range.setStart(startInfo.node, startInfo.offset);
                range.setEnd(endInfo.node, endInfo.offset);
                
                try {
                    const contents = range.extractContents();
                    const highlightSpan = document.createElement('span');
                    highlightSpan.className = 'input-word-highlight';
                    highlightSpan.appendChild(contents);
                    range.insertNode(highlightSpan);
                } catch (e) {
                    // Fallback if range operations fail
                    console.warn('Could not highlight input word:', e);
                }
            }
        }
    }
}

function getTextNodes(element) {
    const textNodes = [];
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    let node;
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    return textNodes;
}

function findTextNodeAndOffset(textNodes, targetOffset) {
    let currentOffset = 0;
    for (const node of textNodes) {
        const nodeLength = node.textContent.length;
        if (targetOffset <= currentOffset + nodeLength) {
            return {
                node: node,
                offset: targetOffset - currentOffset
            };
        }
        currentOffset += nodeLength;
    }
    return null;
}

function clearAllHighlights() {
    const highlightedElements = document.querySelectorAll('.word-highlight, .input-word-highlight');
    highlightedElements.forEach(el => {
        if (el.classList.contains('input-word-highlight')) {
            // For input highlights, replace the span with its text content
            const parent = el.parentNode;
            parent.replaceChild(document.createTextNode(el.textContent), el);
            parent.normalize(); // Merge adjacent text nodes
        } else {
            el.classList.remove('word-highlight');
        }
    });
}

function addInputAreaHoverListener() {
    const inputArea = document.getElementById('input-area');
    let lastHighlightedIndex = -1;
    
    inputArea.addEventListener('mousemove', (e) => {
        // Don't highlight during input processing
        if (isProcessingInput) return;
        
        // Get the current text and split into words
        const text = (inputArea.textContent || inputArea.innerText).replace(/\s+/g, ' ').trim();
        const words = text.split(/\s+/).filter(word => word.length > 0);
        
        if (words.length === 0) {
            if (lastHighlightedIndex !== -1) {
                clearAllHighlights();
                lastHighlightedIndex = -1;
            }
            return;
        }
        
        // Get character position from mouse coordinates
        const range = document.caretRangeFromPoint(e.clientX, e.clientY);
        if (!range) return;
        
        const tempRange = document.createRange();
        tempRange.selectNodeContents(inputArea);
        tempRange.setEnd(range.startContainer, range.startOffset);
        const charPosition = tempRange.toString().length;
        
        // Find which word the character position falls into
        let currentPos = 0;
        let wordIndex = -1;
        
        for (let i = 0; i < words.length; i++) {
            const wordStart = currentPos;
            const wordEnd = currentPos + words[i].length;
            
            if (charPosition >= wordStart && charPosition <= wordEnd) {
                wordIndex = i;
                break;
            }
            
            currentPos = wordEnd + 1; // +1 for space
        }
        
        // Only update highlighting if we're hovering over a different word
        if (wordIndex !== lastHighlightedIndex) {
            if (wordIndex >= 0 && wordIndex < words.length) {
                highlightWord(wordIndex);
                lastHighlightedIndex = wordIndex;
            } else {
                clearAllHighlights();
                lastHighlightedIndex = -1;
            }
        }
    });
    
    inputArea.addEventListener('mouseleave', () => {
        clearAllHighlights();
        lastHighlightedIndex = -1;
    });
}

function addOutputHoverListeners() {
    const outputDivs = document.querySelectorAll('#output-area .output_div');
    outputDivs.forEach((div, index) => {
        // Remove existing event listeners
        div.removeEventListener('mouseenter', div._hoverHandler);
        div.removeEventListener('mouseleave', div._leaveHandler);
        
        // Add new event listeners
        div._hoverHandler = () => {
            if (isProcessingInput) return;
            highlightWord(index);
        };
        div._leaveHandler = clearAllHighlights;
        
        div.addEventListener('mouseenter', div._hoverHandler);
        div.addEventListener('mouseleave', div._leaveHandler);
    });
}

// Load the language data from the API
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

// Setup the interval behavior for the input area
function setupInputAreaInterval() {
    let intervalId;
    const input_area = document.getElementById("input-area");
    input_area.addEventListener("focus", () => {
        isProcessingInput = true;
        clearAllHighlights();
        intervalId = setInterval(initiate, 200); // Run every 0.2 seconds
    });

    // Stop the loop when the textarea loses focus
    input_area.addEventListener("blur", () => {
        isProcessingInput = false;
        clearInterval(intervalId); // Stop the interval
    });
}


// SETUP
// Call this function when the page loads
loadLanguageData();

// Call this function to set up the interval behavior
setupInputAreaInterval();

// Initialize highlight functionality
addInputAreaHoverListener();
