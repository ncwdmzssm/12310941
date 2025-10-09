#寻找下一页链接
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin 
import time 
import random 
import requests
from playwright.sync_api import sync_playwright
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,args=["--disable-blink-features=AutomationControlled"])
    page = browser.new_page(user_agent=random.choice(USER_AGENTS))
    page.goto("https://www.tandfonline.com/action/showOpenAccess?journalCode=mmis20")
    time.sleep(random.uniform(3, 6))
    try:
    # 等待标题元素出现（最长等10秒）
        page.wait_for_selector("div.art_title span", timeout=10000)
        page_content = page.content()
    except Exception as e:
        print("关键元素未加载，跳过该页")
    page.screenshot(path="example.png")
    page_content = page.content()
    browser.close()

soup3=BeautifulSoup(page_content, 'html.parser')
arts=soup3.select("div.articleEntryContainer")
articles=[]
page_num=1
next_page = soup3.find('li', class_="pageLink-with-arrow").find('a')['href']
next_link=urljoin("https://www.tandfonline.com/action/showOpenAccess?journalCode=mmis20",next_page)
print(f"链接一：{next_page}/n 链接二：{next_link}")
print(f"当前页面文章数：{len(arts)}")
print(f"第二页链接：{next_link}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,args=["--disable-blink-features=AutomationControlled"])
    page = browser.new_page(user_agent=random.choice(USER_AGENTS))
    page.goto(next_link)
    time.sleep(random.uniform(3, 6))
    try:
    # 等待标题元素出现（最长等10秒）
        page.wait_for_selector("div.art_title span", timeout=10000)
        page_content = page.content()
    except Exception as e:
        print("关键元素未加载，跳过该页")
    page.screenshot(path="example2.png")
    page_content = page.content()
    browser.close()
soup4=BeautifulSoup(page_content, 'html.parser')
arts2=soup4.select("div.articleEntryContainer")
print(f"第二页当前页面文章数：{len(arts2)}")
for article in arts2:
    try:
        #find都是输出HTML,不能直接用
        art_title=article.find('div', class_='art_title').find('span').get_text(strip=True)
        art_authors=article.find('div', class_='articleEntryAuthor').find_all('a')
        art_authors=[author.get_text(strip=True) for author in art_authors]
        art_date=article.find('div', class_='article-date').get_text(strip=True)
        articles.append({'title':art_title,'authors':art_authors,'date':art_date,'page':page_num})
    except Exception as e:
        print(f"解析文章时出错: {e}")

    time.sleep(random.uniform(1, 3))  # 随机延时1到3秒，模拟人类行为，避免被封IP
df2=pd.DataFrame(articles)
df2.to_csv('data2.csv', encoding= 'utf-8',index=False)
print("数据已保存到 data2.csv")
next_page = soup4.find('li', class_="pageLink-with-arrow").find('a')['href']
next_link=urljoin("https://www.tandfonline.com/action/showOpenAccess?journalCode=mmis20",next_page)
print(f"第三页链接：{next_link}")
i=3
next_link=f"https://www.tandfonline.com/pb/widgets/ajax/graphql/topContentView/ajaxOpenAccessController?pbContext=%3BsubPage%3Astring%3AOpen+Access+Content%3Bctype%3Astring%3AJournal+Content%3Bjournal%3Ajournal%3Ammis20%3Bwgroup%3Astring%3APublication+Websites%3Bwebsite%3Awebsite%3ATFOPB%3BrequestedJournal%3Ajournal%3Ammis20%3Bpage%3Astring%3ATop+Content+View&widgetId=94efccda-badd-445b-a3dd-54ae401791d6&pageSize=10&subjectTitle=&startPage={i}"
print(f"尝试第三页链接：{next_link}")