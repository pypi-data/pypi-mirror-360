import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 React App Deployed with AWS Amplify</h1>
        <p>
          This React application was deployed using the devops-ai-amplify module!
        </p>
        <div className="features">
          <h2>Features:</h2>
          <ul>
            <li>✅ Automatic deployment from GitHub</li>
            <li>✅ Branch-specific deployments</li>
            <li>✅ Environment variable management</li>
            <li>✅ Custom domain support</li>
            <li>✅ SSL certificate management</li>
            <li>✅ Preview deployments for PRs</li>
          </ul>
        </div>
        <div className="links">
          <a
            className="App-link"
            href="https://github.com/cosmicfusionlabs/devops-ai"
            target="_blank"
            rel="noopener noreferrer"
          >
            View on GitHub
          </a>
        </div>
      </header>
    </div>
  );
}

export default App; 