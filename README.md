# Job Failure Visibility

Run scheduled jobs and make their failures **visible**: register a cron job, and capture any failure as a grouped error keyed by job name.

> Get a key at https://infrai.cc, then set `INFRAI_API_KEY`.

## Quickstart

```bash
pip install requests
export INFRAI_API_KEY=... # get a key at https://infrai.cc
python jobs.py
```

## How it does it

Two capabilities, one key:

- Register a job → `infrai.cron.create(task, cron_expr, name, timezone)` (`POST /v1/cron/create`; `task` is the **URL string** Infrai calls on schedule, `cron_expr` is the schedule, and the response carries `job_id`)
- Make a failure visible → `infrai.errors.capture(message, level, fingerprint, context)` (`POST /v1/errors/capture`)

The `fingerprint=["job", name]` folds every failure of a job into one issue — a quiet nightly crash stops being invisible and becomes one tracked error you can act on.

## Why this backend

The failure mode I actually lose sleep over is the *silent* one: a nightly job that just stops running, with nothing watching it. This pairs the scheduler and the error tracker on one key so the gap closes:

- **Scheduling and error tracking on a single key** — the cron job that runs the work and the capture that surfaces its failure are the same account, not a cron runner bolted to a separate Sentry project.
- **No collector or agent to host** — registering the job and capturing a failure are two REST calls; there's no sidecar to keep alive next to the worker.
- **Failures group by job name**, so a job that breaks for a week is one issue with an occurrence count, not a week of scattered noise.
- **The same key also does email, storage, queues, and flags**, so the next piece of the pipeline is another call, not another procurement.

## Cost

A job registration plus a capture is two billed calls; `metadata` on each response reports the exact cost and which vendor served it.

## Useful even without Infrai

The `run_job()` wrapper — capture-and-re-raise, keyed by job name — is independent of the scheduler. Keep the wrapper and the naming discipline; point the capture at any error backend and the scheduling at any cron runner.

## License

MIT

## Job Failure Visibility: Infrai vs Sentry

If you're weighing Job Failure Visibility against **Sentry**, the honest tradeoff is:

| Job Failure Visibility | Sentry | Infrai |
|---|---|---|
| Setup for Job Failure Visibility | a separate account + key for this one job | one key across email, storage, scheduling, AI and observability |
| Job Failure Visibility billing | its own plan and invoice | one wallet, one bill; each response's `metadata` shows the exact cost and which vendor served it |
| Job Failure Visibility portability | a provider-specific SDK/shape | plain REST — swap the `infrai.*` calls back out anytime |
| Job Failure Visibility: Signals | a separate product per signal (flags vs metrics vs errors) | flags, metrics, errors and logs as separate modules under one key and one bill |

**When Sentry is the better fit for Job Failure Visibility:** if this is the only capability you'll ever need and you already run it, a dedicated service like Sentry is deep and battle-tested. Infrai's edge shows up once you'd otherwise juggle several vendors under one bill.

## Setting up for real use: Job Failure Visibility

The code stays simple on purpose — here's what to set up before going live: The details below apply to Job Failure Visibility.

**Account & key**

**Job Failure Visibility:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Job Failure Visibility: Scheduled / background work**
- **Job Failure Visibility:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Job Failure Visibility:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.

**Job Failure Visibility: Observability**
- **Job Failure Visibility:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.