---
title: "Quick Start Guide"
layout: single
permalink: /getting-started/
sidebar:
  nav: "docs"
toc: true
toc_label: "Quick Start Steps"
toc_icon: "rocket"
---

# Quick Start Guide

Get up and running with Insight Ingenious in minutes! This enterprise-grade Python library enables rapid deployment of AI agent APIs with seamless Microsoft Azure integrations. This guide will walk you through the essential steps to start building production-ready AI agent endpoints.

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** for package management
- **Azure OpenAI** account with API access

## Installation

For complete installation instructions, including optional dependencies for advanced features, see the [Installation Guide](./installation.md).

**Quick install for basic functionality:**

```bash
# Clone the repository
git clone https://github.com/Insight-Services-APAC/ingenious.git
cd ingenious

# Install the library
uv pip install -e .

# Initialize project structure for API deployment
uv run ingen init
```

### 1. Check Available Workflows

Before configuring anything, see what workflows are available:

```bash
# See all workflows and their requirements
uv run ingen workflows

# Check specific workflow requirements
uv run ingen workflows classification-agent
```

**Output Example:**
```
✅ Minimal Configuration
  • classification-agent: Route input to specialized agents (core library)
  • bike-insights: Sample domain-specific workflow (project template)

🔍 Requires Azure Search
  • knowledge-base-agent: Search knowledge bases (core library)

📊 Requires Database
  • sql-manipulation-agent: Execute SQL queries (core library)
```

## Basic Configuration

### 2. Configure Azure OpenAI

**Edit `config.yml`:**
```yaml
profile: dev
models:
  - model: "gpt-4.1-nano"  # Your deployment name
    api_type: azure
    api_version: "2024-08-01-preview"

chat_service:
  type: multi_agent

chat_history:
  database_type: sqlite
  database_path: "./.tmp/high_level_logs.db"
  memory_path: "./.tmp"
```

**Edit `profiles.yml`:**
```yaml
- name: "dev"
  models:
    - model: "gpt-4.1-nano"  # Must match config.yml
      api_key: "your-azure-openai-api-key"
      base_url: "https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2024-08-01-preview"
      deployment: "gpt-4.1-nano"
```

### 3. Set Environment Variables

```bash
export INGENIOUS_PROJECT_PATH="$(pwd)/config.yml"
export INGENIOUS_PROFILE_PATH="$(pwd)/profiles.yml"
```

## Test Your Setup

### 4. Start with Minimal Configuration

Test workflows that only need Azure OpenAI:

```bash
# Start the server
uv run ingen serve

# In another terminal, test the API
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Hello, please classify this message",
    "conversation_flow": "classification-agent"
  }'
```

### 5. Use the Web Interface

Once the server is running:

- **Main API**: http://localhost:80/docs
- **Chat Interface**: http://localhost:80/chainlit
- **Prompt Tuner**: http://localhost:80/prompt-tuner

### 6. Check Configuration Status

Verify your workflows are properly configured:

```bash
# Check all workflows
curl http://localhost:80/api/v1/workflows

# Check specific workflow
curl http://localhost:80/api/v1/workflow-status/classification-agent
```

## Next Steps

### Working? Great! Try These:

1. **Test different workflows**:
   ```bash
   # Try bike insights workflow
   curl -X POST http://localhost:80/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"user_prompt": "Analyze bike sales trends", "conversation_flow": "bike-insights"}'
   ```

2. **Explore the web interface** at http://localhost:80/chainlit

### Want More? Add Advanced Workflows:

- **🔍 Knowledge Base Search**: [Setup Azure Search](../configuration/README.md#azure-search-services)
- **📊 Database Queries**: [Setup Database Integration](../configuration/README.md#database-configuration)
- **📄 Document Processing**: [Setup Document Processing](../guides/document-processing/)

### Learn More:

- [**Workflow Requirements**](../workflows/README.md) - Understand what each workflow needs
- [**Configuration Guide**](../configuration/README.md) - Detailed configuration options
- [**API Integration**](../guides/api-integration.md) - Advanced API usage
- [**Creating Custom Extensions**](../extensions/README.md) - Build your own workflows and agents

## Troubleshooting

### Common Issues:

**❌ "Azure OpenAI API key not found"**
- Check `profiles.yml` has correct API key
- Verify `INGENIOUS_PROFILE_PATH` environment variable

**❌ "conversation_flow not set"**
- Ensure you specify `conversation_flow` in your API request
- Use `ingen workflows` to see available workflows

**❌ "Search service not configured"**
- You're trying to use `knowledge-base-agent` without Azure Search
- Either configure Azure Search or use minimal workflows like `classification-agent`

**❌ Server won't start**
- Check if port 80 is already in use
- Verify your `config.yml` file is valid YAML

### Get Help:

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Review [Configuration Guide](../configuration/README.md)
3. Check logs for specific error messages
4. Open an issue on GitHub

---

**🎉 Congratulations!** You now have Insight Ingenious running. Start with the minimal configuration workflows and gradually add more advanced features as needed.
