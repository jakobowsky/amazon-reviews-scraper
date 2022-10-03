import json

from requests_html import HTMLSession, HTML
from typing import List


class ReviewsScraper:
    def __init__(self, asin: str, pages: int):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.11 (KHTML, like Gecko) '
                          'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        self.asin = asin
        self.pages = pages
        self.url = f'https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_getr_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&pageNumber='
        self.session = HTMLSession()

    def get_reviews_from_page(self, page_content: int) -> List[dict]:
        reviews = []
        for tag in page_content.find('div[data-hook=review]'):
            user = tag.find('span[class=a-profile-name]', first=True).text
            title = tag.find('a[data-hook=review-title]', first=True).text
            star_rating = tag.find('i[data-hook=review-star-rating]', first=True).text
            date = tag.find('span[data-hook=review-date]', first=True).text
            message = tag.find('span[data-hook=review-body]', first=True).text.replace('\n', '')
            reviews.append({
                'user': user,
                'title': title,
                'star_rating': star_rating,
                'date': date,
                'message': message
            })
        return reviews

    def has_reviews(self, page_content: HTML) -> bool:
        if page_content.find('div[data-hook=review]'):
            return True
        return False

    def iterate_over_pages(self) -> List[dict]:
        reviews = []
        for i in range(1, self.pages + 1):
            print(f"Page: {i}")
            r = self.session.get(f'{self.url}{i}', headers=self.headers)
            if self.has_reviews(r.html):
                new_reviews = self.get_reviews_from_page(r.html)
                print("New reviews")
                print(new_reviews)
                reviews += new_reviews
            else:
                print("No reviews")
                print(r.html)
                break
        return reviews

    def save_to_file(self, reviews: List[dict]):
        with open('results.json', 'w') as f:
            json.dump(reviews, f)


if __name__ == '__main__':
    asin = 'B000MTST70'
    scraper = ReviewsScraper(asin, 3)
    all_reviews = scraper.iterate_over_pages()
    print("Done.")
    print(all_reviews)
    scraper.save_to_file(all_reviews)
