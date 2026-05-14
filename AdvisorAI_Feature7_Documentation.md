# Advisor AI - Feature 7: Human-in-the-Loop (HITL) Supervision Queue
**Technical Implementation Report**

## 1. Executive Summary
Feature 7 implements a critical "Human-in-the-Loop" (HITL) supervision framework, ensuring that all AI-generated financial advice adheres to strict regulatory standards (SEC/FINRA). By intercepting high-risk recommendations before they reach the advisor, the system provides a robust safety net that combines AI efficiency with human accountability.

## 2. Problem Statement
In highly regulated financial environments, allowing an LLM to provide direct investment advice without oversight poses significant legal and reputational risks. Automatic filters (Feature 4) can block advice, but complex cases require a human supervisor to review, override, or approve recommendations with specific audit notes.

## 3. Architecture & Workflow
The supervision workflow is integrated across the entire AWS stack:

### A. Interception (AWS Lambda)
- **Engine:** The Compliance Engine (Llama 3.1) analyzes the generated response.
- **Trigger:** If a violation is detected (e.g., "Guaranteed Returns" or "Risk Profile Mismatch"), the Lambda suspends the output.
- **Persistence:** Flagged advice, client context, and violation rationale are saved to the `advisor-ai-supervision` DynamoDB table with a `PENDING` status.
- **Response:** The Advisor receives a "Review ID" instead of the suspended advice.

### B. Supervision Dashboard (UI)
- **Role-Based Access:** A dedicated "Compliance View" section in the sidebar.
- **Real-Time Polling:** The dashboard polls the `advisor-ai-supervision` table for pending reviews.
- **Audit Trails:** Supervisors must provide mandatory notes before taking action (Approve/Override).

### C. Backend API (FastAPI)
- **Endpoints:**
    - `GET /api/supervision/pending`: Fetches all items requiring human action.
    - `POST /api/supervision/action`: Processes the supervisor's decision and logs the audit note.

## 4. Technical Stack
- **Database:** Amazon DynamoDB (`advisor-ai-supervision` table).
- **Compute:** AWS Lambda (Python 3.12) & Amazon EC2 (FastAPI).
- **State Management:** Real-time UI badges and status-coded response interception.
- **Security:** Logic-based role separation for "Management & Risk" tools.

## 5. Compliance & Audit
Every human action is logged with:
- **Timestamp:** Precise moment of intervention.
- **Supervisor ID:** Identity of the reviewer.
- **Original AI Output:** What the AI wanted to say.
- **Compliance Rationale:** Why it was blocked.
- **Human Decision:** Approved or Overridden.
- **Audit Notes:** Detailed explanation for the decision.

## 6. Business Impact
- **Regulatory Readiness:** Directly addresses FINRA/SEC requirements for human oversight.
- **Risk Mitigation:** Prevents rogue AI behavior in production environments.
- **Enterprise Scalability:** Enables back-office teams to manage AI outputs across thousands of advisors.

---
*Built for the Incedo Advisor AI Hackathon | May 2026*
