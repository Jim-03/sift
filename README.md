# SIFT

A scheduled automation pipeline that scrapes job postings across a defined list of companies,
filters them against your own profile using semantic similarity, generates a per-job fit assessment
with Gemini and emails you only the postings worth your time.

Sift exists to replace manual job-board scrolling with something that runs in the background and
only interrupts you when there's something genuinely worth looking at.

## How it works

Sift runs end-to-end as a single scheduled job: it reads your source list, visits each company's
careers page, extracts job postings, filters out anything that doesn't look like a match, has Gemini
turn the survivors into structured data and a short fit note and emails you the result.

The full breakdown of each stage - data ingestion, scraping, embedding-based filtering, extraction,
scoring and storage - is documented in [docs/work.md](docs/work.md).

## Features

- Scrapes multiple companies' job boards from a single configurable source list
- Filters postings against your profile using embedding-based cosine similarity, before spending any
  LLM calls on them
- Extracts structured job details (title, requirements, benefits, deadline, etc.) via Gemini
- Generates a short, grounded fit assessment per job - strengths and gaps, no fabricated scores
- Emails only new, relevant postings as a clean HTML digest
- Tracks previously seen postings so the same job never gets re-sent
- Runs unattended as a scheduled GitHub Actions workflow - no server to maintain, no manual
  triggering

## Requirements

- [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key)
- [uv](https://docs.astral.sh/uv/)
- Python 3.12.x
- A [Supabase](https://supabase.com/) project with a storage bucket
- A Gmail account with an [app password](https://myaccount.google.com/apppasswords) for sending
  email

## Installation

### 1. Clone the repository

```shell
git clone https://github.com/Jim-03/sift.git
cd sift
```

### 2. Install dependencies

```shell
uv sync
```

### 3. Create your configuration files

Sift reads two files at runtime - `data.json` (your profile and source list) and `url.txt`
(previously seen postings) - plus a `.env` file for credentials. On the very first run, neither
`data.json` nor `url.txt` exists yet, so you'll need to create them manually before Sift can pull
them from Supabase on every run after that.

1. Create `data.json` with your summary, skills and company source list.
2. Create an empty `url.txt` (it populates itself after the first successful run).
3. Create `.env` with your Gemini, email and Supabase credentials.

Full field-by-field structure and explanations for all three files are in
[docs/files.md](docs/files.md).

### 4. Upload the initial files to Supabase

Since every run downloads `data.json` and `url.txt` from your Supabase bucket if they don't exist
locally, upload your manually created versions there once, so the first scheduled run has something
to fetch:

```shell
uv run python -c "from src.data import supabase; supabase.storage.from_('<your-bucket>').upload('data.json', open('data.json', 'rb')); supabase.storage.from_('<your-bucket>').upload('url.txt', open('url.txt', 'rb'))"
```

(Replace `<your-bucket>` with your `SUPABASE_BUCKET` value.)

### 5. Run it

```shell
uv run python main.py
```

## Running on a schedule

Sift is designed to run as a scheduled GitHub Actions workflow rather than a long-lived service - no
server, no idle costs, no manual triggers. See [.github/workflows](.github/workflows) for the cron
configuration and [docs/work.md](docs/work.md) for why this shape was chosen over alternatives.

## Documentation

- [docs/work.md](docs/work.md) - how the pipeline works end to end, stage by stage
- [docs/files.md](docs/files.md) - the structure and purpose of `data.json` and `.env`

## Notes

- Sift is a fixed, deterministic pipeline with LLM-powered stages - not an autonomous agent that
  decides its own next action. Every run follows the same sequence: scrape, filter, extract, score,
  email.
- `data.json` and `url.txt` are intentionally not committed to the repository or persisted between
  runs on the CI runner - they live in Supabase storage so a stateless, ephemeral GitHub Actions
  runner can pick up exactly where the last run left off.