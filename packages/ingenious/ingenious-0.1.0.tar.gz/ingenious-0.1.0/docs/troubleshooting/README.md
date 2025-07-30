---
title: "Troubleshooting Guide"
layout: single
permalink: /troubleshooting/
sidebar:
  nav: "docs"
toc: true
toc_label: "Troubleshooting"
toc_icon: "wrench"
---

# 🔧 Troubleshooting Guide

This guide helps you resolve common issues when setting up and using Insight Ingenious - an enterprise-grade Python library for AI agent APIs with Microsoft Azure integrations. The library includes comprehensive debugging utilities to help diagnose and resolve deployment issues.

## � Quick Test Commands

### Hello World Test (bike-insights)
```bash
# The "Hello World" of Ingenious - try this first!
curl -X POST http://localhost:80/api/v1/chat \
   -H "Content-Type: application/json" \
   -d '{
   "user_prompt": "{\"stores\": [{\"name\": \"Hello Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"HELLO-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-01\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect introduction!\"}}], \"bike_stock\": []}], \"revision_id\": \"hello-1\", \"identifier\": \"world\"}",
   "conversation_flow": "bike-insights"
   }'
```

### Simple Alternative Test (classification-agent)
```bash
# If bike-insights seems too complex, try this simpler workflow
curl -X POST http://localhost:80/api/v1/chat \
   -H "Content-Type: application/json" \
   -d '{
   "user_prompt": "Analyze this feedback: Great product!",
   "conversation_flow": "classification-agent"
   }'
```

---

## �🚨 Common Setup Issues

### 1. Profile Validation Errors

**Symptoms**:
```
ValidationError: 9 validation errors for Profiles
0.chat_history.database_connection_string
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```

**Causes**:
- Environment variables not set or empty
- Missing required fields in profiles.yml
- Incorrect environment variable syntax

**Solutions**:

1. **Check your .env file**:
   ```bash
   # Make sure .env exists and has these minimum variables
   cat .env
   ```
   Should contain:
   ```env
   AZURE_OPENAI_API_KEY=your-actual-key
   AZURE_OPENAI_BASE_URL=https://your-endpoint.cognitiveservices.azure.com/
   ```

2. **Use minimal profiles.yml**:
   ```bash
   # Copy the minimal template
   cp ingenious/ingenious/ingenious_extensions_template/profiles.minimal.yml ./profiles.yml
   ```

3. **Set environment variables**:
   ```bash
   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
   ```

---

### 2. Server Port Issues

**Symptoms**:
- Server ignores `--port` parameter
- Server starts on port 80 instead of specified port

**Solutions**:

1. **Set port in environment**:
   ```bash
   export WEB_PORT=8081
   ```

2. **Or set in config.yml**:
   ```yaml
   web_configuration:
     port: 8081
   ```

3. **Check if port is available**:
   ```bash
   lsof -i :80  # Check what's using port 80
   ```

---

