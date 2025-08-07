class WordsManager {
    constructor() {
        this.selectedCharacters = [];
        this.currentCharacter = null;
        this.currentEditWordId = null;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Character search
        document.getElementById('search-character')?.addEventListener('click', () => this.searchCharacter());
        document.getElementById('character-code')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchCharacter();
        });

        // Word construction
        document.getElementById('add-character')?.addEventListener('click', () => this.addCharacter());
        document.getElementById('save-word')?.addEventListener('click', () => this.saveWord());
        document.getElementById('clear-word')?.addEventListener('click', () => this.clearWord());

        // Word management
        document.getElementById('filter-language')?.addEventListener('change', (e) => this.filterWords(e.target.value));

        // Modal handlers
        document.querySelector('.close')?.addEventListener('click', () => this.closeModal());
        document.getElementById('cancel-edit')?.addEventListener('click', () => this.closeModal());
        document.getElementById('save-edit')?.addEventListener('click', () => this.saveEditedWord());

        // Dynamic event listeners for word actions
        this.attachWordActionListeners();
    }

    attachWordActionListeners() {
        // Edit buttons
        document.querySelectorAll('.edit-word-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const wordData = JSON.parse(e.target.dataset.word);
                this.editWord(wordData);
            });
        });

        // Delete buttons
        document.querySelectorAll('.delete-word-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const wordId = e.target.dataset.wordId;
                this.deleteWord(wordId);
            });
        });
    }

    async searchCharacter() {
        const characterId = document.getElementById('character-code').value;
        const language = document.getElementById('language-select').value;

        if (!characterId) {
            this.showMessage('Please enter a character code', 'error');
            return;
        }

        if (!Number.isInteger(parseInt(characterId))) {
            this.showMessage('Please enter a valid character code', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/characters/${characterId}?language=${language}`);
            const data = await response.json();

            if (data.success) {
                this.displayCharacter(data.character);
            } else {
                this.showMessage(data.error || 'Character not found', 'error');
                this.hideCharacterDisplay();
            }
        } catch (error) {
            this.showMessage('Failed to retrieve character information', 'error');
            console.error('Search error:', error);
        }
    }

    displayCharacter(character) {
        this.currentCharacter = character;
        
        // Show character display section
        const displaySection = document.getElementById('character-display');
        displaySection.style.display = 'block';

        // Update character info
        document.getElementById('character-display-hanzi').textContent = character.character;
        document.getElementById('character-display-id').textContent = `(ID: ${character.id})`;

        // Update romanizations list
        const romanizationsList = document.getElementById('romanizations-list');
        romanizationsList.innerHTML = '';

        if (character.romanizations && character.romanizations.length > 0) {
            character.romanizations.forEach((romanization, index) => {
                const radioDiv = document.createElement('div');
                radioDiv.className = 'romanization-option';
                
                radioDiv.innerHTML = `
                    <input type="radio" id="roman_${index}" name="character-romanization" value="${romanization}">
                    <label for="roman_${index}">${romanization} (${character.character})</label>
                `;
                
                romanizationsList.appendChild(radioDiv);
            });

            // Auto-select first romanization
            document.querySelector('input[name="character-romanization"]').checked = true;
        } else {
            romanizationsList.innerHTML = '<div class="no-romanizations">No romanizations found for this character in the selected language.</div>';
        }

        // Enable add character button if romanizations exist
        document.getElementById('add-character').disabled = !character.romanizations || character.romanizations.length === 0;
    }

    hideCharacterDisplay() {
        document.getElementById('character-display').style.display = 'none';
        document.getElementById('add-character').disabled = true;
    }

    addCharacter() {
        if (!this.currentCharacter) return;

        const selectedRomanization = document.querySelector('input[name="character-romanization"]:checked');
        if (!selectedRomanization) {
            this.showMessage('Please select a romanization', 'error');
            return;
        }

        // Add character to selected list
        const characterData = {
            id: this.currentCharacter.id,
            character: this.currentCharacter.character,
            romanization: selectedRomanization.value
        };

        this.selectedCharacters.push(characterData);
        this.updateCharacterSequence();
        this.updateWordRomanization();
        this.enableSaveButton();

        // Clear current search
        document.getElementById('character-code').value = '';
        this.hideCharacterDisplay();
        this.currentCharacter = null;
    }

    updateCharacterSequence() {
        const sequenceDiv = document.getElementById('character-sequence');
        
        if (this.selectedCharacters.length === 0) {
            sequenceDiv.innerHTML = '<div class="empty-character-slot">Click "Add Character" to start building a word</div>';
            return;
        }

        sequenceDiv.innerHTML = '';
        this.selectedCharacters.forEach((char, index) => {
            const charDiv = document.createElement('div');
            charDiv.className = 'selected-character';
            charDiv.innerHTML = `
                <span class="character-text">${char.character}</span>
                <span class="character-romanization">${char.romanization}</span>
                <button type="button" class="remove-character" data-index="${index}">×</button>
            `;
            sequenceDiv.appendChild(charDiv);
        });

        // Add remove character event listeners
        document.querySelectorAll('.remove-character').forEach(button => {
            button.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.removeCharacter(index);
            });
        });
    }

    removeCharacter(index) {
        this.selectedCharacters.splice(index, 1);
        this.updateCharacterSequence();
        this.updateWordRomanization();
        
        if (this.selectedCharacters.length === 0) {
            this.disableSaveButton();
        }
    }

    updateWordRomanization() {
        const romanization = this.selectedCharacters.map(char => char.romanization).join(' ');
        document.getElementById('word-romanization').value = romanization;
    }

    enableSaveButton() {
        document.getElementById('save-word').disabled = false;
    }

    disableSaveButton() {
        document.getElementById('save-word').disabled = true;
    }

    async saveWord() {
        const romanization = document.getElementById('word-romanization').value.trim();
        const language = document.getElementById('word-language').value;

        if (!romanization) {
            this.showMessage('Please enter a romanization', 'error');
            return;
        }

        if (this.selectedCharacters.length === 0) {
            this.showMessage('Please add at least one character', 'error');
            return;
        }

        const wordData = {
            romanization: romanization,
            language: language,
            characters: this.selectedCharacters.map(char => char.id)
        };

        try {
            const response = await fetch('/api/words', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(wordData)
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('Word saved successfully!', 'success');
                this.clearWord();
                this.refreshWordsList();
            } else {
                this.showMessage(data.error || 'Failed to save word', 'error');
            }
        } catch (error) {
            this.showMessage('Failed to save word. Please try again.', 'error');
            console.error('Save error:', error);
        }
    }

    clearWord() {
        this.selectedCharacters = [];
        this.updateCharacterSequence();
        document.getElementById('word-romanization').value = '';
        document.getElementById('word-language').selectedIndex = 0;
        this.disableSaveButton();
        this.hideCharacterDisplay();
        document.getElementById('character-code').value = '';
        this.currentCharacter = null;
    }

    filterWords(language) {
        const wordItems = document.querySelectorAll('.word-item');
        
        wordItems.forEach(item => {
            if (!language || item.dataset.language === language) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    editWord(wordData) {
        this.currentEditWordId = wordData.id;
        
        // Populate modal fields
        document.getElementById('edit-romanization').value = wordData.romanization;
        document.getElementById('edit-language').value = wordData.language;
        
        // Show modal
        document.getElementById('edit-modal').style.display = 'block';
    }

    async saveEditedWord() {
        const romanization = document.getElementById('edit-romanization').value.trim();
        const language = document.getElementById('edit-language').value;

        if (!romanization) {
            this.showMessage('Please enter a romanization', 'error');
            return;
        }

        const wordData = {
            romanization: romanization,
            language: language,
            characters: [] // Note: We're not allowing character editing in this implementation
        };

        try {
            const response = await fetch(`/api/words/${this.currentEditWordId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(wordData)
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('Word updated successfully!', 'success');
                this.closeModal();
                this.refreshWordsList();
            } else {
                this.showMessage(data.error || 'Failed to update word', 'error');
            }
        } catch (error) {
            this.showMessage('Failed to update word. Please try again.', 'error');
            console.error('Update error:', error);
        }
    }

    async deleteWord(wordId) {
        if (!confirm('Are you sure you want to delete this word?')) {
            return;
        }

        try {
            const response = await fetch(`/api/words/${wordId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('Word deleted successfully!', 'success');
                this.refreshWordsList();
            } else {
                this.showMessage(data.error || 'Failed to delete word', 'error');
            }
        } catch (error) {
            this.showMessage('Failed to delete word. Please try again.', 'error');
            console.error('Delete error:', error);
        }
    }

    closeModal() {
        document.getElementById('edit-modal').style.display = 'none';
        this.currentEditWordId = null;
    }

    async refreshWordsList() {
        try {
            const response = await fetch('/api/words');
            const data = await response.json();

            if (data.success) {
                this.updateWordsDisplay(data.words);
            }
        } catch (error) {
            console.error('Error refreshing words list:', error);
        }
    }

    updateWordsDisplay(words) {
        const wordsListDiv = document.getElementById('words-list');
        
        if (words.length === 0) {
            wordsListDiv.innerHTML = '<div class="no-words">No words found. Create your first word above!</div>';
            return;
        }

        wordsListDiv.innerHTML = '';
        words.forEach(word => {
            const wordDiv = document.createElement('div');
            wordDiv.className = 'word-item';
            wordDiv.dataset.wordId = word.id;
            wordDiv.dataset.language = word.language;

            const charactersText = word.character_details.map(char => char.character).join('');
            
            wordDiv.innerHTML = `
                <div class="word-content">
                    <span class="word-characters">${charactersText}</span>
                    <span class="word-romanization">(${word.romanization})</span>
                    <span class="word-language">- ${word.language.charAt(0).toUpperCase() + word.language.slice(1)}</span>
                </div>
                <div class="word-actions">
                    <button type="button" class="edit-word-button" data-word='${JSON.stringify(word)}'>Edit</button>
                    <button type="button" class="delete-word-button" data-word-id="${word.id}">Delete</button>
                </div>
            `;
            
            wordsListDiv.appendChild(wordDiv);
        });

        // Reattach event listeners
        this.attachWordActionListeners();
    }

    showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('message-container');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        messageContainer.appendChild(messageDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WordsManager();
});