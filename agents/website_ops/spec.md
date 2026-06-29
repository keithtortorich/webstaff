# Website Operations Manager — Agent Spec
Department: Operations  |  Plans: Essentials, Growth, Pro

## Role
Monitors uptime, keeps the site live, secure, and current. Hands-free.

## Trigger
5-minute uptime ping + weekly content review

## Inputs
- site URL
- uptime status
- PageSpeed score
- content freshness date

## Outputs
- downtime alert SMS within 5 min
- monthly health report

## Tools Required
- UptimeRobot API
- Google PageSpeed API
- Netlify API
- Twilio SMS

## Success Metric
99.9% uptime; PageSpeed mobile > 80; alert within 5 min of downtime

## Stack Note
Celery beat every 5min → UptimeRobot check → alert if down; weekly PageSpeed batch

## System Prompt
```
Reviewing a contractor website monthly health metrics. Write a plain-English 3-4 sentence summary for the business owner: uptime, speed, issues, what was fixed.
```

## Implementation Checklist
- [ ] Webhook / trigger endpoint
- [ ] Celery task skeleton
- [ ] OpenAI integration
- [ ] Tool API connections
- [ ] Logging + error handling
- [ ] Unit tests
- [ ] Deployed to production
