# Amazon Product Web Scraping Using Python, MongoDB Atlas and Data Analytics

ECI146 Python Course Project, Lovely Professional University

A Python system that collects product data, cleans it with Pandas, stores it in
MongoDB Atlas, analyses it, and shows the results in an interactive Streamlit
dashboard.

> **Note about the data source.** Amazon's terms of service and robots.txt
> restrict automated scraping, and this project never bypasses CAPTCHAs or
> anti-bot protection. The authorized route to Amazon data is the official
> *Product Advertising API*. By default this project scrapes the
> [webscraper.io e-commerce test site](https://webscraper.io/test-sites/e-commerce/static),
> a website built for scraping practice. The code is designed so an
> authorized Amazon source can be plugged in later (see
> [Adapting to an authorized Amazon source](#adapting-to-an-authorized-amazon-source)).
> Always re-check a website's terms and robots.txt before scraping it.

## Features

- Reusable scraper (Requests + BeautifulSoup) with robots.txt check, request
  delays, retries, error handling and duplicate removal
- Data fields: name, price, rating, review count, URL, availability,
  category, scrape date and time
- MongoDB Atlas storage with a unique index on `product_url` (no duplicates)
- Pandas cleaning and analysis: totals, average/highest/lowest price, average
  rating, category distribution, missing values, price comparison, sorting,
  duplicate detection
- Plotly charts and a Streamlit dashboard with search, filters, sorting,
  refresh button and product details
- Offline demo mode using `data/sample_products.csv`
- 40 automated tests (pytest)

## Architecture

```
Practice website / CSV file
        |  Requests + BeautifulSoup
        v
 scraper/amazon_scraper.py ---> utils/data_cleaning.py ---> database/mongodb.py ---> MongoDB Atlas
   (raw records)                  (Pandas clean + dedupe)     (upsert by URL)              |
                                                                                           v
        dashboard/dashboard.py  <---------  analysis/analysis.py  <------------  stored records
        (Streamlit + Plotly)                (stats + charts)
```

| Folder / file | Purpose |
|---|---|
| `scraper/amazon_scraper.py` | Data sources: `PracticeSiteScraper`, `CsvProductSource` |
| `utils/data_cleaning.py` | Cleaning, missing-value report, duplicate detection |
| `database/mongodb.py` | `ProductDatabase`: connect, save (no duplicates), read |
| `analysis/analysis.py` | Statistics and Plotly charts |
| `dashboard/dashboard.py` | Streamlit dashboard |
| `main.py` | Command-line pipeline: collect, clean, store, summarize |
| `data/sample_products.csv` | **Demo data (not scraped)**, including a few deliberately messy rows |
| `tests/` | pytest tests |
| `docs/` | Project report and viva questions |

## Installation

Requirements: Python 3.10 or newer, Git, VS Code (recommended).

```bash
git clone https://github.com/<your-username>/Amazon-Product-Scraper.git
cd Amazon-Product-Scraper

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac / Linux

pip install -r requirements.txt
```

## Quick start (no database needed)

```bash
python main.py --source sample --no-db
streamlit run dashboard/dashboard.py
```

The dashboard opens at http://localhost:8501 and shows the sample data.

## MongoDB Atlas setup

The steps below match the Atlas website as I know it; button names may differ
slightly if MongoDB changes its interface.

1. Create a free account at https://www.mongodb.com/cloud/atlas.
2. Create a **free (M0) cluster** and choose any nearby region.
3. **Database Access** > *Add New Database User*. Choose a username and a
   password. If the password contains special characters such as `@` or `#`,
   it must be URL-encoded in the connection string (or choose a simple
   password).
4. **Network Access** > *Add IP Address*. Add your current IP address. For a
   college demo you may allow `0.0.0.0/0` (anywhere), but this is less secure,
   so remove it after the demo.
5. Open your cluster, click **Connect** > **Drivers** > Python, and copy the
   connection string. It looks like
   `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`.
6. Copy the template and edit it:
   ```bash
   copy .env.example .env        # Windows
   # cp .env.example .env        # Mac / Linux
   ```
   Open `.env` and replace `<username>` and `<password>` in `MONGODB_URI`.
   **Never upload `.env` to GitHub.** It is already listed in `.gitignore`.
7. Run the pipeline with the database:
   ```bash
   python main.py --source sample
   ```
   The database `amazon_product_project` and collection `products` are created
   automatically on first save. You can view the data in Atlas under
   *Browse Collections*.

## Usage

```bash
python main.py --source sample --no-db         # offline demo
python main.py --source sample                 # demo data -> Atlas
python main.py --source live --max-pages 2     # scrape practice site -> Atlas
python main.py --source live --no-db           # scrape, skip database
streamlit run dashboard/dashboard.py           # open the dashboard
python -m pytest                               # run the tests
```

Install test tools first with `pip install -r requirements-dev.txt`.

The dashboard reads from Atlas if `MONGODB_URI` is set, otherwise from
`data/scraped_products.csv` (created by `main.py`), otherwise from the sample
CSV. The sidebar shows which source is in use. The **Refresh data** button
reloads it.

## Screenshots

Add your own screenshots to the `screenshots/` folder after running the
dashboard, then keep or edit these lines:

```
![Dashboard overview](screenshots/dashboard_overview.png)
![Charts](screenshots/charts.png)
![MongoDB Atlas collection](screenshots/atlas_collection.png)
```

## Testing: what was and was not verified

Automated tests (`python -m pytest`) cover:

- Scraper parsing, retries, robots.txt handling and duplicate removal, using a
  hand-written HTML fixture and a fake HTTP session (no internet)
- Data cleaning, analysis and chart creation
- Database save/read/duplicate logic using `mongomock` (an in-memory fake)
- The dashboard, run headlessly with Streamlit's test runner

**Not verified by these tests, so please check on your own computer:**

1. The **live scrape**. The CSS selectors in `parse_listing` follow the
   webscraper.io page structure as I know it, but they were tested only against
   my fixture. Run `python main.py --source live --max-pages 1` and confirm
   products appear. If the site changed, adjust the selectors in
   `parse_listing`.
2. The **real Atlas connection** with your credentials.

## Adapting to an authorized Amazon source

Every source extends `BaseProductSource` and returns dictionaries with the
fields listed in `PRODUCT_FIELDS`. To use Amazon's Product Advertising API
(requires an approved Associates account), write a new class in the `scraper/`
folder with a `fetch_products()` method that calls the API and returns the same
fields, then choose it in `main.py`. Cleaning, database and dashboard need no
changes.

## Limitations

- The practice site has no stock status, so `availability` is stored as
  "Not listed".
- Only listing pages are scraped (not individual product pages).
- Prices are in the site's currency (dollars).

## License / Academic note

Created for the ECI146 course at Lovely Professional University. Use scraped
data only in line with each website's terms.
