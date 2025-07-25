# Credentials Setup for FIA v3.0

## Google Cloud Credentials

For local development, you need to set up your Google Cloud credentials:

1. **Place your credentials file** in the project root:
   ```
   animemate-ddb62-5161876d56bc.json
   ```

2. **Update your .env file**:
   ```
   GOOGLE_APPLICATION_CREDENTIALS="animemate-ddb62-5161876d56bc.json"
   ```

3. **For production (Railway)**, set the environment variable:
   - Upload your credentials JSON content as an environment variable
   - Or use Railway's secrets management

## Security Notes

- ✅ Credentials files are excluded from Git via `.gitignore`
- ✅ Use environment variables for all sensitive data
- ✅ Never commit credentials to the repository

## Environment Variables Required

```bash
# Security
SECRET_KEY="your-secret-key"
JWT_SECRET_KEY="your-jwt-secret-key"

# Database
DATABASE_URL="postgresql+asyncpg://..."

# Gemini AI
GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
GOOGLE_CLOUD_PROJECT="animemate-ddb62"
GOOGLE_CLOUD_REGION="europe-west1"
GEMINI_MODEL_NAME="gemini-2.0-flash-001"

# Email (Brevo)
BREVO_API_KEY="your-brevo-key"
BREVO_SENDER_EMAIL="your-email@domain.com"
```