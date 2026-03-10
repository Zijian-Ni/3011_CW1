# Generative AI Usage Declaration
**COMP3011 Coursework 1 — SportsPulse**  
**Student:** Zijian Ni | **Date:** March 2026

---

## Declaration

I declare that I have used Generative AI tools in the development of this coursework as described below. All AI-assisted content has been reviewed, verified, and adapted by me. I take full responsibility for all submitted work.

Non-declared use of GenAI would constitute academic misconduct. This declaration is submitted in accordance with the COMP3011 GREEN classification for GenAI usage.

---

## Tools Used

| Tool | Provider | Version | Access Method |
|---|---|---|---|
| Claude (Sonnet 4.6) | Anthropic | claude-sonnet-4-6 | OpenClaw personal assistant |
| GitHub Copilot | GitHub/OpenAI | GPT-4o | VS Code extension |

---

## Usage Log

### Phase 1 — Architecture and Stack Selection

**Prompt type:** Conceptual exploration  
**AI tool:** Claude  
**Description:** Used AI to discuss and compare architectural patterns for the API:
- DRF ViewSet vs APIView vs GenericAPIView trade-offs
- Whether to use a service layer vs. embedding logic in views
- Token auth vs JWT for a coursework-scale project

**Outcome:** Decided on ViewSet + service layer architecture. The service layer in `api/services.py` was a direct outcome of this exploration.

**Assessment level:** High-level (understanding technology and new concepts) → 70–79 band

---

### Phase 2 — Code Generation (Serialisers and Validators)

**Prompt type:** Code generation with review  
**AI tool:** Claude + GitHub Copilot  
**Description:** AI generated initial boilerplate for:
- Serialiser field definitions in `api/serializers.py`
- Validator logic skeleton in `api/validators.py`
- Seed data management command structure in `api/management/commands/seed_data.py`

**Developer action:** All generated code was manually reviewed, tested, and modified. The season format validator (`YYYY/YYYY` with sequential year check) was a custom requirement added by the developer.

**Assessment level:** Medium-level (code generation with developer oversight) → 60–79 band

---

### Phase 3 — Analytics Query Development

**Prompt type:** Debugging and optimisation  
**AI tool:** Claude  
**Description:** Complex Django ORM queries for analytics (leaderboard, head-to-head) were initially drafted with AI assistance. Multiple iterations were required to correct semantic errors in the football domain context.

**Example:** Initial AI-generated leaderboard query used `values('player')` without proper join to player name. Developer identified and corrected this to use `select_related` and annotation.

**Assessment level:** High-level (creative thinking and exploration of alternatives) → 80–89 band

---

### Phase 4 — Test Case Design

**Prompt type:** Brainstorming and edge case discovery  
**AI tool:** Claude  
**Description:** Used AI to identify test categories and edge cases:
- Boundary conditions for season format validation
- Auth boundary testing (unauthenticated write, authenticated write)
- Throttle behaviour in test isolation

All 79 test cases were individually implemented and verified by the developer.

**Assessment level:** Medium-level → 70–79 band

---

### Phase 5 — Deployment Debugging

**Prompt type:** Error diagnosis  
**AI tool:** Claude  
**Description:** When deploying to PythonAnywhere, encountered:
- `ImproperlyConfigured: api has multiple filesystem locations`
- `DisallowedHost: Invalid HTTP_HOST`

AI diagnosed the root causes and suggested fixes. Developer applied and verified solutions.

**Assessment level:** Low-level (debugging) → 50–59 band

---

### Phase 6 — Documentation and Report Writing

**Prompt type:** Content generation with review  
**AI tool:** Claude  
**Description:** AI assisted in:
- Drafting `@extend_schema` docstrings for OpenAPI documentation
- Structuring this technical report
- Writing deployment instructions in README

All content was reviewed for accuracy against the actual implementation.

**Assessment level:** Medium to high-level → 70–89 band

---

## Overall Assessment of GenAI Usage

The use of AI in this project spans from low-level (debugging) to high-level (architecture exploration and creative problem-solving). The most impactful uses were in **architectural decision-making** and **analytics query design**, where AI helped explore alternatives that directly shaped the final system design.

This usage profile aligns with the **80–89 (Excellent)** band: *"High level — creative thinking and solution exploration."*

---

## Conversation Log Excerpts

*[Attach exported conversation logs as a supplementary PDF. Include at minimum:]*
1. *Architecture discussion — service layer decision*
2. *Analytics ORM query iteration*
3. *PythonAnywhere deployment debugging*

---

*Supplementary conversation logs are included as `docs/genai_conversation_logs.pdf`*
