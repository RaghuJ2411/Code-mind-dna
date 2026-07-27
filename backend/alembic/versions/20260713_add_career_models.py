"""add career intelligence models

Revision ID: 20260713_add_career_models
Revises: 20260712_add_ai_models
Create Date: 2026-07-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "20260713_add_career_models"
down_revision = "20260712_add_ai_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("career_roles"):
        op.create_table(
            "career_roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("seniority_level", sa.String(length=50), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("required_skills_json", sa.JSON(), nullable=False),
            sa.Column("target_score_min", sa.Integer(), nullable=False),
            sa.Column("target_score_max", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )

    if not inspector.has_table("student_resume_entries"):
        op.create_table(
            "student_resume_entries",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("student_id", sa.Integer(), nullable=False, index=True),
            sa.Column("section", sa.String(length=100), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("skills_json", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )

    if not inspector.has_table("student_projects"):
        op.create_table(
            "student_projects",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("student_id", sa.Integer(), nullable=False, index=True),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("technologies_json", sa.JSON(), nullable=False),
            sa.Column("outcome", sa.Text(), nullable=True),
            sa.Column("project_url", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )

    if not inspector.has_table("interview_practice_sessions"):
        op.create_table(
            "interview_practice_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("student_id", sa.Integer(), nullable=False, index=True),
            sa.Column("role_name", sa.String(length=255), nullable=True),
            sa.Column("question", sa.Text(), nullable=False),
            sa.Column("answer", sa.Text(), nullable=False),
            sa.Column("feedback_score", sa.Integer(), nullable=False),
            sa.Column("feedback_text", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    op.drop_table("interview_practice_sessions")
    op.drop_table("student_projects")
    op.drop_table("student_resume_entries")
    op.drop_table("career_roles")
