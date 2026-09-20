# cloudservRAG: AI-assisted support ticket pipeline for CloudServe

Classifies a support ticket, retrieves the relevant passages from CloudServe's 29 knowledge-base
articles, decides whether to answer automatically or escalate, drafts a cited answer, validates
it with blocking guardrails, and logs every decision. Escalations carry a summary, the retrieved
articles, the draft and what the system was unsure about.

Results and every design decision with its measurements: `Docs/architecture.md`.
Governance (risk register, fairness audit, guardrails, incident procedure, kill switch, AI-use
declaration): `Docs/governance.md`. Prompt register: `prompts/README.md`.

## 1. Requirements

- **Python 3.11.** The pinned `requirements.txt` (from the course pack, six pins adjusted) builds
  on 3.11; Python 3.13 cannot build the pinned pandas 2.0.0. CI runs on 3.11.
- git, about 3 GB of disk (PyTorch and the model caches), and internet on the first run (two
  small Hugging Face models are downloaded: `all-MiniLM-L6-v2` and `cross-encoder/nli-MiniLM2-L6-H768`).
- An OpenRouter API key (`https://openrouter.ai/keys`). The default model is
  `meta-llama/llama-3.1-8b-instruct`; a full 500-ticket run costs about $0.03. Without a key the
  system still runs: every ticket escalates with the reason "provider unavailable".
- **Docker is optional.** Nothing in sections 2 to 5 needs it: the API, the client, the harness and
  the tests run with Python alone. Docker (Docker Desktop on Windows and macOS, Docker Engine with
  the compose plugin on Linux) is needed only for the Grafana dashboard in section 6; the same
  metrics are readable without it (`python -m src.client metrics`).

## 2. Setup (about five minutes plus the download)

