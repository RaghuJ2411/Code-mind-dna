# PHASE 4 IMPLEMENTATION PLAN

## A. EXISTING FIELDS (Sufficient for Phase 4)

### CodingEvent (app/models/execution.py)
✅ **Current fields are sufficient:**
- `id`, `student_id`, `problem_id`, `session_id`, `event_type`, `language`, `metadata_json`, `created_at`

**Action:** Extend to support more event types (currently only RUN_CODE, SUBMIT_CODE recorded)

### CodingSession (app/models/execution.py)
✅ **Current fields mostly sufficient:**
- `id`, `student_id`, `problem_id`, `started_at`, `last_activity_at`, `ended_at`
- `language`, `run_count`, `submit_count`, `is_solved`

**Action:** Add computed error counters (wrong_answer_count, compilation_error_count, etc.)

### Submission (app/models/execution.py)
✅ **All necessary fields present:**
- verdict, passed_test_cases, total_test_cases, runtime_ms, memory_kb, attempt_number, created_at

### Problem (app/models/problem.py)
✅ **Has difficulty and topic:**
- difficulty: DifficultyLevel (EASY, MEDIUM, HARD)
- topic: TopicType (ARRAYS, STRINGS, GRAPHS, TREES, etc.)

---

## B. FIELDS THAT NEED EXTENSION

### CodingSession
**Add error tracking columns:**
- `wrong_answer_count: int` (default 0)
- `compilation_error_count: int` (default 0)
- `runtime_error_count: int` (default 0)
- `time_limit_count: int` (default 0)

---

## C. NEW MODELS TO CREATE

### 1. StudentDailyAnalytics
```python
# backend/app/models/analytics.py

class StudentDailyAnalytics(Base):
    __tablename__ = "student_daily_analytics"
    
    id, student_id, analytics_date (Unique: student_id + analytics_date)
    problems_attempted, problems_solved
    submissions_count, runs_count, active_minutes
    wrong_answer_count, compilation_error_count
    runtime_error_count, time_limit_count
    easy_attempted, easy_solved, medium_attempted, medium_solved
    hard_attempted, hard_solved
    unique_topics_attempted
    created_at, updated_at
```

### 2. StudentWeeklyAnalytics
```python
# Same file

class StudentWeeklyAnalytics(Base):
    __tablename__ = "student_weekly_analytics"
    
    id, student_id, week_start, week_end (Unique: student_id + week_start)
    problems_attempted, problems_solved, solve_rate
    submissions_count, runs_count, active_minutes, active_days
    average_attempts_to_solve, average_solve_time_minutes
    error_recovery_rate
    easy_solve_rate, medium_solve_rate, hard_solve_rate
    unique_topics_attempted, difficulty_progression_delta
    created_at, updated_at
```

### 3. Configuration Models (for evidence thresholds)
```python
# backend/app/core/config.py additions

CODING_SESSION_IDLE_MINUTES: int = 30
MIN_TOPIC_ATTEMPTS_FOR_CLASSIFICATION: int = 3
MIN_PROBLEMS_FOR_PROGRESSION: int = 5
MIN_ACCEPTED_FOR_OPTIMIZATION: int = 2
```

---

## D. FILES TO CREATE

### Backend Structure
```
backend/app/services/analytics/
    __init__.py
    behavior_feature_service.py      # Feature extraction
    aggregation_service.py           # Daily/weekly aggregation
    data_quality_service.py          # Data validation
    
backend/app/models/
    analytics.py                     # Daily/Weekly Analytics models

backend/app/schemas/
    analytics.py                     # Response schemas

backend/app/api/
    analytics.py                     # Analytics endpoints

backend/alembic/versions/
    YYYYMMDD_add_analytics_models.py # Migration

frontend/src/pages/student/
    AnalyticsPage.jsx               # Student Analytics UI
    
frontend/src/components/
    ActivityHeatmap.jsx             # Activity visualization
    ProgressionChart.jsx            # Progression chart
```

---

## E. FILES TO MODIFY

### Backend
- `backend/app/models/execution.py` — Add error counters to CodingSession
- `backend/app/core/config.py` — Add analytics configuration
- `backend/app/main.py` — Register analytics router
- `backend/app/api/execution.py` — Record more event types
- `backend/app/services/execution_service.py` — Record lifecycle events
- `.env.example` — Add CODING_SESSION_IDLE_MINUTES

### Frontend  
- `frontend/src/pages/student/StudentDashboard.jsx` — Link to analytics
- `frontend/src/routes/ProtectedRoute.jsx` or add new analytics route

---

## F. NEW API ENDPOINTS

