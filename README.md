# Sith Synth

It's an application that allows users to configure certain parameters from an input panel 
which are used as inputs into to a selected model (LSTM or Transformer). These models then run 
inference on the values to produce a MIDI file and an XML file which can be visualized and played.

For backend server
```commandline
conda create -n kyloren python=3.9
conda activate kyloren
pip install -r requirements_solved.txt
```

To run backend server:
```commandline
python run.py
```

To run the frontend server in dev mode:
```commandline
npm run dev
```

---

Roadmap:
* Delete to-delete directory
* Fix UI bug for displaying sheet music
* Create a method to allow multiple generations at the same time
* Implement asyncio code in server

---

Here’s a high-level roadmap to turn your current FastAPI + Svelte app into a production-ready service. I’ve broken it into phases—feel free to adjust priorities based on your needs and team size.

1. Core Stability & Quality
    • Input validation & error handling
   – Use Pydantic request models instead of raw Body(...), so FastAPI will auto-validate types, ranges, required fields.
   – Return structured JSON errors for downstream clients.
    • Logging & Monitoring
   – Integrate structured logging (e.g. Python’s `logging` + JSON formatter).
   – Add request/response middleware to log request IDs, timings and error traces.
   – Hook up metrics (Prometheus) and an APM (e.g. Sentry) for exception capture.
    • Automated Testing
   – Unit tests for your lead-sheet generation logic (models.py, utils.py).
   – FastAPI integration tests (via `TestClient`) for your `/generate`, `/xml`, `/midi` endpoints.
   – Front-end component tests (Vitest/Svelte Testing Library).
   – End-to-end smoke tests (Playwright or Cypress) that “click Generate → see sheet → hear music.”
2. Security & Configuration
    • Secrets & Env management
   – Move all secrets (if any) into environment variables or a secrets manager.
   – Use `python-dotenv` only in dev; never commit `.env` to Git.
    • CORS & Auth
   – Lock down `allow_origins` to your front-end domain in prod.
   – If you need user-specific generation, layer on an authentication scheme (JWT or OAuth).
    • Rate-limiting & Abuse Protection
   – Add simple throttling (e.g. FastAPI-Limiter backed by Redis) to prevent spamming heavy generate calls.
3. Packaging & Deployment
    • Containerization
   – Create multi-stage Dockerfiles for both backend and front-end.
   – Bake in health-check and minimal production Python image (e.g. python:3.11-slim).
    • CI/CD
   – GitHub Actions (or GitLab CI) pipelines to:


    1. run lint, tests, type-checks

    2. build Docker images, push to registry

    3. deploy to staging/production (e.g. via Kubernetes/ECS/EKS, or serverless containers).
           • Static Front-End Hosting
          – Build your Svelte UI with `npm run build` and deploy to a CDN (Netlify, Vercel, S3+CloudFront).
          – Ensure environment variables are injected at build or via runtime config.
4. Scalability & Reliability
    • Asynchronous Generation
   – Offload the heavy music-gen call into a task queue (Celery/RQ) so your API can respond immediately with a job ID.
   – Front-end polls a “/status/{job_id}” endpoint, then fetches `/xml` + `/midi` when ready.
    • Artifact Storage
   – Instead of local `app/generations`, upload results to an object store (S3 or MinIO) and serve via signed URLs.
    • Horizontal Scaling
   – If using Docker/K8s, ensure workers are stateless and can spin up/down.
   – Use a shared Redis or database for queues, rate-limits, and session state.
5. UX, Accessibility & Optimization
    • Front-end Performance
   – Code-split your Svelte pages; lazy-load OSMD and Tone.js only when needed.
   – Optimize assets (minify, gzip/Brotli).
    • Accessibility
   – Sweep with axe or WAVE to catch a11y issues (ARIA labels, focus management, keyboard nav).
    • Responsiveness & Localization
   – Ensure the UI works across mobile + desktop; adopt i18n if you plan multilingual support.
6. Documentation & Onboarding
    • API Docs & Example Clients
   – FastAPI gives you Swagger/OpenAPI out of the box. Publish your OpenAPI spec.
   – Provide a short Python or JS snippet showing “how to call `/generate` and fetch the files.”
    • Developer Guides
   – Document how to run locally, run tests, build, and deploy.
   – Add CONTRIBUTING.md, CODE_OF_CONDUCT.md if open source.

Once you’ve worked through Core Stability and Security, you’ll be in a solid place to containerize and set up CI/CD. After that, you can tackle scaling and advanced workflows (queues, artifact stores) as demand grows.
