# PHASE 4 - Real AI Integration - Detailed Implementation Plan

## Current State Analysis
The codebase already has a strong foundation:
- **✅ Analytics Pipeline**: Models, AggregationService, BehaviorFeatureService, DataQualityService, full API
- **✅ DNA Scoring Engine**: 6 dimensions (logic, debugging, optimization, consistency, learning_velocity, breadth), full scoring logic, profile service
- **✅ Career Service**: Role matching, readiness scoring, resume/project/interview CRUD
- **✅ AI Infrastructure**: Provider factory (Mock/OpenAI), code review service, assistance service, usage limits, prompt registry
- **✅ Frontend**: SkillDNAPage, AnalyticsPage, CareerPage (basic UIs)
- **✅ Error Counters**: Already added to CodingSession model

## What Needs to Be Built

### Step 1: AI Schemas for Skill Gap & Career Prediction
- **File: `backend/app/schemas/ai_career.py`** (NEW)
  - `SkillGapRequest`, `SkillGapResponse` - request/response for AI skill gap analysis
  - `CareerPredictionRequest`, `CareerPredictionResponse` - career path prediction
  - `ResumeParseResponse` - AI-parsed resume structure
  - `InterviewFeedbackRequest`, `InterviewFeedbackResponse` - AI interview feedback

### Step 2: AI Career Service (Skill Gap + Prediction)
- **File: `backend/app/services/ai/career_ai_service.py`** (NEW)
  - `CareerAIService` class using existing AI provider infrastructure
  - `analyze_skill_gap()` - Compare DNA profile vs role requirements
  - `predict_career_paths()` - AI-powered multi-path recommendations
  - `parse_resume_content()` - Extract structured data from resume text
  - `generate_interview_feedback()` - AI-generated interview feedback

### Step 3: AI Career API Endpoints
- **File: `backend/app/api/student_ai_career.py`** (NEW)
  - `POST /student/ai-career/skill-gap` - AI skill gap analysis
  - `POST /student/ai-career/career-prediction` - Career path prediction
  - `POST /student/ai-career/parse-resume` - Parse resume content
  - `POST /student/ai-career/interview-feedback` - AI interview feedback
  - Uses existing AI provider + daily limit middleware

### Step 4: Enhanced Career Service (Integrate AI)
- **Modify: `backend/app/services/career/career_service.py`**
  - Add `generate_ai_interview_feedback()` to replace heuristic scoring
  - Add `get_ai_skill_gap_analysis()` for role comparison
  - Add `get_career_path_predictions()` for multi-path recommendations

### Step 5: Register New Routes
- **Modify: `backend/app/main.py`**
  - Import and register `student_ai_career_router`

### Step 6: Frontend AI Career API Client
- **File: `frontend/src/api/aiCareer.js`** (NEW)
  - API calls for skill gap, career prediction, resume parsing, interview feedback

### Step 7: Enhanced SkillDNA Page (Radar Chart + Dimension Breakdown)
- **Modify: `frontend/src/pages/student/SkillDNAPage.jsx`**
  - Add radar/radar-like chart for 6 DNA dimensions
  - Add detailed dimension cards with explanations
  - Add improvement tips per dimension
  - Show evidence status & confidence per dimension

### Step 8: Enhanced Career Page (AI Insights)
- **Modify: `frontend/src/pages/student/CareerPage.jsx`**
  - Add AI Skill Gap Analysis section
  - Add Career Path Prediction visualization
  - Add AI Interview Feedback display
  - Add Resume AI Analysis section

### Step 9: Update AIMentorPage
- **Modify: `frontend/src/pages/student/AIMentorPage.jsx`**
  - Integrate career AI features
  - Add skill gap chat interface
  - Add career prediction display

### Step 10: Update TODO.md
- Mark Phase 4 components as complete

