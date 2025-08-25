Title: Tracking AI Model Deprecations with Git Scraping: Introducing deprecations.info
Date: 2024-08-24 14:00
Category: data-engineering
Tags: git-scraper, rss, automation, ai, monitoring
Slug: deprecations-info-git-scraper
Author: François Leblanc
Summary: How I built deprecations.info using Simon Willison's git scraper pattern to track AI model shutdowns and prevent service disruptions

If you've ever had your AI application break because a model was suddenly
deprecated, you know the pain. OpenAI very famously sunset GPT-4o from ChatGPT
when they first launched GPT-5. Anthropic retired `claude-3-opus`. Google
deprecated `gemini-1.0-pro-vision`. These deprecations happen regularly,
sometimes with just a few months notice, and keeping track of them across
multiple providers is a manual, error-prone process.

That's why I built [deprecations.info](https://deprecations.info) – an
automated service that monitors AI model deprecation announcements from OpenAI,
Anthropic, Google Vertex AI, AWS Bedrock, and Cohere, delivering them as an RSS
feed you can consume programmatically.

It doesn't mean we'll catch every single deprecation (sometimes they just
happen without notice), but it gives you a fighting chance to stay ahead of
changes and avoid unexpected service disruptions.

## The Git Scraper Pattern

The project uses what Simon Willison calls the ["git scraper"
pattern](https://simonwillison.net/2020/Oct/9/git-scraping/). The concept is
elegantly simple: use Git's version control as a time-series database for
tracking changes to data over time.

Here's how it works:

1. A scheduled GitHub Action runs periodically (daily in this case)
2. It fetches deprecation pages from various AI providers
3. Parses the content and extracts deprecation announcements
4. Commits any changes to a `data.json` file
5. Git automatically tracks what changed and when

The beauty of this approach is that Git gives you a complete history of changes
for free. You can see exactly when a deprecation was announced, track how
notices evolve over time, and even roll back if something goes wrong. The
entire "database" is just a JSON file in a Git repository.

## Programmatic Use Cases

While you can subscribe to the RSS feed in any feed reader, the real power
comes from automation. Here are some practical implementations:

### Automatic GitHub Issue Creation

```python
import feedparser
from github import Github

feed = feedparser.parse('https://leblancfg.com/deprecations-rss/rss/v1/feed.xml')
g = Github(os.environ['GITHUB_TOKEN'])
repo = g.get_repo('your-org/your-repo')

for entry in feed.entries:
    if 'gpt-4' in entry.title.lower():  # Filter for relevant models
        repo.create_issue(
            title=f"Model Deprecation Alert: {entry.title}",
            body=f"{entry.summary}\n\nSource: {entry.link}",
            labels=['deprecation', 'urgent']
        )
```

### Slack Notifications via Webhook

```typescript
import Parser from 'rss-parser';
import axios from 'axios';

const parser = new Parser();
const feed = await parser.parseURL('https://leblancfg.com/deprecations-rss/rss/v1/feed.xml');

for (const item of feed.items) {
    await axios.post(process.env.SLACK_WEBHOOK_URL, {
        text: `⚠️ AI Model Deprecation: ${item.title}`,
        blocks: [{
            type: 'section',
            text: {
                type: 'mrkdwn',
                text: `*${item.title}*\n${item.contentSnippet}\n<${item.link}|View Details>`
            }
        }]
    });
}
```

### Infrastructure as Code Updates

You could even automate updates to your infrastructure definitions:

```bash
#!/bin/bash
# Check for deprecated models in your Terraform configs
deprecated_models=$(curl -s https://leblancfg.com/deprecations-rss/rss/v1/feed.xml | \
    grep -oP '(?<=<title>)[^<]+' | \
    grep -oP 'gpt-[0-9.]+-[0-9]+|claude-[a-z-]+[0-9.]+')

for model in $deprecated_models; do
    if grep -r "$model" ./terraform/; then
        echo "WARNING: Deprecated model $model found in Terraform configs"
        # Could trigger a CI pipeline to update to newer models
    fi
done
```

### Dependency Scanning

Integrate deprecation checking into your CI/CD pipeline to catch issues before they reach production:

```python
import json
import sys
import requests

# Fetch current deprecations
deprecations = requests.get('https://raw.githubusercontent.com/leblancfg/deprecations-rss/main/data.json').json()

# Check your config
with open('config.json') as f:
    config = json.load(f)
    
for deprecated_model in deprecations['models']:
    if deprecated_model['name'] in config.get('ai_models', []):
        print(f"ERROR: Using deprecated model {deprecated_model['name']}")
        print(f"Deprecation date: {deprecated_model['date']}")
        sys.exit(1)
```

## Beyond Basic Notifications

The git scraper pattern enables some interesting advanced use cases:

**Historical Analysis**: Since every change is tracked in Git, you can analyze
deprecation patterns. How much notice do providers typically give? Are
deprecations becoming more frequent?

**Compliance Auditing**: For regulated industries, having a Git history of when
you became aware of deprecations could be valuable for compliance
documentation.

**Proactive Migration**: By parsing deprecation dates from the feed, you could
automatically create Jira tickets or GitHub issues with appropriate deadlines
based on the sunset date.

**Multi-Environment Validation**: Check all your environments (dev, staging,
production) for deprecated model usage and generate a migration report.

## Implementation Details

The service is built with Python and uses GitHub Actions for scheduling. The
scraper ([view on GitHub](https://github.com/leblancfg/deprecations-rss)) runs
daily, checking each provider's deprecation page for changes. When new
deprecations are detected, they're added to the data store and the RSS feed is
regenerated.

The RSS feed format was chosen deliberately – it's a battle-tested standard
that integrates with hundreds of existing tools and services. You can consume
it with Zapier, IFTTT, Microsoft Power Automate, or any programming language
with an RSS library.

## Getting Started

The simplest way to start is to subscribe to the RSS feed at
`https://leblancfg.com/deprecations-rss/rss/v1/feed.xml`. But I encourage you
to think beyond basic subscriptions. Consider:

- What would break in your system if a model was deprecated?
- How much lead time do you need for migrations?
- Who needs to be notified when deprecations are announced?

Then build automation around those requirements. The feed is there, ready to be
consumed programmatically.

## Looking Forward

The git scraper pattern has proven to be remarkably robust for this use case.
The combination of Git's versioning, GitHub's infrastructure, and RSS's
universality creates a system that's both simple and powerful.

As AI providers continue to iterate rapidly on their models, having automated
deprecation tracking becomes less of a nice-to-have and more of a necessity.
Whether you're managing a single application or an entire fleet of AI-powered
services, knowing about deprecations early – and programmatically – can save
you from unexpected outages and frantic late-night debugging sessions.

The project is open source and contributions are welcome. If there's a provider
you'd like to see added or a notification method you need, feel free to open an
issue or submit a pull request.

Remember: the best time to find out about a deprecation is months before it
happens, not minutes after your service goes down.
