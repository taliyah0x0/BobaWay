# Words Database Feature Specification

## Overview

This feature adds a new tab to the admin portal that allows administrators to manage words in the database. Words are composed of characters (referenced by integer IDs) and have associated romanizations and language information.

## Database Schema

### Tables

#### `words` table
- `id` (INTEGER, PRIMARY KEY, AUTO_INCREMENT)
- `romanization` (TEXT, NOT NULL) - The romanized pronunciation of the word
- `language` (TEXT, NOT NULL) - The language code (e.g., 'taiwanese', 'mandarin', etc.)
- `characters` (INTEGER ARRAY, NOT NULL) - Array of character IDs in order (e.g., [123, 456, 789])

#### `characters` table (Assumed to exist)
- `id` (INTEGER, PRIMARY KEY, AUTO_INCREMENT)
- `hanzi` (TEXT, NOT NULL) - The actual character (e.g., '你', '好')

#### `korean` table (Assumed to exist)
- `hanzi_id` (INTEGER, NOT NULL) - Foreign key to characters table
- `roman` (TEXT, NOT NULL) - The character romanization

#### `shanghainese` table (Assumed to exist)
- `hanzi_id` (INTEGER, NOT NULL) - Foreign key to characters table
- `roman` (TEXT, NOT NULL) - The character romanization

#### `vietnamese` table (Assumed to exist)
- `hanzi_id` (INTEGER, NOT NULL) - Foreign key to characters table
- `roman` (TEXT, NOT NULL) - The character romanization

#### `taiwanese` table (Assumed to exist)
- `hanzi_id` (INTEGER, NOT NULL) - Foreign key to characters table
- `roman` (TEXT, NOT NULL) - The character romanization

Note: it can be assumed that korean, shanghainese, vietnamese, and taiwanese are the only language options.

## Admin Portal Interface

### New Tab: "Words Management"

#### Location
- Add a new tab in the admin portal navigation
- Tab name: "Words Management"
- Tab icon: 📝 (or appropriate icon)

#### Main Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Words Management                                            │
├─────────────────────────────────────────────────────────────┤
│ Language: [Dropdown ▼] | Character Code: [Input] [Search]   │
├─────────────────────────────────────────────────────────────┤
│ Current Word: [Display area]                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Character: 你 (ID: 123)                                 │ │
│ │ Romanizations:                                          │ │
│ │ ○ ni3 (你)                                              │ │
│ │ ○ ni2 (你)                                              │ │
│ │ ○ ni4 (你)                                              │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Word Construction:                                          │
│ [Character 1: 你] [Character 2: 好] [Character 3: ___]       │
│ Romanization: [ni3 hao3]                                    │
│ Language: [taiwanese]                                       │
│                                                             │
│ [Save Word] [Clear] [Back]                                  │
├─────────────────────────────────────────────────────────────┤
│ All Words:                                                  │
│ • 你好 (ni3 hao3) - taiwanese [Edit] [Delete]                │
│ • 謝謝 (xie4 xie4) - taiwanese [Edit] [Delete]               │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Functionality

### 1. Language Selection
- **Dropdown menu** with all available languages from the database
- **Default selection**: 'shanghainese'
- **Dynamic loading**: Languages are fetched from the database
- **Validation**: Must select a language before proceeding

### 2. Character Code Input
- **Input field**: Accepts integer character codes
- **Search button**: Triggers character lookup
- **Validation**: 
  - Must be a valid integer
  - Character must exist in the database
  - Show error message if character not found

### 3. Character Display and Romanization Selection
- **Character display**: Show the actual character and its ID
- **Romanization list**: Display all romanizations associated with the character
- **Selection method**: Radio buttons for single selection
- **Format**: "romanization (character)" - e.g., "ni3 (你)"
- **Empty state**: Show "No romanizations found" if none exist

### 4. Word Construction
- **Character sequence**: Display selected characters in order
- **Character removal**: Allow removing individual characters (X button)
- **Character reordering**: Drag and drop functionality (optional enhancement)
- **Romanization concatenation**: Auto-generate combined romanization
- **Manual override**: Allow manual editing of final romanization

### 5. Word Management
- **Save functionality**: 
  - Validate all required fields
  - Check for duplicate words
  - Save to database with proper relationships
- **Clear functionality**: Reset all inputs and selections
- **Back functionality**: Return to previous state or main admin panel

### 6. Recent Words Display
- **List format**: Show recently created/edited words
- **Display format**: "Character (romanization) - language"
- **Actions**: Edit and Delete buttons for each word
- **Pagination**: If many words exist
- **Search/filter**: Optional enhancement

## API Endpoints

### Required Backend Routes

#### GET `/admin/words`
- **Purpose**: Display the words management interface
- **Response**: HTML template with form and current words list

#### GET `/api/characters/<int:character_id>`
- **Purpose**: Get character details and romanizations
- **Response**: JSON
```json
{
  "success": true,
  "character": {
    "id": 123,
    "character": "你",
    "romanizations": [
      "ni3",
      "ni2"
    ]
  }
}
```

