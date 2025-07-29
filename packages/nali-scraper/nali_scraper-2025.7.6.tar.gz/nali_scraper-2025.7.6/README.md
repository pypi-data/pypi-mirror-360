<div style="text-align: center">
  <img src="1.png"  alt="1"/>
  <h3>nali</h3>
  <p>대학별 공지사항 크롤링을 위한 통합 스크래핑 도구</p>
</div>

## Legal Disclaimer

이 프로젝트는 비공식 프로젝트이며, 특정 대학교 또는 기관과 아무런 공식적인 관련이 없습니다. 모든 데이터는 공개된 웹페이지를 기반으로 수집되며, 수집된 정보의 정확성이나 최신성은 보장되지 않습니다.

사용자는 본 소프트웨어를 사용할 때 발생할 수 있는 모든 책임을 스스로 부담하며, 개발자는 이로 인해 발생하는 어떠한 직접적, 간접적 손해에 대해서도 책임지지 않습니다.

# nali

## Overview

nali 패키지(이하 '날리')는 대학별 공지사항을 스크래핑하기 위한 Python 라이브러리입니다.

모듈화되고 추상화된 설계 방식을 사용하여 새로운 대학교를 쉽게 확장할 수 있도록 하였으며, 외부 의존성은 `requests`와 `beautifulsoup4`만으로 최소화했습니다.

예외 처리, 명확한 인터페이스, 그리고 기여자가 쉽게 확장할 수 있는 구조를 보장하도록 노력하고 있습니다.

## Quick start

```pycon
>>> from nali import Nali, School
>>> n = Nali(School.SOME_UNIV)
>>> notices = n.get_notices(page=1, search="장학금")
```

## Installation

```shell
$ pip install nali
```

## Package Structure

```
nali/
 ├── src/  # 실제 패키지 소스
 │    └── nali/
 │         ├── scrapers/
 │         │    ├── __init__.py
 │         │    ├── base.py
 │         │    ├── some_univ.py
 │         │    └── ...
 │         ├── __init__.py
 │         ├── core.py
 │         ├── enums.py
 │         ├── exceptions.py
 │         └── models.py
 ├── tests/  # 테스트 코드
 │    ├── __init__.py
 │    └── test_scrapers.py
 └── pyproject.toml
```

## Contributing

> 이걸 보고 계시는 여러분의 도움이 필요합니다!
>
> 오픈소스 프로젝트에 거리낌 없이 기여해주세요. 늘 기다리고 있습니다. :D

다음과 같은 기여를 하실 수 있습니다:

- 대학교 스크래퍼 신규 추가 ⭐
- 웹페이지 구조 변경에 따른 스크래핑 로직 수정
- 모듈의 소스코드 오류 수정

[기여 가이드라인](https://github.com/wizley9999/nali/blob/main/CONTRIBUTING.md)을 확인해주세요.

## License

MIT 라이선스를 따르고 있습니다. 자세한 내용은 `LICENSE`를 확인하세요.
