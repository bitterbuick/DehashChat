#!/bin/bash

EMAIL="adam.w.freeman@gmail.com"
API_KEY="7SWflveHqilluIGb8Sd7e74ttL+TNz7jnik3ERPeZPHyq6zxYQXb+GA="

echo "Testing DeHashed API endpoints..."
echo "================================="
echo ""

# Array of endpoints to test
endpoints=(
    "https://api.dehashed.com/search"
    "https://api.dehashed.com/v2/search"
    "https://api.dehashed.com/v1/search"
    "https://dehashed.com/api/search"
    "https://api.dehashed.com/query"
)

for endpoint in "${endpoints[@]}"; do
    echo "Testing: $endpoint"
    echo "---"
    
    # Test with Basic Auth
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -u "$EMAIL:$API_KEY" "$endpoint?query=email:test@example.com")
    echo "$response"
    echo ""
    echo "================================="
    echo ""
done

echo ""
echo "Testing with X-API headers..."
echo "================================="
curl -s -w "\nHTTP_CODE:%{http_code}" \
    -H "X-API-Email: $EMAIL" \
    -H "X-API-Key: $API_KEY" \
    "https://api.dehashed.com/search?query=email:test@example.com"
echo ""
echo ""

echo "Testing account info endpoint (if exists)..."
curl -s -w "\nHTTP_CODE:%{http_code}" -u "$EMAIL:$API_KEY" "https://api.dehashed.com/account"
echo ""
