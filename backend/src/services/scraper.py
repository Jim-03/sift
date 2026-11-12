"""Module handling web scraping"""

import json
import os.path
from urllib.parse import urljoin

from playwright.async_api import Page, async_playwright

from src.config.logger import logger
from src.dto.company_dto import CompaniesList, Company
from src.dto.job_dto import LLMJobDto
from src.services.gemini import GeminiService

PAGE_TIMEOUT = 60_000


async def get_links(company: Company, page: Page) -> set[str]:
    """Retrieve job links from a company's job board

    Args:
        company: Company details
        page: Browser page

    Returns:
        (list[str]): Set of job links

    """
    urls: set[str] = set()
    seen_urls: set[str] = set()

    if os.path.exists("urls.txt"):
        with open("urls.txt", "r") as f:
            seen_urls = {line.strip() for line in f}

    await page.goto(
        company.career_link, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT
    )
    base_url = page.url

    locator = page.locator(company.link_container)
    count = await locator.count()

    for i in range(count):
        href = await locator.nth(i).get_attribute(company.link_tag)

        if href and href not in seen_urls:
            absolute_url = urljoin(base_url, href)
            urls.add(absolute_url)

    return urls


async def get_listings(job_links: set[str], job_container: str, page: Page) -> set[str]:
    """Retrieve the inner text of a job link

    Args:
        job_links: List of job URLs
        job_container: Tag enclosing the job description
        page: Browser page

    Returns:
        (set[str]): List of inner text from job links

    """
    listings: set[str] = set()

    for link in job_links:
        await page.goto(link, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)

        blocks = page.locator(job_container)
        count = await blocks.count()

        texts = [await blocks.nth(text).inner_text() for text in range(count)]

        listings.add(f"URL: {link}\n" + max(texts, key=len, default=""))

    return listings


async def search_jobs() -> list[LLMJobDto]:
    """Get job postings

    Returns:
        (list[str]): A  list of new job postings from specified companies

    """
    jobs: list[LLMJobDto] = []
    gemini = GeminiService()

    with open("settings.json", "r") as f:
        settings = json.load(f)

    companies = CompaniesList.model_validate(settings).companies

    async with async_playwright() as p:
        browser = await p.webkit.launch()
        page = await browser.new_page()

        for company in companies:
            logger.info(f"Browsing {company.name}:")

            job_links = await get_links(company, page)

            if len(job_links) == 0:
                logger.warning("\tNo new careers found. Skipping...")
                continue

            logger.info(f"\tFound {len(job_links)} new openings.")
            company_listings = await get_listings(
                job_links, company.job_container, page
            )

            for listing in company_listings:
                job = await gemini.extract_job(listing)
                jobs.append(job)

        await browser.close()
    return jobs
