# Good reference: https://pantip.com
# Data collected on Oct 18, 2021, 8:28 PM
# Data collected from https://pantip.com/tag/มนุษย์เงินเดือน with filter on "คลังกระทู้โปรด" (Favourite posts)
# only collect posts with more than 50 comments.

import datetime
import time
from os import path
import re

import pytz

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

MAIN_TAG_URL = 'https://pantip.com/tag/มนุษย์เงินเดือน'
CHROME_DRIVER_PATH = './chromedriver'
COMMENT_COUNT_THRESHOLD = 50

service = Service(CHROME_DRIVER_PATH)
browser = webdriver.Chrome(service=service)


# Text Preprocessing
def pre_process(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               "]+", flags=re.UNICODE)

    url_pattern = re.compile("http\S+")

    text = url_pattern.sub(r'', text)

    return emoji_pattern.sub(r'', text)


# Utilities
def parse_post_date(raw_date_time: str):
    month_dict = {
        'มกราคม': 1,
        'กุมภาพันธ์': 2,
        'มีนาคม': 3,
        'เมษายน': 4,
        'พฤษภาคม': 5,
        'มิถุนายน': 6,
        'กรกฎาคม': 7,
        'สิงหาคม': 8,
        'กันยายน': 9,
        'ตุลาคม': 10,
        'พฤศจิกายน': 11,
        'ธันวาคม': 12
    }
    date, time_text = raw_date_time.split(' เวลา ')
    date_number, month_text, be_year = date.split(' ')
    month = month_dict[month_text]
    time_24_hr, _ = time_text.split(' ')
    hour, minute = time_24_hr.split(':')
    return datetime.datetime(int(be_year) - 543, month, int(date_number), int(hour), int(minute), 0, 0,
                             pytz.timezone('Asia/Bangkok'))


def parse_comment_date(raw_date_time: str):
    month_dict = {
        'มกราคม': 1,
        'กุมภาพันธ์': 2,
        'มีนาคม': 3,
        'เมษายน': 4,
        'พฤษภาคม': 5,
        'มิถุนายน': 6,
        'กรกฎาคม': 7,
        'สิงหาคม': 8,
        'กันยายน': 9,
        'ตุลาคม': 10,
        'พฤศจิกายน': 11,
        'ธันวาคม': 12
    }
    date, time_text = raw_date_time.split(' เวลา  ')
    date_number, month_text, be_year = date.split(' ')
    month = month_dict[month_text]
    time_24_hr, _ = time_text.split(' ')
    hour, minute, second = time_24_hr.split(':')
    return datetime.datetime(int(be_year) - 543, month, int(date_number), int(hour), int(minute), int(second), 0,
                             pytz.timezone('Asia/Bangkok'))


def execute_javascript(driver: WebDriver, script: str):
    driver.execute_script(script)


def scroll_down(driver, pixel: int):
    execute_javascript(driver, f'window.scrollTo(0, {pixel})')