Windows (PowerShell or cmd). Clone into a short path such as `C:\work` (a deep folder pushes some
installed files past Windows' 260-character path limit and `pip install` fails with "No such file
or directory"):

```
git clone https://github.com/anshulghogre4/cloudservRAG.git
cd cloudservRAG
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
```

Linux or macOS:

```
git clone https://github.com/anshulghogre4/cloudservRAG.git
cd cloudservRAG
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu   # optional: CPU-only wheel, much smaller
python -m pip install -r requirements.txt
cp .env.example .env
```

If `py -3.11` or `python3.11` is not on the machine, `uv venv --python 3.11 --seed .venv` (from
`https://docs.astral.sh/uv/`) downloads a 3.11 interpreter and creates the same virtual environment.

Then open `.env` and set `OPENROUTER_API_KEY=` to your key. Everything else in `.env.example`
has a working default; the values are explained inline. Never commit `.env`; it is in `.gitignore`.

## 3. Run the tests (no key needed)

```
python -m pytest tests/ -q
```

152 tests; every test uses fakes for the model provider, the embedder and the NLI model, so the
suite runs offline in under ten seconds. This is the command CI runs on every push
(`.github/workflows/ci.yml`), followed by a smoke run of the real pipeline with the provider
disconnected.

## 4. Start the system and submit tickets by hand

```
python -m src.api
```

The first start downloads the two models and builds the vector store under `storage/` (one to
two minutes); later starts take about twenty seconds. Wait for `Application startup complete`.
The API listens on `http://127.0.0.1:8000`; Prometheus metrics on `http://127.0.0.1:8001/metrics`.

In a second terminal, from the repository root with the virtual environment active, submit one ticket
per channel with the bundled client, which prints the reply in a readable, coloured layout (the
decision, the reason, the retrieved passages, the guardrail verdicts, then the reply with its
citations or the escalation package):

```
python -m src.client ticket data/samples/ticket_email.json
python -m src.client ticket data/samples/ticket_chat.json
python -m src.client ticket data/samples/ticket_docs_comment.json
python -m src.client ticket data/samples/ticket_forum.json
```

Expected: email escalates (feature request, policy rule), chat is answered with `DOC-DEPLOY-003`
citations, docs comment escalates (compliance request, policy rule), forum is answered with
`DOC-ACCT-001` citations. The client uses only the standard library and works on Windows, macOS
and Linux; add `--raw` to see the JSON record, `--no-color` for plain text.

The same requests with curl, which prints the raw JSON record on one line (on Windows PowerShell
type `curl.exe`, not `curl`):

```
curl -X POST http://127.0.0.1:8000/tickets -H "content-type: application/json" -d @data/samples/ticket_email.json
curl -X POST http://127.0.0.1:8000/tickets -H "content-type: application/json" -d @data/samples/ticket_chat.json
curl -X POST http://127.0.0.1:8000/tickets -H "content-type: application/json" -d @data/samples/ticket_docs_comment.json
curl -X POST http://127.0.0.1:8000/tickets -H "content-type: application/json" -d @data/samples/ticket_forum.json
```

Each response is one JSON record: `action` (`auto_respond`, `escalate` or `block`), `intent`,
`urgency`, `confidence`, `route_reason` in plain language, `answer` with `citations` when it
answered, otherwise `escalation` (summary, uncertainty, article ids, draft), `guardrails` with the
verdict of every check, `latency_ms`, `error`.

A guardrail-trigger ticket (the body asks the system to repeat the customer's name and account id):

```
python -m src.client ticket data/samples/trig_pii_001.json
```

or, raw: `curl -X POST http://127.0.0.1:8000/tickets -H "content-type: application/json" -d @data/samples/trig_pii_001.json`

Expect `"action": "block"` with the blocking guardrail named in `route_reason`, `answer: null`
and the blocked draft inside `escalation`. Which guardrail fires on a live model depends on what
the model writes (in our runs this ticket was blocked by the grounding check); every guardrail's
verdict is in `guardrails`, and each block path is proven deterministically in `tests/`. The other
trigger tickets are `trig_inj_001.json` (instruction injection, escalates before drafting),
`trig_tone_001.json` and `trig_grnd_001.json`.

Read back the decision-log rows for any ticket (the most recent submission by default, `--all` for every row),
the health, and a readable summary of any harness output directory:

```
python -m src.client decisions TRIG-PII-001
python -m src.client health
python -m src.client run evaluation/results/2026-09-16_validation
```

Raw equivalents, plus the Prometheus metrics:

```
curl http://127.0.0.1:8000/decisions/TRIG-PII-001
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/metrics
```

Stop automatic answers without a restart (Governance section 5), then resume:

```
python -m src.killswitch on <your name>
python -m src.killswitch status
python -m src.killswitch off
```

## 5. Run a whole ticket file unattended

```
python -m evaluation.harness --input Docs/Capstone_Project/05_Datasets/validation_tickets.json --output evaluation/results/my_run
```

Any file with the ticket schema works as `--input` (labels are optional; with labels the report
adds accuracy figures). The run needs no attention: a failing component, a provider timeout, a
rate limit or a malformed ticket produces an escalation record with the reason, never a crash.
Progress is logged every 25 tickets. The 80 validation tickets take about eight minutes with the
live provider (20 requests per minute pacing); model replies are cached under `storage/llm_cache`,
so a repeated run is fast and free.

The output directory receives:

| File | Content |
|---|---|
| `results.jsonl` | one record per ticket, in input order, written as each ticket completes |
| `metrics.json` | volume, business, technical, governance and per-segment figures (Evaluation Framework), with confidence intervals and the calibration table |
| `run_summary.md` | the same, readable |
| `run_meta.json` | input, ticket count, timestamps, git version, model, thresholds, run count on this input |
| `metrics.prom` | Prometheus snapshot of the run |

The decision log is `storage/decisions.db` (SQLite, append-only). `run_summary.md` ends with the
reconciliation line: rows logged against tickets processed, which must be complete. Options:
`--limit N` (first N tickets), `--resume` (continue an interrupted run), `--sort-urgency`.

Fairness audit over one or more runs (Governance section 3):

```
python -m evaluation.fairness_audit --results evaluation/results/my_run/results.jsonl --output evaluation/results/my_run/fairness
```

Runs already recorded in this repository: `evaluation/results/2026-09-16_dev_full` (development
set, 500 tickets), `evaluation/results/2026-09-16_validation` (validation set, the single evaluation run; a later re-run with cached replies was made only for the video) and the
measurement scripts' outputs (`retrieval_check`, `classify_check`, `route_check`, `guardrail_check`).

## 6. Monitoring

The API exposes Prometheus metrics (tickets by channel and outcome, response time, guardrail
blocks, classification confidence, pipeline failures) on `http://127.0.0.1:8001/metrics`. Without
any extra software, a readable live view:

```
python -m src.client metrics
```

Optional Grafana dashboard (requires Docker). First check that Docker is installed and its engine
is running; on Windows and macOS that means Docker Desktop has been started and shows "Engine
running":

```
docker --version
docker info --format "{{.ServerVersion}}"
```

The second command prints a version number when the engine is running. If it prints "failed to
connect to the docker API" or "Cannot connect to the Docker daemon", start Docker Desktop (or
`sudo systemctl start docker` on Linux), wait until it reports that the engine is running, and try
again. Then, with the API started (`python -m src.api`):

```
docker compose -f monitoring/docker-compose.yml up -d
```

The first run downloads the Prometheus and Grafana images (about 600 MB); later runs start in a few
seconds. Check that everything is up:

```
docker compose -f monitoring/docker-compose.yml ps
curl http://localhost:3000/api/health
curl http://localhost:9090/api/v1/targets
```

Expected: two services with state `running` (`prometheus` and `grafana`); Grafana answers
`"database": "ok"`; the Prometheus target `support-system` shows `"health":"up"`. A target that is
`down` means the API is not running or its metrics port (8001) is blocked; start the API and wait
one scrape (5 seconds). On Windows PowerShell type `curl.exe`.

Open `http://localhost:3000/d/cloudserve-support/cloudserve-support-pipeline` (no login needed for
viewing; admin / admin to edit). The dashboard "CloudServe support pipeline" is provisioned
automatically: counters for processed, answered, escalated, blocked and failed tickets, mean
confidence, a step chart by outcome, tickets by channel, median and p95 response time against the
3-second target, guardrail blocks and the confidence bands. Prometheus scrapes every 5 seconds and
the dashboard refreshes every 5 seconds, so each submitted ticket shows within about ten seconds.
Counters are totals since the API process started. The batch harness is a separate process and does
not feed the live dashboard; it writes a `metrics.prom` snapshot into its output directory.
Prometheus itself is at `http://localhost:9090`. `docker compose -f monitoring/docker-compose.yml down` stops both.

## 7. Layout

```
src/            ingest, classify, retrieve, route, generate, guardrails, logging_store, escalation,
                pipeline, api, client (readable command-line view of the API), monitoring, killswitch,
                llm (provider client), calibration, config, models
prompts/        versioned prompts (PR-01 to PR-07) and the register with change history
tests/          the suite and its fixtures (sample, edge and trigger tickets)
evaluation/     harness, metrics report, fairness audit, measurement scripts, results/
data/samples/   one ticket per channel and the trigger tickets as single JSON files
monitoring/     prometheus.yml, docker-compose.yml, Grafana dashboard and provisioning
Docs/           the course pack, architecture.md (decision record), governance.md, workbooks
storage/        created at runtime (vector store, decision log, reply cache, kill-switch flag); ignored by git
.github/        CI workflow
```

## 8. If something goes wrong

- `pandas` fails to build: the interpreter is not 3.11. Recreate the venv with 3.11 (section 2).
- The first `python -m src.api` seems stuck: it is downloading the models; watch for
  `retriever ready` and `Application startup complete` in the log.
- `429` from the provider: the client backs off and retries; a run slows down but continues.
- No key or provider down: every ticket escalates with `provider unavailable`; the run and the
  log still complete (this is tested in CI).
- Port 8000 or 8001 in use: set `API_PORT` or `METRICS_PORT` in `.env`.
- `curl` returns `{"detail":[{"type":"missing","loc":["body"] ...` (HTTP 422): the `-d @file` path
  did not resolve, so an empty body was sent. Run the command from the repository root.
- `python -m src.client ...` says it cannot reach the API: start `python -m src.api` in another
  terminal first; if the API uses another port, pass `--url http://127.0.0.1:<port>`.
- `docker compose ... up -d` fails with "failed to connect to the docker API" or "Cannot connect to
  the Docker daemon": Docker is installed but its engine is not running. Start Docker Desktop (or
  the docker service on Linux) and wait for "Engine running". Docker is only needed for Grafana.
- Grafana opens but every panel says "No data": the API is not running, or it was started after
  Prometheus and no ticket has been submitted yet. Start `python -m src.api`, submit a ticket
  (section 4), and wait ten seconds. Check the scrape target at `http://localhost:9090/targets`.
- Port 3000 or 9090 already in use: change the left-hand side of the `ports` entries in
  `monitoring/docker-compose.yml` (for example `"3001:3000"`) and open that port instead.
- The client's output shows codes like `[92m` instead of colours: the terminal does not support
  colour; add `--no-color` (the layout is the same).
- A ticket is answered when it should not be: `python -m src.killswitch on`, then read the ticket's
  rows with `/decisions/<ticket_id>`; the incident steps are in `Docs/governance.md` section 5.

## 9. AI assistance

The code, prompts and technical notes were produced with Claude (Anthropic) under the author's
direction; the full declaration is `Docs/governance.md` section 7. The problem statement, the
evaluation interpretation and the reflection are the author's own.
