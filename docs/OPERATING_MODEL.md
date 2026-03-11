# Operating Model

## Repository Assessment

This repository is a source fork of the ERPNext app, not a complete standalone deployment stack.

- Application code lives under `erpnext/`.
- Runtime setup is expected to be managed by Frappe Bench.
- Production container builds are delegated upstream to `frappe_docker`, not this repository.
- CI in this repository validates code quality and app behavior, but does not define a full production deployment pipeline.

Evidence in this repository:

- `README.md` documents Bench-based local setup and points production Docker users to `frappe_docker`.
- `.github/helper/install.sh` bootstraps a Bench environment, installs Frappe, installs this app, and runs `bench build` and test site setup.
- `.github/workflows/server-tests-mariadb.yml` and `.github/workflows/server-tests-postgres.yml` run the app inside Bench on Ubuntu with MariaDB or Postgres.
- There is no `Dockerfile` or `docker-compose.yml` in this repository.

## Operating Assumptions

1. Development and CI should target Linux behavior.
2. On Windows, local work should run in WSL2 Ubuntu, not native Windows services.
3. Deployment should install this repository as the ERPNext app into a Bench-managed environment.
4. Upstream ERPNext updates should be merged into this repository deliberately, not copied ad hoc.

## Update Strategy

### Branch Model

Use a small branch model:

- `main`: your deployable branch.
- `upstream-sync/<date-or-version>`: temporary merge branches used to bring in upstream ERPNext changes.
- `feature/<name>`: normal development branches.

### Remote Model

Keep your existing `origin` as the canonical repository for your organization. Add upstream ERPNext as a read-only remote when syncing:

```powershell
git remote add upstream https://github.com/frappe/erpnext.git
git fetch upstream
```

Do not develop directly against an ad hoc checked-out upstream tree. Always merge through a branch so conflicts and regressions are reviewable.

### Update Procedure

When you need upstream changes:

```powershell
git fetch origin
git fetch upstream
git checkout main
git pull origin main
git checkout -b upstream-sync/2026-03-11
git merge upstream/develop
```

Then:

1. Resolve merge conflicts.
2. Run linters and targeted tests in Bench.
3. Smoke test critical ERP flows you actually use.
4. Open a pull request into `main`.

### Customization Rule

Minimize edits to existing ERPNext core files where possible. Prefer adding new code in isolated modules, patches, reports, scripts, or narrowly scoped overrides so upstream merges stay manageable.

If a change must modify core behavior, keep the diff small and document why in the pull request.

## Development Strategy

### Local Environment

Recommended local environment:

- Windows host.
- WSL2 with Ubuntu.
- Bench-managed Frappe environment.
- MariaDB for primary compatibility.
- Optional Postgres validation if you intend to support it.

This recommendation is not generic preference. It follows directly from this repository's own automation, which assumes `bash`, `apt`, `sudo`, Redis, MariaDB or Postgres, Node, Python, and Bench.

### Development Baseline

Use tool versions aligned with this repository's current automation:

- Python 3.14
- Node 24 for CI parity
- Bench with a Frappe `develop`/v17-compatible branch
- Yarn/npm as required by Bench asset builds

### Suggested Local Setup

Inside WSL2:

```bash
pip install frappe-bench
bench init --skip-assets frappe-bench
cd frappe-bench
bench get-app payments --branch develop
bench get-app erpnext /mnt/d/apps/EnXiN
bench new-site dev.localhost
bench --site dev.localhost install-app erpnext
bench start
```

Notes:

- Use the repository path as the app source so your edits are live in the Bench workspace.
- Keep the Bench workspace outside this repo. Bench creates runtime state, sites, logs, caches, and generated assets that do not belong in source control.
- Treat this repository as app source only.

### Day-to-Day Workflow

1. Branch from `main`.
2. Make code changes in this repository.
3. Run formatting and linting before commit.
4. Validate behavior in a local Bench site.
5. Merge by pull request.

Recommended checks:

```bash
pre-commit run --all-files
bench --site dev.localhost run-tests --app erpnext
bench build --app erpnext
```

For large changes, run targeted tests first and full app tests before merge.

## Deployment Strategy

### What Not To Do

Do not try to deploy this repository by itself as if it were a standalone web service. It does not contain:

- process orchestration for all required services,
- a production container definition,
- a site/database provisioning model,
- a full reverse proxy or secrets strategy.

### Supported Deployment Shape

Deploy this repository into a separate Linux Bench environment.

High-level production shape:

1. Linux host or container platform.
2. Bench environment with Frappe.
3. This repository installed as the `erpnext` app from your `origin`.
4. Site backups, asset builds, migrations, and service restarts managed by Bench-based release steps.

### Release Procedure

On the target server or release runner:

```bash
cd /opt/frappe-bench
bench get-app erpnext https://github.com/<your-org>/EnXiN.git --branch main
bench --site <site-name> install-app erpnext
```

For subsequent releases:

```bash
cd /opt/frappe-bench/apps/erpnext
git fetch origin
git checkout main
git pull origin main
cd /opt/frappe-bench
bench --site <site-name> migrate
bench build --app erpnext
bench restart
```

If the app is already installed in Bench, the essential release operations are pull, migrate, build, and restart.

### Deployment Recommendation

Use one of these two deployment paths:

1. Bench on a Linux VM for simpler operations and easier debugging.
2. `frappe_docker` for containerized production, while still sourcing this repository as the app code.

If your team is still establishing process, start with a Linux VM Bench deployment first. It is easier to inspect, patch, and recover during early customization work.

## CI/CD Recommendation For This Repository

Keep or add the following automation in your own repository:

1. PR lint job using pre-commit.
2. PR test job using Bench with MariaDB.
3. Optional Postgres validation job only if you need that database in production.
4. Protected `main` branch.
5. Manual or tagged production deployment workflow that runs Bench release commands on the target environment.

Avoid fully automatic production deploys on every merge until your migration and rollback process is proven.

## Practical Rules

1. Treat this repository as source only.
2. Treat Bench as the runtime and operational boundary.
3. Do local development in WSL2/Linux, not native Windows.
4. Merge upstream ERPNext updates through review branches.
5. Keep customizations isolated so upstream sync remains survivable.
6. Deploy by pulling this repository into Bench and then running migrate, build, and restart.

## Immediate Next Steps

1. Commit the imported ERPNext baseline into `main`.
2. Add upstream ERPNext as a read-only `upstream` remote.
3. Stand up a WSL2 Bench dev environment that points at this repository.
4. Decide whether production will be Linux VM Bench or `frappe_docker`.
5. Add your own CI workflow in this repository before making major customizations.