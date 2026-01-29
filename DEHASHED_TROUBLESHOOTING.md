# DeHashed API Troubleshooting Checklist

## Issue: Getting `{"message": "Need Help? Visit https://app.dehashed.com/documentation/api"}`

This error indicates the API endpoint is rejecting your request **before** checking authentication.

### Critical Steps to Verify:

1. **Log into DeHashed Web Dashboard**
   - Go to: https://www.dehashed.com/ (or https://app.dehashed.com/)
   - Log in with: adam.w.freeman@gmail.com
   
2. **Check Your Plan/Subscription**
   - Navigate to Account Settings or Billing
   - Confirm you have an **active paid subscription**
   - DeHashed API is NOT available on free accounts
   - You need at minimum a "Professional" or "Enterprise" plan
   
3. **Verify API Access is Enabled**
   - Look for "API Access" or "API Keys" section in your dashboard
   - Some plans require you to explicitly enable API access
   - Check if there's a toggle or separate purchase required
   
4. **Get the Correct Endpoint from Documentation**
   - In your DeHashed dashboard, look for:
     - "API Documentation" link
     - "Developer" section
     - "Integration" guide
   - The actual endpoint URL may be different than public docs suggest
   
5. **Check API Key Format**
   - Your new key: `7SWflveHqilluIGb8Sd7e74ttL+TNz7jnik3ERPeZPHyq6zxYQXb+GA=`
   - This looks like a base64-encoded token
   - Some APIs need this WITHOUT encoding again
   - Some need it WITH the email as username
   
6. **Contact DeHashed Support**
   - If you have paid access but API still fails
   - Ask specifically: "What is the correct curl command to test my API access?"
   - They should provide you with a working example

### Alternative: Check if API is Available

Try accessing the web interface search:
- If you can search in the web UI: Your account has data access
- If API still fails: Your plan doesn't include API access

### Next Steps:
1. Log into https://app.dehashed.com/
2. Check your account tier/plan
3. Look for "API" section
4. Verify API is included in your subscription
5. Get the exact endpoint URL from their dashboard docs
