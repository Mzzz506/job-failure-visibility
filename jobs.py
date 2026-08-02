"""Run scheduled jobs and make their failures visible.

Two capabilities, one key: schedule_nightly() registers a server-side cron job
(the `task` is the URL Infrai calls on schedule), and run_job() wraps a job body
so any exception is captured as a grouped error keyed by the job name — so a
silently-failing nightly task surfaces instead of vanishing. Both are single
Infrai REST calls (see infrai.py).
"""
import infrai

# The URL Infrai hits on schedule — your own worker endpoint.
NIGHTLY_TASK_URL = "https://worker.example.com/tasks/nightly-rollup"


def schedule_nightly() -> str:
    """Register a server-side cron job; returns the job id."""
    job = infrai.cron.create(
        task=NIGHTLY_TASK_URL,          # string URL Infrai calls on schedule
        cron_expr="0 2 * * *",          # 02:00 daily
        name="nightly-rollup",
        timezone="UTC",
    )
    return job.get("job_id")


def run_job(name: str, fn):
    """Execute a job body; capture failures so they don't disappear."""
    try:
        return fn()
    except Exception as exc:
        infrai.errors.capture(
            message=f"job '{name}' failed: {exc}",
            level="error",
            fingerprint=["job", name],      # group all failures of this job
            context={"job": name, "kind": "scheduled"},
        )
        raise


if __name__ == "__main__":
    print("scheduled cron job:", schedule_nightly())
    try:
        run_job("nightly-rollup", lambda: 1 / 0)
    except ZeroDivisionError:
        print("captured job failure (grouped by job name)")
