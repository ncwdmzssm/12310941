import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin 
import time 
import random 
import requests
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.tandfonline.com/journals/mmis20")
    page.screenshot(path="example.png")
    page_content = page.content()
    print(page_content)
    browser.close()

soup3=BeautifulSoup(page_content, 'html.parser')
arts=soup3.select("div.articleEntryContainer")
articles=[]
for article in arts:
    try:
        #find都是输出HTML,不能直接用
        art_title=article.find('div', class_='art_title').find('span').get_text(strip=True)
        art_authors=article.find('div', class_='articleEntryAuthor').find_all('span')
        art_authors=[author.get_text(strip=True) for author in art_authors]
        art_date=article.find('span', class_='article-date').get_text(strip=True)
        articles.append({'title':art_title,'authors':art_authors,'date':art_date})
    except Exception as e:
        print(f"解析文章时出错: {e}")
    except requests.RequestException as e:
        print(f"抓取详情页失败: {e}")
    time.sleep(random.uniform(1, 3))  # 随机延时1到3秒，模拟人类行为，避免被封IP
    
df1=pd.DataFrame(articles)
df1.to_csv('data.csv', encoding= 'utf-8',index=False) 
print("数据已保存到 data.csv")
