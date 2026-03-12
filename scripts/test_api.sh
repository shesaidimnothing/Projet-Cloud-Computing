#!/bin/bash
# ============================================================
# API Test Script
# Usage: ./test_api.sh <VM_IP>
# ============================================================

set -euo pipefail

IP="${1:?Usage: $0 <VM_PUBLIC_IP>}"
BASE="http://${IP}:5000"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

echo "============================================="
echo " Testing Flask API at ${BASE}"
echo "============================================="

# 1 - Health check
echo ""
echo "--- Test 1: Health check ---"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/health")
[ "$HTTP" = "200" ] && pass "GET /health -> 200" || fail "GET /health -> ${HTTP}"

# 2 - Upload a file
echo ""
echo "--- Test 2: Upload file ---"
echo "Hello from test script" > /tmp/test_upload.txt
UPLOAD=$(curl -s -w "\n%{http_code}" -X POST "${BASE}/api/files" \
  -F "file=@/tmp/test_upload.txt" \
  -F "category=logs")
HTTP=$(echo "$UPLOAD" | tail -1)
BODY=$(echo "$UPLOAD" | sed '$d')
[ "$HTTP" = "201" ] && pass "POST /api/files -> 201" || fail "POST /api/files -> ${HTTP}"

FILE_ID=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
echo "  Created file ID: ${FILE_ID}"

# 3 - List files
echo ""
echo "--- Test 3: List files ---"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/files")
[ "$HTTP" = "200" ] && pass "GET /api/files -> 200" || fail "GET /api/files -> ${HTTP}"

# 4 - Get file info
if [ -n "$FILE_ID" ]; then
  echo ""
  echo "--- Test 4: Get file info ---"
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/files/${FILE_ID}")
  [ "$HTTP" = "200" ] && pass "GET /api/files/${FILE_ID} -> 200" || fail "GET /api/files/${FILE_ID} -> ${HTTP}"

  # 5 - Download file
  echo ""
  echo "--- Test 5: Download file ---"
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/files/${FILE_ID}/download")
  [ "$HTTP" = "200" ] && pass "GET /api/files/${FILE_ID}/download -> 200" || fail "GET -> ${HTTP}"

  # 6 - Delete file
  echo ""
  echo "--- Test 6: Delete file ---"
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "${BASE}/api/files/${FILE_ID}")
  [ "$HTTP" = "200" ] && pass "DELETE /api/files/${FILE_ID} -> 200" || fail "DELETE -> ${HTTP}"
fi

# 7 - List containers
echo ""
echo "--- Test 7: List storage containers ---"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/storage/containers")
[ "$HTTP" = "200" ] && pass "GET /api/storage/containers -> 200" || fail "GET -> ${HTTP}"

# 8 - List blobs
echo ""
echo "--- Test 8: List blobs in 'images' container ---"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/storage/list?container=images")
[ "$HTTP" = "200" ] && pass "GET /api/storage/list -> 200" || fail "GET -> ${HTTP}"

echo ""
echo "============================================="
echo " Tests complete"
echo "============================================="

rm -f /tmp/test_upload.txt
