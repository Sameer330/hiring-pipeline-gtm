from pydantic import BaseModel
from typing import Optional

class JobSignal(BaseModel):
    job_id: str
    title: str
    company_name: str
    location: Optional[str] = None
    department: Optional[str] = None
    job_url: Optional[str] = None
    description_snippet: Optional[str] = None

class CompanyHiringReport(BaseModel):
    jobs: list[JobSignal]
    total_jobs: int
    processed_jobs: int
    company_slug: str

    @property
    def hiring_intensity(self) -> float:
        # return % of open roles
        if self.total_jobs == 0:
            return 0.0
        return round((self.processed_jobs / self.total_jobs) * 100, 1)

class OutboundPitch(BaseModel):
    company: str
    target_persona: str
    observation_hook: str
    pain_point_bridge: str
    call_to_action: str

if __name__ == '__main__':
    print(JobSignal(job_id='xyz_abc_inc_ttyl', title='XYZ', company_name='ABC Inc.').model_dump_json())
    print(JobSignal(job_id='123456', title='QWERTY', company_name='POIUY Inc.').model_dump_json())
    print(JobSignal(job_id='101010', title='zxcvbnm', company_name='Google LLC', description_snippet='Hiring for role of ABCD at Google LLC').model_dump_json())