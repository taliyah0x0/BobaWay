let news_titles = ['Featured','Interview','Interview','Interview','Interview','報道','訪問'];
let news_des = ['Taiwan Plus','Taiwan Plus','Talking Taiwan','Radio Taiwan International','TaiwaneseAmericanOrg','世界新聞網','寶島聯播網'];
let news_links = ['https://www.youtube.com/watch?v=qEXrODPL-Cw&t=277s','https://www.youtube.com/results?search_query=taiwan+plus+taliyah','https://talkingtaiwan.com/taliyah-huang-young-inventor-of-bobaway-online-translator-that-converts-english-to-taiwanese-ep-253/','https://en.rti.org.tw/radio/programMessagePlayer/programId/1435/id/108711','https://www.taiwaneseamerican.org/2023/07/taliyah-huang-interview-bobaway/','https://www.worldjournal.com/wj/story/121359/7289244','https://podcasters.spotify.com/pod/show/rkes7e3m79o/episodes/TaliyahBobaWay--20230724-e279v5h'];
let slide_page = 0;

function loadNow() {
    const container = document.getElementById("current-news");
    for (let i = 0; i < 3; i++) {
        container.innerHTML += `
            <a href="${news_links[i]}" target="_blank" class="news-item">
                <h4>${news_titles[i]}</h4>
                <p>${news_des[i]}</p>
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
                <h4>${news_titles[idx]}</h4>
                <p>${news_des[idx]}</p>
            </a>
        `;
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadNow();
});