### 3. Module Import Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'ingenious_extensions'
```

**Solutions**:

1. **Make sure you're in the project root**:
   ```bash
   pwd  # Should be your project directory
   ls   # Should see ingenious_extensions/ folder
   ```

2. **Reinstall the library**:
   ```bash
   uv pip install -e ./ingenious
   ```

3. **Check Python path**:
   ```bash
   uv run python -c "import sys; print('\n'.join(sys.path))"
   ```

---

### 4. Workflow Execution Errors

**Symptoms**:
- "Class ConversationFlow not found"
- "Expecting value: line 1 column 1 (char 0)"

**Solutions**:

1. **Use correct workflow names**:
   ```bash
   # ✅ Correct (preferred)
   "conversation_flow": "bike-insights"

   # ✅ Also supported (legacy)
   "conversation_flow": "bike_insights"
   ```

2. **Check bike-insights input format**:
   ```bash
   # bike-insights needs JSON in user_prompt
   curl -X POST http://localhost:80/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "user_prompt": "{\"stores\": [...], \"revision_id\": \"test\", \"identifier\": \"test\"}",
       "conversation_flow": "bike-insights"
     }'
   ```

---

### 5. Azure SQL Database Issues

**Symptoms**:
- "pyodbc.InterfaceError: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] Data source name not found..."
- "Module pyodbc not found"
- Chat history not persisting between sessions
- Connection timeout errors

**Prerequisites Check**:

1. **Verify ODBC Driver is installed**:
   ```bash
   odbcinst -q -d
   # Should show: [ODBC Driver 18 for SQL Server]
   ```

2. **Install ODBC Driver (if missing)**:
   
   **On macOS**:
   ```bash
   brew tap microsoft/mssql-release
   brew install msodbcsql18 mssql-tools18
   ```
   
   **On Ubuntu/Debian**:
   ```bash
   curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
   curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
   apt-get update
   ACCEPT_EULA=Y apt-get install msodbcsql18
   ```

**Configuration Solutions**:

1. **Check environment variable is set**:
   ```bash
   echo $AZURE_SQL_CONNECTION_STRING
   # Should show your connection string
   ```

2. **Verify configuration files**:
   ```yaml
   # config.yml
   chat_history:
     database_type: "azuresql"
     database_name: "your_database_name"
   
   # profiles.yml  
   chat_history:
     database_connection_string: ${AZURE_SQL_CONNECTION_STRING:REQUIRED_SET_IN_ENV}
   ```

3. **Test connection directly**:
   ```bash
   uv run python -c "
   import pyodbc
   import os
   conn_str = os.getenv('AZURE_SQL_CONNECTION_STRING')
   if not conn_str:
       print('❌ AZURE_SQL_CONNECTION_STRING not set')
   else:
       try:
           conn = pyodbc.connect(conn_str)
           print('✅ Azure SQL connection successful')
           conn.close()
       except Exception as e:
           print(f'❌ Connection failed: {e}')
   "
   ```

4. **Test through Ingenious repository**:
   ```bash
   uv run python -c "
   import asyncio
   from ingenious.ingenious.dependencies import get_config
   from ingenious.ingenious.db.chat_history_repository import ChatHistoryRepository
   from ingenious.models.database_client import DatabaseClientType
   
   async def test():
       config = get_config()
       db_type = DatabaseClientType(config.chat_history.database_type)
       repo = ChatHistoryRepository(db_type=db_type, config=config)
       try:
           messages = await repo.get_thread_messages('test-thread')
           print(f'✅ Azure SQL repository working! (Found {len(messages)} messages)')
       except Exception as e:
           print(f'❌ Repository error: {e}')
   
   asyncio.run(test())
   "
   ```

**Common Connection String Issues**:

- **Missing driver**: Ensure `Driver={ODBC Driver 18 for SQL Server}` is in the connection string
- **Port issues**: Use `Server=tcp:your-server.database.windows.net,1433`
- **Encryption**: Include `Encrypt=yes;TrustServerCertificate=no`
- **Timeout**: Add `Connection Timeout=30` for slow networks

**Security Notes**:
- Never commit connection strings to version control
- Always use environment variables for database credentials
- Rotate passwords regularly for production deployments

---

## 🐛 Debugging Commands

### Check System Status
```bash
uv run ingen status
```

### List Available Workflows
```bash
uv run ingen workflows
```

### Check Specific Workflow Requirements
```bash
uv run ingen workflows bike-insights
```

### Test Installation
```bash
uv run python -c "import ingenious; print('✅ Ingenious imported successfully')"
```

### Check Configuration Loading
```bash
export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
uv run python -c "
import ingenious.config.config as config
try:
    cfg = config.get_config()
    print('✅ Configuration loaded successfully')
    print(f'Models: {len(cfg.models)}')
    print(f'Profile: {cfg.chat_history.database_type}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

---

## 🔍 Log Analysis

### Enable Debug Logging

1. **In config.yml**:
   ```yaml
   logging:
     root_log_level: debug
     log_level: debug
   ```

2. **Or via environment**:
   ```bash
   export LOGLEVEL=DEBUG
   export ROOTLOGLEVEL=DEBUG
   ```

### Common Log Messages

**✅ Good Signs**:
```
Profile loaded from file
Module ingenious_extensions.services.chat_services.multi_agent.conversation_flows.bike_insights.bike_insights found.
DEBUG: Successfully loaded conversation flow class
INFO:     Uvicorn running on http://0.0.0.0:80
```

**⚠️ Warning Signs**:
```
Profile not found at /path/to/profiles.yml
Template directory not found. Skipping...
Validation error in field
```

**❌ Error Signs**:
```
ModuleNotFoundError: No module named
ValidationError: 9 validation errors
Class ConversationFlow not found in module
```

---

## 🧪 Testing & Verification

### Minimal Test
```bash
# Test server is running
curl -s http://localhost:80/api/v1/health || echo "Server not responding"

# Test bike-insights workflow
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [], \"revision_id\": \"test\", \"identifier\": \"test\"}",
    "conversation_flow": "bike-insights"
  }' | jq '.message_id // "ERROR"'
```

### Full Integration Test
```bash
#!/bin/bash
set -e

echo "🧪 Running full integration test..."

# 1. Check environment
echo "1. Checking environment..."
[ -n "$AZURE_OPENAI_API_KEY" ] || { echo "❌ AZURE_OPENAI_API_KEY not set"; exit 1; }
[ -f "config.yml" ] || { echo "❌ config.yml not found"; exit 1; }
[ -f "profiles.yml" ] || { echo "❌ profiles.yml not found"; exit 1; }

# 2. Test import
echo "2. Testing Python import..."
uv run python -c "import ingenious; print('✅ Import OK')"

# 3. Test configuration
echo "3. Testing configuration..."
export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
uv run ingen status

# 4. Test workflows
echo "4. Testing workflows..."
uv run ingen workflows | grep -q "bike-insights" && echo "✅ bike-insights available"

echo "✅ All tests passed!"
```

---

## 📋 Environment Checklist

Before running Ingenious, ensure:

- [ ] Python 3.13+ installed
- [ ] uv package manager available
- [ ] Ingenious library installed: `uv pip install -e ./ingenious`
- [ ] Project initialized: `uv run ingen init`
- [ ] .env file created with Azure OpenAI credentials
- [ ] Environment variables set:
  - [ ] `AZURE_OPENAI_API_KEY`
  - [ ] `AZURE_OPENAI_BASE_URL`
  - [ ] `INGENIOUS_PROJECT_PATH`
  - [ ] `INGENIOUS_PROFILE_PATH`
- [ ] Port available (default 80)
- [ ] Network access to Azure OpenAI endpoint

---

## 🆘 Getting Help

### Self-Help Commands
```bash
# Get general help
uv run ingen --help

# Get command-specific help
uv run ingen serve --help
uv run ingen workflows --help

# Check system status
uv run ingen status

# List all workflows
uv run ingen workflows
```

### Common Solutions Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Import errors | `uv pip install -e ./ingenious` |
| Profile validation | Use `profiles.minimal.yml` template |
| Port not working | Set `WEB_PORT` environment variable |
| Workflow not found | Use `bike-insights` (preferred) or `bike_insights` (legacy) |
| JSON parse error | Escape quotes in `user_prompt` for bike-insights |
| Server won't start | Check port availability and config.yml |

### Still Need Help?

1. Check the logs for specific error messages
2. Review configuration files against templates
3. Test with minimal configuration first
4. Check the API documentation: `/docs/api/WORKFLOWS.md`
5. Verify environment variables are loaded correctly

---

## 🔄 Reset Instructions

If everything is broken, start fresh:

```bash
# 1. Clean slate
rm -rf ingenious_extensions/ tmp/ config.yml profiles.yml .env

# 2. Reinstall
uv pip install -e ./ingenious

# 3. Initialize
uv run ingen init

# 4. Configure
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 5. Set environment
export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml

# 6. Test
uv run ingen status
uv run ingen serve
```
