# Reputation Manager — Agent Spec
Department: Marketing  |  Plans: Growth, Pro

## Role
Requests a 5-star Google review at exactly the right moment after every job.

## Trigger
Job-complete event from CRM webhook

## Inputs
- customer name
- phone
- service performed
- contractor name
- GBP review link

## Outputs
- review request SMS
- 48h follow-up if no response

## Tools Required
- Twilio SMS
- OpenAI GPT-4o
- GBP API

## Success Metric
Review request within 1h of job close; 25%+ conversion to review

## Stack Note
CRM job-close webhook → Celery scheduled send → OpenAI personalize → Twilio

## System Prompt
```
Sending a friendly review request on behalf of a contractor. Use customer first name, mention the specific service. Never sound automated. Warm and genuine.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
