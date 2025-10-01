import os
import pytest
import asyncio
from dotenv import load_dotenv

from app.genai.clients.gemini_client import GeminiClient


def test_gemini_client_generate_exam_smoke():
    load_dotenv('.env')

    async def run():
        client = GeminiClient()
        if not client.is_configured():
            pytest.skip("GEMINI not configured")

        prompt = (
            "Create 1 multiple-choice question about basic biology. "
            "Return ONLY a JSON array with objects having keys: "
            "question_text, options, correct_answer, explanation."
        )
        res = await client.generate_exam(prompt, temperature=0.0, max_tokens=300)
        print("[GEMINI] success:", res.get('success'))
        print("[GEMINI] metadata:", res.get('metadata'))
        assert res.get('success') is True
        questions = res.get('questions', [])
        assert isinstance(questions, list) and len(questions) >= 1
        q0 = questions[0]
        print("[GEMINI] first_question:", q0)
        for k in ['question_text', 'options', 'correct_answer']:
            assert k in q0

    asyncio.run(run())


