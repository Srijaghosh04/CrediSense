import os
import io
import json
import pdfplumber
import pandas as pd
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from models.schemas import (
    ExtractedFinancials, StructuredDataAnomaly, IngestedDocument,
    DocumentType, RiskSeverity
)

load_dotenv()

FINANCIAL_KEYWORDS = ["revenue", "profit", "balance sheet", "equity", "borrowing",
                      "covenant", "contingent", "related party", "debt", "liabilities",
                      "assets", "cash flow", "interest", "depreciation", "ebitda",
                      "turnover", "net worth", "reserves", "surplus"]


class IngestorService:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=api_key
        )

        # Prompt for extracting financial data from PDF text
        self.extraction_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are an expert Indian credit analyst. Extract financial information from this document text.

Return ONLY a valid JSON object with these exact keys (use null if not found):
{{
    "revenue": <number in INR or null>,
    "net_profit": <number in INR or null>,
    "total_debt": <number in INR or null>,
    "total_equity": <number in INR or null>,
    "debt_to_equity": <ratio as float or null>,
    "current_ratio": <ratio as float or null>,
    "interest_coverage_ratio": <ratio as float or null>,
    "covenants": [<list of financial covenants/conditions as strings>],
    "related_party_transactions": [<list of related party transaction descriptions>],
    "contingent_liabilities": [<list of contingent liabilities>]
}}

IMPORTANT:
- Convert all amounts to raw numbers in INR (e.g., "₹50 Cr" → 500000000)
- Look for hidden risks in the text
- Extract ALL covenants even if they seem minor
- For ratios, return as decimal (e.g., 2.5 not "2.5:1")