#### POST `/api/words`
- **Purpose**: Create a new word
- **Request Body**: JSON
```json
{
  "romanization": "ni3 hao3",
  "language": "taiwanese",
  "characters": [
    123,
    456
  ]
}
```
- **Response**: JSON with success status and word ID

#### PUT `/api/words/<int:word_id>`
- **Purpose**: Update an existing word
- **Request Body**: Same as POST
- **Response**: JSON with success status

#### DELETE `/api/words/<int:word_id>`
- **Purpose**: Delete a word
- **Response**: JSON with success status

#### GET `/api/words`
- **Purpose**: Get list of words (for recent words display)
- **Query Parameters**: 
  - `language` (optional): Filter by language
  - `limit` (optional): Number of words to return
  - `offset` (optional): Pagination offset
- **Response**: JSON
```json
{
  "success": true,
  "words": [
    {
      "id": 1,
      "romanization": "ni3 hao3",
      "language": "taiwanese",
      "characters": [123, 456],
      "character_details": [
        {"id": 123, "character": "你"},
        {"id": 456, "character": "好"}
      ]
    }
  ]
}
```

## Database Queries

### Required SQL Queries

#### 1. Get Character with Romanizations
```sql
SELECT c.id, c.character, r.romanization
FROM characters c
LEFT JOIN character_romanizations r ON c.id = r.character_id
WHERE c.id = ?
ORDER BY r.romanization;
```

#### 2. Get All Languages
```sql
SELECT DISTINCT language FROM words ORDER BY language;
```

#### 3. Create Word
```sql
INSERT INTO words (romanization, language, characters) 
VALUES (?, ?, ?);
```

#### 4. Get Words with Character Details
```sql
SELECT w.id, w.romanization, w.language, w.characters
FROM words w
WHERE w.language = ?
ORDER BY w.id DESC;
```

#### 5. Get Character Details for Word
```sql
SELECT c.id, c.character
FROM characters c
WHERE c.id IN (SELECT unnest(w.characters) FROM words w WHERE w.id = ?)
ORDER BY array_position(w.characters, c.id);
```

#### 6. Check for Duplicate Words
```sql
SELECT COUNT(*) 
FROM words 
WHERE romanization = ? AND language = ? AND characters = ?;
```

#### 7. Update Word
```sql
UPDATE words 
SET romanization = ?, language = ?, characters = ?
WHERE id = ?;
```

#### 8. Delete Word
```sql
DELETE FROM words WHERE id = ?;
```

## Error Handling

### Validation Errors
- **Character not found**: "Character with ID {id} not found"
- **Invalid character code**: "Please enter a valid character code"
- **No language selected**: "Please select a language"
- **No characters selected**: "Please add at least one character"
- **Duplicate word**: "A word with these characters and romanization already exists"

### System Errors
- **Database connection**: "Unable to connect to database"
- **Character lookup failed**: "Failed to retrieve character information"
- **Save failed**: "Failed to save word. Please try again."

## User Experience Considerations

### Accessibility
- **Keyboard navigation**: All interactive elements must be keyboard accessible
- **Screen reader support**: Proper ARIA labels and semantic HTML
- **Focus management**: Clear focus indicators and logical tab order
- **Error announcements**: Screen reader announcements for validation errors

### Mobile Responsiveness
- **Touch targets**: Minimum 44px for touch interactions
- **Responsive layout**: Adapt to different screen sizes
- **Touch-friendly**: Large buttons and easy scrolling

### Performance
- **Lazy loading**: Load character data only when needed
- **Caching**: Cache frequently accessed data (languages, common characters)
- **Debouncing**: Debounce character code input to avoid excessive API calls

## Security Considerations

### Input Validation
- **SQL injection**: Use parameterized queries
- **XSS prevention**: Sanitize all user inputs
- **CSRF protection**: Include CSRF tokens in forms
- **Access control**: Ensure only admin users can access

### Data Integrity
- **Foreign key constraints**: Proper database constraints
- **Transaction handling**: Use transactions for multi-table operations
- **Data validation**: Validate all inputs before database operations

## Implementation Notes

### Technology Stack
- **Backend**: Python Flask (existing)
- **Database**: SQLite/PostgreSQL (existing)
- **Frontend**: HTML, CSS, JavaScript (existing)
- **AJAX**: For dynamic character lookup and word management

### Development Phases
1. **Phase 1**: Basic word creation and management
2. **Phase 2**: Enhanced UI/UX and error handling
3. **Phase 3**: Advanced features and optimizations

### Code Organization
- **Models**: `Word` class with character array handling
- **Views**: Admin routes and API endpoints
- **Templates**: Words management interface
- **Static files**: CSS and JavaScript for the interface
- **Tests**: Unit and integration tests

### Database Considerations
- **Array handling**: Ensure proper handling of integer arrays in the database
- **Character validation**: Validate that all character IDs exist before saving
- **Performance**: Consider indexing on language and romanization fields
- **Data migration**: Plan for any existing data migration if needed

This specification provides a comprehensive foundation for implementing the words database feature in the admin portal.
