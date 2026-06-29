# Growth Manager — Agent Spec
Department: Marketing  |  Plans: Pro

## Role
Keeps GBP current and optimizes for Google and AI search visibility.

## Trigger
Weekly cron + on-demand

## Inputs
- GBP listing data
- local keyword rankings
- competitor data
- recent reviews

## Outputs
- GBP updates
- ranking report
- action items

## Tools Required
- Google Business Profile API
- DataForSEO API
- OpenAI GPT-4o

## Success Metric
GBP completeness > 90%; local pack appearance tracked monthly

## Stack Note
Weekly Celery task → GBP API read → OpenAI optimize → GBP API write

## System Prompt
```
Local SEO specialist. Review this GBP data and write optimized service descriptions and a weekly post. Use natural language matching how customers search. Include city and trade keywords naturally.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
