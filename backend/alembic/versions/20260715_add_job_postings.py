"""add recruiter job postings table

Revision ID: 20260715_add_job_postings
Revises: 20260714_add_mentor_career_review
Create Date: 2026-07-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "20260715_add_job_postings"
down_revision = "20260714_add_mentor_career_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("job_postings"):
        op.create_table(
            "job_postings",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("recruiter_id", sa.Integer(), nullable=False, index=True),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("company", sa.String(length=255), nullable=False),
            sa.Column("location", sa.String(length=255), nullable=False),
            sa.Column("seniority_level", sa.String(length=50), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("requirements_json", sa.JSON(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    op.drop_table("job_postings")
