# Reddit Aww Viewer

A small project that fetches the latest posts from the popular Reddit subreddit **r/aww** and displays them in a simple frontend built with Astro. 

## Features
- Fetches the 100 newest posts from r/aww using Reddit’s public API.
- Filters posts to only include those created in the last hour.
- Stores posts in a local SQLite database, avoiding duplicates.
- Displays posts with titles, thumbnails, text, and links.
- Easy-to-extend backend in Python for future automation or API endpoints.

## Tech Stack
- **Backend:** Python 3, requests, SQLite
- **Frontend:** Astro, Tailwind CSS
- **Database:** SQLite

## Goals
- Practice API integration, data filtering, and storage.
- Experiment with frontend display of dynamic content.
- Learn scheduling and automation for periodic updates.
