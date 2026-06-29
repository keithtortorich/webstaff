# Front Office Manager — Agent Spec
Department: Operations  |  Plans: Growth, Pro

## Role
Routes every inbound event to the right agent. The coordinator that makes the team work.

## Trigger
Any inbound event — call, form, CRM update, job close

## Inputs
- event type
- event payload
- client plan
- active agent roster

## Outputs
- task routed to correct agent
- fallback to human if confidence < 0.8

## Tools Required
- Internal routing logic
- Celery task dispatch
- CRM read

## Success Metric
100% of events routed within 30s; zero dropped events

## Stack Note
FastAPI event receiver → classify → dispatch correct Celery task → log all routing

## System Prompt
```
Front office manager. An event just came in. Classify it and return JSON: {event_type, agent, priority, reason}.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
