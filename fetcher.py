import httpx
import asyncio
from models import JobSignal, CompanyHiringReport
import re

TARGET_KEYWORDS = {'engineer', 'developer', 'ai', 'architect'}

async def fetch_job_listings(client: httpx.AsyncClient, company_slug: str) -> CompanyHiringReport:
        response = await client.get(
            f'https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs',
            headers={
                'User-Agent': 'hiring-pipeline',
            }
        )

        jobs = response.json().get('jobs', [])

        job_signal_list: list[JobSignal] = []

        for job in jobs:

            title = job['title']

            if not match_target(title=title):
                continue

            
            departments = job.get('departments', [])
            department_name = departments[0].get('name') if departments else None

            location = job.get('location', {}).get('name') if job.get('location') else None

            job_signal_list.append(
                JobSignal(
                    job_id=str(job['id']),
                    title=title,
                    company_name=job['company_name'],
                    location=location,
                    department=department_name,
                    job_url=job['absolute_url'],
                    description_snippet=None,
                )
            )

        # print('----xxxx----')
        # print(f'Company: {company_slug}')
        # print(f'Number of Jobs available: {len(jobs)}')
        # print(f'Total Jobs Processed: {len(job_signal_list)} \n')

        return CompanyHiringReport(
             company_slug=company_slug,
             total_jobs=len(jobs),
             processed_jobs=len(job_signal_list),
             jobs=job_signal_list,
        )

# match whole words only using regex
def match_target(title: str) -> bool:
    for kw in TARGET_KEYWORDS:
        # \b ensures "ai" matches "AI Engineer" but NOT "Retail" or "Campaign"
        if re.search(r'\b' + re.escape(kw) + r'\b', title.lower()):
            return True
    return False

if __name__ == '__main__':
    asyncio.run(fetch_job_listings(client=httpx.AsyncClient(), company_slug='vercel'))