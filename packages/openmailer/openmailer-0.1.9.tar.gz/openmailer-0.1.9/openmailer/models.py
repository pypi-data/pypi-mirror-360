from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

from openmailer.base import Base  # ✅ Adjust this to your actual Base import

def generate_uuid():
    return str(uuid.uuid4())

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    key = Column(String, unique=True, index=True, nullable=False)
    
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    team_id = Column(PG_UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    workspace_id = Column(PG_UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True)

    permissions = Column(String, default="send:email")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User")
    team = relationship("Team")
    workspace = relationship("Workspace")

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    team_id = Column(PG_UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    workspace_id = Column(PG_UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True)

    to = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    status = Column(String, default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    team = relationship("Team")
    workspace = relationship("Workspace")



class SMTPCredential(Base):
    __tablename__ = "smtp_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("verified_domains.id", ondelete="CASCADE"))

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="SET NULL"))

    smtp_username = Column(String, nullable=False, unique=True)
    smtp_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    domain = relationship("VerifiedDomain", back_populates="smtp_credential")