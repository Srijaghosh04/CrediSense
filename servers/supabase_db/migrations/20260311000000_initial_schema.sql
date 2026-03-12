-- Initial Database Schema for CreditSense (Supabase / Postgres)
-- Generated from /servers/models/schemas.py

-- 1. Create Enums
CREATE TYPE application_status AS ENUM ('pending', 'ingesting', 'researching', 'under_review', 'approved', 'rejected');
CREATE TYPE risk_severity AS ENUM ('HIGH', 'MEDIUM', 'LOW');
CREATE TYPE alert_category AS ENUM ('litigation', 'regulatory', 'promoter', 'sector', 'financial');
CREATE TYPE document_type AS ENUM ('annual_report', 'bank_statement', 'gst_filing', 'sanction_letter', 'rating_report', 'legal_notice', 'other');
CREATE TYPE insight_category AS ENUM ('site_visit', 'management_interview', 'market_feedback', 'other');
CREATE TYPE insight_impact AS ENUM ('positive', 'negative', 'neutral');
CREATE TYPE decision_enum AS ENUM ('APPROVE', 'APPROVE_WITH_CONDITIONS', 'REJECT');

-- 2. Applications Table
CREATE TABLE applications (
    id VARCHAR(50) PRIMARY KEY, -- e.g. "APP-001"
    company_name VARCHAR(255) NOT NULL,
    pan VARCHAR(20) NOT NULL,
    gstin VARCHAR(30) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    requested_loan_amount NUMERIC(20, 2), -- Handling large INR amounts
    status application_status DEFAULT 'pending'::application_status,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Ingested Documents Table
CREATE TABLE ingested_documents (
    id VARCHAR(50) PRIMARY KEY, -- e.g. "DOC-..."
    application_id VARCHAR(50) REFERENCES applications(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type document_type NOT NULL,
    extracted_text_preview TEXT,
    financials JSONB, -- Stores ExtractedFinancials exactly as JSON
    anomalies JSONB,  -- Stores list of StructuredDataAnomaly exactly as JSON array
    processing_status VARCHAR(50) DEFAULT 'completed',
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Research Results Table (Aggregated per application)
CREATE TABLE research_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id VARCHAR(50) REFERENCES applications(id) ON DELETE CASCADE,
    sector_outlook TEXT,
    promoter_background TEXT,
    researched_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Risk Alerts Table (Child of Research Results)
CREATE TABLE risk_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id VARCHAR(50) REFERENCES applications(id) ON DELETE CASCADE,
    severity risk_severity NOT NULL,
    source VARCHAR(255) NOT NULL,
    category alert_category NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    url VARCHAR(500),
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Primary Insights Table (Credit Officer notes)
CREATE TABLE primary_insights (
    id VARCHAR(50) PRIMARY KEY, -- e.g. "INS-..."
    application_id VARCHAR(50) REFERENCES applications(id) ON DELETE CASCADE,
    category insight_category NOT NULL,
    note TEXT NOT NULL,
    impact insight_impact NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. CAM Reports Table (Final Output Data)
CREATE TABLE cam_reports (
    id VARCHAR(50) PRIMARY KEY, -- e.g. "CAM-..."
    application_id VARCHAR(50) REFERENCES applications(id) ON DELETE CASCADE UNIQUE,
    sector_outlook TEXT,
    promoter_background TEXT,
    five_cs_scores JSONB,      -- Stores FiveCsScore as JSON
    five_cs_narrative JSONB,   -- Stores FiveCsNarrative as JSON
    decision JSONB,            -- Stores CreditDecision as JSON (decision, suggested_limit, reasoning, factors, strengths)
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create simple updating trigger for `updated_at` column in `applications` table
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now(); 
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_applications_modtime
BEFORE UPDATE ON applications
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- Enable Row Level Security (RLS) policies placeholder (Assuming backend uses service role for now)
-- ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ingested_documents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE risk_alerts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE primary_insights ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cam_reports ENABLE ROW LEVEL SECURITY;
