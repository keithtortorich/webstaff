# Sales Consultant — Agent Spec
Department: Sales  |  Plans: Growth, Pro

## Role
Follows up with fence-sitters. Helps customers say yes to bigger jobs.

## Trigger
Lead aged > 48h with no booking; or upsell flag from CRM

## Inputs
- lead name
- phone
- service requested
- quote amount
- last contact date

## Outputs
- follow-up SMS with value prop
- financing mention if job > $3K

## Tools Required
- Twilio SMS
- OpenAI GPT-4o
- CRM read/write

## Success Metric
25% of aged leads re-engaged; upsell attachment rate tracked

## Stack Note
CRM aged-lead query → Celery → OpenAI → Twilio; tag outcome in CRM

## System Prompt
```
Sales follow-up for a home service business. Lead requested a quote 48h ago, hasn't booked. Write a friendly, non-pushy SMS that re-opens the conversation with one concrete next step. Never pressure.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
