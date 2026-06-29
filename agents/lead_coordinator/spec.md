# Lead Coordinator — Agent Spec
Department: Front Office  |  Plans: Growth, Pro

## Role
Replies to every form inquiry in under 5 minutes. Speed wins the job.

## Trigger
Form submission webhook from client site /api/leads

## Inputs
- lead name
- phone
- service requested
- message
- source URL

## Outputs
- SMS to lead within 5 min
- notification to contractor
- lead record

## Tools Required
- Twilio SMS
- OpenAI GPT-4o
- CRM write

## Success Metric
100% of leads receive first contact within 5 minutes

## Stack Note
Webhook → Celery → OpenAI personalize → Twilio send → DB log

## System Prompt
```
Lead coordinator for a home service business. A customer just submitted a web form. Write a warm SMS reply that acknowledges their request and asks one qualifying question. Under 160 characters.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
