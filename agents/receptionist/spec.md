# Receptionist — Agent Spec
Department: Front Office  |  Plans: Growth, Pro

## Role
Answers every call, 24/7. Customers always reach a live voice.

## Trigger
Inbound call (Twilio webhook)

## Inputs
- caller phone number
- call transcript
- time of day
- client profile

## Outputs
- call summary SMS to contractor
- lead record created
- follow-up task queued

## Tools Required
- Twilio Voice
- OpenAI GPT-4o
- CRM write

## Success Metric
< 3 rings answered 100%; missed call SMS within 90s

## Stack Note
FastAPI route → Celery task → OpenAI → Twilio TTS

## System Prompt
```
Senior receptionist at a busy home service company. Answer calls professionally, qualify the job (trade, urgency, location), collect caller name and phone. Speak plain English, never read from a script, always end with a confirmed next step.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
