"""add audit logs table

Revision ID: 20260716_add_audit_logs
Revises: 20260715_add_job_postings
Create Date: 2026-07-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "20260716_add_audit_logs"
down_revision = "20260715_add_job_postings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_email", sa.String(length=255), nullable=True),
            sa.Column("path", sa.String(length=255), nullable=False),
            sa.Column("method", sa.String(length=16), nullable=False),
            sa.Column("status_code", sa.Integer(), nullable=False),
            sa.Column("remote_addr", sa.String(length=100), nullable=True),
            sa.Column("user_agent", sa.String(length=512), nullable=True),
            sa.Column("request_metadata_json", sa.JSON(), nullable=True),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    op.drop_table("audit_logs")
