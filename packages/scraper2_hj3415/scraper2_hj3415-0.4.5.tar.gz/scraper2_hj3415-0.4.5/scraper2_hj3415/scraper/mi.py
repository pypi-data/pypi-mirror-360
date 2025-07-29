import asyncio
import random
import time
from playwright.async_api import async_playwright, Page

from utils_hj3415 import setup_logger, tools
from . import helper
from db2_hj3415.mi import Sp500, Kospi, Kosdaq, Wti, Usdidx, Usdkrw, Silver, Gold, Gbond3y, Chf, Aud


mylogger = setup_logger(__name__, 'WARNING')


async def parse_markets_type1(page: Page, market:str, url: str, columns: list | None, header: int | list, selector: str) -> dict:
    page.set_default_timeout(3000)
    mylogger.info(f"Fetching {market} from {url}")
    await page.goto(url, timeout=10000, wait_until="domcontentloaded")
    mylogger.debug(f"페이지 제목: {await page.title()}")
    await asyncio.sleep(2)

    try:
        table_locator = page.locator(selector)
        await helper.wait_with_retry(table_locator)
        table_html = await table_locator.inner_html()
        mylogger.debug(table_html[:100])

        df = await helper.get_df_from_table(table_locator, header)
        df = df.dropna(how="all").reset_index(drop=True)  # 전부 NaN인 행 제거
        if columns:
            df.columns = columns
        mylogger.debug(df)

        if df.empty:
            mylogger.warning(f"{market} 테이블이 비어있음")
            return {}

        return df.iloc[0].to_dict()

    except Exception as e:
        mylogger.error(f"{market} 테이블 파싱 실패: {e}")
        return {}


async def parse_sp500(page: Page) -> Sp500 | None:
    market = 'sp500'
    url='https://finance.naver.com/world/sise.nhn?symbol=SPI@SPX'
    columns = ['날짜', '종가', '전일대비', '시가', '고가', '저가']
    header = 0
    selector = "#dayTable"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    if data_dict:
        return Sp500(**data_dict)
    return None


async def parse_kospi(page: Page) -> Kospi | None:
    market = 'kospi'
    url = "https://finance.naver.com/sise/sise_index_day.nhn?code=KOSPI"
    columns = None
    header = 0
    selector = "table.type_1"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    converted_data = {
        "날짜": data_dict["날짜"],
        "거래대금": data_dict["거래대금(백만)"] * 1_000_000,
        "거래량": data_dict["거래량(천주)"] * 1_000,
        "등락률": data_dict["등락률"],
        "전일비": data_dict["전일비"],
        "체결가": data_dict["체결가"]
    }
    if converted_data:
        return Kospi(**converted_data)
    return None


async def parse_kosdaq(page: Page) -> Kosdaq | None:
    market = 'kosdaq'
    url = "https://finance.naver.com/sise/sise_index_day.nhn?code=KOSDAQ"
    columns = None
    header = 0
    selector = "table.type_1"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    converted_data = {
        "날짜": data_dict["날짜"],
        "거래대금": data_dict["거래대금(백만)"] * 1_000_000,
        "거래량": data_dict["거래량(천주)"] * 1_000,
        "등락률": data_dict["등락률"],
        "전일비": data_dict["전일비"],
        "체결가": data_dict["체결가"]
    }
    if converted_data:
        return Kosdaq(**converted_data)
    return None


async def parse_wti(page: Page) -> Wti | None:
    market = 'wti'
    url = "https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=OIL_CL&fdtc=2"
    columns = ['날짜', '종가', '전일대비', '등략률']
    header = 0
    selector = "body > div > table"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    if data_dict:
        return Wti(**data_dict)
    return None


async def parse_usdkrw(page: Page) -> Usdkrw | None:
    market = 'usdkrw'
    url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW"
    columns = ['날짜', '매매기준율', '전일대비', '현찰로 사실 때', '현찰로 파실 때', '송금 보내실 때', '송금 받으실 때']
    header = [0,1]
    selector = "body > div > table"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    if data_dict:
        return Usdkrw(**data_dict)
    return None


async def parse_silver(page: Page) -> Silver | None:
    market = 'silver'
    url = "https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=CMDT_SI&fdtc=2"
    columns = ['날짜', '종가', '전일대비', '등략률']
    header = 0
    selector = "body > div > table"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    if data_dict:
        return Silver(**data_dict)
    return None


async def parse_gold(page: Page) -> Gold | None:
    market = 'gold'
    url = "https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=CMDT_GC&fdtc=2"
    columns = ['날짜', '종가', '전일대비', '등략률']
    header = 0
    selector = "body > div > table"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    if data_dict:
        return Gold(**data_dict)
    return None


async def parse_gbond3y(page: Page) -> Gbond3y | None:
    market = 'gbond3y'
    url = "https://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y"
    columns = ['날짜', '종가', '전일대비', '등략률']
    header = 0
    selector = "body > div > table"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    if data_dict:
        return Gbond3y(**data_dict)
    return None


async def parse_chf(page: Page) -> Chf | None:
    market = 'chf'
    url = "https://finance.naver.com/marketindex/worldDailyQuote.nhn?fdtc=4&marketindexCd=FX_USDCHF"
    columns = ['날짜', '종가', '전일대비', '등략률']
    header = 0
    selector = "body > div > table"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    if data_dict:
        return Chf(**data_dict)
    return None


