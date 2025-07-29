import argparse
import asyncio
from ..krx300.krx300 import sync_with_mongo

def main():
    parser = argparse.ArgumentParser(description="Krx300 CLI")
    subparsers = parser.add_subparsers(dest='command', help='명령어', required=True)

    # 'sync' 명령어 추가
    subparsers.add_parser('sync', help='몽고db와 krx300의 싱크를 맞춥니다.')

    args = parser.parse_args()

    match args.command:
        case 'sync':
            try:
                asyncio.run(sync_with_mongo())
            except Exception as e:
                print(f"에러 발생: {e}")

        case _:
            print("지원하지 않는 명령입니다.")
