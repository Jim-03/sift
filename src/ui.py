import html
from datetime import datetime

from src.dto import Job, Metadata

GOLD = "#C9A34E"
GOLD_DARK = "#9C7B2E"
BG = "#FAF7F0"
CARD_BG = "#FFFFFF"
INK = "#2A2620"
INK_DIM = "#786F5C"
BORDER = "#E8E0CC"


def _esc(text: str) -> str:
  return html.escape(text or "")


def _days_remaining(deadline_str: str) -> tuple[int, str, str]:
  try:
    deadline = datetime.strptime(deadline_str, "%d-%m-%Y").date()
  except ValueError:
    return 0, "Unknown", INK_DIM
  days = (deadline - datetime.today().date()).days
  if days < 0:
    return days, "Deadline passed", "#B3452C"
  if days <= 5:
    return days, f"{days} day{'s' if days != 1 else ''} left", "#B3452C"
  if days <= 14:
    return days, f"{days} days left", GOLD_DARK
  return days, f"{days} days left", "#4C7A4C"


def _bullet_list(items: list[str], limit: int = 5) -> str:
  if not items:
    return ""
  shown = items[:limit]
  extra = len(items) - limit
  lis = "".join(
      f'<li style="margin-bottom:4px;color:{INK};font-size:13px;line-height:1.5;">{_esc(item)}</li>'
      for item in shown
  )
  more = (
    f'<li style="color:{INK_DIM};font-size:13px;list-style:none;margin-top:2px;">+{extra} more — see full posting</li>'
    if extra > 0
    else ""
  )
  return f'<ul style="margin:4px 0 0 18px;padding:0;">{lis}{more}</ul>'


def _fit_notes_block(meta) -> str:
  if meta is None:
    return ""

  strengths_html = "".join(
      f'<li style="margin-bottom:4px;color:{INK};font-size:14px;line-height:1.5;">{_esc(s)}</li>'
      for s in meta.strengths
  )
  gaps_html = "".join(
      f'<li style="margin-bottom:4px;color:{INK};font-size:14px;line-height:1.5;">{_esc(g)}</li>'
      for g in meta.gaps
  )

  strengths_section = (
    f"""
      <p style="margin:10px 0 4px;color:{INK};font-size:13px;font-weight:600;">Strengths</p>
      <ul style="margin:0 0 10px 18px;padding:0;">{strengths_html}</ul>
    """
    if meta.strengths
    else ""
  )

  gaps_section = (
    f"""
      <p style="margin:10px 0 4px;color:{INK};font-size:13px;font-weight:600;">Gaps</p>
      <ul style="margin:0 0 10px 18px;padding:0;">{gaps_html}</ul>
    """
    if meta.gaps
    else ""
  )

  return f"""
    <tr><td style="padding-top:16px;border-top:1px solid {BORDER};">
      <p style="margin:12px 0 6px;color:{GOLD_DARK};font-size:12px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;">
        Fit notes
      </p>
      {strengths_section}
      {gaps_section}
      <p style="margin:10px 0 0;color:{INK};font-size:14px;line-height:1.5;">{_esc(meta.verdict)}</p>
    </td></tr>"""


def _job_card(job: Job, meta: Metadata | None) -> str:
  days, deadline_label, deadline_color = _days_remaining(job.deadline)

  salary_line = ""
  if job.salary and job.salary != "Unknown":
    currency = (
      f"{job.currency} " if job.currency and job.currency != "Unknown" else ""
    )
    salary_line = f"""
        <tr><td style="padding-top:6px;color:{INK_DIM};font-size:13px;">
          {currency}{_esc(job.salary)}
        </td></tr>"""

  benefits_block = ""
  if job.benefits:
    benefits_block = f"""
        <tr><td style="padding-top:14px;">
          <p style="margin:0 0 4px;color:{INK};font-size:13px;font-weight:600;">Benefits</p>
          {_bullet_list(job.benefits, limit=4)}
        </td></tr>"""

  notes_block = _fit_notes_block(meta)

  return f'''
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;margin-bottom:16px;">
      <tr>
        <td style="padding:20px 22px;border-left:4px solid {GOLD};border-radius:10px 0 0 10px;">

          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>
                <p style="margin:0;color:{INK};font-size:17px;font-weight:700;">{_esc(job.title)}</p>
                <p style="margin:2px 0 0;color:{INK_DIM};font-size:14px;">{_esc(job.company_name)} · {_esc(job.location)}</p>
              </td>
              <td align="right" valign="top">
                <span style="background:{deadline_color}1A;color:{deadline_color};font-size:12px;font-weight:600;padding:4px 10px;border-radius:12px;white-space:nowrap;">
                  {deadline_label}
                </span>
              </td>
            </tr>
            {salary_line}
            <tr><td colspan="2" style="padding-top:12px;color:{INK};font-size:14px;line-height:1.5;">
              {_esc(job.description[:280])}{"…" if len(job.description) > 280 else ""}
            </td></tr>
            <tr><td colspan="2" style="padding-top:14px;">
              <p style="margin:0 0 4px;color:{INK};font-size:13px;font-weight:600;">Requirements</p>
              {_bullet_list(job.requirements, limit=5)}
            </td></tr>
            {benefits_block}
            {notes_block}
            <tr><td colspan="2" style="padding-top:16px;">
              <a href="{_esc(job.source_url)}" style="display:inline-block;background:{GOLD};color:#2A2620;text-decoration:none;font-size:13px;font-weight:700;padding:9px 18px;border-radius:6px;">
                View posting →
              </a>
            </td></tr>
          </table>

        </td>
      </tr>
    </table>'''


def template(jobs: list[Job], metadata: list[Metadata]) -> str:
  """HTML body

  Args:
      jobs (list[Job]): A list of jobs
      metadata (list[Metadata]): A list of notes for each job

  Returns:
      (string): HTML content
  """
  metadata_by_id = {m.job_id: m for m in metadata}
  cards = "".join(_job_card(job, metadata_by_id.get(job.id)) for job in jobs)
  count = len(jobs)

  return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    @media only screen and (max-width: 480px) {{
      .container {{ width: 100% !important; padding: 0 12px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background:{BG};">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{BG};">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <table role="presentation" width="600" class="container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">
          <tr>
            <td style="padding-bottom:24px;">
              <p style="margin:0;color:{GOLD_DARK};font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Sift</p>
              <p style="margin:4px 0 0;color:{INK};font-size:22px;font-weight:700;">{count} new job match{"es" if count != 1 else ""}</p>
            </td>
          </tr>
          <tr><td>{cards}</td></tr>
          <tr>
            <td style="padding-top:8px;color:{INK_DIM};font-size:12px;text-align:center;">
              Sent automatically by your Sift agent.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