def go_to_bottom(driver):
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def post_collection():
    browser.get(MAIN_TAG_URL)

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-type="7"]'))
    )

    scroll_down(browser, 700)
    time.sleep(1)

    favorite_posts_button = browser.find_element(by=By.CSS_SELECTOR, value='a[data-type="7"]')
    favorite_posts_button.click()

    time.sleep(2)

    for _ in range(50):
        go_to_bottom(browser)
        time.sleep(1)

    post_list = browser.find_elements(by=By.CSS_SELECTOR, value='ul.pt-list > li.pt-list-item')
    post_list = post_list[11:]

    processed_list = []
    for post in post_list:
        title_element = post.find_element(by=By.CSS_SELECTOR, value='div.pt-list-item__title > h2 > a')
        title = title_element.text
        post_url = title_element.get_attribute('href')
        post_id = post_url.replace('https://pantip.com/topic/', '')

        comment_count_element = post.find_element(by=By.CSS_SELECTOR,
                                                  value='div.pt-list-item__stats > span.pt-li_stats-comment')
        raw_comment_count = comment_count_element.text.replace('message', '')

        if 'K' in raw_comment_count:
            comment_count = int(float(raw_comment_count.replace('K', '')) * 1000)
        else:
            comment_count = int(raw_comment_count)

        vote_count_element = post.find_element(by=By.CSS_SELECTOR,
                                               value='div.pt-list-item__stats > span.pt-li_stats-vote')
        raw_vote_count = vote_count_element.text.replace('add_box', '')

        if 'K' in raw_vote_count:
            vote_count = int(float(raw_vote_count.replace('K', '')) * 1000)
        else:
            vote_count = int(raw_vote_count)

        published_date_element = post.find_element(by=By.CSS_SELECTOR, value='div.pt-list-item__info > span')
        published_date = parse_post_date(published_date_element.get_attribute('title'))

        processed_list.append({
            'post_id': post_id,
            'title': title,
            'url': post_url,
            'comment_count': comment_count,
            'vote_count': vote_count,
            'published_date': published_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
        })

    filtered_post = list(filter(lambda p: p['comment_count'] > COMMENT_COUNT_THRESHOLD, processed_list))

    df = pd.DataFrame(filtered_post)
    df.to_csv('posts.csv')


def comment_collection():
    posts_df = pd.read_csv('posts.csv')
    posts_df.rename(columns={"Unnamed: 0": "index"})

    comments = []
    for idx, post in posts_df.iterrows():
        browser.get(post.url)
        time.sleep(1)
        go_to_bottom(browser)
        time.sleep(1)

        isCompleted = False
        while not isCompleted:
            try:
                loading_bar_element = browser.find_element(by=By.CSS_SELECTOR,
                                                           value='a.bar-paging-ed')
                browser.execute_script("arguments[0].click();", loading_bar_element)
                time.sleep(3)
                go_to_bottom(browser)
                time.sleep(2)
            except:
                isCompleted = True

        post_content_element = browser.find_element(by=By.CSS_SELECTOR, value='.main-post .display-post-story')
        post_content = pre_process(post_content_element.text)
        published_at_element = browser.find_element(by=By.CSS_SELECTOR,
                                                    value='.main-post .display-post-timestamp abbr')
        published_at = parse_comment_date(published_at_element.get_attribute('title'))

        comments.append({
            'comment_id': f'{post.post_id}-0',
            'comment_body': post_content,
            'collected_at': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            'published_at': published_at.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            'reply_to': None,
        })

        comment_element_list = browser.find_elements(by=By.CSS_SELECTOR,
                                                     value='.section-comment:not(.sub-comment):not(.hideid):not(.remove-comment)')
        for comment_element in comment_element_list:
            comment_number_id = comment_element.find_element(by=By.CSS_SELECTOR,
                                                             value='span.display-post-number').id
            comment_id = f'{post.post_id}-{comment_number_id}'

            comment_body_element = comment_element.find_element(by=By.CSS_SELECTOR, value='.display-post-story')
            comment_body = pre_process(comment_body_element.text)

            comment_published_at_element = comment_element.find_element(by=By.CSS_SELECTOR,
                                                                        value='.display-post-timestamp abbr')
            comment_published_at = parse_comment_date(comment_published_at_element.get_attribute('title'))

            comments.append({
                'comment_id': comment_id,
                'comment_body': comment_body,
                'collected_at': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                'published_at': comment_published_at.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                'reply_to': post.post_id,
            })

        posts_df.loc[idx, 'comment_count'] = len(comments) - 1
        posts_df.loc[idx, 'published_date'] = published_at.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        print(f'{int((idx + 1) / len(posts_df) * 100)}% - Done {idx + 1} post(s) from {len(posts_df)} posts')

    posts_df.to_csv('posts.csv')
    comments_df = pd.DataFrame(comments)
    comments_df.to_csv('comments.csv')


if __name__ == '__main__':
    if not path.exists('posts.csv'):
        post_collection()
    if not path.exists('comments.csv'):
        comment_collection()
    else:
        pass

    browser.quit()
