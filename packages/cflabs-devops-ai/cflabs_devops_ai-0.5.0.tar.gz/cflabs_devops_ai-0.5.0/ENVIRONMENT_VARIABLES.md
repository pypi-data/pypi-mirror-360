# Environment Variables in devops-ai

This document explains how to use environment variables with devops-ai deployments.

## Overview

devops-ai supports multiple ways to pass environment variables to your Lambda function:

1. **Direct key=value pairs**: `--env-vars "KEY1=value1,KEY2=value2"`
2. **GitHub Secrets references**: `--env-vars "KEY1=${{ secrets.SECRET_NAME }},KEY2=${{ secrets.ANOTHER_SECRET }}"`
3. **Mixed format**: `--env-vars "KEY1=value1,KEY2=${{ secrets.SECRET_NAME }},KEY3=value3"`
4. **Keys only**: `--env-vars "KEY1,KEY2"` (values taken from environment variables)

## Usage Examples

### 1. Direct Key-Value Pairs

```bash
devops-ai serverless deploy \
  --name my-app \
  --env-vars "API_KEY=abc123,DATABASE_URL=postgresql://user:pass@host:5432/db"
```

### 2. GitHub Secrets References

In GitHub Actions workflow:

```yaml
- name: Deploy with GitHub secrets
  run: |
    devops-ai serverless deploy \
      --name my-app \
      --env-vars "UploadsBucketName=${{ secrets.S3_DATA_BUCKET }},DbHost=${{ secrets.DB_HOST }},DbPort=${{ secrets.DB_PORT }},DbUser=${{ secrets.DB_USER }},DbPassword=${{ secrets.DB_PASSWORD }},DbName=${{ secrets.DB_NAME }},PineconeApiKey=${{ secrets.PINECONE_API_KEY }},OpenaiApiKey=${{ secrets.OPENAI_API_KEY }},VoyageApiKey=${{ secrets.VOYAGE_API_KEY }}"
```

### 3. Mixed Format

```bash
devops-ai serverless deploy \
  --name my-app \
  --env-vars "DEBUG=true,API_KEY=${{ secrets.API_KEY }},DATABASE_URL=${{ secrets.DB_URL }},ENVIRONMENT=production"
```

### 4. Keys Only (Values from Environment)

```bash
# Set environment variables first
export API_KEY=abc123
export DATABASE_URL=postgresql://user:pass@host:5432/db

# Deploy with keys only
devops-ai serverless deploy \
  --name my-app \
  --env-vars "API_KEY,DATABASE_URL"
```

## GitHub Actions Integration

### Setting up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add your secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `S3_DATA_BUCKET`
   - `DB_HOST`
   - `DB_PORT`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`
   - `PINECONE_API_KEY`
   - `OPENAI_API_KEY`
   - `VOYAGE_API_KEY`

### Complete Workflow Example

```yaml
name: Deploy to AWS Lambda with Secrets

on:
  push:
    branches: [ main, master ]

env:
  AWS_REGION: ap-south-1
  LAMBDA_NAME: my-app
  MEMORY_SIZE: 512
  TIMEOUT: 30

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Install devops-ai
      run: |
        python -m pip install --upgrade pip
        pip install cflabs-devops-ai
    
    - name: Deploy with devops-ai and GitHub secrets
      run: |
        devops-ai serverless deploy \
          --name ${{ env.LAMBDA_NAME }} \
          --region ${{ env.AWS_REGION }} \
          --memory ${{ env.MEMORY_SIZE }} \
          --timeout ${{ env.TIMEOUT }} \
          --environment prod \
          --env-vars "UploadsBucketName=${{ secrets.S3_DATA_BUCKET }},DbHost=${{ secrets.DB_HOST }},DbPort=${{ secrets.DB_PORT }},DbUser=${{ secrets.DB_USER }},DbPassword=${{ secrets.DB_PASSWORD }},DbName=${{ secrets.DB_NAME }},PineconeApiKey=${{ secrets.PINECONE_API_KEY }},OpenaiApiKey=${{ secrets.OPENAI_API_KEY }},VoyageApiKey=${{ secrets.VOYAGE_API_KEY }}"
```

## Environment Variable Sources Priority

1. **Command line `--env-vars`** (highest priority)
2. **`.env` file** (if exists)
3. **Environment variables** (lowest priority)

## Security Notes

- GitHub secrets are automatically masked in logs
- Sensitive values are displayed as `***` in console output
- Environment variables from `.env` files are shown in plain text (be careful with sensitive data)

## Troubleshooting

### Secret Not Found

If you see a warning like:
```
⚠️  Warning: GitHub secret 'SECRET_NAME' not found in environment variables
```

Check that:
1. The secret is properly set in GitHub repository settings
2. The secret name matches exactly (case-sensitive)
3. The workflow has access to the secret

### Parameter Override Errors

If you see SAM parameter override errors:
1. Ensure the parameter names match your SAM template
2. Check that values don't contain unescaped quotes
3. Verify the parameter format is correct

## Best Practices

1. **Use GitHub secrets for sensitive data**: API keys, passwords, database URLs
2. **Use direct values for non-sensitive data**: Environment names, feature flags
3. **Keep secrets organized**: Use consistent naming conventions
4. **Test locally**: Use `.env` files for local development
5. **Document your secrets**: Keep a list of required secrets in your README 