Document Text:
{text}"""
        )


    # PDF Parsing (Annual Reports, Legal Notices)

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Hybrid: PyPDF2 fast-scans all pages, pdfplumber extracts financial pages."""
        try:
            # Step 1: Fast scan with PyPDF2 to find financial pages
            reader = PdfReader(io.BytesIO(file_content))
            financial_page_numbers = []

            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if any(kw in text.lower() for kw in FINANCIAL_KEYWORDS):
                    financial_page_numbers.append(i)

            # Step 2: pdfplumber extracts tables from financial pages only
            text_pages = []
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                if financial_page_numbers:
                    for page_num in financial_page_numbers[:40]:
                        if page_num < len(pdf.pages):
                            page_text = pdf.pages[page_num].extract_text()
                            if page_text:
                                text_pages.append(page_text)
                else:
                    # Fallback: first 20 pages
                    for page in pdf.pages[:20]:
                        page_text = page.extract_text()
                        if page_text:
                            text_pages.append(page_text)

            return "\n\n".join(text_pages)
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {e}")

    def _llm_extract_financials(self, text: str) -> ExtractedFinancials:
        """Send text to Gemini and get structured financial data back."""
        try:
            chain = self.extraction_prompt | self.llm | StrOutputParser()

            # Send up to 40K chars to Gemini
            truncated_text = text[:40000]

            response = chain.invoke({"text": truncated_text})

            # Clean up markdown formatting if present
            content = response.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            parsed = json.loads(content.strip())

            return ExtractedFinancials(
                revenue=parsed.get("revenue"),
                net_profit=parsed.get("net_profit"),
                total_debt=parsed.get("total_debt"),
                total_equity=parsed.get("total_equity"),
                debt_to_equity=parsed.get("debt_to_equity"),
                current_ratio=parsed.get("current_ratio"),
                interest_coverage_ratio=parsed.get("interest_coverage_ratio"),
                covenants=parsed.get("covenants") or [],
                related_party_transactions=parsed.get("related_party_transactions") or [],
                contingent_liabilities=parsed.get("contingent_liabilities") or []
            )
        except json.JSONDecodeError:
            # LLM didn't return valid JSON — return empty financials
            return ExtractedFinancials()
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return ExtractedFinancials()

    def parse_pdf(self, file_content: bytes, file_name: str, application_id: str, doc_id: str) -> IngestedDocument:
        """Full PDF parsing pipeline: extract text → send to LLM → return structured document."""

        # Step 1: Extract raw text from PDF
        raw_text = self._extract_text_from_pdf(file_content)

        if not raw_text.strip():
            return IngestedDocument(
                id=doc_id,
                application_id=application_id,
                file_name=file_name,
                file_type=DocumentType.ANNUAL_REPORT,
                extracted_text_preview="No text could be extracted from this PDF.",
                financials=None,
                anomalies=[],
                processing_status="failed"
            )

        # Step 2: Send text to LLM for structured extraction
        financials = self._llm_extract_financials(raw_text)

        # Step 3: Build and return the IngestedDocument
        return IngestedDocument(
            id=doc_id,
            application_id=application_id,
            file_name=file_name,
            file_type=DocumentType.ANNUAL_REPORT,
            extracted_text_preview=raw_text[:500],
            financials=financials,
            anomalies=[],
            processing_status="completed"
        )

    
    # Structured Data Processing (GST, Bank Statements)
    

    def _read_file_to_dataframe(self, file_content: bytes, file_name: str) -> pd.DataFrame:
        """Read CSV or Excel file into a Pandas DataFrame."""
        try:
            if file_name.endswith(".csv"):
                return pd.read_csv(io.BytesIO(file_content))
            elif file_name.endswith((".xlsx", ".xls")):
                return pd.read_excel(io.BytesIO(file_content))
            else:
                raise Exception(f"Unsupported file format: {file_name}")
        except Exception as e:
            raise Exception(f"Failed to read structured file: {e}")

    def _detect_anomalies(self, df: pd.DataFrame, file_type: DocumentType) -> list[StructuredDataAnomaly]:
        """Run anomaly detection on structured data."""
        anomalies = []

        if file_type == DocumentType.GST_FILING:
            anomalies.extend(self._check_gst_anomalies(df))
        elif file_type == DocumentType.BANK_STATEMENT:
            anomalies.extend(self._check_bank_anomalies(df))

        return anomalies

    def _check_gst_anomalies(self, df: pd.DataFrame) -> list[StructuredDataAnomaly]:
        """Check GST filing data for mismatches and red flags."""
        anomalies = []
        columns_lower = [col.lower() for col in df.columns]

        # Check 1: GSTR-3B vs GSTR-2A mismatch (if both columns exist)
        gstr3b_col = None
        gstr2a_col = None
        for col in df.columns:
            if "3b" in col.lower():
                gstr3b_col = col
            if "2a" in col.lower():
                gstr2a_col = col

        if gstr3b_col and gstr2a_col:
            df[gstr3b_col] = pd.to_numeric(df[gstr3b_col], errors="coerce")
            df[gstr2a_col] = pd.to_numeric(df[gstr2a_col], errors="coerce")
            mismatch = (df[gstr3b_col].sum() - df[gstr2a_col].sum())
            if abs(mismatch) > 100000:  # More than ₹1 lakh mismatch
                anomalies.append(StructuredDataAnomaly(
                    anomaly_type="gstr_mismatch",
                    description=f"GSTR-3B total exceeds GSTR-2A by ₹{mismatch:,.0f}. Possible input tax credit inflation.",
                    severity=RiskSeverity.HIGH if abs(mismatch) > 1000000 else RiskSeverity.MEDIUM,
                    data_points={"gstr_3b_total": float(df[gstr3b_col].sum()), "gstr_2a_total": float(df[gstr2a_col].sum()), "difference": float(mismatch)}
                ))

        # Check 2: Revenue concentration — any single month > 40% of total
        revenue_cols = [col for col in df.columns if any(kw in col.lower() for kw in ["revenue", "sales", "turnover", "taxable"])]
        for col in revenue_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            total = df[col].sum()
            if total > 0:
                max_month = df[col].max()
                if max_month / total > 0.4:
                    anomalies.append(StructuredDataAnomaly(
                        anomaly_type="revenue_concentration",
                        description=f"Single period accounts for {max_month/total*100:.1f}% of total revenue. Possible revenue spike or manipulation.",
                        severity=RiskSeverity.MEDIUM,
                        data_points={"max_period_value": float(max_month), "total": float(total), "concentration_pct": float(max_month/total*100)}
                    ))

        return anomalies

    def _check_bank_anomalies(self, df: pd.DataFrame) -> list[StructuredDataAnomaly]:
        """Check bank statement data for circular trading and suspicious patterns."""
        anomalies = []

        # Check 1: Circular trading — same large amounts appearing as both credit and debit
        credit_col = None
        debit_col = None
        for col in df.columns:
            if any(kw in col.lower() for kw in ["credit", "deposit", "cr"]):
                credit_col = col
            if any(kw in col.lower() for kw in ["debit", "withdrawal", "dr"]):
                debit_col = col

        if credit_col and debit_col:
            df[credit_col] = pd.to_numeric(df[credit_col], errors="coerce").fillna(0)
            df[debit_col] = pd.to_numeric(df[debit_col], errors="coerce").fillna(0)

            # Find large transactions that appear as both credit and debit (within 5% tolerance)
            large_credits = df[df[credit_col] > 500000][credit_col].values
            large_debits = df[df[debit_col] > 500000][debit_col].values

            circular_count = 0
            for credit in large_credits:
                for debit in large_debits:
                    if abs(credit - debit) / max(credit, debit) < 0.05:  # Within 5%
                        circular_count += 1

            if circular_count >= 3:
                anomalies.append(StructuredDataAnomaly(
                    anomaly_type="circular_trading",
                    description=f"Found {circular_count} instances of matching large credit-debit pairs (within 5% tolerance). Possible circular trading.",
                    severity=RiskSeverity.HIGH,
                    data_points={"matching_pairs": circular_count}
                ))

        # Check 2: Sudden large inflows just before month-end (window dressing)
        date_col = None
        for col in df.columns:
            if any(kw in col.lower() for kw in ["date", "txn_date", "value_date"]):
                date_col = col
                break

        if date_col and credit_col:
            try:
                df["_parsed_date"] = pd.to_datetime(df[date_col], errors="coerce")
                df["_day"] = df["_parsed_date"].dt.day
                month_end_credits = df[df["_day"] >= 28][credit_col].sum()
                total_credits = df[credit_col].sum()
                if total_credits > 0 and month_end_credits / total_credits > 0.35:
                    anomalies.append(StructuredDataAnomaly(
                        anomaly_type="window_dressing",
                        description=f"{month_end_credits/total_credits*100:.1f}% of total credits occur in last 3 days of months. Possible window dressing.",
                        severity=RiskSeverity.MEDIUM,
                        data_points={"month_end_pct": float(month_end_credits/total_credits*100)}
                    ))
                df.drop(columns=["_parsed_date", "_day"], inplace=True, errors="ignore")
            except Exception:
                pass

        return anomalies

    def process_structured(self, file_content: bytes, file_name: str, file_type: DocumentType,
                           application_id: str, doc_id: str) -> IngestedDocument:
        """Full structured data pipeline: read file → detect anomalies → return document."""

        # Step 1: Read into DataFrame
        df = self._read_file_to_dataframe(file_content, file_name)

        # Step 2: Run anomaly detection
        anomalies = self._detect_anomalies(df, file_type)

        # Step 3: Generate a text preview of the data
        preview = f"Columns: {list(df.columns)}\nRows: {len(df)}\nSample:\n{df.head(3).to_string()}"

        # Step 4: Build and return
        return IngestedDocument(
            id=doc_id,
            application_id=application_id,
            file_name=file_name,
            file_type=file_type,
            extracted_text_preview=preview[:500],
            financials=None,
            anomalies=anomalies,
            processing_status="completed"
        )
