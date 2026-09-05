# Restores the canonical seed dump (pharvo_db.backup) into PostgreSQL and
# reconciles Django migrations so the database matches the committed code.
#
# Usage (from repository root):
#   .\scripts\restore_db.ps1
#
# Optional: PG_BIN  = directory containing psql/pg_restore/createdb (default: empty,
#                     relying on PATH). Set manually if they are not on PATH.
#           DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT can be overridden
#                     via environment variables or a repo-root .env file.

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackupPath = Join-Path $RepoRoot "pharvo_db.backup"
$BackendDir = Join-Path $RepoRoot "Backend"

if (-not (Test-Path -LiteralPath $BackupPath)) {
    throw "Seed dump not found: $BackupPath"
}

# --- Configuration (defaults match a local default PostgreSQL install) ---
$DB_NAME     = "pharvo_db"
$DB_USER     = "postgres"
$DB_HOST     = "localhost"
$DB_PORT     = "5432"

# The database password is NEVER hardcoded here. It must be provided via the
# repo-root .env file or a DB_PASSWORD environment variable.
$DB_PASSWORD = $null

# Load .env if present (very light-weight parser: KEY=VALUE lines only).
$EnvFile = Join-Path $RepoRoot ".env"
if (Test-Path -LiteralPath $EnvFile) {
    Get-Content -LiteralPath $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
            $key = $matches[1]; $value = $matches[2]
            switch ($key) {
                "DB_NAME"     { $DB_NAME = $value }
                "DB_USER"     { $DB_USER = $value }
                "DB_HOST"     { $DB_HOST = $value }
                "DB_PORT"     { $DB_PORT = $value }
                "DB_PASSWORD" { $DB_PASSWORD = $value }
            }
        }
    }
}
# Environment variables take precedence over .env.
if ($env:DB_NAME)     { $DB_NAME = $env:DB_NAME }
if ($env:DB_USER)     { $DB_USER = $env:DB_USER }
if ($env:DB_HOST)     { $DB_HOST = $env:DB_HOST }
if ($env:DB_PORT)     { $DB_PORT = $env:DB_PORT }
if ($env:DB_PASSWORD) { $DB_PASSWORD = $env:DB_PASSWORD }

if ([string]::IsNullOrEmpty($DB_PASSWORD)) {
    throw "DB_PASSWORD is not set. Copy .env.example to .env at the repository root, set DB_PASSWORD to your local PostgreSQL password, and re-run this script."
}

$env:PGPASSWORD = $DB_PASSWORD

# --- Locate PostgreSQL client tools ---
function Get-PgTool([string]$Name) {
    if ($env:PG_BIN -and (Test-Path -LiteralPath (Join-Path $env:PG_BIN "$Name.exe"))) {
        return Join-Path $env:PG_BIN "$Name.exe"
    }
    Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
}

$psql      = Get-PgTool "psql"
$pg_restore = Get-PgTool "pg_restore"
if (-not $psql -or -not $pg_restore) {
    throw "psql/pg_restore not found. Install PostgreSQL or set PG_BIN to the bin directory (e.g. C:\Program Files\PostgreSQL\18\bin)."
}

# --- Create the database if it does not exist ---
$connArgs = @("--host=$DB_HOST", "--port=$DB_PORT", "--username=$DB_USER")
$exists = & $psql $connArgs -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';"
if ($exists -ne "1") {
    Write-Host "Creating database '$DB_NAME'..."
    & $psql $connArgs -d postgres -c "CREATE DATABASE `"$DB_NAME`";"
} else {
    Write-Host "Database '$DB_NAME' already exists."
}

# --- Restore the seed dump ---
Write-Host "Restoring $BackupPath -> $DB_NAME ..."
& $pg_restore $connArgs -d $DB_NAME --clean --if-exists $BackupPath
if ($LASTEXITCODE -ne 0) { throw "pg_restore failed (exit $LASTEXITCODE)." }
Write-Host "Database restored."

# --- Reconcile Django migrations (no-op against a freshly restored seed) ---
Write-Host "Reconciling Django migrations..."
Push-Location $BackendDir
try {
    $env:DB_NAME = $DB_NAME
    $env:DB_USER = $DB_USER
    $env:DB_PASSWORD = $DB_PASSWORD
    $env:DB_HOST = $DB_HOST
    $env:DB_PORT = $DB_PORT
    python manage.py migrate --fake-initial
    if ($LASTEXITCODE -ne 0) { throw "migrate --fake-initial failed." }
    python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "migrate failed." }
} finally {
    Pop-Location
}

Write-Host "Done. Backend start: cd Backend; python manage.py runserver"
Write-Host "Demo login: rafi / 787878"