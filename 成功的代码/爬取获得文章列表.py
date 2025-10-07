import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin 
import time 
import random 
import requests
from playwright.sync_api import sync_playwright

base_url = "https://www.tandfonline.com/action/showOpenAccess?journalCode=mmis20"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
]

current_url = base_url
all_articles = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,args=["--disable-blink-features=AutomationControlled"])

    page = browser.new_page(user_agent=random.choice(USER_AGENTS))
    # 隐藏自动化痕迹
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    """)
    i=0
    while current_url:
        print(f"正在爬取页面: page {i+1}")
        page.goto(current_url)
        time.sleep(random.uniform(3, 6))
        try:
            # 等待标题元素出现（最长等10秒）
            page.wait_for_selector("div.art_title span", timeout=10000)
            page_content = page.content()
        except Exception as e:
            print("关键元素未加载，跳过该页")
            continue

        soup = BeautifulSoup(page_content, 'html.parser')
        articles = soup.select("div.articleEntryContainer")
        for article in articles:
            try:
                art_title=article.find('div', class_='art_title').find('span').get_text(strip=True)
                art_authors=article.find('div', class_='articleEntryAuthor').find_all('a')
                art_authors=[author.get_text(strip=True) for author in art_authors]
                art_date=article.find('div', class_='article-date').get_text(strip=True)
                art_link=article.find('div', class_='art_title').find('a')['href']
                all_articles.append({'title': art_title, 'authors': art_authors, 'date': art_date,'link': urljoin(base_url, art_link)})
            except Exception as e:
                print(f"解析文章时出错: {e}")
        i+=1
        target = soup.select_one('li.pageLink-with-arrow a.nextPage.js__ajaxSearchTrigger')
        if target:
            next_link=f"https://www.tandfonline.com/pb/widgets/ajax/graphql/topContentView/ajaxOpenAccessController?pbContext=%3BsubPage%3Astring%3AOpen+Access+Content%3Bctype%3Astring%3AJournal+Content%3Bjournal%3Ajournal%3Ammis20%3Bwgroup%3Astring%3APublication+Websites%3Bwebsite%3Awebsite%3ATFOPB%3BrequestedJournal%3Ajournal%3Ammis20%3Bpage%3Astring%3ATop+Content+View&widgetId=94efccda-badd-445b-a3dd-54ae401791d6&pageSize=10&subjectTitle=&startPage={i}"
            current_url=next_link if next_link else None
        else:
            print("未找到下一页，爬取结束")
            current_url = None
        time.sleep(random.uniform(2, 5))

    browser.close()

df1=pd.DataFrame(all_articles)
df1.to_csv('文章基础信息.csv', encoding= 'utf-8',index=False) 
print("数据已保存到 文章基础信息.csv")
