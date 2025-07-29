# Contributing Guidelines

그 어떤 기여도 환영합니다!

코드 리뷰가 원활하게 진행되고, 기여하신 내용이 머지(Merge)될 가능성을 높이기 위해 이 페이지의 내용을 꼭 정독해 주세요.

## 버그 제보

버그 제보는 [이슈](https://github.com/wizley9999/nali/issues)를 등록해 주세요.

## Pull Requests

기여하실 때는 GitHub에서 [날리 저장소](https://github.com/wizley9999/nali)를 포크(fork)하는 방식을 권장합니다.

1. [날리 저장소](https://github.com/wizley9999/nali)를 포크하세요. 페이지 상단 근처에 있는 'Fork' 버튼을 클릭하면, 여러분의 GitHub 계정 아래 코드 복사본이 생성됩니다.

2. 이렇게 생성한 복사본을 여러분의 컴퓨터로 클론(clone)해 주세요.
   ```shell
   $ git clone https://github.com/[YOUR_USERNAME]/nali.git
   $ cd nali
   ```

3. 변경 사항을 담을 새로운 브랜치(branch)를 만들고 작업을 해주세요. `main` 브랜치에서는 작업이 불가합니다.
   ```shell
   $ git checkout -b my-feature
   ```

4. 작업이 완료되면, 변경 사항을 Git에 기록하기 위해 다음 명령어를 실행해 주세요.
   ```shell
   $ git add modified_files
   $ git commit
   ```

5. 변경 사항을 GitHub에 푸시(push)해 주세요.
   ```shell
   $ git push -u origin my-feature
   ```

6. 마지막으로, 복사한 `nali` 저장소의 GitHub 웹 페이지로 이동한 뒤, 'Pull Request' 버튼을 눌러 변경 사항을 리뷰 요청하면 됩니다.

## 대학교 스크래퍼 신규 추가 ⭐

1. `nali/enums.py`에 학교를 등록해 주세요.
   ```python
   class School(Enum):
       SEOUL = "seoul"
       # Add more universities here, e.g.,
   ```

   ⚠️ Enum 값(예: "seoul")은 고유한 문자열이어야 하며, 해당 scraper 파일명과 동일하게 사용하는 것이 좋습니다.

2. `nali/scrapers/`에 Scraper 클래스를 작성해 주세요.
   ```shell
   $ touch seoul.py
   ```

   파일 안에는 BaseScraper를 상속받는 새로운 클래스(예: SeoulScraper)를 정의해야 합니다.

   ```python
   from .base import BaseScraper
   from ..models import Notice
   
   
   class SeoulScraper(BaseScraper):
       def scrape(self, page: int, search: str | None = None) -> list[Notice]:
           soup = self.fetch_page(url="your_url")

           # your scraping logic here

           return []
   ```

   `base.py`에 구현된 BaseScraper의 `fetch_page` 함수를 통해 간단하게 `GET`, `POST` 요청을 보내고 response.text를 `BeautifulSoup` 객체로 받을 수
   있습니다.

3. 마지막으로, `nali/scrapers/__init__.py`에 새로 만든 Scraper 클래스를 등록합니다.
   ```python
   def get_scraper(school: School):
       scrapers = {
           School.SEOUL: SeoulScraper,
           # Add new scraper mappings here
       }

       return scrapers.get(school)()
   ```

## 웹페이지 구조 변경에 따른 스크래핑 로직 수정

`nali/scrapers/[YOUR_SCRAPER].py`의 `scrape` 함수를 수정해 주세요.

```python
from .base import BaseScraper
from ..models import Notice


class SeoulScraper(BaseScraper):
    def scrape(self, page: int, search: str | None = None) -> list[Notice]:
        soup = self.fetch_page(url="your_url")

        # your scraping logic here

        return []
```

웹페이지의 URL, 구조 등이 변경되면 로직 수정이 필요합니다.

## 테스트 (Optional)

기여한 스크래퍼에 대한 테스트는 `tests/` 폴더에 자동화되어 있습니다.

PR을 보내기 전, 아래 명령어로 테스트가 통과하는지 확인해 주세요.

```shell
$ pytest
```

또는 특정 학교에 대해서만 테스트하고 싶은 경우

```shell
$ pytest --school=SEOUL
```

명령어를 통해 테스트 통과 여부를 확인할 수 있습니다.
