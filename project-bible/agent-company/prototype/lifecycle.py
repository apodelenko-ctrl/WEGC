"""Local simulation only. Actor is a fixture, NOT authentication. No external I/O."""
from dataclasses import dataclass, replace
from uuid import uuid4


@dataclass(frozen=True)
class Actor:
    tenant_id: str
    principal_ref: str
    role: str
    agent_id: str = ""


@dataclass(frozen=True)
class Application:
    id: str
    tenant_id: str
    principal_ref: str
    name: str
    state: str = "review_required"
    formation: str = "not_submitted"
    payments: str = "not_requested"
    mandate: str = "inactive"
    agent_id: str = ""
    scopes: tuple[str, ...] = ()
    simulation: bool = True


class Lifecycle:
    """In-memory state rules, not a server, bank adapter or security boundary."""

    def __init__(self) -> None:
        self._records: dict[str, Application] = {}
        self._keys: dict[tuple[str, str], str] = {}

    def create(self, actor: Actor, name: str, key: str) -> Application:
        if not all(isinstance(x, str) and x.strip() for x in
                   (actor.tenant_id, actor.principal_ref, name, key)):
            raise ValueError("missing_required_field")
        self._role(actor, "agent", "operator")
        index = (actor.tenant_id, key)
        if index in self._keys:
            record = self.get(actor, self._keys[index])
            if record.name != name.strip():
                raise ValueError("idempotency_conflict")
            return record
        record = Application(str(uuid4()), actor.tenant_id,
                             actor.principal_ref, name.strip())
        self._records[record.id] = record
        self._keys[index] = record.id
        return record

    def get(self, actor: Actor, record_id: str) -> Application:
        record = self._records[record_id]
        if (actor.tenant_id, actor.principal_ref) != (record.tenant_id, record.principal_ref):
            raise PermissionError("tenant_or_principal_scope")
        return record

    @staticmethod
    def _role(actor: Actor, *allowed: str) -> None:
        if actor.role not in allowed:
            raise PermissionError("role_not_allowed")

    @staticmethod
    def _require(condition: bool) -> None:
        if not condition:
            raise ValueError("invalid_transition")

    def transition(self, actor: Actor, record_id: str, event: str,
                   evidence_ref: str = "") -> Application:
        record = self.get(actor, record_id)
        if event == "approve_submission":
            self._role(actor, "operator")
            self._require(record.state == "review_required")
            updated = replace(record, state="approved_for_submission")
        elif event == "submit_formation":
            self._role(actor, "operator", "agent")
            self._require(record.state == "approved_for_submission")
            updated = replace(record, state="submitted", formation="submitted")
        elif event in ("formation_confirmed", "payments_approved"):
            self._role(actor, "provider_fixture")
            if not evidence_ref.startswith("sim:") or len(evidence_ref) <= 4:
                raise ValueError("simulation_evidence_required")
            if event == "formation_confirmed":
                self._require(record.formation == "submitted")
                updated = replace(record, state="completed", formation="formed")
            else:
                self._require(record.payments == "submitted")
                updated = replace(record, payments="approved")
        elif event == "submit_payments":
            self._role(actor, "operator", "agent")
            self._require(record.formation == "formed" and record.payments == "not_requested")
            updated = replace(record, payments="submitted")
        else:
            raise ValueError("unknown_event")
        self._records[record_id] = updated
        return updated

    def grant(self, actor: Actor, record_id: str, agent_id: str,
              scopes: tuple[str, ...]) -> Application:
        self._role(actor, "operator")
        record = self.get(actor, record_id)
        self._require(record.formation == "formed")
        allowed = {"read_documents", "prepare_invoice"}
        if not agent_id or not scopes or not set(scopes).issubset(allowed):
            raise ValueError("invalid_mandate")
        updated = replace(record, mandate="active", agent_id=agent_id, scopes=tuple(scopes))
        self._records[record_id] = updated
        return updated

    def revoke(self, actor: Actor, record_id: str) -> Application:
        self._role(actor, "operator")
        updated = replace(self.get(actor, record_id), mandate="revoked", scopes=())
        self._records[record_id] = updated
        return updated

    def operate(self, actor: Actor, record_id: str, action: str) -> dict[str, object]:
        self._role(actor, "agent")
        record = self.get(actor, record_id)
        if (record.mandate != "active" or record.agent_id != actor.agent_id
                or action not in record.scopes):
            raise PermissionError("mandate_denied")
        return {"simulation": True, "status": "simulated", "action": action,
                "application_id": record.id, "external_side_effect": False}
