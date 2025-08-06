# Environment Variables Setup for Render

⚠️ **NEVER commit credentials to git!**

## Setup Instructions:

1. Go to your Render backend service dashboard
2. Click "Environment" tab
3. Add these variables (without the actual private key):

```
GOOGLE_TYPE=service_account
GOOGLE_PROJECT_ID=hiringsystem-468006
GOOGLE_PRIVATE_KEY_ID=93a55515e3a94869246525cb6f2e8fbb191467ad
GOOGLE_CLIENT_EMAIL=hiringsystem1@hiringsystem-468006.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=111657562153360913827
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs/hiringsystem1%40hiringsystem-468006.iam.gserviceaccount.com
GOOGLE_SHEET_ID=14eHVi6M0nkRf9u2SJ26FFqWp0dNYw05hsFcuCi5rty0
```

**For GOOGLE_PRIVATE_KEY**: Copy the value from your local credentials.json file.

## Security Notes:
- Keep credentials.json local only
- Never commit private keys to git
- Use environment variables in production
- Regularly rotate your service account keys
