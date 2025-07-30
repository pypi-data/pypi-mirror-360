![logo](https://github.com/user-attachments/assets/5a0dc36c-1b62-40ba-b740-fe3b941b67fa)
openwrite is a minimalist blogging platform built for writing freely, hosting independently, and publishing without noise.

[![version](https://img.shields.io/badge/version-0.10.0-purple)](CHANGELOG.md)
[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL--3.0--or--later-blue.svg)](LICENSE)
![pythonver](https://img.shields.io/badge/python%20version-3.11-blue)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/openwriteio/openwrite/python-tests.yml)

---

## Features

- Multiple blogs per user(limit defined in .env)
- Single-blog mode
- Supports sqlite and mysql databases
- Upload images to local storage or bunny cdn
- Simple markdown editor in posting
- Discover section
- Privacy: 
    - Set if blog should be indexed in search engines
    - Set if post should be listed in "Discover" section
    - Set if username should appear in post page (anonymous posts)
- Lightweight
- No tracking, only data collected is anonymized(hashed) IP for post view counting and likes
- Custom CSS per blog
- Federation using ActivityPub protocol: Follow and Like
- Likes system
- Posts importing from xml/csv
- Blog themes
- Gemini protocol
- Statistics per post


