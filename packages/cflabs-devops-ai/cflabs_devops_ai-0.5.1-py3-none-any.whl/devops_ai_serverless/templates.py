"""Jinja2 templates for devops-ai: container-based Flask Lambda deployment (no app.py changes required)."""

from jinja2 import Template

# Dockerfile for AWS Lambda Python container using aws_lambda_wsgi and lambda_entry.py
DOCKERFILE_TEMPLATE = Template("""
# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port for local testing (Lambda ignores this)
EXPOSE {{ port }}

# Build with: docker buildx build --platform linux/amd64 -t <your-image-name> .
                               
# install aws_lambda_wsgi
RUN pip install aws_lambda_wsgi

# Set the Lambda handler to the wrapper
CMD ["lambda_entry.lambda_handler"]
""")

# lambda_entry.py: wrapper to expose Flask app as Lambda handler (no app.py changes needed)
LAMBDA_ENTRY_TEMPLATE = Template("""
import aws_lambda_wsgi
from {{ app_module }} import {{ app_object }}

def lambda_handler(event, context):
    return aws_lambda_wsgi.response({{ app_object }}, event, context)
""")

# AWS SAM template for Lambda container deployment
SAM_TEMPLATE = Template("""AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Flask application deployed with devops-ai

Parameters:
  ImageUri:
    Type: String
    Description: URI of the container image
  Stage:
    Type: String
    Description: The deployment stage (e.g., dev, prod, staging)
    AllowedValues: [dev, prod, staging]
    Default: dev
  {% if env_vars %}
  {% for key, value in env_vars.items() %}
  {{ key }}:
    Type: String
    Description: Environment variable {{ key }}
    Default: "enter your value here"
  {% endfor %}
  {% endif %}

Globals:
  Function:
    Timeout: {{ timeout }}
    MemorySize: {{ memory_size }}
    Environment:
      Variables:
        PORT: {{ port }}
        STAGE: !Ref Stage
        {% if env_vars %}
        {% for key, value in env_vars.items() %}
        {{ key }}: !Ref {{ key }}
        {% endfor %}
        {% endif %}

Resources:
  FlaskFunction:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      CodeUri: .
      ImageUri: !Ref ImageUri
      Architectures:
        - x86_64
      Environment:
        Variables:
          PORT: {{ port }}
          STAGE: !Ref Stage
          {% if env_vars %}
          {% for key, value in env_vars.items() %}
          {{ key }}: !Ref {{ key }}
          {% endfor %}
          {% endif %}
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
        RootEvent:
          Type: Api
          Properties:
            Path: /
            Method: ANY

Outputs:
  FlaskApi:
    Description: "API Gateway endpoint URL for Flask function"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/prod/"
    Export:
      Name: !Sub "${AWS::StackName}-ApiUrl"

  FlaskFunction:
    Description: "Flask Lambda Function ARN"
    Value: !GetAtt FlaskFunction.Arn
    Export:
      Name: !Sub "${AWS::StackName}-FunctionArn"

  FlaskFunctionRole:
    Description: "Implicit IAM Role created for Flask function"
    Value: !GetAtt FlaskFunctionRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-FunctionRoleArn"
""")

# devops-ai config template
default_config_yaml = """# devops-ai configuration
app:
  module: {{ app_module }}
  object: {{ app_object }}
  port: {{ port }}

deployment:
  stack_name: {{ stack_name }}
  region: {{ region }}
  memory_size: {{ memory_size }}
  timeout: {{ timeout }}

container:
  base_image: {{ base_image }}
  working_dir: {{ working_dir }}
"""
CONFIG_TEMPLATE = Template(default_config_yaml)

# requirements.txt template (Flask + aws_lambda_wsgi)
REQUIREMENTS_TEMPLATE = Template("""# Flask application dependencies
Flask>=2.3.0
aws_lambda_wsgi

# Add your other dependencies below
# requests>=2.31.0
# boto3>=1.26.0
# sqlalchemy>=2.0.0
""")

# .dockerignore template
DOCKERIGNORE_TEMPLATE = Template("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

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

# Git
.git/
.gitignore

# devops-ai
cflabs-config.yaml
template.yml
.aws-sam/

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
""")

# samconfig.toml template
SAM_CONFIG_TEMPLATE = Template("""version = 0.1
[default]
[default.deploy]
[default.deploy.parameters]
stack_name = "{{ stack_name }}"
region = "{{ region }}"
confirm_changeset = false
capabilities = "CAPABILITY_NAMED_IAM"
parameter_overrides = "ImageUri={{ image_uri }}"
no_fail_on_empty_changeset = true
""") 