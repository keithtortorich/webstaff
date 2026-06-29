# WebStaff Agents

9 AI employees, each with a single job. No agent framework — direct OpenAI calls via Celery tasks.

## Architecture decision

The CrewAI prototype (see commit history) was ported to a simpler stack:

| CrewAI prototype | This implementation |
|---|---|
| `Agent(role, goal, backstory)` | `AGENTS[slug]["system"]` prompt constant |
| `Task(description, agent)` | `call_agent(slug, message, context)` |
| `Crew(agents, tasks, process="sequential")` | `lead_to_booked_workflow()` — plain Python |
| `crew.kickoff()` | `workflow(lead_data)` → dict |
| LangChain + CrewAI deps | `openai` SDK only |
| No real tool execution | Celery tasks call Twilio / GBP API / SendGrid directly |

**Why:** Every agent needs real tool calls (Twilio SMS, GBP API, SendGrid). CrewAI wraps LLM text — it can't send a text message or post to Google Business. The simple stack is also fully auditable: every agent call is logged with agent slug, model, and token count.

## Files

```
agents/
├── README.md                      ← you are here
├── workflows.py                   ← all agent definitions + workflow functions
├── receptionist/
│   ├── spec.md                    ← trigger, inputs, outputs, tools, metric
│   └── handler.py                 ← Celery task skeleton (calls workflows.call_agent)
├── lead_coordinator/
├── reputation_manager/
├── marketing_coordinator/
├── growth_manager/
├── website_ops/
├── sales_consultant/
├── service_advisor/
└── front_office_manager/
```

## Usage

```python
from agents.workflows import call_agent, lead_to_booked_workflow, route_event

# Single agent call
sms = call_agent("lead_coordinator", "Draft follow-up for John at (602) 555-0100")

# Full workflow (synchronous — use Celery .delay() in production)
result = lead_to_booked_workflow({
    "name": "John",
    "issue": "Emergency plumbing",
    "city": "Phoenix",
    "phone": "(602) 555-0100",
})

# Route any event
routing = route_event({"type": "inbound_call", "caller": "+16025550100"})
# → {"event_type": "inbound_call", "agent": "receptionist", "priority": "high", ...}
```

## Model routing

| Agent | Model | Reason |
|---|---|---|
| Receptionist | gpt-4o-mini | High volume, routine qualification |
| Lead Coordinator | gpt-4o-mini | Short SMS, low complexity |
| Reputation Manager | gpt-4o-mini | Templated review request |
| Marketing Coordinator | gpt-4o-mini | Short social posts |
| Website Ops | gpt-4o-mini | Health summary, structured output |
| Service Advisor | gpt-4o-mini | Structured Q&A, low stakes |
| Growth Manager | gpt-4o | SEO copy requires nuance |
| Sales Consultant | gpt-4o | High-value follow-up, judgment needed |
| Front Office Manager | gpt-4o | Routing decisions must be reliable |

## Next: wire Celery

Each `handler.py` is a Celery task stub. To go live:
1. Set `OPENAI_API_KEY`, `TWILIO_SID`, `TWILIO_AUTH`, `REDIS_URL` in env
2. `pip install celery redis openai twilio`
3. Replace `raise NotImplementedError` in each handler with `call_agent(...)` + tool call
4. Run: `celery -A api.build worker --loglevel=info`
