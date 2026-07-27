"""add ai request log and code review tables

Revision ID: 20260712_add_ai_models
Revises: 20260711_add_student_recommendations_goals,20260711_add_mentor_risk_alerts,c5f4a7e9b2c8
Create Date: 2026-07-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260712_add_ai_models"
down_revision = ("20260711_add_student_recommendations_goals", "20260711_add_mentor_risk_alerts", "c5f4a7e9b2c8")
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("ai_request_logs"):
        op.create_table(
            "ai_request_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("task_type", sa.String(length=100), nullable=False),
            sa.Column("provider", sa.String(length=100), nullable=True),
            sa.Column("model", sa.String(length=100), nullable=True),
            sa.Column("prompt_version", sa.String(length=50), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("input_token_count", sa.Integer(), nullable=True),
            sa.Column("output_token_count", sa.Integer(), nullable=True),
            sa.Column("latency_ms", sa.Integer(), nullable=True),
            sa.Column("error_category", sa.String(length=200), nullable=True),
            sa.Column("request_metadata_json", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )

    if not inspector.has_table("ai_code_reviews"):
        op.create_table(
            "ai_code_reviews",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("student_id", sa.Integer(), nullable=False),
            sa.Column("submission_id", sa.Integer(), nullable=False),
            sa.Column("review_json", sa.JSON(), nullable=False),
            sa.Column("prompt_version", sa.String(length=50), nullable=True),
            sa.Column("provider", sa.String(length=100), nullable=True),
            sa.Column("model_name", sa.String(length=100), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    op.drop_table("ai_code_reviews")
    op.drop_table("ai_request_logs")
