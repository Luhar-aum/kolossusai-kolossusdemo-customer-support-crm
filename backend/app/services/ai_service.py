"""
AI service with provider abstraction (Anthropic/OpenAI/mock).
All AI-generated content is clearly labeled and requires human approval before sending.
"""
import random
from typing import Optional, List
from app.core.config import settings


async def qualify_lead(lead) -> dict:
    """Score and classify a lead. Returns structured AI output."""
    if settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _qualify_anthropic(lead)
    elif settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return await _qualify_openai(lead)
    return _qualify_mock(lead)


def _qualify_mock(lead) -> dict:
    score = random.randint(30, 90)
    if score >= 70:
        classification = "hot"
    elif score >= 45:
        classification = "warm"
    else:
        classification = "cold"
    return {
        "score": score,
        "classification": classification,
        "intent": "medium_purchase_intent",
        "reasoning": [
            f"Lead industry: {lead.industry or 'unknown'}",
            "Company profile matches target segment",
            "Contact information is complete",
        ],
        "recommended_action": "Schedule an introductory call",
        "confidence": round(random.uniform(0.6, 0.95), 2),
        "model_name": "mock",
    }


async def _qualify_anthropic(lead) -> dict:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        prompt = f"""Analyze this sales lead and return a JSON object:
Name: {lead.name}
Email: {lead.email}
Company: {lead.company}
Industry: {lead.industry}
Job Title: {lead.job_title}
Country: {lead.country}
Notes: {lead.notes}

Return JSON: {{"score": 0-100, "classification": "hot|warm|cold", "intent": "string", "reasoning": ["..."], "recommended_action": "string", "confidence": 0-1}}"""
        message = client.messages.create(
            model="claude-haiku-5-5",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        import json, re
        text = message.content[0].text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = json.loads(match.group())
            result["model_name"] = "claude-haiku-5-5"
            return result
    except Exception:
        pass
    return _qualify_mock(lead)


async def _qualify_openai(lead) -> dict:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = f"Analyze lead: {lead.name}, {lead.company}, {lead.industry}. Return JSON with score(0-100), classification(hot/warm/cold), intent, reasoning array, recommended_action, confidence."
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        import json
        result = json.loads(resp.choices[0].message.content)
        result["model_name"] = "gpt-4o-mini"
        return result
    except Exception:
        pass
    return _qualify_mock(lead)


async def suggest_reply(conversation, messages: list) -> str:
    context = "\n".join([f"{m.sender_type}: {m.body}" for m in messages[-5:]])
    if settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model="claude-haiku-5-5",
                max_tokens=256,
                messages=[{"role": "user", "content": f"Suggest a professional reply for this customer conversation:\n{context}\n\nReply as a support agent:"}]
            )
            return msg.content[0].text
        except Exception:
            pass
    return f"Thank you for reaching out. I've reviewed your message and will get back to you shortly with a detailed response.\n\n[AI-GENERATED — Requires human approval before sending]"


async def summarize_conversation(messages: list) -> str:
    if not messages:
        return "No messages to summarize."
    context = "\n".join([f"{m.sender_type}: {m.body}" for m in messages])
    if settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model="claude-haiku-5-5",
                max_tokens=256,
                messages=[{"role": "user", "content": f"Summarize this customer support conversation in 2-3 sentences:\n{context}"}]
            )
            return msg.content[0].text
        except Exception:
            pass
    return f"[AI Summary] Conversation with {len(messages)} messages covering customer inquiry. Key topics discussed and resolution status tracked. [AI-GENERATED]"
