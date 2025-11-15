# Pre-Push Security Check Script
# Run this before pushing to GitHub

Write-Host "🔍 Running Security Check..." -ForegroundColor Cyan
Write-Host ""

$errors = 0

# Check 1: Verify .gitignore exists
Write-Host "✓ Checking .gitignore..." -NoNewline
if (Test-Path ".gitignore") {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL - .gitignore missing!" -ForegroundColor Red
    $errors++
}

# Check 2: Verify no .env files in git
Write-Host "✓ Checking no .env files tracked..." -NoNewline
$envFiles = git ls-files | Select-String -Pattern "\.env$"
if ($envFiles) {
    Write-Host " FAIL - .env files found in git!" -ForegroundColor Red
    $envFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    $errors++
} else {
    Write-Host " PASS" -ForegroundColor Green
}

# Check 3: Verify example files exist
Write-Host "✓ Checking example files..." -NoNewline
$backendExample = Test-Path "backend\.env.example"
$frontendExample = Test-Path "frontend\.env.local.example"
if ($backendExample -and $frontendExample) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL - Example files missing!" -ForegroundColor Red
    if (-not $backendExample) { Write-Host "  - backend/.env.example missing" -ForegroundColor Red }
    if (-not $frontendExample) { Write-Host "  - frontend/.env.local.example missing" -ForegroundColor Red }
    $errors++
}

# Check 4: Verify credentials files are ignored
Write-Host "✓ Checking credentials files ignored..." -NoNewline
$credsIgnored = git check-ignore backend/test_credentials.json 2>&1
if ($credsIgnored -match "test_credentials.json") {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " WARNING - Verify credentials are ignored" -ForegroundColor Yellow
}

# Check 5: Verify README exists
Write-Host "✓ Checking README.md..." -NoNewline
if (Test-Path "README.md") {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL - README.md missing!" -ForegroundColor Red
    $errors++
}

# Check 6: Verify SECURITY.md exists
Write-Host "✓ Checking SECURITY.md..." -NoNewline
if (Test-Path "SECURITY.md") {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " WARNING - SECURITY.md recommended" -ForegroundColor Yellow
}

# Check 7: Verify no secrets in staged files
Write-Host "✓ Checking no secrets in staged files..." -NoNewline
$stagedSecrets = git diff --cached | Select-String -Pattern "AIzaSy|sjkdfnkjs|2461@localhost" -SimpleMatch
if ($stagedSecrets) {
    Write-Host " FAIL - Secrets found in staged files!" -ForegroundColor Red
    $errors++
} else {
    Write-Host " PASS" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" -repeat 60
if ($errors -eq 0) {
    Write-Host "✅ ALL CHECKS PASSED - SAFE TO PUSH!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Open GitHub Desktop"
    Write-Host "2. Review changes"
    Write-Host "3. Click 'Publish repository'"
    Write-Host "4. Choose repository name"
    Write-Host "5. Select Public or Private"
    Write-Host "6. Click 'Publish repository'"
} else {
    Write-Host "❌ $errors ERROR(S) FOUND - DO NOT PUSH YET!" -ForegroundColor Red
    Write-Host "Fix the errors above before pushing to GitHub" -ForegroundColor Yellow
}
Write-Host "=" -repeat 60
