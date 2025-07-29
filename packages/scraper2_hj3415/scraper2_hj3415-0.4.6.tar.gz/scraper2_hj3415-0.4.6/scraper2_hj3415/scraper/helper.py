import random
import subprocess
import asyncio
import pandas as pd
from io import StringIO
from pathlib import Path

from playwright.async_api import Locator
from utils_hj3415 import setup_logger


mylogger = setup_logger(__name__, 'WARNING')


COMMON_USER_AGENTS = [
    # --- Chrome (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.5481.100 Safari/537.36",

    # --- Chrome (Mac) ---
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/111.0.5563.64 Safari/537.36",

    # --- Firefox (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) "
    "Gecko/20100101 Firefox/108.0",

    # --- Firefox (Linux) ---
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
    "Gecko/20100101 Firefox/109.0",

    # --- Edge (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.5481.100 Safari/537.36 "
    "Edg/110.0.1587.49",

    # --- Safari (Mac) ---
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/16.1 Safari/605.1.15",

    # --- Safari (iPhone iOS) ---
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/16.0 Mobile/15E148 Safari/604.1",

    # --- Chrome (Android) ---
    "Mozilla/5.0 (Linux; Android 13; SM-S908N) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.5481.65 Mobile Safari/537.36",

    # --- Opera (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.5481.77 Safari/537.36 OPR/96.0.4693.80",

    # --- Older Edge (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/92.0.902.62 Safari/537.36 "
    "Edg/92.0.902.62",
]

def get_random_user_agent() -> str:
    """랜덤 User-Agent 하나 반환"""
    return random.choice(COMMON_USER_AGENTS)


def ensure_playwright_installed():
    # 사용자 홈 디렉토리 기준으로 설치 경로 확인
    cache_dir = Path.home() / ".cache" / "ms-playwright"

    if not cache_dir.exists():
        print("Playwright driver installing...")
        subprocess.run(["playwright", "install"], check=True)


async def get_df_from_table(table_locator: Locator, header=0) -> pd.DataFrame:
    """
    Playwright에서 받은 table locator로부터 HTML을 추출해 pandas DataFrame으로 변환

    - table_locator: Playwright의 table 요소 Locator 객체
    - header: 테이블의 헤더구조 - 기본형 : 0 아니면 [0,1,...]
    - return: pandas.DataFrame
    """
    # HTML 추출
    html = await table_locator.evaluate("el => el.outerHTML")  # <table> 태그까지 포함

    try:
        df = pd.read_html(StringIO(html), header=header)[0]
        mylogger.debug(df)
    except ValueError as e:
        raise ValueError("pandas.read_html()에서 테이블을 찾지 못했습니다") from e

    if header == 0: # 일반적인 헤더의 경우만
        # '항목' 열 정리 (있는 경우)
        if '항목' in df.columns:
            df['항목'] = df['항목'].str.replace('펼치기', '').str.strip()

        # 열 이름 정리
        df.columns = (df.columns
                      .str.replace('연간컨센서스보기', '', regex=False)
                      .str.replace('연간컨센서스닫기', '', regex=False)
                      .str.replace('(IFRS연결)', '', regex=False)
                      .str.replace('(IFRS별도)', '', regex=False)
                      .str.replace('(GAAP개별)', '', regex=False)
                      .str.replace('(YoY)', '', regex=False)
                      .str.replace('(QoQ)', '', regex=False)
                      .str.replace('(E)', '', regex=False)
                      .str.replace('.', '', regex=False)
                      .str.strip())

    return df


async def wait_with_retry(locator, retries=3, delay=3):
    for i in range(retries):
        try:
            await locator.wait_for(state="attached", timeout=10000)
            return True
        except Exception:
            if i < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise


def is_ymd_format(date_str: str) -> bool:
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False