async def parse_aud(page: Page) -> Aud | None:
    market = 'aud'
    url = "https://finance.naver.com/marketindex/worldDailyQuote.nhn?fdtc=4&marketindexCd=FX_USDAUD"
    columns = ['날짜', '종가', '전일대비', '등략률']
    header = 0
    selector = "body > div > table"
    data_dict = await parse_markets_type1(page, market, url, columns, header, selector)
    mylogger.debug(data_dict)
    if data_dict:
        return Aud(**data_dict)
    return None


async def parse_usdidx(page: Page) -> Usdidx | None:
    market = 'usdidx'
    url = "https://finance.naver.com/marketindex/worldExchangeDetail.nhn?marketindexCd=FX_USDX"

    page.set_default_timeout(3000)
    mylogger.info(f"Fetching {market} from {url}")
    await page.goto(url, timeout=10000, wait_until="domcontentloaded")
    mylogger.debug(f"페이지 제목: {await page.title()}")
    await asyncio.sleep(2)

    result = {}
    try:
        # 날짜 추출
        date_locator = page.locator("#content > div.spot > div.exchange_info > span.date")
        await helper.wait_with_retry(date_locator)
        date_str = await date_locator.inner_text()
        mylogger.debug(f"날짜: {date_str}")
        result['날짜'] = date_str

        # 인덱스값 추출
        index_locator = page.locator("#content > div.spot > div.today > p.no_today > em[class^='no_'] span")
        # await helper.wait_with_retry(index_locator)
        span_texts = await index_locator.all_text_contents()  # em.no_down > span 의 모든 텍스트를 리스트로 가져옴
        index_str = ''.join(span_texts)  # 리스트를 문자열로 합쳐서 최종 숫자 형태 만들기
        mylogger.debug(f"인덱스: {index_str}")  # 예: 98.9000
        result['인덱스'] = tools.to_float(index_str)

        # 전일대비 추출
        exday_locator = page.locator("#content > div.spot > div.today > p.no_exday")
        await helper.wait_with_retry(exday_locator)
        mylogger.debug((await exday_locator.inner_html()))

        ico_locator = exday_locator.locator("em").nth(0)  # 등락 아이콘 추출
        ico_class = await ico_locator.locator("span.ico").get_attribute("class")  # 예: 'ico down' 또는 'ico up'

        abs_value_locator = exday_locator.locator("em[class^='no_']").nth(0)  # 전일대비의 절대값
        span_texts = await abs_value_locator.locator('span[class^="no"], span.jum').all_inner_texts()
        abs_value = ''.join(span_texts)  # '0.2400'

        sign = '-' if 'down' in ico_class else '+'  # 부호 적용
        change_value = float(sign + abs_value)

        result['전일대비'] = change_value

        # 등락율 추출
        percent_locator = exday_locator.locator("em[class^='no_']").nth(1)
        percent_html = await percent_locator.inner_html()   # 부호 판단: inner_html에 'minus'가 있으면 '-'
        sign = '-' if 'minus' in percent_html else '+'
        digits = await percent_locator.locator('span[class^="no"], span.jum').all_inner_texts() # 숫자 부분 추출
        percent_value = sign + ''.join(digits) + '%'
        result['등락률'] = percent_value

    except Exception as e:
        mylogger.error(f"{market} 파싱 실패: {e}")
        return None

    data_dict = result
    mylogger.debug(data_dict)
    if data_dict:
        return Usdidx(**data_dict)
    return None

T = Sp500 | Kospi | Kosdaq | Wti | Usdkrw | Silver | Gold | Gbond3y | Chf | Aud | Usdidx | None

async def parse_all() -> dict[str, T]:
    start_time = time.time()  # 시작 시간 기록

    results: dict[str, T] = {}
    parsers = [
        parse_sp500,
        parse_kospi,
        parse_kosdaq,
        parse_wti,
        parse_usdkrw,
        parse_usdidx,
        parse_silver,
        parse_gold,
        parse_gbond3y,
        parse_chf,
        parse_aud
    ]
    max_retry = 2
    retry_counts: dict[str, int] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=helper.get_random_user_agent(),
                                            locale="ko-KR")

        i = 0
        while i < len(parsers):
            parser = parsers[i]
            name = parser.__name__.split('_')[1]  # 예 - parse_sp500 의 뒤쪽 문자열 sp500
            print("Parsing... " + name)

            page = await context.new_page()
            try:
                result = await parser(page)
                if result == {}:
                    retry_counts[name] = retry_counts.get(name, 0) + 1
                    if retry_counts[name] <= max_retry:
                        mylogger.warning(f"{name} 빈 결과 재시도 {retry_counts[name]}회")
                        parsers.append(parser)
                    else:
                        mylogger.error(f"{name} 실패 - 최대 재시도 초과")
                        results[name] = None
                else:
                    print(result)
                    results[name] = result
                i += 1
            except Exception as e:
                mylogger.error(f"Error while parsing {name}: {e}")
                results[name] = None
                i += 1
            finally:
                await page.close()
                await asyncio.sleep(random.uniform(4.0, 6.0))
        await context.close()
        await browser.close()

    end_time = time.time()  # 종료 시간 기록
    elapsed = end_time - start_time
    print(f"총 실행 시간: {elapsed:.2f}초")  # 또는 mylogger.info 사용 가능

    return results