```
GET /api/student/analytics/overview
GET /api/student/analytics/topics
GET /api/student/analytics/difficulty
GET /api/student/analytics/progression
GET /api/student/analytics/activity?days=30

PATCH /api/coding-sessions/{session_id}/activity
POST /api/coding-sessions/{session_id}/end
```

---

## G. METRIC DEFINITIONS

### Activity Metrics
- **problems_attempted**: Unique problems with at least one submission
- **problems_solved**: Unique problems with ACCEPTED verdict
- **total_submissions**: Total count of submissions (attempt includes multiple runs)
- **total_runs**: Count of Run API calls
- **active_minutes**: Sum of (last_activity_at - started_at) per session, excluding idle > threshold
- **active_days**: Count of distinct calendar dates with sessions

### Success Metrics
- **solve_rate**: problems_solved / problems_attempted
- **first_attempt_acceptance_rate**: (problems accepted on first official submission) / problems_attempted
- **average_attempts_to_solve**: sum(attempt_number for accepted submissions) / problems_solved

### Debugging Metrics
- **total_wrong_answers**: Count of WRONG_ANSWER verdicts
- **total_compilation_errors**: Count of COMPILATION_ERROR verdicts
- **error_recovery_rate**: Sequences ending in ACCEPTED after errors / total recoverable sequences
- **repeated_error_rate**: Consecutive error type transitions / total error transitions

### Difficulty Metrics
- **easy/medium/hard_attempted**: Unique problems attempted by difficulty
- **easy/medium/hard_solved**: Unique problems solved by difficulty
- **solve_rate per difficulty**: solved / attempted per difficulty
- **weighted difficulty**: (easy*1 + medium*2 + hard*3) / count

### Topic Metrics  
- **topics_attempted**: Distinct topics with at least one attempt
- **topics_solved**: Distinct topics with at least one solved problem
- Per-topic: attempted, solved, solve_rate, avg_attempts, avg_solve_time

### Consistency Metrics
- **active_days_last_7**: Distinct dates in last 7 days with activity
- **active_days_last_30**: Distinct dates in last 30 days with activity
- **current_streak**: Consecutive days of activity ending today
- **longest_streak**: Maximum consecutive days of activity ever
- **weekly_consistency_ratio**: std_dev(weekly_active_days) — lower is more consistent

### Progression Metrics
- **attempt_efficiency_delta**: avg_attempts_previous - avg_attempts_recent
- **solve_rate_delta**: solve_rate_recent - solve_rate_previous  
- **solve_time_improvement_minutes**: avg_solve_time_previous - avg_solve_time_recent
- **difficulty_progression_delta**: weighted_difficulty_recent - weighted_difficulty_previous

---

## H. MIGRATION STRATEGY

```bash
# Create migration
alembic revision --autogenerate -m "Add analytics models and CodingSession error counters"

# Run migration
alembic upgrade head
```

---

## I. TESTING CHECKLIST

- [ ] Session start/resume works
- [ ] Session end captures metrics correctly
- [ ] Stale sessions close automatically
- [ ] Error counters increment correctly
- [ ] Active time excludes idle gaps
- [ ] Solve rate calculation handles edge cases
- [ ] First-attempt acceptance tracks correctly
- [ ] Error recovery detects recovery sequences
- [ ] Topic analytics group correctly
- [ ] Difficulty progression detects changes
- [ ] Daily analytics aggregates correctly
- [ ] Weekly analytics rolls up from daily
- [ ] Aggregation is idempotent
- [ ] Evidence thresholds work correctly
- [ ] Empty data states handled gracefully
- [ ] Analytics endpoints auth required
- [ ] Student cannot see another's analytics

---

## J. KNOWN LIMITATIONS (Phase 4)

1. Runtime measurements are from execution provider — may vary based on system load
2. No optimization analysis without static code analysis tool
3. No advanced behavior clustering or pattern detection
4. No ML model scoring yet (Phase 5)
5. Aggregation not on background worker (direct API call for now)
6. No real-time streaming events (batch aggregation only)

---

## K. DATA VALIDATION RULES

### Data Quality Checks
- Sessions: `ended_at` >= `started_at`
- Sessions: `last_activity_at` >= `started_at` and <= `ended_at` (if ended)
- Active time: Never negative
- Attempt numbers: Always positive
- Error counts: Never negative
- Percentages: Between 0.0 and 1.0
- Timestamps: All UTC with timezone

---

## L. BEFORE PHASE 5

Required for Coding DNA scoring to work:
1. ✅ Reliable behavior feature extraction
2. ✅ Sufficient data collection (5+ attempted problems minimum)
3. ✅ Clean analytics pipeline
4. ✅ Consistent metric definitions
5. ✅ Evidence-based classifications
6. No random or synthetic metrics
