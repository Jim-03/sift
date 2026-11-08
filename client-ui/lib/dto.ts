export interface Statistics {
  total_jobs: number;
  total_matches: number;
  applied: number;
  best_match_jobs: JobDto[];
  recent_jobs: JobDto[];
}

export interface JobDto {
  id: string;
  title: string;
  url: string;
  company: string;
  experience_level: ExperienceLevel;
  employment_type: EmploymentType;
  description: string;
  responsibilities: string[];
  requirements: string[];
  benefits: string[];
  salary: string;
  applied: boolean;
  read: boolean;
  deadline: string;
  created_at: string;
}

export enum ExperienceLevel {
  SENIOR = 'SENIOR',
  JUNIOR = 'JUNIOR/ENTRY-LEVEL',
  INTERN = 'INTERNSHIP',
  MID = 'MID-LEVEL',
}

export enum EmploymentType {
  FULL_TIME = 'FULL-TIME',
  INTERNSHIP = 'INTERNSHIP',
  CONTRACT = 'CONTRACT',
}

export enum Verdict {
  STRONG = 'strong',
  GOOD = 'good',
  PARTIAL = 'partial',
  WEAK = 'weak',
  NONE = 'none',
}

export interface JobReview {
  reasoning: string;
  matches: string[];
  partial: string[];
  gaps: string[];
  verdict: Verdict;
}

export interface FullJobDto extends JobDto {
  job_metadata?: JobReview;
}
