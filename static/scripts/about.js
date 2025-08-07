let news_titles = [
    'Reviving Taiwanese: A Language Being Reclaimed Across Borders | Connected Feature',
    'Taliyah Huang: Young Inventor of Bobaway, Online Translator that Converts English to Taiwanese Ep 253',
    'Taiwanese American College Student Invents App To Preserve Taiwanese Hokkien | TaiwanPlus News',
    'The college student who developed an English to Taiwanese translator ft. Taliyah Huang',
    'How she built this: sophomore Taliyah Huang invents a Taiwanese-English translation tool to bridge language gaps',
    '台裔女大生創建BobaWay台英翻譯網頁 助台裔美國人學台語',
    '【寶島有意思】台裔女大生Taliyah創建BobaWay'];
let news_des = [
    'CONNECTED on TaiwanPlus',
    'Talking Taiwan',
    'TaiwanPlus News',
    'Radio Taiwan International',
    'TaiwaneseAmericanOrg',
    '世界新聞網',
    '寶島聯播網'];
let news_links = ['https://www.youtube.com/watch?v=qEXrODPL-Cw&t=279s',
                  'https://talkingtaiwan.com/taliyah-huang-young-inventor-of-bobaway-online-translator-that-converts-english-to-taiwanese-ep-253/',
                  'https://www.youtube.com/watch?v=VlkX0hAB5Fw',
                  'https://en.rti.org.tw/radio/programMessagePlayer/programId/1435/id/108711',
                  'https://www.taiwaneseamerican.org/2023/07/taliyah-huang-interview-bobaway/',
        'https://web.archive.org/web/20230710092638/https://www.worldjournal.com/wj/story/121359/7289244',
                  'https://podcasters.spotify.com/pod/show/rkes7e3m79o/episodes/TaliyahBobaWay--20230724-e279v5h'];
let news_dates = ['December 2024', 'September 2024', 'April 2024', 'August 2023', 'July 2023', 'July 2023', 'July 2023']
let slide_page = 0;

function loadNow() {
    const container = document.getElementById("current-news");
    for (let i = 0; i < 3; i++) {
        container.innerHTML += `
            <a href="${news_links[i]}" target="_blank" class="news-item">
                <h4><strong><u>${news_titles[i]}</u></strong></h4>
                <p><u>${news_des[i]}</u></p>
                <p><i>${news_dates[i]}</i></p>
            </a>
        `;
    }
}

function changeSlide(index) {
    const container = document.getElementById("current-news");
    container.innerHTML = '';
    slide_page += index;
    
    if (slide_page >= news_titles.length) {
        slide_page %= news_titles.length;
    }
    if (slide_page < 0) {
        slide_page = news_titles.length - 1;
    }
    
    for (let i = slide_page; i < slide_page + 3; i++) {
        idx = i % news_titles.length;
        container.innerHTML += `
            <a href="${news_links[idx]}" target="_blank" class="news-item">
                <h4><strong><u>${news_titles[idx]}</u></strong></h4>
                <p><u>${news_des[idx]}</u></p>
                <p><i>${news_dates[idx]}</i></p>
            </a>
        `;
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadNow();
});