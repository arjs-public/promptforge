"""Utilities for assembling crafted prompt content."""


def assemble_craft(data: dict) -> str:
    # Build a C.R.A.F.T. oriented prompt text
    t = data.get("title","").strip()
    ctx = data.get("context","").strip()
    role = data.get("ai_role","").strip()
    add = data.get("additional_info","").strip()
    fmt = data.get("output_format","").strip()
    aud = data.get("target_audience","").strip()
    # If all fields are empty, return an empty string
    if not any((t, ctx, role, add, fmt, aud)):
        return ""

    parts = []
    parts.append(f"Title:\n  {t}\n")
    parts.append(f"Context:\n  {ctx}\n")
    parts.append(f"Role (AI):\n  You are {role}. Your tone and constraints: be concise, factual, and explain assumptions.\n")
    parts.append(f"Additional Information:\n  {add}\n")
    parts.append(f"Format:\n  {fmt}\n")
    parts.append(f"Target Audience:\n  {aud}\n")
    parts.append("Goal:\n Compose a high-quality and perfect prompt that, when given to a chatbot or an coding agent bot, will produce extremely useful and accurate outputs for the target audience. Always think and plan before you generate answer. If possible run the answer through your review process and see if it fits the requirements.\n")
    return "\n".join(parts)

