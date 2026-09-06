# Configuration files

Sift reads its configuration from two places: `data.json`, which describes you and your target
companies and `.env`, which holds credentials. Neither is committed to the repository - see
[work.md](work.md) for how they're persisted between runs instead.

## data.json

Contains everything Gemini needs to judge fit and everything the scraper needs to know where to
look.

### Structure

```json
{
  "summary": "I am a computer science graduate with experience building systems...",
  "companies": [
    {
      "name": "Company X",
      "url": "https://companyx.com/jobs",
      "descriptor": "a[href*=\"job\"]",
      "attribute": "href",
      "content_selector": "[class=\"jobCard\"]"
    }
  ],
  "skills": [
    "Python programming using FastAPI, Playwright",
    "Test Driven Development with Jest"
  ]
}
```

### Fields

#### `summary`

A short account of who you are, your experience and your education level, written the way you'd
describe yourself to a recruiter.

**Used for:**

- The relevance filter - compared against each scraped listing via cosine similarity to decide
  whether it's worth extracting.
- Gemini's fit assessment - read alongside the job description to write the verdict and note any
  gaps.

#### `skills`

A list of specific, concrete skills - not a vague summary. This is what Gemini checks a job's
requirements against when identifying strengths and gaps.

#### `companies`

The core configuration: the list of companies Sift scrapes. Each entry needs:

| Property           | Example                       | Purpose                                                                                |
|:-------------------|:------------------------------|:---------------------------------------------------------------------------------------|
| `name`             | `"Company X"`                 | Cosmetic - used to identify the company in the email digest.                           |
| `url`              | `"https://companyx.com/jobs"` | The page Playwright opens to look for job links.                                       |
| `descriptor`       | `"a[href*=\"career\"]"`       | The selector matching every element that links to a job posting.                       |
| `attribute`        | `"href"`                      | The attribute Playwright reads off each matched element to get the link.               |
| `content_selector` | `"div[class=\"jobCard\"]"`    | The selector matching the container(s) holding job description text on a listing page. |

## .env

Holds every credential Sift needs at runtime. None of these should ever be committed.

### Structure

```dotenv
## Gemini API key
GEMINI_API_KEY=geminikey

## Email credentials ##
SENDER_EMAIL=originemail
APP_PASSWORD=gmailpassword
RECEIVER_EMAIL=receivingemail

## Supabase
SUPABASE_URL=urltosupabaseproject
SUPABASE_KEY=secretkeytoaccessapi
SUPABASE_BUCKET=bucketname
```

### Fields

#### `GEMINI_API_KEY`

Grants access to the Gemini API. Two models are used:

- `gemini-3.1-flash-lite` - extracting structured job details and generating fit assessments.
- `gemini-embedding-2` - converting text into embeddings for the relevance filter.

Both are chosen for speed and cost, not because a larger model couldn't do the job - `flash-lite`
is deliberately proportionate to how well-defined these tasks are. Swap the model name in
`gemini.py` if you'd rather use something else. See
[these instructions](https://ai.google.dev/gemini-api/docs/api-key) for generating a key.

#### Email credentials

- `SENDER_EMAIL` - the Gmail address Sift sends from.
- `APP_PASSWORD` - an [app password](https://myaccount.google.com/apppasswords) generated for that
  account (not your regular Gmail password - Google requires this for programmatic SMTP access).
- `RECEIVER_EMAIL` - where the digest gets sent. Can be the same address as `SENDER_EMAIL`.

#### Supabase credentials

- `SUPABASE_URL` - your project's URL, from the project dashboard.
- `SUPABASE_KEY` - a secret key from Project Settings → API Keys. Use a `service_role` key, not the
  public `anon` key - Supabase Storage enforces row-level security by default and the anon key will
  be rejected on upload unless you've explicitly configured a storage policy permitting it.
- `SUPABASE_BUCKET` - the bucket name where `data.json` and `url.txt` are stored. See
  [this guide](https://supabase.com/docs/guides/storage/buckets/creating-buckets?queryGroups=language&language=python)
  for creating one.