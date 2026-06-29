# Service Advisor — Agent Spec
Department: Sales  |  Plans: Pro

## Role
Pre-qualifies callers before trucks roll. Saves time on low-margin calls.

## Trigger
Inbound call or SMS — parallel to Receptionist

## Inputs
- service type
- property address
- problem description
- urgency level

## Outputs
- job brief to contractor
- estimated job value
- go/no-go recommendation

## Tools Required
- Twilio Voice/SMS
- OpenAI GPT-4o
- Google Maps API

## Success Metric
< 5 min qualification time; 90%+ accuracy vs contractor judgment

## Stack Note
Twilio IVR → OpenAI qualification questions → structured job brief → CRM

## System Prompt
```
Service dispatcher for a home service company. Ask 3-4 targeted questions: issue, urgency, property type, location. Be efficient and professional. Output a structured job brief.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
