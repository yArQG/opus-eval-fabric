# CI measurement correction and paired pilot

Parent: PR #6, commit c5b817f3ee5ea15dd3f7d85c81bd3f94d485040f.
Status: shadow experiment; canonical CI remains unchanged. This is not CP33 promotion.

## Correcting the measurement model

Job completion minus job start is wall elapsed time, including setup, network,
I/O and teardown. It is not CPU compute time. Job start minus workflow creation
also includes dependency barriers; it is not necessarily scheduler queue time.
A maximum single job duration is not a longest path for dependent jobs.

Schema 0.2 intentionally replaces the misleading 0.1 fields:
- `compute_duration_s` -> `job_elapsed_s`
- `queue_delay_s` -> `start_offset_s`
- `critical_compute_s` -> `max_job_elapsed_s`
- `max_queue_delay_s` -> `max_start_offset_s`

If a complete, explicit `dependencies` map is supplied (roots use empty lists),
`execution_path_elapsed_s` reports the longest sum of measured job durations
along that DAG, excluding waits. Without a DAG it is null, not inferred parallel.
This is descriptive: observed durations may themselves depend on contention.
`ready_to_start_s` is the residual after predecessor completion, not a causal
measurement of scheduler service. `finalization_s` accounts for the workflow tail.

In general, max(start offset) + max(job duration) is NOT the workflow duration:
the maxima can belong to different jobs. Do not sum them or optimize either
as a universal proxy for user latency. Track end-to-end latency separately.
Use a genuine completion timestamp, not API `updated_at` or a poll observation.
Use the specific run attempt; original creation timestamps on reruns include
historical gaps. Validate job inventory before constructing analyzer input.

Malformed chronology, empty inventories, duplicate job names, naive timestamps,
incomplete dependency maps, cycles and impossible predecessor order fail closed.
Historical JSON fixtures retain their original schema as archival observations.

## Fixed pilot protocol

`paired-install-shadow.yml` runs only on the dedicated experiment branch.
Six jobs: Python 3.11/3.12/3.13 crossed with two blocks. Each job runs four pairs
on one runner; AB/BA order alternates and reverses in the second block. There
are 24 pairs total, eight per interpreter, clustered within six runner jobs.
These are NOT 24 independent runner samples. No inferential confidence interval
or automatic speedup/promotion claim is made from this pilot.

Each arm uses a fresh virtual environment. Both disable local pip cache;
upstream caches/network conditions remain uncontrolled. The experiment compares
whole installation strategies with current dependency resolution; build tool
versions can differ across arms or drift. It does not isolate the causal effect
of the isolation flag alone. Build requirements come from pyproject.toml.

High-resolution monotonic wall timers record environment creation, explicit
bootstrap, editable installation, version capture and each verification command.
The primary descriptive installation delta includes bootstrap for the explicit
arm. Environment creation and verification are separately recorded. Pip logs
and installed-version inventories are uploaded with benchmark JSON receipts.
The same checked-out commit is verified against GITHUB_SHA before any install.
All unit, smoke, foundation and incremental benchmark commands must succeed.
Junit output parity and whole-workflow latency are not measured by this pilot;
therefore it cannot replace canonical CI on proof-equivalence grounds either.

On failure the partial receipt is retained, the job fails, and no successful
summary is produced. On success, per-pair differences, median and range are
reported descriptively, with promotion permanently BLOCKED_PILOT_ONLY.

## Next decision

Inspect receipts and failure rate first. If effects are small compared with
within/between-runner variation, stop tuning this path. If an effect is promising,
pre-register a practical threshold and a larger fixed runner-block sample;
freeze dependency versions and compare cold/warm caches in separate strata.
Do not pool interpreter versions, retry until significant, or select only wins.
CP33 remains pending receipt review and sufficient repeated evidence.

Rollback: close the stacked draft PR; delete its experiment branch when desired.
No canonical workflow or package runtime is changed. No recurring automation.

Sources: https://docs.github.com/en/rest/actions/workflow-jobs
https://pip.pypa.io/en/stable/reference/build-system/
