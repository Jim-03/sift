from playwright.sync_api import Page, sync_playwright

from src.data import get_data


def get_links(company: dict[str, str], page: Page) -> list[str]:
    """Retrieve links from a company's job board

    Args:
        company (dict[str, str]): company data
        page (Page): page to browse from

    Returns:
        list[str]: List of links to job postings in a company
    """
    links: list[str] = []
    # Visit the company's job listing site
    page.goto(company["url"])
    # Wait for page to finish loading
    page.wait_for_load_state("networkidle")
    # Extract all career links
    located = page.locator(company["descriptor"]).all()

    for link in located:
        href = link.get_attribute(company["descriptor"])

        if href:
            links.append(href)

    return links


def get_listings(selector: str, links: list[str], page: Page) -> list[str]:
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
        page.goto(link)
        # Wait for idle network traffic
        page.wait_for_load_state("networkidle")

        # Extract elements containing the same selector
        blocks = page.locator(selector)
        # Extract all the texts from all elements
        texts = [blocks.nth(i).inner_text() for i in range(blocks.count())]
        # Select the largest text containing the actual description
        listings.append(max(texts, key=len, default="").replace("\n", " "))
    return listings


def get_jobs():
    """Retrieve job postings from all defined companies

    Returns:
        list[dict[str, object]]: A list of all companies with their available job postings
    """
    jobs: list[dict[str, object]] = []
    with sync_playwright() as p:
        # Launch browser and open a page
        browser = p.webkit.launch()
        page = browser.new_page()
        # Get a list of all companies
        companies = get_data("companies")
        for company in companies:
            print(f"Fetching from {company['name']}")
            links = get_links(company, page)

            if len(links) == 0:
                print(f"No listings from {company['name']}")
                continue
            listings = get_listings(company["content_selector"], links, page)
            jobs.append(
                {
                    "company": company["name"],
                    "jobs": [
                        {"url": links[i], "inner_text": listings[i]}
                        for i in range(len(links))
                    ],
                }
            )
        browser.close()

    return jobs
