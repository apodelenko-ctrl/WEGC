"""Synthetic fixtures only; no legal, customer or financial data."""
import unittest
from dataclasses import FrozenInstanceError
from lifecycle import Actor, Lifecycle


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.flow = Lifecycle()
        self.agent = Actor("fixture_tenant", "fixture_principal", "agent", "fixture_agent")
        self.owner = Actor("fixture_tenant", "fixture_principal", "operator")
        self.provider = Actor("fixture_tenant", "fixture_principal", "provider_fixture")
        self.record = self.flow.create(self.agent, "SIMULATION ONLY", "fixture_key")

    def formed(self):
        self.flow.transition(self.owner, self.record.id, "approve_submission")
        self.flow.transition(self.agent, self.record.id, "submit_formation")
        return self.flow.transition(self.provider, self.record.id,
                                    "formation_confirmed", "sim:formation_fixture")

    def test_idempotent_create(self):
        self.assertEqual(self.record, self.flow.create(self.agent, "SIMULATION ONLY", "fixture_key"))

    def test_key_payload_conflict(self):
        with self.assertRaisesRegex(ValueError, "idempotency_conflict"):
            self.flow.create(self.agent, "DIFFERENT FIXTURE", "fixture_key")

    def test_principal_required(self):
        with self.assertRaisesRegex(ValueError, "missing_required_field"):
            self.flow.create(Actor("fixture_tenant", "", "agent"), "FIXTURE", "key")

    def test_other_tenant_denied(self):
        with self.assertRaises(PermissionError):
            self.flow.get(Actor("other", "fixture_principal", "agent"), self.record.id)

    def test_other_principal_denied(self):
        with self.assertRaises(PermissionError):
            self.flow.get(Actor("fixture_tenant", "other", "operator"), self.record.id)

    def test_agent_cannot_approve_itself(self):
        with self.assertRaises(PermissionError):
            self.flow.transition(self.agent, self.record.id, "approve_submission")

    def test_submission_needs_approval(self):
        with self.assertRaises(ValueError):
            self.flow.transition(self.agent, self.record.id, "submit_formation")

    def test_submitted_is_not_formed(self):
        self.flow.transition(self.owner, self.record.id, "approve_submission")
        result = self.flow.transition(self.agent, self.record.id, "submit_formation")
        self.assertEqual(result.formation, "submitted")
        self.assertEqual(result.payments, "not_requested")

    def test_external_event_needs_simulation_evidence(self):
        self.flow.transition(self.owner, self.record.id, "approve_submission")
        self.flow.transition(self.agent, self.record.id, "submit_formation")
        with self.assertRaisesRegex(ValueError, "simulation_evidence_required"):
            self.flow.transition(self.provider, self.record.id, "formation_confirmed")

    def test_formed_does_not_approve_payments(self):
        self.assertEqual(self.formed().payments, "not_requested")

    def test_payment_approval_needs_application(self):
        self.formed()
        with self.assertRaises(ValueError):
            self.flow.transition(self.provider, self.record.id, "payments_approved", "sim:bank_fixture")
        self.flow.transition(self.agent, self.record.id, "submit_payments")
        result = self.flow.transition(self.provider, self.record.id, "payments_approved", "sim:bank_fixture")
        self.assertEqual(result.payments, "approved")
        self.assertTrue(result.simulation)

    def test_revoke_stops_agent(self):
        self.formed()
        self.flow.grant(self.owner, self.record.id, self.agent.agent_id, ("read_documents",))
        self.assertFalse(self.flow.operate(self.agent, self.record.id, "read_documents")["external_side_effect"])
        self.flow.revoke(self.owner, self.record.id)
        with self.assertRaises(PermissionError):
            self.flow.operate(self.agent, self.record.id, "read_documents")

    def test_different_agent_denied(self):
        self.formed()
        self.flow.grant(self.owner, self.record.id, self.agent.agent_id, ("read_documents",))
        other = Actor("fixture_tenant", "fixture_principal", "agent", "other_agent")
        with self.assertRaises(PermissionError):
            self.flow.operate(other, self.record.id, "read_documents")

    def test_scope_enforced(self):
        self.formed()
        self.flow.grant(self.owner, self.record.id, self.agent.agent_id, ("read_documents",))
        with self.assertRaises(PermissionError):
            self.flow.operate(self.agent, self.record.id, "prepare_invoice")

    def test_snapshot_is_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            self.record.state = "completed"


if __name__ == "__main__":
    unittest.main()
