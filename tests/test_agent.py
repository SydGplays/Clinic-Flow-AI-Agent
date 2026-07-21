"""Pruebas de los controles deterministas de ClinicFlow."""

import unittest

from src.agent import ClinicAgent


class FakeRetriever:
    def __init__(self, sources=None):
        self.sources = sources or []

    def search(self, query, top_k=4):
        return self.sources


class ClinicAgentSafetyTests(unittest.TestCase):
    def test_rejects_empty_question(self):
        agent = ClinicAgent(FakeRetriever(), api_key="test")
        with self.assertRaises(ValueError):
            agent.answer("   ")

    def test_emergency_bypasses_provider(self):
        agent = ClinicAgent(FakeRetriever(), api_key=None)
        result = agent.answer("Tengo dolor intenso en el pecho")
        self.assertIn("emergencia", result["answer"].lower())
        self.assertEqual(result["sources"], [])

    def test_out_of_scope_uses_safe_fallback(self):
        agent = ClinicAgent(FakeRetriever(), api_key=None)
        result = agent.answer("¿Cuál es la capital de Japón?")
        self.assertIn("no encontré información suficiente", result["answer"].lower())
        self.assertEqual(result["sources"], [])

    def test_missing_key_is_reported_for_relevant_question(self):
        sources = [{"title": "Citas", "content": "Información", "category": "Citas", "source": "FAQ", "score": 0.8}]
        agent = ClinicAgent(FakeRetriever(sources), api_key=None)
        with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
            agent.answer("¿Cómo solicito una cita?")


if __name__ == "__main__":
    unittest.main()