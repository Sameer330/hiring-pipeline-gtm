import httpx
from fetcher import fetch_job_listings
import asyncio
from models import CompanyHiringReport, OutboundPitch
import subprocess
import json

TARGET_COMPANIES = ['stripe', 'supabase', 'vercel', 'figma', 'airbnb']

async def pipeline():
    hiring_report_list: list[CompanyHiringReport] = []

    try:
        with open('pitch-prompt.txt', 'r', encoding='utf-8') as file:
            pitch_prompt = file.read()
    except:
        print('File `pitch-prompt.txt` not found')
        return

    async with httpx.AsyncClient() as client:
        for company_slug in TARGET_COMPANIES:
            hiring_report = await fetch_job_listings(client=client, company_slug=company_slug)

            hiring_report_list.append(hiring_report)

        sorted_reports = sorted(
            hiring_report_list,
            key=lambda report: report.processed_jobs,
            reverse=True,
        )

        print("🏆 TARGET ACCOUNT HIRING LEADERBOARD:")
        for r in sorted_reports:
            print(f"• {r.company_slug.upper()}: {r.processed_jobs} technical roles ({r.hiring_intensity}% of total {r.total_jobs} jobs)")

            if len(r.jobs) > 0:
                formatted_prompt = pitch_prompt.format(
                    company_slug=r.company_slug.upper(),
                    total_jobs=r.total_jobs,
                    tech_jobs=r.processed_jobs,
                    hiring_intensity=r.hiring_intensity,
                    featured_role=r.jobs[0].title,
                )

                result = subprocess.run(
                    ['agy', '-p', formatted_prompt],
                    capture_output=True,
                    text=True,
                )

                ai_output = json.loads(result.stdout.strip())

                outbound_pitch = OutboundPitch(
                    company=r.company_slug.upper(),
                    target_persona=ai_output.get('target_persona'),
                    observation_hook=ai_output.get('observation_hook'),
                    pain_point_bridge=ai_output.get('pain_point_bridge'),
                    call_to_action=ai_output.get('call_to_action'),
                )

                print(f'Outbound pitch for {r.company_slug.upper()} \n{outbound_pitch.model_dump_json(indent=2)}')

            print('\n')

if __name__ == '__main__':
    asyncio.run(pipeline())