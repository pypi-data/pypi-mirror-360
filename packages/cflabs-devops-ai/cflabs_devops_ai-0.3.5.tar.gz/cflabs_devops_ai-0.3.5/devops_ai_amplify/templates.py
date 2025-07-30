"""Jinja2 templates for AWS Amplify deployment."""

from jinja2 import Template

# Amplify build configuration template
AMPLIFY_YML_TEMPLATE = Template("""version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: build
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
""")

# React-specific amplify.yml template with environment variables
REACT_AMPLIFY_YML_TEMPLATE = Template("""version: 1
frontend:
  phases:
    preBuild:
      commands:
        - echo "Installing dependencies..."
        - npm ci
    build:
      commands:
        - echo "Building React app..."
        - npm run build
  artifacts:
    baseDirectory: build
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
  customHeaders:
    - pattern: '**/*'
      headers:
        - key: 'Cache-Control'
          value: 'max-age=0, no-cache, no-store, must-revalidate'
        - key: 'Pragma'
          value: 'no-cache'
        - key: 'Expires'
          value: '0'
""")

# Next.js specific amplify.yml template
NEXTJS_AMPLIFY_YML_TEMPLATE = Template("""version: 1
frontend:
  phases:
    preBuild:
      commands:
        - echo "Installing dependencies..."
        - npm ci
    build:
      commands:
        - echo "Building Next.js app..."
        - npm run build
        - npm run export
  artifacts:
    baseDirectory: out
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
      - .next/cache/**/*
""")

# Vue.js specific amplify.yml template
VUE_AMPLIFY_YML_TEMPLATE = Template("""version: 1
frontend:
  phases:
    preBuild:
      commands:
        - echo "Installing dependencies..."
        - npm ci
    build:
      commands:
        - echo "Building Vue.js app..."
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
""")

# Angular specific amplify.yml template
ANGULAR_AMPLIFY_YML_TEMPLATE = Template("""version: 1
frontend:
  phases:
    preBuild:
      commands:
        - echo "Installing dependencies..."
        - npm ci
    build:
      commands:
        - echo "Building Angular app..."
        - npm run build --prod
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
""")

# Environment variables template
ENV_TEMPLATE = Template("""# Environment variables for {{ app_name }}
# Add your environment variables here
REACT_APP_API_URL={{ api_url }}
REACT_APP_ENVIRONMENT=production
NODE_ENV=production
""")

# Redirects template for SPA routing
REDIRECTS_TEMPLATE = Template("""# Redirects for Single Page Application
# This ensures that all routes are handled by index.html
/*    /index.html   200
""")

# Rewrites template for SPA routing
REWRITES_TEMPLATE = Template("""# Rewrites for Single Page Application
# This ensures that all routes are handled by index.html
{{ redirects }}
  from = "/*"
  to = "/index.html"
  status = "200"
""")

# GitHub Actions workflow template for Amplify
GITHUB_ACTIONS_AMPLIFY_TEMPLATE = Template("""name: Deploy to AWS Amplify

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

env:
  AWS_REGION: {{ region }}
  AMPLIFY_APP_ID: {{ app_id }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build application
      run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Deploy to Amplify
      run: |
        aws amplify start-job \
          --app-id ${{ env.AMPLIFY_APP_ID }} \
          --branch-name main \
          --job-type RELEASE
""")

# package.json template for React app
PACKAGE_JSON_TEMPLATE = Template("""{
  "name": "{{ app_name }}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/react": "^13.3.0",
    "@testing-library/user-event": "^13.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
""")

# README template for Amplify deployment
README_AMPLIFY_TEMPLATE = Template("""# {{ app_name }}

This React application is deployed using AWS Amplify.

## Deployment

This app is automatically deployed to AWS Amplify when changes are pushed to the main branch.

### App Information
- **App ID**: {{ app_id }}
- **App URL**: https://{{ app_id }}.amplifyapp.com
- **Branch URL**: https://{{ branch }}.{{ app_id }}.amplifyapp.com

### Local Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

### Environment Variables

The following environment variables are configured in Amplify:
- `REACT_APP_API_URL`: API endpoint URL
- `NODE_ENV`: Set to 'production' in Amplify

### Build Configuration

The build process is configured in `amplify.yml` and includes:
- Installing dependencies with `npm ci`
- Building the app with `npm run build`
- Serving static files from the `build` directory

### Branch Deployments

- **main/master**: Production deployment
- **feature branches**: Preview deployments (if enabled)

### Troubleshooting

If the build fails:
1. Check the Amplify console for build logs
2. Verify all dependencies are in `package.json`
3. Ensure the build script exists in `package.json`
4. Check for any environment variable issues
""")

# .gitignore template for React apps
GITIGNORE_TEMPLATE = Template("""# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# production
/build

# misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Amplify
amplify-config.json
amplify.yml

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
""")

# AWS Amplify CLI configuration template
AMPLIFY_CONFIG_TEMPLATE = Template("""{
  "app": {
    "name": "{{ app_name }}",
    "id": "{{ app_id }}",
    "repository": "{{ repository }}",
    "branch": "{{ branch }}"
  },
  "aws": {
    "region": "{{ region }}"
  },
  "build": {
    "framework": "react",
    "buildCommand": "npm run build",
    "outputDirectory": "build",
    "installCommand": "npm ci"
  }
}
""") 