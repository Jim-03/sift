# How it works

This is a stage-by-stage breakdown of the pipeline executed by [main.py](../main.py). Sift is a
fixed sequence, the same steps run in the same order on every scheduled invocation, with LLM calls
handling specific stages rather than deciding what happens next.

## 1. Data ingestion

The pipeline starts by loading your profile and source list from `data.json`. If the file doesn't
exist locally, which is always true on a fresh GitHub Actions runner, it's pulled from the Supabase
bucket first.

[data.py](../src/data.py)

```python
def get_data(detail: str):
  if not os.path.exists("data.json"):
    print("Downloading 'data.json'")
    file_bytes = supabase.storage.from_(bucket).download("data.json")
    with open("data.json", "wb") as f:
      f.write(file_bytes)

  with open("data.json", "r") as f:
    data = json.load(f)
    return data[detail]
```

## 2. Company browsing

Sift then visits each company's careers page and collects links to individual postings. Since a
posting typically stays live for days or weeks, previously visited URLs are tracked in `url.txt`
so subsequent runs skip anything already seen. This keeps each run's workload bounded rather than
growing with the total number of postings a company has ever listed.

URLs are stored as a Python `set`, giving O (1) membership checks regardless of how large the list
grows over time.

[data.py](../src/data.py)

```python
def get_urls():
  if not os.path.exists("url.txt"):
    print("Downloading 'url.txt'")
    file_bytes = supabase.storage.from_(bucket).download("url.txt")
    with open("url.txt", "wb") as f:
      f.write(file_bytes)

  with open("url.txt", "r") as f:
    return {line.strip() for line in f}
```

[scraper.py](../src/scraper.py)

```python
def get_links():
  # ...
  if href and href not in seen_urls:
    links.append(href)
```

## 3. Job extraction (raw text)

Each unseen link is visited and its content extracted. Rather than relying on one exact selector per
site, which breaks the moment a site's markup shifts, Sift collects every element matching a broader
selector, reads each one's inner text, and keeps only the longest.

[scraper.py](../src/scraper.py)

```python
def get_listings():
  # ...
  blocks = page.locator(selector)
  texts = [await blocks.nth(i).inner_text() for i in range(await blocks.count())]
  listings.append(max(texts, key=len, default="").replace("\n", " "))
  return listings
```

The longest block is, in practice, reliably the actual job description. Everything else on a careers
page (nav links, hero banners, footers) is short by comparison. This also keeps the token count sent
to Gemini down, since the extracted text is close to just the posting itself rather than the full
page.

## 4. Relevance filtering

Before anything reaches Gemini for extraction, every scraped listing is compared against your
profile summary using embeddings and cosine similarity. This is a cheap, deterministic gate whose
only job is deciding whether a posting is worth spending an LLM call on, not judging fit precisely.

[ml.py](../src/ml.py)

```python
def get_relevant_jobs(jobs: list[str], gemini: Gemini):
  print("Extracting relevant jobs")
  relevant: list[str] = []

  job_embedding = gemini.embed(jobs)
  summary_embedding = np.array(
      gemini.embed(str(get_data("summary")))[0].values
  ).reshape(1, -1)

  for i in range(len(job_embedding)):
    job_vec = np.array(job_embedding[i].values).reshape(1, -1)
    score = cosine_similarity(summary_embedding, job_vec)[0][0]

    if score > 0.5:
      relevant.append(jobs[i])

  return relevant
```

The threshold is set at `0.5` rather than higher, because the text being compared is still raw and
noisy - inconsistent wording, boilerplate, and leftover markup all pull scores down. The goal here
is to reject the clearly irrelevant, not to make a fine-grained judgment call; fine-grained judgment
happens later, with Gemini, on cleaner text.

## 5. Structured extraction

Listings that pass the filter are sent to Gemini in batches of 5, to keep each call's context
focused and the output quality consistent.

[gemini.py](../src/gemini.py)

```python
def extract(self, jobs: list[str]) -> JobListings:
  if not jobs:
    raise Exception("No jobs content provided!")

  SYSTEM_PROMPT = f"""
        You are a helpful extraction assistant. You have been provided a list of
        scraped HTML content containing a job description. Your task is to extract
        the job description from the content following the strict rules at
        </importantInstructions>

        <importantInstructions>
        1. Extract only the provided job details from the scraped data.
        2. For any content that doesn't contain a job description, set the
           'is_valid_job' property to false.
        3. **DO NOT** generate any content that isn't provided in the description.
        4. Dates may always be mixed up between month and day, check the date at
           </date> to determine the difference.
        5. All date formats should be in dd-mm-YYYY format
        </importantInstructions>

        <date>
        The current date in dd-mm-YYYY format is {datetime.now().today().strftime("%d-%m-%Y")}
        </date>
        """

  interactions = self.__client.interactions.create(
      model="gemini-3.1-flash-lite",
      system_instruction=SYSTEM_PROMPT,
      input=", ".join(jobs),
      store=False,
      generation_config={"temperature": 0.1},
      response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": JobListings.model_json_schema(),
      },
  )

  results = interactions.output_text
  if not results:
    raise Exception("Gemini failed to generate response")

  return JobListings.model_validate_json(results)
```

Since the "longest text block" heuristic from step 3 can occasionally pick up something that isn't
actually a job description, every extracted result carries an `is_valid_job` flag - postings that
fail this check are dropped before anything downstream sees them.

`gemini-3.1-flash-lite` is used deliberately, not by default: it's fast, cheap, and sufficient for
extraction and note-writing. A larger model would add cost and latency without adding accuracy for a
task this well-defined.

## 6. Fit assessment and emailing

Valid jobs are passed to Gemini again, in batches, for a short assessment: what matches, what's
missing, and a plain-language verdict - grounded in your listed skills and summary, with no
manufactured numeric score. The results are compiled into an HTML digest and emailed for your
review.

## 7. Persisting state

Once a run completes, the updated set of seen URLs - along with `data.json`, unchanged unless you
edit it yourself - is written back to the Supabase bucket, so the next scheduled run picks up
exactly where this one left off.

## Operational notes

- Sift runs as a GitHub Actions cron job on weekdays.
- `data.json` and `url.txt` are deliberately not committed to the repository or persisted on the CI
  runner between runs - the runner's filesystem is thrown away after each run, so both files live in
  Supabase storage instead, as the single source of truth every run reads from and writes back to.