---
title: Build log
---

# Build log — all posts

Every post on the development blog, newest first.

{% for post in site.posts %}
- {{ post.date | date: "%Y-%m-%d" }} — [{{ post.title }}]({{ post.url | relative_url }})
{% endfor %}

Subscribe via the [RSS feed]({{ 'feed.xml' | relative_url }}).

The terse workshop journal — shorter notes, no pictures — lives in
[`log.md`](https://github.com/jmcpheron/vault-study/blob/main/log.md)
in the repo root.
