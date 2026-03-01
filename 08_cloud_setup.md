# Cloud Deployment Setup

After successful local testing, the system will be deployed to the cloud for continuous, automated execution.

## Purpose of Cloud Deployment
- Run even when laptop is turned off
- Automatic posting without manual login
- 24/7 availability
- Reliable scheduling (2 posts/day)

## Cloud Provider (Planned)
- Entry-level VM (DigitalOcean / AWS Lightsail / similar)
- Linux (Ubuntu)
- Docker-based deployment

## Minimum Server Requirements
- 1 vCPU
- 2 GB RAM
- 40–50 GB storage
- Docker installed

## Estimated Monthly Cost
- Cloud VM: ₹500 – ₹800
- Storage: Included
- Bandwidth: Minimal (short videos)

## Deployment Flow
1. Create cloud VM
2. Install Docker & Docker Compose
3. Pull project repository
4. Add environment variables (.env)
5. Start services using Docker
6. Enable scheduler (cron)

## Scheduling
- Morning post: Automated
- Evening post: Automated
- No human intervention required

## Scalability
- Upgrade RAM/CPU as needed
- Add more agents or platforms easily

## Outcome
Once deployed, the system runs fully automated and publishes content daily without dependency on local machine.