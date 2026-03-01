# Workflow & Execution Flow

This document explains **how the AI Content Factory runs step-by-step**, from idea discovery to content publishing.

The workflow is designed to be **fully automated**, **cost-efficient**, and **fault-tolerant**.

## Daily Execution Schedule

The system runs **twice per day**:
- Morning post
- Evening post

Each run follows the same execution pipeline.


## Step-by-Step Workflow

### 1️ Trigger & Initialization
- Scheduler Agent triggers the workflow
- Manager Agent initializes the pipeline
- Execution context (date, platform, time) is set


### 2️ Trend Discovery
- Trend Hunter Agent collects trending topics
- Content Strategist Agent validates relevance
- One topic is finalized for content creation



### 3️ Script Creation
- Script Writer Agent generates a short-form script
- Focus on strong hook + concise message
- Script length optimized for Shorts/Reels


### 4️ Voice Generation
- Voice Agent converts script to speech
- Audio file is generated and validated
- Output stored for video processing


### 5️ Visual Selection
- Visual Agent selects background media
- Content matched with script context
- Assets prepared for assembly


### 6️ Video Assembly
- Video Agent combines:
  - Voice
  - Visuals
  - Captions
- Final video rendered in platform-supported format


### 7️ Caption & SEO Optimization
- SEO Agent generates:
  - Caption text
  - Hashtags
  - Metadata
- Platform-specific optimization applied


### 8️ Content Upload
- Upload Agent posts content to platforms
- Captions and hashtags attached
- Upload confirmation received


### 9️ Performance Tracking
- Performance Agent collects engagement metrics
- Data stored for future analysis
- Metrics include views, likes, and comments


### 10 learning agent
- Learning Agent analyzes performance data
- Insights shared with:
  - Content Strategist Agent
  - Script Writer Agent
- Future content quality improves automatically

---

## Failure Handling Strategy

- Each agent works independently
- If one agent fails:
  - Manager Agent retries or skips gracefully
- Partial failures do not stop the entire pipeline

---

## Benefits of This Workflow

- Fully automated execution
- Minimal manual intervention
- Scalable and modular design
- Easy debugging and improvements
- Cost-controlled API usage

---

## Summary

This workflow ensures that content creation, publishing, and learning happen **consistently, reliably, and at scale** without daily human involvement.