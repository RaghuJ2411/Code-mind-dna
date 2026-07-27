"""add mentor risk alerts table

Revision ID: 20260711_add_mentor_risk_alerts
Revises: b3c3f447a01b
Create Date: 2026-07-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "20260711_add_mentor_risk_alerts"
down_revision = "b3c3f447a01b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    alert_type_enum = sa.Enum(
        "ENGAGEMENT_DROP",
        "LOW_SUCCESS_RATE",
        "INCONSISTENT_PRACTICE",
        "ATTENDANCE_ISSUE",
        name="mentoralerttype",
    )
    severity_enum = sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", name="alertseverity")
    status_enum = sa.Enum("OPEN", "ACKNOWLEDGED", "RESOLVED", name="mentoralertstatus")

    alert_type_enum.create(op.get_bind(), checkfirst=True)
    severity_enum.create(op.get_bind(), checkfirst=True)
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "mentor_risk_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mentor_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("alert_type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mentor_risk_alerts_created_at"), "mentor_risk_alerts", ["created_at"], unique=False)
    op.create_index(op.f("ix_mentor_risk_alerts_mentor_id"), "mentor_risk_alerts", ["mentor_id"], unique=False)
    op.create_index(op.f("ix_mentor_risk_alerts_student_id"), "mentor_risk_alerts", ["student_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_mentor_risk_alerts_student_id"), table_name="mentor_risk_alerts")
    op.drop_index(op.f("ix_mentor_risk_alerts_mentor_id"), table_name="mentor_risk_alerts")
    op.drop_index(op.f("ix_mentor_risk_alerts_created_at"), table_name="mentor_risk_alerts")
    op.drop_table("mentor_risk_alerts")
    sa.Enum(name="mentoralertstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="alertseverity").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="mentoralerttype").drop(op.get_bind(), checkfirst=True)
