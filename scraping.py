# モジュールのインポート
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd


# WebDriverの設定関数
def setup_driver(driver_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")  # シークレットモードで起動
    cService = webdriver.ChromeService(executable_path=driver_path)
    return webdriver.Chrome(service=cService, options=options)


# 情報を収集する関数
def collect_info(url, filename, SAMPLE_SIZE=40):
    if SAMPLE_SIZE > 40:
        SAMPLE_SIZE = 40

    driver.get(url)  # 対象サイトにアクセス

    links = get_link(sample=SAMPLE_SIZE)  # ワインのリンクを取得
    print(f"{len(links)}件のワインリンクを取得しました。")

    df = create_df(links)  # 各ワインの詳細ページにアクセスして情報を取得
    print(f"\n{len(df)}件のワイン情報を取得しました。")

    df.to_csv(
        filename, index=False, encoding="utf-8-sig"
    )  # データフレームをCSVファイルに保存
    print(f"{filename}に保存しました。")


# ワインのリンクを取得する関数
def get_link(sample=40):
    print("ワインのリンクを取得しています...")
    links = []
    for i in range(1, 2 * sample, 2):
        wine = driver.find_element(
            By.CSS_SELECTOR,
            f"#__layout > div > div.flex.min-h-screen.flex-col > div.flex.flex-grow.flex-col.justify-start > div.pb-60px.md\:pb-20 > div > div > div > div:nth-child({i}) > div.relative.whitespace-normal.mb-4 > p > a",
        )
        links.append(wine.get_attribute("href"))
    return links


# 各ワインの詳細ページにアクセスして情報を取得する関数
def create_df(links):
    names, texts, cnt = [], [], 0
    print("各ワインの詳細ページにアクセスしています...")
    for i, link in enumerate(links):
        driver.get(link)
        try:
            name = get_name()  # ワインの名前を取得
            text = get_text()  # ワインの説明を取得
            names.append(name)
            texts.append(text)
            cnt += 1
            print(f"\n{cnt}件目: {name}\n説明: {text}")
        except:
            print(f"\n{i + 1}/{len(links)}：リンクの情報取得に失敗しました。")
            continue
    return pd.DataFrame({"name": names, "text": texts})


# ワインの名前を取得する関数
def get_name():
    selector = "#__layout > div > div.flex.min-h-screen.flex-col > div.flex.flex-grow.flex-col.justify-start > div.pb-60px.md\:pb-20 > div > div > div.relative.mx-auto.mb-10.md\:mb-20.md\:flex.md\:justify-center > div.max-w-screen-sm.md\:relative.md\:flex-grow > section.mb-8.mt-5.md\:mb-10.md\:mt-0 > div.mb-7.flex.justify-between.md\:mb-8 > h1 > span.mb-2\.5.block"
    cnt = 0
    while True:
        cnt += 1
        if cnt > 100:
            raise Exception(
                "ワインの名前が取得できませんでした。CSSセレクタを確認してください。"
            )
        try:
            name = driver.find_element(By.CSS_SELECTOR, selector)
            return name.text
        except:
            continue


# ワインの説明を取得する関数
def get_text():
    selector = "#__layout > div > div.flex.min-h-screen.flex-col > div.flex.flex-grow.flex-col.justify-start > div.pb-60px.md\:pb-20 > div > div > div:nth-child(3) > section > div.mb-4.md\:mb-8 > p"
    cnt = 0
    while True:
        cnt += 1
        if cnt > 100:
            raise Exception(
                "ワインの説明が取得できませんでした。CSSセレクタを確認してください。"
            )
        try:
            text = driver.find_element(By.CSS_SELECTOR, selector)
            return text.text
        except:
            continue


if __name__ == "__main__":
    CHROMEDRIVER = "chromedriver-win64\chromedriver.exe"
    HOME_URL = "https://www.enoteca.co.jp/ranking/"
    CSV_FOLDER = "static/csv/"

    # driverの設定
    driver = setup_driver(CHROMEDRIVER)

    redwine_url = f"{HOME_URL}red?td_seg=tds773385tds990077"
    whitewine_url = f"{HOME_URL}white?td_seg=tds990077tds773385"
    sparklingwine_url = f"{HOME_URL}sparkling?td_seg=tds990077tds773385"

    # 情報の収集
    collect_info(url=redwine_url, filename=f"{CSV_FOLDER}redwine.csv")
    collect_info(url=whitewine_url, filename=f"{CSV_FOLDER}whitewine.csv")
    collect_info(url=sparklingwine_url, filename=f"{CSV_FOLDER}sparklingwine.csv")
    print("情報の収集が完了しました。")

    # 収集した情報を統合してCSVファイルに保存
    redwine_df = pd.read_csv(f"{CSV_FOLDER}redwine.csv")
    whitewine_df = pd.read_csv(f"{CSV_FOLDER}whitewine.csv")
    sparklingwine_df = pd.read_csv(f"{CSV_FOLDER}sparklingwine.csv")
    wine_df = pd.concat([redwine_df, whitewine_df, sparklingwine_df], ignore_index=True)
    print(wine_df)

    # 全ワイン情報をCSVファイルに保存
    wine_df.to_csv(f"{CSV_FOLDER}wine.csv", index=False, encoding="utf-8-sig")
    print("全ワイン情報をwine.csvに保存しました。")
