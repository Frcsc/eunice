# Eunice Django Server

This is a python based application that is intended to scrape coindesk.com for the latest news articles and expose the data via API endpoints. Django and Django REST framework (DRF) where used along with beautifulsoup to achieve this task. Django provides a custom command setup that can be customized to run commands and DRF is is a powerful and flexible toolkit for building APIs.

## Development Installation

Make sure you are in the root directory of the project, the one with `Pipfile` in it.

I'll recommend collaborators to create a new file called `.env` in the root directory. Then copy the contents of `dev-example.env` into the newly created
`.env` file. This holds the environmental variables to configure the project. The provided `dev-example.env` file is for development use, and not for production.

Please note that I have also configured the necessary defaults for this application to run if collaborators do not want to set up environmental variables.

### Application building

This project requires the following dependencies, so first install them on your system using your preferred method. Also note that PostgreSQL is the database of choice for this application. Since the exercise instructions allow the assumption that the database is up and running, we can assume the databse available and accessible with the provided credentials from the excercise file.

- Python 3.10
- Pipenv

1. Install application packages

```

pipenv install
```

2. Apply database migrations (With the assumption that the database is already available)

```

pipenv run ./manage.py migrate
```

3. (optional) create an admin user for the admin panel

```

pipenv run ./manage.py create_admin_user
```

### Run the scraping command

The script utilises django's custom command, and it can be found in `coin_desk/management/scrap_coin_desk`. It will scrap the 20 latest articles that meets the tasks's requirements and store them in the database without duplicating articles.

1. Run this command

```

pipenv run ./manage.py scrap_coin_desk
```

### Access the data through an API endpoint

Please note that you have to start the local server before testing the api endpoints. Also note the default server port is 8000

1. Run this command to start the local server

```

pipenv run ./manage.py runserver
```

After the local server starts, you can test the API endpoints with postman or curl. With curl, use the following:

2. Get all articles

Please note that I have returned the `article_id` in this response to allow for easy retrieval of a single article instance in the subsequent API.
```
curl http://127.0.0.1:8000/articles

```

or
```
curl http://localhost:8000/articles

```

3. Get a single article based on `article_id`

```
curl http://127.0.0.1:8000/articles/article_id

```

or
```
curl http://localhost:8000/articles/article_id

```

### Test Cases

- I wrote test cases for both the scraping script and the API endpoints. For external api calls during scraping,
I relied on mocking the methods that make external API calls. All tests can be found in `coin_desk/tests/`. For generating data during testing I utilized [factory-boy](https://factoryboy.readthedocs.io/en/stable/orms.html).


- To run all test cases, use this command

```
pipenv run ./manage.py test
```

- To run a specific test class, provide the path. For example, `coin_desk.tests.test_articles_api.TestArticleListAndRetrieve`

```
pipenv run ./manage.py test coin_desk.tests.test_articles_api.TestArticleListAndRetrieve
```

- To run a specific test function, provide the test path. For example, `coin_desk.tests.test_articles_api.TestArticleListAndRetrieve.test_get_all_articles`

```
pipenv run ./manage.py test coin_desk.tests.test_articles_api.TestArticleListAndRetrieve.test_get_all_articles
```

### Database Design and Model Explanation

To store the scraped articles, I created a Django model named Article, which maps to a table in the PostgreSQL database. This model is designed to efficiently capture and store all necessary information about each article, including metadata like the title, author, publication date, content, url and associated tags. Additionally I relied on Django's ORM for all database interactions. The case for django's ORM includes protection against sql Injection, readability abstraction and maintainability.

### Scraping Design Explanation

After investigation the coindesk website I found out that the latest articles page was showing about 20 artciles with a `show more` button at the bottom of the page. Upon clicking this button, another batch of articles were displayed. After some digging and inspection, I found an API endpoint that coindesk was calling that returned about 40 articles per page in a pagination. The two most useful items from this API response where `_id` and `url` for the article_id and the url to the details page of the article respectively. Using each `url`, I retrieved the details of the articles that matched our criteria and stored them in our database.

### Scraping Implementation

1. Parent class: I built a parent class called `CoinDeskScrapper`, which was intended to handles external API calls, timestamp formating, scraping article details etc. The following methods are present in this class.

- `format_time(self)`: Used for datetime formating
- `map_section(self, partial_url)`: This method was used to check if the scraped article belongs to the sections that needs to be excluded. It takes a single argument.
- `get_articles(page, size)`: This method was used for retrieving a list of articles. Due to the api pagination, a mamixmum of 40 articles can be requested on a single page. It takes two arguments, `page` and `size` which represent page number within the pagination and how many articles should be returned on that page respectively. Please refer to the references for the external coin desk api and the relevant params.
- `get_item_details(self, url)`: This method was used for scraping an articles details page. It takes a single arguement `url`, which is the full url to the article details page. Using `BeautifulSoup`, these values where extracted: `author`, `title`, `published_at`, `content` and `a list of tags`.

2. Child class and it's processes: I built a second class called `Command` that inherits the first class `CoinDeskScrapper`. This class has four broad methods:

- `fetch_article_urls_and_ids(self)`: This method calls `get_articles(page, size)` from the parent class in a while loop to collect 20 valid articles and append them to a list called `valid_urls_and_ids`. The method return this list when called.

- `fetch_articles_details(self, articles)`: This methods takes a list of dictionaries that have `_id` and `url` keys as an argument. It return a list of dictionaries that contain these keys `id, title, url, author, published_at, content, tags`

- `save_articles(self, articles)`: This method takes a single aruguement which is a list of dictionaries primarily returned from this method `fetch_articles_details(self, articles)`. This method saves the articles in the database, if a unique key already existing in the database, the other fields are updated.
- `handle(self, *args, **options)`: This is the method that is called first when the scrapping script is ran. It first calls `fetch_article_urls_and_ids()` if not valid data is returned the program is exited. Otherwise, it then calls `fetch_articles_details(article_urls_and_ids)` passing the valid list returned from `fetch_article_urls_and_ids()`. If no issues the program attemps to save the scrapped articles in the databse.

### API Development

I used Django Rest framework to build two API endpoint

- `ArticleListView`: This class process requests made to `/articles`. It retrieves all the article instances in the databse and returns them with the fields `id, title, author, published_at, snippet and url`. The `id` was not mentioned in the exercise as a key to be returned, but I included it to allow collaborators to be able to retreive a single article. If no articles exists in the database, an empty list is returned.

- `ArticleDetailView`: This class process requests made to `/articles/article_id`. It retrieves a single article instance from the databse based on the `article_id` in the params and returns the instance with these keys `id, title, author, published_at, snippet and url`. If the `article_id` is not found a `404 Not found` status is returned.

### References

- Coindesk API : [clik here](https://www.coindesk.com/pf/api/v3/content/fetch/please-stop)
- Sample of Coindesk API call with pagination on the 5th page [click here](https://www.coindesk.com/pf/api/v3/content/fetch/please-stop?query={"language":"en","size":20,"page":5,"format":"timeline"}):
- Django: [clik here](https://www.djangoproject.com/)
- Django REST framwork: [clik here](https://www.django-rest-framework.org/)
- Pre-commit: [click here](https://pre-commit.com/#install)
