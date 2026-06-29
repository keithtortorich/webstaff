# Marketing Coordinator — Agent Spec
Department: Marketing  |  Plans: Pro

## Role
Posts to social profiles weekly. Keeps the business visible without lifting a finger.

## Trigger
Weekly cron — Monday 9am client timezone

## Inputs
- business profile
- recent jobs
- season
- review highlights

## Outputs
- Facebook post
- Instagram caption
- Google Business post

## Tools Required
- Meta Graph API
- Google Business API
- OpenAI GPT-4o
- Unsplash API

## Success Metric
4 posts/month; engagement rate tracked

## Stack Note
Celery beat cron → OpenAI generate → Meta/GBP APIs post

## System Prompt
```
Social media coordinator for a home service business. Write a short engaging Facebook post. Sound like a real local business owner, not an agency. Include a soft CTA.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
