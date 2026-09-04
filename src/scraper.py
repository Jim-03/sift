from playwright.async_api import Page, async_playwright

from src.data import get_data
from src.data import get_urls

seen_urls = get_urls()


async def get_links(company: dict[str, str], page: Page) -> list[str]:
  """Retrieve links from a company's job board

  Args:
      company (dict[str, str]): company data
      page (Page): page to browse from

  Returns:
      list[str]: List of links to job postings in a company
  """
  links: list[str] = []
  # Visit the company's job listing site
  await page.goto(company["url"])
  # Wait for page to finish loading
  await page.wait_for_load_state("networkidle")
  # Extract all career links
  located = page.locator(company["descriptor"])
  count = await located.count()

  for link in range(count):
    href = await located.nth(link).get_attribute(company["attribute"])

    if href and not href in seen_urls:
      links.append(href)

  return links


async def get_listings(selector: str, links: list[str], page: Page) -> list[
  str]:
  """Retrieve the inner text of job postings.

  Args:
      selector (str): The HTML element/attribute containing the job data
      links (list[str]): Links directing to a job post
      page (Page): page to browse from

  Returns:
      list[str]: A list of inner texts from parsed HTML content
  """
  listings: list[str] = []

  for link in links:
    # Visit the posting
    await page.goto(link)
    # Wait for idle network traffic
    await page.wait_for_load_state("networkidle")

    # Extract elements containing the same selector
    blocks = page.locator(selector)
    # Extract all the texts from all elements
    texts = [await blocks.nth(i).inner_text() for i in
             range(await blocks.count())]
    # Select the largest text containing the actual description
    listings.append(max(texts, key=len, default="").replace("\n", " "))
  return listings


async def get_jobs():
  """Retrieve job postings from all defined companies

  Returns:
      list[str]: A list of all companies with their available job postings
  """
  jobs: list[str] = []
  async with async_playwright() as p:
    # Launch browser and open a page
    browser = await p.webkit.launch()
    page = await browser.new_page()
    # Get a list of all companies
    companies = get_data("companies")
    for company in companies:
      print(f"Fetching from {company['name']}")
      links = await get_links(company, page)

      if len(links) == 0:
        print(f"No new listings from {company['name']}")
        continue
      listings = await get_listings(company["content_selector"], links, page)
      for url, text in zip(links, listings):
        jobs.append(f"""
                Company Name: {company["name"]}
                URL: {url}
                Raw text: {text}
                """)
    await browser.close()

  return jobs
