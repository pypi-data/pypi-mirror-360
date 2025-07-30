# React App - AWS Amplify Example

This is a sample React application that demonstrates how to deploy to AWS Amplify using the `devops-ai-amplify` module.

## Features

- 🚀 **Zero-config deployment** to AWS Amplify
- 🌿 **Branch-specific deployments** (main, develop, feature branches)
- 🔄 **Automatic builds** on code push
- 🎯 **Preview deployments** for pull requests
- 🔧 **Framework-specific configurations** (React, Next.js, Vue, Angular)
- 📱 **Responsive design** with modern UI
- 🔒 **SSL certificates** and custom domains

## Quick Start

### 1. Install the devops-ai-amplify module

```bash
pip install devops-ai
```

### 2. Create an Amplify app

```bash
devops-ai-amplify create-app \
  --name my-react-app \
  --repo https://github.com/username/my-react-app \
  --branch main \
  --region us-east-1
```

### 3. Configure the app for React

```bash
devops-ai-amplify configure-app \
  --framework react \
  --force
```

### 4. Deploy a specific branch

```bash
devops-ai-amplify deploy-branch \
  --branch main \
  --wait
```

## Available Commands

### App Management

- `create-app` - Create a new Amplify app and connect to GitHub
- `list-apps` - List all Amplify apps in a region
- `delete-app` - Delete an Amplify app
- `status` - Show app status and branches

### Branch Management

- `create-branch` - Create a new branch for deployment
- `list-branches` - List all branches for an app
- `delete-branch` - Delete a branch
- `deploy-branch` - Deploy a specific branch

### Configuration

- `configure-app` - Configure app with framework-specific settings

## Framework Support

The module supports multiple frameworks:

- **React** - Standard React apps with Create React App
- **Next.js** - Next.js applications with static export
- **Vue.js** - Vue.js applications
- **Angular** - Angular applications

## Environment Variables

Configure environment variables in the Amplify console or via the CLI:

```bash
# Example environment variables for React
REACT_APP_API_URL=https://api.example.com
REACT_APP_ENVIRONMENT=production
NODE_ENV=production
```

## Branch Strategy

- **main/master** - Production deployment
- **develop** - Staging deployment
- **feature branches** - Preview deployments (optional)

## Custom Domains

1. Add your custom domain in the Amplify console
2. Configure DNS settings
3. SSL certificates are automatically provisioned

## Troubleshooting

### Build Failures

1. Check the Amplify console for build logs
2. Verify all dependencies are in `package.json`
3. Ensure the build script exists in `package.json`
4. Check for environment variable issues

### Deployment Issues

1. Verify AWS credentials are configured
2. Check that the GitHub repository is accessible
3. Ensure the branch exists in the repository
4. Verify Amplify app permissions

## Example Workflow

```bash
# 1. Create app
devops-ai-amplify create-app --name my-app --repo https://github.com/user/repo

# 2. Configure for React
devops-ai-amplify configure-app --framework react

# 3. Create feature branch
devops-ai-amplify create-branch --branch feature/new-feature

# 4. Deploy feature branch
devops-ai-amplify deploy-branch --branch feature/new-feature

# 5. Check status
devops-ai-amplify status
```

## Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## App URLs

- **Main app**: `https://{app-id}.amplifyapp.com`
- **Branch-specific**: `https://{branch}.{app-id}.amplifyapp.com`
- **Custom domain**: `https://yourdomain.com`

## Contributing

This example demonstrates the capabilities of the `devops-ai-amplify` module. For more information, visit the [devops-ai repository](https://github.com/cosmicfusionlabs/devops-ai). 