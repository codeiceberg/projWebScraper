import requests
from bs4 import BeautifulSoup
from urllib import parse
import datetime
from pathlib import Path
import pandas as pd

BASE_URL = 'https://books.toscrape.com/'


def scrape_categories():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    book_categories = []

    category_list = soup.select(
        "#default > div.container-fluid.page > div > div > aside > div.side_categories > ul > li > ul")[0]
    for category in category_list.find_all("li"):
        category_link = category.a["href"]
        category_name = category.a.text.strip()
        book_categories.append({'title': category_name, 'link': category_link})
    return book_categories


def scrape_books(category, pages):
    books_data = []
    index_url = BASE_URL + "{}"

    url = index_url.format(category)
    page = 1
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("h3")
        for book in books:
            book_url = parse.urljoin(url, book.a["href"])
            book_details = scrape_book_details(book_url)
            books_data.append(book_details)

        print(f"PAGE: {page}, BOOKS COUNT: {len(books_data)}")

        next_page = soup.select_one(".next")
        if page == pages:
            break
        elif next_page:
            url = parse.urljoin(url, next_page.a["href"])
        else:
            break

        page += 1

    return books_data


def scrape_book_details(book_url):
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1').text.strip()
    description = soup.select_one('#content_inner > article > p').text.strip()
    rating = soup.find('p', class_='star-rating')['class'][1]
    image_url = parse.urljoin(book_url, soup.find('img')['src'])
    price = soup.find('p', class_='price_color').text.strip()
    availability = soup.find('p', class_='instock availability').text.strip()

    return {'Title': title,
            'Description': description,
            'Rating': rating,
            'Image URL': image_url,
            'Availability': availability,
            'Price': price}


def get_category(title):
    # result = None
    # for category in side_categories:
    #     if category['title'] == 'Travel':
    #         result = category.get('link')
    #         break
    # print(result)
    book_categories = scrape_categories()
    result = [element for element in book_categories
              if element['title'] == title]
    return result


def save_csv(data, category):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_folder = Path('out') / category
    output_folder.mkdir(parents=True, exist_ok=True)
    filename = f'{timestamp}.csv'
    output_path = output_folder / filename
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)


def main():

    category_name_input = input("Please enter book category: ")
    pages = int(input("Please enter number of page or (0 for all): "))

    categories = get_category(category_name_input)
    if categories:
        category_sub_url = categories[0].get('link')
        scraped_books = scrape_books(category_sub_url, pages)
        save_csv(scraped_books, category_name_input)
        # print(scraped_books)
    else:
        print("Category not found.")


if __name__ == "__main__":
    main()
