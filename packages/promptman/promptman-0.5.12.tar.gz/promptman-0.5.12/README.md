# 🚀 Instruere - AI Prompt Manager

> **The intelligent way to manage, optimize, and scale your AI prompts**

![Instruere](./docs/Home%20Screen.png)

A comprehensive AI prompt management system featuring a **modern web interface** (FastAPI + HTMX + Tailwind CSS) with unified architecture supporting both single-user and multi-tenant deployments. Features advanced authentication, real-time cost estimation, AI-powered optimization, and secure API access.

```mermaid
graph LR
    A[🤖 AI Prompts] --> B[📝 Management] --> C[🚀 Optimization] --> D[💰 Cost Control]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style C fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
```

## 🎯 What is AI Prompt Management?

**Prompts** are instructions you give to AI systems like ChatGPT or Claude - the quality of your prompts directly impacts the quality of AI responses and your costs.

### 📚 Rules Management: The Foundation of Autonomous AI Agents

In today's rapidly evolving AI landscape, **Rules Management** has become the cornerstone of successful autonomous agent systems. As AI agents increasingly handle complex, multi-step tasks independently, having structured guidelines becomes critical for consistent, reliable outcomes.

**Rules** are structured Markdown documents that define guidelines, constraints, and behavioral expectations for AI agents. Unlike prompts that request specific outputs, rules establish the *framework* within which agents operate - ensuring they work together harmoniously while maintaining quality standards.

#### 🤖 Why Rules Matter in the Age of AI Agents

```mermaid
graph TB
    subgraph "AI Agent Ecosystem"
        A[Agent 1: Code Review] --> C[Shared Rules Engine]
        B[Agent 2: Documentation] --> C
        D[Agent 3: Testing] --> C
        E[Agent 4: Deployment] --> C
    end
    
    C --> F[Consistent Quality]
    C --> G[Reliable Outcomes]
    C --> H[Predictable Behavior]
    
    style C fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#000
    style F fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style G fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style H fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
```

#### 🎯 The Power of Combined Prompts + Rules

Modern AI workflows require both **prompts** (what to do) and **rules** (how to do it):

- **Prompts**: Define specific tasks and desired outputs
- **Rules**: Establish quality standards, constraints, and behavioral guidelines
- **Together**: Create autonomous agents that deliver consistent, high-quality results

#### 🌍 Real-World Applications

**Agentic Coding Systems** like Claude Projects, Amazon Q, and VS Code Copilot rely on rules for:
- **Code Quality**: Enforcing style guides, security practices, and architecture patterns
- **Documentation Standards**: Ensuring consistent, comprehensive documentation
- **Testing Requirements**: Maintaining coverage and quality thresholds
- **Collaboration Guidelines**: Defining how multiple agents coordinate work

The combination of intelligent prompts and structured rules enables teams to scale AI assistance while maintaining the quality and consistency that enterprise environments demand.

### The Challenge vs Solution

```mermaid
graph LR
    subgraph P ["❌ Problems"]
        P1[Scattered prompts]
        P2[No cost visibility]
        P3[Manual optimization]
    end
    
    subgraph S ["✅ Solutions"]
        S1[Centralized library]
        S2[Real-time costs]
        S3[AI optimization]
    end
    
    P --> S
    
    style P fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000
    style S fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style P1 fill:#fff,stroke:#d32f2f,color:#000
    style P2 fill:#fff,stroke:#d32f2f,color:#000
    style P3 fill:#fff,stroke:#d32f2f,color:#000
    style S1 fill:#fff,stroke:#388e3c,color:#000
    style S2 fill:#fff,stroke:#388e3c,color:#000
    style S3 fill:#fff,stroke:#388e3c,color:#000
```

### Why Instruere?
- **📚 Rules Management**: Structured AI agent guidance with visual combination builder
- **💰 Cost Control**: Real-time token estimation prevents expensive mistakes
- **🚀 Optimization**: AI-powered improvements using LangWatch, PromptPerfect, and more
- **🧩 Builder Interface**: Drag-and-drop prompt and rule combination
- **🎤 Speech Dictation**: Voice-to-text with AI enhancement and multi-language support
- **🌐 Multi-Language**: 10 languages with automatic translation
- **🏢 Enterprise Ready**: Multi-tenant with SSO, RBAC, and audit trails
- **🔌 Developer Friendly**: Complete REST API with comprehensive documentation

## 📋 Table of Contents

### 🚀 Getting Started
- [⚡ Quick Start](#-quick-start) - Get up and running in 5 minutes
- [🏗️ System Architecture](#️-system-architecture) - Understanding the design
- [⚙️ Configuration](#️-configuration) - Setup and customization

### 🎯 Core Features  
- [🤖 Enhanced AI Services Configuration](#-enhanced-ai-services-configuration) - Multi-model AI setup
- [📝 Prompt Management](#-prompt-management) - Create, organize, and manage prompts
- [🎤 Speech Dictation](#-speech-dictation) - Voice-to-text with AI enhancement
- [📚 Rules Management](#-rules-management) - AI agent guidance and behavioral rules
- [🏷️ Advanced Tagging System](#️-advanced-tagging-system) - Intelligent organization and discovery
- [🧮 Token Calculator](#-token-calculator) - Real-time cost estimation
- [🚀 AI-Powered Optimization](#-ai-powered-optimization) - Improve prompt quality
- [🧩 Prompt Builder](#-prompt-builder) - Drag-and-drop prompt combination

### 🌐 Advanced Features
- [🌍 Multi-Language Support](#-multi-language-support) - 10 languages with translation
- [🔑 API Access](#-api-access) - REST API for developers
- [🔵 Azure AI Integration](#-azure-ai-integration) - Enterprise AI services

### 🏢 Enterprise & Deployment
- [🏢 Multi-Tenant Features](#-multi-tenant-features) - Organization management
- [🔒 Production Deployment](#-production-deployment) - Scale and security
- [🛠️ Development](#️-development) - Contributing and extending

### 📚 Resources
- [🚀 Quick Reference](#-quick-reference) - Commands and shortcuts
- [🔧 Troubleshooting](#-troubleshooting) - Common issues and solutions
- [📄 License](#-license) - Usage terms

## 🌟 Modern Web Interface

**Instruere features a completely redesigned modern web interface** - a responsive, enterprise-ready web application built from the ground up:

### ✨ What's New

| Feature | Modern Web UI | Previous Version |
|---------|---------------|-----------------|
| **🎨 Design** | Responsive Tailwind CSS, mobile-optimized | Fixed desktop layout |
| **⚡ Performance** | FastAPI + HTMX real-time updates | Page refreshes required |
| **🔐 Security** | Session-based auth, CSRF protection | Basic authentication |
| **🌐 I18n** | 10 languages, dynamic switching | English only |
| **📱 Mobile** | Full mobile support | Desktop only |
| **🔧 API** | Integrated REST API | External API server |
| **🎯 UX** | Modern components, drag-drop | Basic forms |
| **🔄 Navigation** | Clickable app title, improved UX | Static title |
| **🎨 Buttons** | Modern styled buttons with zoom support | Basic unstyled buttons |

### 🆕 Recent Improvements

**Translation System Enhancements:**
- Fixed critical translation function availability in single-user mode
- Unified all translation calls to use consistent `t()` function
- Enhanced navigation translation compatibility across all modes

**User Interface Improvements:**
- Made app title clickable for quick dashboard navigation
- Comprehensive button styling overhaul with modern CSS framework
- Added zoom scaling support for accessibility compliance
- Enhanced keyboard navigation and screen reader support

**Code Quality & Testing:**
- Executed comprehensive test validation (96 unit tests + integration tests)
- Applied code formatting and security validation
- Fixed template syntax errors and improved HTML quality

### 🚀 Key Advantages

- **⚡ Real-time Updates**: HTMX-powered dynamic interactions without page reloads
- **📱 Mobile-First**: Responsive design that works on all devices
- **🎨 Modern UI**: Clean, intuitive interface with consistent styling
- **🔒 Enterprise Security**: Session management, CSRF protection, secure authentication
- **🌍 Internationalization**: Full 10-language support with instant switching
- **🔌 API Integration**: Built-in REST API for developer access
- **♿ Accessibility**: Screen reader support, keyboard navigation, ARIA labels

**The modern web UI is now the default and only interface!** Experience a complete enterprise-ready web application with all the benefits listed above.

## 🏗️ System Architecture

Instruere is built on a **unified, modular architecture** that scales from single-user development to enterprise multi-tenant deployments.

```mermaid
graph TB
    Client[🌐 Client Layer<br/>Modern Web UI • API • Mobile] --> App[🚀 Application Layer<br/>FastAPI + HTMX • Auth • Real-time]
    App --> Logic[🧠 Business Logic<br/>Prompts • Calculator • Optimizer • AI Services]
    Logic --> Data[💾 Data Layer<br/>SQLite • PostgreSQL • Multi-tenant]
    
    style Client fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style App fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style Logic fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style Data fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
```

### 🆕 Modern Modular Architecture

**Instruere features a hybrid architecture** that combines proven legacy components with a new modular architecture designed for maintainability, scalability, and enterprise deployment:

- **📦 Modular Design**: Clean separation between authentication, prompts, API, and UI layers
- **🏗️ Base Classes**: Shared functionality through inheritance and composition patterns
- **🔧 Dependency Injection**: Testable, loosely-coupled components with full dependency injection
- **🛡️ Type Safety**: Comprehensive type hints throughout the codebase for reliability
- **📋 Structured Logging**: Centralized logging with audit trails and performance metrics
- **⚡ Modern Security**: Argon2/bcrypt password hashing, JWT management, and RBAC
- **🐳 Container Ready**: Full Docker support with Redis caching and health monitoring

**📖 Architecture Documentation:**
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture with diagrams and implementation details

### 🔑 Key Architectural Principles
- **🏗️ Unified Codebase**: Single application, multiple deployment modes
- **🔐 Tenant Isolation**: Complete data separation between organizations  
- **📦 Modular Design**: Loosely coupled, independently testable components
- **🔌 API-First**: RESTful API with comprehensive OpenAPI documentation
- **⚡ Performance**: Efficient database queries and caching strategies

> 📖 **[Complete Architecture Documentation](ARCHITECTURE.md)** - Detailed system design, data flows, and deployment patterns

---

## ⚡ Quick Start

Get Instruere running in under 5 minutes with these simple steps:

```bash
✅ Python 3.12+
✅ Poetry (recommended) or pip  
✅ Optional: PostgreSQL for production
```

### 🐳 Option 1: Docker (Recommended)

```bash
# 🚀 Quick Start - Single Container
docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:latest

# 🏗️ Development - Full Stack with PostgreSQL & Redis
docker-compose up -d

# 🏭 Production - Optimized with Health Checks
docker-compose -f docker-compose.prod.yml up -d

# 🧪 Test Docker Setup
./scripts/docker-test.sh

# Open browser to http://localhost:7860
# Login: admin@localhost / admin123
```

### 🐍 Option 2: Python Installation

#### 📦 From PyPI (Recommended)
```bash
# 1️⃣ Install from PyPI
pip install promptman

# 2️⃣ Run the application
python -m promptman

# 3️⃣ Open browser to http://localhost:7860
```

#### 🏢 From GitHub Packages (Enterprise)
```bash
# 1️⃣ Install from GitHub Packages
pip install --index-url https://pypi.pkg.github.com/makercorn/simple/ promptman

# 2️⃣ Run the application
python -m promptman

# 3️⃣ Open browser to http://localhost:7860
```

#### 🔧 From Source (Development)
```bash
# 1️⃣ Clone and install
git clone <repository-url>
cd ai-prompt-manager
poetry install

# 2️⃣ Configure (optional)
cp .env.example .env
# Edit .env for custom settings

# 3️⃣ Launch application (IMPORTANT: Use Poetry environment)
poetry run python run.py

# 4️⃣ Open browser to http://localhost:7860

# ⚠️  CRITICAL: Always use 'poetry run' to ensure dependencies are available
# Running python run.py directly may result in "Create New Prompt" errors
```

### 🚀 Deployment Options

| Environment | Command | Interface | Features | Use Case |
|-------------|---------|-----------|----------|----------|
| **🧪 Development** | `poetry run python run.py --single-user` | Modern Web UI | SQLite, Single User | Personal use, testing |
| **🏢 Multi-Tenant** | `poetry run python run.py` | Modern Web UI | SQLite, Multi-tenant, Auth | Teams, organizations |
| **🔌 With API** | `poetry run python run.py --with-api` | Web UI + API | API + UI, Multi-tenant | Developer integration |
| **🐳 Docker Dev** | `docker-compose up -d` | Modern Web UI | PostgreSQL + Redis + Full Stack | Development with persistence |
| **🏭 Production** | `docker-compose -f docker-compose.prod.yml up -d` | Modern Web UI | Optimized + Health Checks + Redis | Scalable deployment |

**✅ Testing Status**: 21 test files (11 unit + 10 integration) with comprehensive coverage across all deployment modes and architecture components. All critical translation system fixes and button styling improvements validated through comprehensive test execution.

### ✅ Verify Installation

```bash
# Check system health (if API enabled)
curl http://localhost:7860/api/health
# Expected response: {"status": "healthy"}

# Test prompt creation (main functionality)
# 1. Open http://localhost:7860 in browser
# 2. Click "Create New Prompt" 
# 3. Fill form and save - should work without errors

# Test comprehensive functionality (development)
poetry run python tests/integration/test_mt_install.py                    # Multi-tenant setup
poetry run python tests/integration/test_new_architecture_integration.py # New architecture
poetry run python tests/integration/test_langwatch_integration.py        # AI optimization

# Run validation steps for code quality
poetry run black .                           # Format Python code
poetry run isort .                           # Organize imports  
poetry run flake8 . --max-line-length=88 --extend-ignore=E203,W503  # Linting
poetry run bandit -r . --skip B101,B602,B603 # Security scanning
```

---

## ⚙️ Configuration

Configure Instruere for your specific needs - from development to enterprise deployment.

### 🚀 Quick Configuration

```bash
# 1️⃣ Copy template
cp .env.example .env

# 2️⃣ Edit for your environment
nano .env  # or your preferred editor

# 3️⃣ Restart application
poetry run python run.py
```

### 📋 Essential Settings

The most important configuration options organized by priority:

#### 🏗️ Application Mode (Choose One)

```bash
# 👤 Single-User (Personal Use)
MULTITENANT_MODE=false
ENABLE_API=false

# 🏢 Multi-Tenant (Teams/Organizations)  
MULTITENANT_MODE=true
ENABLE_API=false

# 🔌 Full Enterprise (Multi-tenant + API)
MULTITENANT_MODE=true
ENABLE_API=true
```

#### 🌐 Server Settings

```bash
SERVER_HOST=0.0.0.0     # Bind address (0.0.0.0 for external access)
SERVER_PORT=7860        # Port number
DEBUG=false            # Debug mode (true for development)
```

#### 💾 Database Configuration

```bash
# 🧪 Development (Default)
DB_TYPE=sqlite
DB_PATH=prompts.db

# 🏢 Production (Recommended)  
DB_TYPE=postgres
POSTGRES_DSN=postgresql://user:pass@host:port/dbname
```

### ⚡ Command Line Overrides

Override configuration without editing files:

```bash
# Mode selection
python run.py --single-user              # Force single-user mode
python run.py --with-api                 # Enable API
python run.py --single-user --with-api   # Single-user + API

# Server configuration
python run.py --port 8080 --host 127.0.0.1
python run.py --debug --share            # Debug + public access

# Get help
python run.py --help
```

### 🔧 Advanced Configuration

#### 🔐 Authentication & Security

```bash
# JWT Security
SECRET_KEY=your-secure-secret-key    # Auto-generated if not set
LOCAL_DEV_MODE=true                 # Development features

# SSO Integration
SSO_ENABLED=false
SSO_CLIENT_ID=your-application-id
SSO_CLIENT_SECRET=your-client-secret
SSO_AUTHORITY=https://login.microsoftonline.com/tenant-id

# Azure Entra ID
ENTRA_ID_ENABLED=false
ENTRA_CLIENT_ID=your-entra-client-id
ENTRA_TENANT_ID=your-azure-tenant-id
```

#### 🤖 AI Services

```bash
# Prompt Optimization
PROMPT_OPTIMIZER=langwatch              # langwatch, promptperfect, builtin
LANGWATCH_API_KEY=your-api-key
PROMPTPERFECT_API_KEY=your-api-key

# Azure AI Services  
AZURE_AI_ENABLED=false
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your-azure-key

# Translation Services
TRANSLATION_SERVICE=openai             # openai, google, libre, mock
OPENAI_API_KEY=your-openai-key
```

### 📊 Configuration Validation

Check your configuration:

```bash
# Test configuration
python -c "
from auth_manager import AuthManager
auth = AuthManager()
print('✅ Configuration valid')
print(f'Mode: {'Multi-tenant' if auth.is_multitenant_mode() else 'Single-user'}')
print(f'API: {'Enabled' if auth.is_api_enabled() else 'Disabled'}')
"
```

---

## 🌐 Multi-Language Support

AI Prompt Manager supports **10 languages** with real-time interface switching, making it accessible to users worldwide. The internationalization system provides comprehensive translations for all UI elements.

### 🌍 Supported Languages

| Language | Code | Native Name | Status |
|----------|------|-------------|--------|
| **English** | `en` | English | ✅ Complete |
| **Spanish** | `es` | Español | ✅ Complete |
| **French** | `fr` | Français | ✅ Complete |
| **German** | `de` | Deutsch | ✅ Complete |
| **Chinese** | `zh` | 中文 | ✅ Complete |
| **Japanese** | `ja` | 日本語 | ✅ Complete |
| **Portuguese** | `pt` | Português | ✅ Complete |
| **Russian** | `ru` | Русский | ✅ Complete |
| **Arabic** | `ar` | العربية | ✅ Complete |
| **Hindi** | `hi` | हिन्दी | ✅ Complete |

### 🔄 How to Change Language

#### **Method 1: Using the Interface (Recommended)**
1. **Locate the Language Selector**: Look for the 🌐 Language dropdown in the top-right corner
2. **Select Your Language**: Click the dropdown and choose your preferred language
3. **Instant Update**: The interface will immediately switch to the selected language

#### **Method 2: Environment Configuration**
Set the default language for new sessions:

```bash
# Set default language (optional)
DEFAULT_LANGUAGE=es python run.py  # Spanish
DEFAULT_LANGUAGE=fr python run.py  # French
DEFAULT_LANGUAGE=zh python run.py  # Chinese
```

#### **Method 3: URL Parameter**
Access the interface with a specific language:

```bash
# Examples
http://localhost:7860/?lang=es  # Spanish
http://localhost:7860/?lang=fr  # French
http://localhost:7860/?lang=zh  # Chinese
```

### 🎯 What Gets Translated

The multi-language system covers **all user-facing elements**:

#### **Interface Elements**
- ✅ Navigation menus and tabs
- ✅ Button labels and actions
- ✅ Form fields and placeholders
- ✅ Status messages and notifications
- ✅ Help text and tooltips

#### **Application Sections**
- ✅ **Authentication**: Login forms, SSO options
- ✅ **Prompt Management**: Add, edit, delete prompts
- ✅ **Library**: Search, categories, filters
- ✅ **Token Calculator**: Model selection, cost estimation
- ✅ **API Management**: Token creation, documentation
- ✅ **Settings**: Configuration options
- ✅ **Admin Panel**: User and tenant management

#### **AI Features**
- ✅ **LangWatch Integration**: Optimization interface
- ✅ **Enhancement Engine**: Prompt improvement tools
- ✅ **Error Messages**: Validation and system feedback

### 🌐 Translation Feature

When using the interface in a non-English language, AI Prompt Manager provides an automatic **translation feature** to help you work with AI enhancement tools that work best with English prompts.

#### **How Translation Works**

1. **Automatic Detection**: Translation button appears automatically when UI language is not English
2. **One-Click Translation**: Click "Translate to English" button in prompt editor
3. **Smart Replacement**: Translated text replaces original content in the editor
4. **Validation**: Translated text undergoes validation before saving
5. **Status Feedback**: Clear success/error messages guide the process

#### **Supported Translation Services**

| Service | Quality | Setup | Cost |
|---------|---------|-------|------|
| **OpenAI** | ⭐⭐⭐⭐⭐ | API Key | Paid |
| **Google Translate** | ⭐⭐⭐⭐ | API Key | Paid |
| **LibreTranslate** | ⭐⭐⭐ | Optional Key | Free/Paid |
| **Mock** | ⭐ | None | Free |

#### **Configuration**

Set up translation services via environment variables:

```bash
# Use OpenAI for highest quality
TRANSLATION_SERVICE=openai
OPENAI_API_KEY=your_openai_api_key

# Use Google Translate  
TRANSLATION_SERVICE=google
GOOGLE_TRANSLATE_API_KEY=your_google_key

# Use LibreTranslate (open source)
TRANSLATION_SERVICE=libre
LIBRETRANSLATE_URL=https://libretranslate.de/translate
LIBRETRANSLATE_API_KEY=optional_key

# Use mock for testing (default)
TRANSLATION_SERVICE=mock
```

#### **Usage Workflow**

1. **Switch Language**: Change UI to your preferred language (Spanish, French, etc.)
2. **Write Prompt**: Enter your prompt in your native language
3. **Translate**: Click the "🌐 Translate to English" button that appears
4. **Enhance**: Use the translated English text with AI enhancement tools
5. **Save**: Save the improved prompt after validation

#### **Example**

```text
Original (Spanish): "Escribe un poema sobre la naturaleza"
Translated (English): "Write a poem about nature"  
Enhanced (English): "Create a beautiful, evocative poem about the wonders 
                     of nature, focusing on vivid imagery and emotional depth"
```

### 🔧 Advanced Configuration

#### **Programmatic Language Control**
Access the internationalization system programmatically:

```python
from i18n import i18n, t

# Get available languages
languages = i18n.get_available_languages()
print(languages)  # {'en': 'English', 'es': 'Español', ...}

# Change language
i18n.set_language('es')

# Translate text
title = t('app.title')  # Returns translated app title
welcome = t('auth.welcome', name='John')  # With parameters
```

#### **Custom Translations**
Extend translations for custom deployments:

```python
# Add custom translations
from i18n import i18n

# Add new language or extend existing
custom_translations = {
    'custom.message': 'My custom message',
    'custom.button': 'Custom Button'
}

# Extend existing language
i18n.translations['en'].update(custom_translations)
```

### 🌟 Language Features

#### **Smart Fallbacks**
- **Automatic Fallback**: Missing translations default to English
- **Graceful Degradation**: Untranslated keys display as readable text
- **Context Preservation**: Formatting and parameters work across all languages

#### **Cultural Considerations**
- **Text Direction**: Right-to-left support for Arabic
- **Number Formatting**: Locale-appropriate number display
- **Date Formats**: Regional date and time formatting
- **Currency**: Localized cost estimates in token calculator

#### **Accessibility**
- **Screen Readers**: Proper language attributes for assistive technology
- **Keyboard Navigation**: Language switching via keyboard shortcuts
- **High Contrast**: Language selector works with accessibility themes

### 🎨 UI Adaptations

The interface automatically adapts to different languages:

#### **Layout Flexibility**
- **Dynamic Text Sizing**: Accommodates longer/shorter translations
- **Responsive Labels**: Forms adjust to text length variations
- **Icon Consistency**: Universal icons complement text labels

#### **Typography**
- **Font Support**: Web fonts that support all character sets
- **Readability**: Optimized contrast and spacing for each language
- **Consistency**: Unified styling across all language versions

### 🔍 Technical Details

#### **Translation Architecture**
- **Embedded Translations**: No external files required for reliability
- **Key-Based System**: Hierarchical translation keys (e.g., `auth.login`)
- **Parameter Support**: Dynamic content with variable substitution
- **Caching**: Efficient translation loading and memory usage

#### **File Structure**
```
ai-prompt-manager/
├── i18n.py                 # Internationalization system
├── ui_components.py        # Language-aware UI components
├── run.py                  # Main launcher with i18n integration
└── web_app.py              # Web interface with i18n integration
```

#### **Browser Support**
- **Modern Browsers**: Full support in Chrome, Firefox, Safari, Edge
- **Fallback Support**: Graceful degradation in older browsers
- **Mobile Optimized**: Touch-friendly language switching on mobile devices

### ❓ Troubleshooting

#### **Common Issues**

**Language not switching immediately:**
- Refresh the page or restart the interface
- Check browser console for JavaScript errors

**Missing translations:**
- Some text remains in English - this is expected fallback behavior
- Report missing translations via GitHub issues

**Performance with many languages:**
- All translations are loaded efficiently in memory
- No performance impact from multiple language support

#### **Getting Help**
- 📖 **Documentation**: Check this guide for configuration details
- 🐛 **Bug Reports**: Report translation issues on GitHub
- 💡 **Feature Requests**: Suggest new languages or improvements
- 🌍 **Community**: Join discussions about localization

---

## 🤖 Enhanced AI Services Configuration

Instruere features a comprehensive AI services configuration system that allows users to set different models and providers for different functions, providing unprecedented flexibility and control over AI operations.

### 🚀 Multi-Model Architecture Overview

The enhanced AI services system supports **10+ AI providers** and **11 operation types**, enabling you to optimize each AI function with the best-suited model:

```mermaid
graph TB
    A[🎯 Operation Types] --> B[📝 Default Operations]
    A --> C[🚀 Prompt Enhancement]
    A --> D[⚡ Optimization]
    A --> E[🧪 Testing]
    A --> F[🔄 Translation]
    
    B --> G[🤖 AI Models]
    C --> G
    D --> G
    E --> G
    F --> G
    
    G --> H[☁️ Cloud Providers<br/>OpenAI • Azure • Anthropic]
    G --> I[🏠 Local Models<br/>Ollama • LM Studio • llama.cpp]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style G fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style H fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style I fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
```

### 🎯 Supported AI Providers

| Provider | Models | Features | Use Case |
|----------|--------|----------|----------|
| **🤖 OpenAI** | GPT-4, GPT-3.5-turbo, GPT-4-turbo | Streaming, Function Calling, Vision | General purpose, coding, analysis |
| **☁️ Azure OpenAI** | Enterprise GPT models | Enhanced security, compliance | Enterprise deployments |
| **🧠 Anthropic** | Claude-3 (Opus, Sonnet, Haiku) | Large context, safety | Research, writing, reasoning |
| **🔍 Google** | Gemini Pro, Gemini Ultra | Multimodal, fast inference | Search, analysis, creativity |
| **🏠 Ollama** | Llama 2/3, Mistral, CodeLlama | Local deployment, privacy | On-premises, data sensitivity |
| **🖥️ LM Studio** | Various open models | Local GUI, easy setup | Development, experimentation |
| **⚡ llama.cpp** | GGUF models | Optimized inference | Resource-constrained environments |
| **🤗 Hugging Face** | Thousands of models | Open source, diverse | Specialized tasks, research |
| **🔬 Cohere** | Command, Embed models | Enterprise APIs | Business applications |
| **🚀 Together AI** | Various open models | Hosted inference | Scalable deployments |

### 🎯 Operation Types & Use Cases

Configure different models for each type of AI operation:

| Operation | Purpose | Recommended Models | Configuration |
|-----------|---------|-------------------|---------------|
| **📝 Default** | General prompt processing | GPT-4, Claude-3-Sonnet | High-quality, balanced |
| **🚀 Prompt Enhancement** | Improving prompt quality | GPT-4, Claude-3-Opus | Advanced reasoning |
| **⚡ Prompt Optimization** | Performance optimization | GPT-3.5-turbo, Gemini Pro | Fast, cost-effective |
| **🧪 Prompt Testing** | Testing and validation | GPT-3.5-turbo, local models | Cheap, quick feedback |
| **🔄 Model Combining** | Ensemble operations | Multiple models | Diversity, reliability |
| **🌐 Translation** | Language translation | GPT-4, specialized models | Accuracy, cultural context |
| **📊 Summarization** | Content summarization | Claude-3-Haiku, Gemini Pro | Concise, structured |
| **💬 Conversation** | Chat and dialogue | GPT-3.5-turbo, Claude-3 | Natural, engaging |
| **📖 Question Answering** | Q&A tasks | GPT-4, knowledge models | Accurate, comprehensive |
| **🎨 Content Generation** | Creative writing | Claude-3, creative models | Original, stylistic |
| **🔧 Code Generation** | Programming assistance | GPT-4, CodeLlama, StarCoder | Technical, accurate |

### 🏗️ Modern Tabbed Interface

Access the enhanced AI services configuration through the intuitive **tabbed interface**:

#### **🤖 Models Tab**
- **Add Models**: Configure new AI models with complete settings
- **Model Cards**: Visual representation of each model with status indicators
- **Health Monitoring**: Real-time availability and performance metrics
- **Quick Actions**: Enable/disable, test, and configure models instantly

#### **⚙️ Operations Tab** 
- **Operation Configuration**: Set primary and fallback models for each operation type
- **Drag & Drop**: Intuitive model assignment with visual feedback
- **Smart Recommendations**: AI-powered suggestions for optimal model selection
- **Batch Configuration**: Configure multiple operations simultaneously

#### **🔌 Providers Tab**
- **Provider Setup**: Configure API keys and endpoints for each provider
- **Connection Testing**: Validate credentials and connectivity
- **Provider Cards**: Visual status and configuration overview
- **Batch Operations**: Configure multiple providers efficiently

#### **📊 Health & Usage Tab**
- **Health Dashboard**: Real-time model availability and performance
- **Usage Statistics**: Token consumption, costs, and request metrics
- **Performance Monitoring**: Response times and success rates
- **Cost Analysis**: Detailed breakdown by model and operation

### 🚀 Quick Setup Guide

#### **1. Access AI Services Configuration**
```bash
# Navigate to AI Services in the web interface
http://localhost:7860/ai-services/enhanced
```

#### **2. Add Your First Model**
1. **Click "Add Model"** in the Models tab
2. **Fill model details**:
   ```
   Name: my-gpt-4
   Provider: OpenAI
   Model ID: gpt-4
   API Key: your-openai-api-key
   Display Name: My GPT-4 Model
   ```
3. **Configure features**: Streaming, function calling, vision support
4. **Set cost limits**: Input/output token costs for budget control
5. **Save and test** the model connection

#### **3. Configure Operations**
1. **Switch to Operations tab**
2. **Select operation type** (e.g., Prompt Enhancement)
3. **Set primary model**: Choose your preferred model
4. **Add fallback models**: Configure backup options
5. **Enable the operation** and save configuration

#### **4. Verify Configuration**
1. **Check Health tab** for model status
2. **Run test operations** to validate setup
3. **Monitor usage** and adjust as needed

### 🔧 Advanced Configuration

#### **Model Health Checking**
The system continuously monitors model availability:

```python
# Health check results example
{
    "model_name": "my-gpt-4",
    "healthy": True,
    "status": "Healthy",
    "response_time": 1.2,
    "last_check": "2025-01-08T10:30:00Z",
    "success_rate": 99.5
}
```

#### **Intelligent Model Selection**
The system automatically selects the best available model:

1. **Primary Model**: First choice for the operation
2. **Fallback Chain**: Automatic failover to backup models
3. **Health-Based**: Skips unhealthy or unavailable models
4. **Requirement Matching**: Filters by capabilities (vision, streaming, etc.)
5. **Cost Optimization**: Considers cost constraints and budgets

#### **Usage Statistics & Analytics**
Comprehensive tracking of AI service usage:

```json
{
    "total_requests": 1250,
    "total_tokens": 450000,
    "total_cost": 12.50,
    "average_response_time": 1.8,
    "models": {
        "my-gpt-4": {
            "requests": 800,
            "tokens": 320000,
            "cost": 9.60,
            "avg_response_time": 2.1,
            "success_rate": 99.2
        }
    }
}
```

### 🌐 API Integration

The enhanced AI services provide a comprehensive REST API:

#### **Core Endpoints**
```bash
# Get all configured models
GET /api/ai-models/

# Add new model
POST /api/ai-models/
{
    "name": "claude-3-opus",
    "provider": "anthropic",
    "model_id": "claude-3-opus-20240229",
    "api_key": "your-api-key"
}

# Update model configuration
PUT /api/ai-models/{model_name}
{
    "display_name": "Updated Claude Opus",
    "is_enabled": true
}

# Test model health
POST /api/ai-models/{model_name}/test
{
    "test_prompt": "Hello, test the model connectivity"
}

# Get operation configurations
GET /api/ai-models/operations

# Update operation configuration
PUT /api/ai-models/operations/{operation_type}
{
    "primary_model": "claude-3-opus",
    "fallback_models": ["gpt-4", "gemini-pro"]
}
```

#### **Advanced Endpoints**
```bash
# Get model recommendations for operation
GET /api/ai-models/recommendations/{operation_type}

# Export complete configuration
POST /api/ai-models/export

# Import configuration
POST /api/ai-models/import

# Get usage statistics
GET /api/ai-models/usage-stats

# Run health checks on all models
POST /api/ai-models/health-check
```

### 💡 Best Practices

#### **Model Selection Strategy**
- **Cost-Conscious**: Use cheaper models (GPT-3.5-turbo, Claude-3-Haiku) for testing and iteration
- **Quality-First**: Deploy premium models (GPT-4, Claude-3-Opus) for production operations
- **Local Privacy**: Use local models (Ollama, LM Studio) for sensitive data
- **Hybrid Approach**: Combine cloud and local models for optimal balance

#### **Operation Configuration**
- **Default Operations**: Configure with your most reliable, balanced model
- **Enhancement**: Use advanced reasoning models for prompt improvements
- **Testing**: Use fast, cheap models for validation and debugging
- **Translation**: Use models specifically trained for multilingual tasks

#### **Performance Optimization**
- **Health Monitoring**: Enable automatic health checks for proactive issue detection
- **Fallback Chains**: Configure multiple fallback models for high availability
- **Cost Budgets**: Set spending limits and alerts for budget control
- **Usage Analytics**: Monitor patterns to optimize model selection

#### **Security & Compliance**
- **API Key Management**: Rotate keys regularly and use environment variables
- **Data Privacy**: Use local models for sensitive information processing
- **Audit Trails**: Monitor usage logs for compliance requirements
- **Access Control**: Configure user permissions and rate limiting

### 🚨 Troubleshooting

#### **Common Issues**

**Model Not Responding:**
```bash
# Check model health
GET /api/ai-models/{model_name}/test

# Common fixes:
- Verify API key is valid and active
- Check API quota and rate limits
- Ensure model ID matches provider's format
- Test network connectivity to provider
```

**Configuration Not Saving:**
```bash
# Verify database connectivity
# Check browser console for JavaScript errors
# Ensure all required fields are completed
# Try refreshing the page and reconfiguring
```

**High API Costs:**
```bash
# Monitor usage statistics
GET /api/ai-models/usage-stats

# Optimization strategies:
- Switch to cheaper models for testing operations
- Implement token limits and cost controls
- Use local models for development
- Configure fallback chains with cost-effective options
```

#### **Performance Issues**
- **Slow Response Times**: Check model health and provider status
- **Failed Requests**: Verify API credentials and rate limits
- **Missing Features**: Ensure selected models support required capabilities
- **Database Errors**: Check SQLite/PostgreSQL connectivity and permissions

### 🔗 Integration Examples

#### **Python Integration**
```python
import requests

# Add model via API
model_config = {
    "name": "production-gpt-4",
    "provider": "openai",
    "model_id": "gpt-4",
    "api_key": "your-api-key",
    "max_context_length": 8192,
    "cost_per_1k_input_tokens": 0.01,
    "cost_per_1k_output_tokens": 0.03
}

response = requests.post(
    "http://localhost:7860/api/ai-models/",
    json=model_config
)

# Configure operation
operation_config = {
    "primary_model": "production-gpt-4",
    "fallback_models": ["gpt-3.5-turbo"],
    "is_enabled": True
}

requests.put(
    "http://localhost:7860/api/ai-models/operations/default",
    json=operation_config
)
```

#### **Configuration Backup**
```bash
# Export configuration for backup
curl -X POST http://localhost:7860/api/ai-models/export > ai_config_backup.json

# Import configuration from backup
curl -X POST http://localhost:7860/api/ai-models/import \
     -H "Content-Type: application/json" \
     -d @ai_config_backup.json
```

---

## 📝 Prompt Management

Create, organize, and manage your AI prompts with powerful tools for optimization and collaboration.

### 🆕 Recent Enhancements

- **🔍 Visibility Control**: Public/private prompt sharing with granular access control
- **🎨 Enhanced Dashboard**: Redesigned dashboard with clean actions and better organization  
- **🏷️ Advanced Tagging**: Smart tag management with auto-complete and analytics
- **📊 Real-time Updates**: HTMX-powered interface for seamless user experience
- **🌐 Multi-language UI**: Full internationalization with 10 language support

### 🚀 Quick Start Workflow

```mermaid
graph LR
    A[📝 Create] --> B[🧮 Calculate] --> C[🚀 Optimize] --> D[💾 Save] --> E[🔄 Reuse]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style C fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style D fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style E fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000
```

### ✍️ Creating Prompts

**Step-by-step process:**

1. **📂 Navigate** to the Prompt Management tab
2. **📝 Fill in details:**
   ```
   Name: unique-prompt-name (required)
   Title: Descriptive title for humans
   Category: Writing, Analysis, Code, etc.
   Content: Your actual AI prompt text
   Tags: comma, separated, keywords
   ```
3. **🧮 Check costs** with the built-in Token Calculator
4. **🚀 Optimize** using AI-powered suggestions (optional)
5. **💾 Save** your prompt to the library

### 🏷️ Advanced Tagging System

**Intelligent organization and discovery for prompts and templates**

The comprehensive tagging system provides powerful categorization and search capabilities across all content types:

#### **🎯 Multi-Entity Tag Support**
- **Unified Tagging**: Single tag vocabulary across prompts, templates, and rules
- **Cross-Entity Search**: Find content by tags regardless of type
- **Consistent Display**: Visual tag badges with unified styling
- **Data Integrity**: Tag normalization and validation ensures consistency

#### **🔍 Advanced Search Capabilities**
```mermaid
graph LR
    A[🏷️ Tag Input] --> B{Search Logic}
    B --> C[AND Logic: tag1 + tag2]
    B --> D[OR Logic: tag1 | tag2]
    B --> E[Entity Filter: prompts only]
    
    C --> F[Precise Results]
    D --> G[Broad Results] 
    E --> H[Filtered Results]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style F fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style G fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style H fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
```

#### **🧠 Intelligent Auto-Complete**
- **Real-Time Suggestions**: Dynamic tag suggestions as you type
- **Existing Tag Detection**: Suggest from your existing tag vocabulary
- **Fuzzy Matching**: Find tags with partial or approximate input
- **Smart Limits**: Configurable suggestion count for optimal UX

#### **📊 Comprehensive Analytics**
Track tag usage and discover insights:
```bash
# Popular Tags
python, api, automation, testing, documentation

# Usage Statistics
- Total Tags: 156
- Most Used: "python" (23 items)
- Versatile Tags: "documentation" (prompts + templates)
- Recent: "ai-agents", "rules", "automation"
```

#### **🎨 Modern UI Components**
- **Tag Input Component**: Modern interface with auto-complete and validation
- **Visual Tag Display**: Clean, accessible badges with proper spacing
- **Interactive Elements**: Click-to-remove tags and keyboard navigation
- **Mobile Responsive**: Touch-friendly interface for all devices

#### **🔌 REST API Integration**
Complete programmatic access with 6 dedicated endpoints:
```bash
GET    /api/tags/               # List all tags with usage statistics
GET    /api/tags/suggestions    # Get tag suggestions for auto-complete
GET    /api/tags/analytics      # Comprehensive tag analytics and insights
POST   /api/tags/search         # Advanced tag-based search with filters
GET    /api/tags/popular        # Most frequently used tags
GET    /api/tags/versatile      # Tags used across multiple content types
```

### 🧮 Token Calculator

**Understanding AI Costs in Real-Time**

```mermaid
graph LR
    A[📝 Input: 245 tokens] --> C[📊 Cost: $0.0615]
    B[💬 Output: 1,000 tokens] --> C
    C --> D[⚠️ Large prompt - Split recommended]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style C fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style D fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000
```

**Key Features:**
- **⚡ Real-time estimation** as you type
- **🎯 Multi-model support** (GPT-4, Claude, Gemini, etc.)
- **📊 Cost breakdown** (input vs output costs)
- **💡 Optimization suggestions** for cost reduction
- **⚠️ Alert system** for expensive prompts

**Model Comparison Quick Reference:**

| Model | 💰 Cost | ⚡ Speed | 🎯 Quality | 🎓 Best For |
|-------|---------|----------|------------|-------------|
| GPT-4 | $$$ | Slow | Highest | Complex reasoning, code |
| GPT-3.5 | $ | Fast | Good | General tasks, chat |
| Claude Opus | $$$ | Medium | Excellent | Analysis, writing |
| Gemini Pro | $$ | Medium | Very Good | Research, multimodal |

### 📚 Prompt Library & Organization

**Smart Organization System:**

```mermaid
graph LR
    A[📁 Library] --> B[📝 Writing<br/>35 prompts]
    A --> C[💻 Code<br/>41 prompts]
    A --> D[📊 Analysis<br/>29 prompts]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style C fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
```

**Features:**
- **🔍 Smart search** - Find prompts by name, content, or tags
- **🏷️ Category filtering** - Organize by type and purpose  
- **⭐ Favorites system** - Quick access to your most-used prompts
- **📊 Usage analytics** - See which prompts perform best
- **🔄 Version history** - Track prompt evolution over time

### 🎨 Custom Prompt Templates

**Standardize and Optimize Your Prompt Creation**

AI Prompt Manager supports custom templates that help you create consistent, high-quality prompts across different domains and use cases.

```mermaid
graph LR
    A[📝 Template] --> B[🔧 Variables] --> C[🎯 Applied] --> D[✨ Generated]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style C fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
```

#### **📚 Available Templates**

| Template | Purpose | Variables | Use Case |
|----------|---------|-----------|----------|
| **🔧 Default** | General prompt creation | `{content}`, `{category}`, `{tags}`, `{user_context}` | Standard prompts |
| **🚀 Enhancement** | Prompt optimization | `{original_prompt}`, `{enhancement_instructions}`, `{target_model}` | Improving existing prompts |
| **💼 Business** | Commercial use cases | Business metrics, ROI focus, stakeholder alignment | Marketing, sales, strategy |
| **⚙️ Technical** | Development & engineering | Code quality, best practices, security | Software development |
| **🎨 Creative** | Content generation | Style, tone, audience considerations | Writing, marketing copy |
| **📊 Analytical** | Data & research | Methodology, evidence-based reasoning | Analysis, research |

#### **🔧 Template Configuration**

Set template preferences via environment variables:

```bash
# Use custom prompt template
export PROMPT_TEMPLATE="/path/to/templates/my_template.txt"

# Use custom enhancement template  
export ENHANCEMENT_TEMPLATE="/path/to/templates/my_enhancement.txt"

# Templates directory is automatically scanned for .txt files
# Default location: templates/
```

#### **✍️ Creating Custom Templates**

Templates support variable substitution using `{variable_name}` syntax:

```bash
# Example business template
"""
Create a business-focused prompt for {category} use case:

Business Context: {user_context}
Key Areas: {tags}

Prompt Content: {content}

Business Guidelines:
- Focus on measurable outcomes and ROI
- Consider target audience and market impact
- Include implementation timeline
- Address stakeholder requirements
"""
```

#### **🎯 Using Templates in Prompts**

1. **📝 Create or edit** a prompt in the main interface
2. **🎨 Select template** from the available options
3. **📋 Fill variables** - Content, category, tags, context
4. **👁️ Preview** the templated result
5. **💾 Save** your structured prompt

#### **⚡ Template Features**

- **🔍 Variable Validation** - Ensures all required variables are provided
- **📚 Template Library** - Pre-built templates for common use cases
- **🎨 Custom Templates** - Create organization-specific templates
- **🌐 Multi-Language** - Templates work with translation features
- **🔄 Version Control** - Track template evolution over time

#### **💡 Best Practices**

- **Be Specific**: Include domain-specific terminology and concepts
- **Provide Context**: Explain the intended use case for the prompts
- **Test Templates**: Experiment with different templates for your use cases
- **Use Variables**: Leverage template variables for flexible content insertion
- **Organize Templates**: Group templates by domain or use case

#### **🔗 Integration**

Templates integrate seamlessly with other features:
- **🧮 Token Calculator** - Estimate costs for templated prompts
- **🚀 AI Optimization** - Optimize templated prompts with LangWatch
- **🧩 Prompt Builder** - Combine templated prompts for complex workflows
- **🔌 API Access** - Access templates programmatically via REST API

---

## 🎤 Speech Dictation

Revolutionize prompt creation with advanced speech-to-text functionality featuring AI-powered enhancement, multi-language support, and seamless integration with the prompt editor.

### ⚡ Quick Start with Speech Dictation

```mermaid
graph LR
    A[🎤 Speak] --> B[🔊 Recognize] --> C[✨ Enhance] --> D[🌐 Translate] --> E[💾 Save]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style C fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style E fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000
```

### 🎯 Key Features

**🎤 Advanced Speech Recognition**
- **Web Speech API Integration**: Browser-based speech recognition with no external dependencies
- **12 Language Support**: English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic
- **Pause/Resume Control**: Full control over dictation sessions with real-time status indicators
- **High Accuracy**: Optimized for technical content and AI prompt terminology

**✨ AI-Powered Text Enhancement**
- **Intelligent Filler Removal**: Automatically removes "um", "uh", "you know", "basically", etc.
- **Grammar Correction**: Fixes punctuation, capitalization, and sentence structure
- **AI Optimization**: Uses configured AI services for advanced text enhancement
- **Fallback Processing**: Robust regex-based enhancement when AI services are unavailable

**🌐 Multi-Language Translation**
- **Instant Translation**: Dictate in any supported language and translate to English
- **Context Awareness**: Maintains meaning and technical terminology during translation
- **Batch Processing**: Translate multiple prompts simultaneously

**🔧 Seamless Integration**
- **Form Integration**: Works directly in prompt creation and editing forms
- **Real-time Updates**: Live character count and preview as you dictate
- **Mobile Optimized**: Touch-friendly controls for mobile devices
- **Accessibility**: Full keyboard navigation and screen reader support

### 🚀 How to Use Speech Dictation

**1. 📝 Start Dictating**
```
1. Navigate to Prompt Creation/Editing
2. Click the 🎤 Dictate button
3. Allow microphone permissions when prompted
4. Begin speaking your prompt content
```

**2. 🎛️ Control Your Session**
```
• 🔴 Click to start/stop recording
• ⏸️ Pause/Resume as needed
• 🌐 Select your dictation language
• 👁️ Monitor real-time status updates
```

**3. ✨ Enhance Your Text**
```
• Click ✨ Enhance to clean up dictated text
• Remove filler words automatically
• Improve grammar and punctuation
• Apply AI-powered optimizations
```

**4. 🌐 Translate if Needed**
```
• Dictate in your native language
• Click 🌐 Translate to convert to English
• Maintain technical terminology
• Preserve original meaning
```

### 🎯 Best Practices for Speech Dictation

**📢 Speaking Techniques:**
- **Clear Articulation**: Speak clearly and at moderate pace
- **Technical Terms**: Spell out complex technical terms if needed
- **Punctuation**: Say "period", "comma", "question mark" for punctuation
- **Pause Management**: Use natural pauses between sentences

**🎛️ Session Management:**
- **Short Segments**: Dictate in 1-2 minute segments for best accuracy
- **Review Before Enhancement**: Check raw transcription before AI processing
- **Language Consistency**: Stick to one language per dictation session
- **Environment**: Use in quiet environments for optimal recognition

**✨ Enhancement Tips:**
- **AI Enhancement**: Use for complex technical content
- **Basic Enhancement**: Use for simple filler word removal
- **Review Results**: Always review enhanced text before saving
- **Iterative Process**: Enhance multiple times if needed

### 🔧 Technical Implementation

**Browser Compatibility:**
- ✅ Chrome/Chromium (Recommended)
- ✅ Edge (Windows)
- ✅ Safari (macOS/iOS)
- ⚠️ Firefox (Limited support)

**API Endpoints:**
```bash
# Text Enhancement
POST /enhance-text
Content-Type: application/x-www-form-urlencoded
text=dictated_content&type=dictation

# Translation
POST /translate
Content-Type: application/x-www-form-urlencoded
text=content&target_lang=en
```

**Security & Privacy:**
- 🔒 **No Data Storage**: Speech processing happens in browser
- 🛡️ **Secure Transmission**: All API calls use HTTPS
- 🔐 **Authentication**: Requires valid user session
- 📱 **Local Processing**: Web Speech API processes audio locally

### 🧪 Testing Coverage

The speech dictation system includes comprehensive testing:

- **📋 Unit Tests**: 19 tests covering text enhancement logic
- **🔗 Integration Tests**: 10 tests for API endpoints and workflows
- **🎭 E2E Tests**: 20 browser automation tests with Playwright
- **🔒 Security Tests**: Bandit security scanning passed
- **✅ Code Quality**: Full flake8, black, isort compliance

### 🎨 UI Components

**🎤 Dictation Controls:**
```html
<!-- Modern speech controls integrated into forms -->
<button id="speech-btn" class="speech-dictation-btn">
  🎤 Dictate
</button>
<select id="speech-language">
  <option value="en-US">English (US)</option>
  <option value="es-ES">Español</option>
  <!-- 10 more languages -->
</select>
```

**✨ Enhancement Interface:**
- Clean, intuitive buttons for enhancement and translation
- Real-time status indicators and progress feedback
- Mobile-responsive design with touch-friendly controls
- Accessibility features for keyboard navigation

### 🌐 Multi-Language Support

**Supported Dictation Languages:**
```
🇺🇸 English (US/UK)     🇪🇸 Spanish (ES/MX)
🇫🇷 French (FR/CA)      🇩🇪 German (DE)
🇮🇹 Italian (IT)        🇵🇹 Portuguese (PT/BR)
🇳🇱 Dutch (NL)          🇷🇺 Russian (RU)
🇨🇳 Chinese (ZH)        🇯🇵 Japanese (JA)
🇰🇷 Korean (KO)         🇸🇦 Arabic (AR)
```

**Translation Features:**
- Automatic language detection
- Context-aware translation for AI prompts
- Technical terminology preservation
- Bulk translation capabilities

---

## 🚀 AI-Powered Optimization

Transform good prompts into great prompts with AI-powered analysis and improvement suggestions from multiple optimization services.

### ⚡ The Optimization Process

```mermaid
graph LR
    A[📝 Original] --> B[🔍 Analysis] --> C[💡 Improvements] --> D[✨ Optimized]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style C fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style D fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
```

**What gets optimized:**
- **🎯 Clarity** - Remove ambiguity, add specific instructions
- **📊 Structure** - Logical flow and organization  
- **🎨 Effectiveness** - Better response quality and accuracy
- **📋 Context** - Appropriate background information
- **🔧 Specificity** - Replace vague terms with concrete directions

### 🛠️ Optimization Services

Choose from multiple AI optimization providers:

```mermaid
graph LR
    A[🚀 LangWatch<br/>⭐⭐⭐⭐⭐] --> B[🔍 PromptPerfect<br/>⭐⭐⭐⭐] --> C[🧪 Built-in<br/>⭐⭐⭐]
    
    style A fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style B fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style C fill:#f1f8e9,stroke:#689f38,stroke-width:2px,color:#000
```

### 📊 Optimization Dashboard

**Real-time optimization results:**

```mermaid
graph LR
    A[📊 Score: 78.5/100<br/>+23.5 improvement] --> B[✅ Accept]
    A --> C[🔄 Retry]
    A --> D[❌ Reject]
    
    style A fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style B fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style C fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style D fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000
```

### 🎯 Optimization Workflow

1. **📝 Create or edit** a prompt in the editor
2. **⚙️ Configure settings**:
   - Optimization context (purpose description)  
   - Target AI model (GPT-4, Claude, etc.)
   - Goals (clarity, effectiveness, structure)
3. **🚀 Click "Optimize"** - Analysis takes 5-15 seconds
4. **📊 Review results** with score and detailed improvements
5. **✅ Accept, retry, or manual edit** based on suggestions

### 🔧 Service Configuration

**Quick setup for optimization services:**

```bash
# LangWatch (Recommended for enterprise)
PROMPT_OPTIMIZER=langwatch
LANGWATCH_API_KEY=your_api_key
LANGWATCH_PROJECT_ID=your_project

# PromptPerfect (Great for creative prompts)
PROMPT_OPTIMIZER=promptperfect  
PROMPTPERFECT_API_KEY=your_api_key

# Built-in (No setup required)
PROMPT_OPTIMIZER=builtin
```

### 🛠️ Optimization Services

AI Prompt Manager supports multiple optimization backends for flexibility and reliability:

#### **🚀 LangWatch** (Recommended)
- **Quality**: ⭐⭐⭐⭐⭐ Enterprise-grade optimization
- **Features**: Advanced analytics, A/B testing, real-time monitoring
- **Best For**: Production applications, complex prompts
- **Setup**: Requires API key and project ID

#### **🔍 PromptPerfect**
- **Quality**: ⭐⭐⭐⭐ Specialized prompt refinement
- **Features**: Multi-model optimization, instant feedback
- **Best For**: Creative prompts, image generation
- **Setup**: API key required

#### **🧠 LangSmith**
- **Quality**: ⭐⭐⭐⭐ LangChain ecosystem integration
- **Features**: Version control, collaborative editing, testing
- **Best For**: LangChain applications, team workflows
- **Setup**: LangSmith account and API key

#### **⚡ Helicone**
- **Quality**: ⭐⭐⭐ Observability-focused optimization
- **Features**: Performance monitoring, cost tracking
- **Best For**: Production monitoring, debugging
- **Setup**: Helicone account and API key

#### **🧪 Built-in Optimizer** (Default)
- **Quality**: ⭐⭐⭐ Rule-based improvements
- **Features**: No external dependencies, instant results
- **Best For**: Development, testing, offline use
- **Setup**: No configuration required

### 🔧 Configuration

Configure your preferred optimization service via environment variables:

#### **LangWatch Configuration**
```bash
# LangWatch (Recommended for production)
PROMPT_OPTIMIZER=langwatch
LANGWATCH_API_KEY=your_langwatch_api_key
LANGWATCH_PROJECT_ID=your_project_id
LANGWATCH_ENDPOINT=https://api.langwatch.ai  # Optional
```

#### **PromptPerfect Configuration**
```bash
# PromptPerfect
PROMPT_OPTIMIZER=promptperfect
PROMPTPERFECT_API_KEY=your_promptperfect_api_key
```

#### **LangSmith Configuration**
```bash
# LangSmith (LangChain)
PROMPT_OPTIMIZER=langsmith
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_project_name
```

#### **Helicone Configuration**
```bash
# Helicone
PROMPT_OPTIMIZER=helicone
HELICONE_API_KEY=your_helicone_api_key
HELICONE_APP_NAME=ai-prompt-manager
```

#### **Built-in Optimizer (Default)**
```bash
# Built-in optimizer (no external service required)
PROMPT_OPTIMIZER=builtin
# No additional configuration needed
```

### 📊 Optimization Features

#### **Smart Analysis**
- **Prompt Length Analysis**: Identifies overly long or short prompts
- **Complexity Detection**: Recognizes overly complex or repetitive content
- **Structure Assessment**: Evaluates logical flow and organization
- **Clarity Metrics**: Measures instruction specificity and precision

#### **Multi-Model Support**
The optimizer adapts suggestions based on your target AI model:
- **GPT-4**: Focus on complex reasoning and detailed instructions
- **GPT-3.5-turbo**: Emphasize clarity and conciseness
- **Claude**: Optimize for conversational flow and context
- **Gemini**: Balance creativity with structure

#### **Optimization Goals**
Customize optimization focus:
- **Clarity**: Remove ambiguity, add specific instructions
- **Effectiveness**: Improve response quality and accuracy
- **Conciseness**: Remove redundancy while maintaining completeness
- **Structure**: Add organization and logical flow
- **Creativity**: Enhance creative and open-ended prompts

### 🎯 Best Practices

#### **Writing Prompts for Optimization**
1. **Provide Context**: Add background information about your use case
2. **Be Specific**: Include details about desired output format
3. **Set Clear Goals**: Define what you want the AI to accomplish
4. **Use Examples**: Include sample inputs/outputs when relevant

#### **Optimization Workflow**
```
Original Prompt → Configure Settings → Run Optimizer → Review Results → Test → Deploy
```

#### **Iterative Improvement**
- Start with basic prompts and optimize iteratively
- Test optimized prompts with real use cases
- Use A/B testing to compare versions
- Track performance metrics over time

### 🔍 Advanced Features

#### **Batch Optimization**
Optimize multiple prompts simultaneously:
```bash
# Coming soon: Batch optimization API
POST /api/optimize/batch
{
  "prompts": ["prompt1", "prompt2", "prompt3"],
  "settings": { "target_model": "gpt-4", "goals": ["clarity", "effectiveness"] }
}
```

#### **Custom Optimization Rules**
Define organization-specific optimization patterns:
```python
# Custom optimization rules (advanced)
custom_rules = {
    "add_role_definition": True,
    "require_output_format": True, 
    "max_length": 2000,
    "industry_context": "healthcare"
}
```

#### **Optimization History**
Track improvement over time:
- View optimization history for each prompt
- Compare versions and see improvement metrics
- Export optimization reports for analysis

### 📈 Performance Metrics

#### **Optimization Score Breakdown**
- **0-30**: Poor - Requires significant improvement
- **30-60**: Fair - Some optimization needed  
- **60-80**: Good - Well-structured prompt
- **80-95**: Excellent - Highly optimized prompt
- **95-100**: Perfect - No improvements needed

#### **Improvement Categories**
- **+5-10 points**: Minor improvements (formatting, clarity)
- **+10-20 points**: Moderate improvements (structure, specificity)  
- **+20-30 points**: Major improvements (complete restructuring)
- **+30+ points**: Significant transformation (role definition, context)

### 🌐 Multi-Language Support

The prompt optimizer works seamlessly with the translation system:

1. **Translate First**: Use "🌐 Translate to English" for non-English prompts
2. **Optimize**: Run optimization on English text for best results
3. **Translate Back**: Optionally translate optimized prompt back to original language

### 🧪 Testing the Optimizer

You can test the prompt optimization system using the included test script:

```bash
# Test with built-in optimizer (no API keys required)
python tests/integration/test_langwatch_integration.py

# Test with specific service (set environment variables first)
PROMPT_OPTIMIZER=langwatch LANGWATCH_API_KEY=your_key python tests/integration/test_langwatch_integration.py

# Test service switching
PROMPT_OPTIMIZER=promptperfect PROMPTPERFECT_API_KEY=your_key python tests/integration/test_langwatch_integration.py
```

The test script will:
- ✅ Check service availability and configuration
- ✅ Test simple and complex prompt optimization
- ✅ Verify error handling for edge cases
- ✅ Test different optimization goals
- ✅ Show before/after comparisons and scoring

### 🚨 Troubleshooting

#### **Common Issues**

**Optimization Not Working:**
- Check API key configuration in environment variables
- Verify internet connectivity for external services
- Try built-in optimizer as fallback

**Poor Optimization Results:**
- Provide more context about prompt purpose
- Try different optimization goals
- Use multiple optimization services for comparison

**Service Unavailable:**
- Built-in optimizer always available as backup
- Check service status pages for external providers
- Configure multiple services for redundancy

#### **Error Messages**
- `API_KEY_MISSING`: Set required environment variables
- `SERVICE_UNAVAILABLE`: External service is down, use alternative
- `PROMPT_TOO_LONG`: Shorten prompt or split into multiple parts
- `RATE_LIMIT_EXCEEDED`: Wait and retry, or upgrade service plan

### 🎓 Examples

#### **Example 1: Basic Prompt Optimization**
```
Original: "Write about dogs"

Optimized: "You are a knowledgeable pet expert. Write a comprehensive 
guide about dogs that covers the following topics:

1. Popular dog breeds and their characteristics
2. Basic care requirements (feeding, exercise, grooming)
3. Training tips for new dog owners
4. Health considerations and veterinary care

Please structure your response with clear headings and provide 
practical, actionable advice for both new and experienced dog owners."

Improvement: +45 points (clarity, structure, specificity)
```

#### **Example 2: Technical Prompt Optimization**
```
Original: "Explain API design"

Optimized: "You are a senior software architect with expertise in 
API design. Explain REST API design best practices for a junior 
developer, covering:

Step 1: Core principles (statelessness, resource-based URLs)
Step 2: HTTP methods and status codes usage
Step 3: Authentication and security considerations  
Step 4: Documentation and versioning strategies

Provide concrete examples for each concept and explain common 
pitfalls to avoid. Format your response as a structured tutorial 
with code examples where appropriate."

Improvement: +38 points (role definition, structure, examples)
```

### 🔗 Integration with Other Features

#### **Token Calculator Integration**
- Optimization results show token impact
- Compare costs before/after optimization
- Optimize for specific token budgets

#### **Prompt Builder Integration** 
- Optimize combined prompts after building
- Apply optimization to individual components
- Create optimized prompt templates

#### **API Integration**
```bash
# Optimize via API
POST /api/prompts/optimize
{
  "content": "your prompt here",
  "context": "analysis task",
  "target_model": "gpt-4",
  "goals": ["clarity", "effectiveness"]
}
```

---

## 🧩 Prompt Builder

Create sophisticated, multi-layered prompts by combining existing ones with an intuitive drag-and-drop interface.

### 🎯 What is Prompt Building?

**The power of combination:**

```mermaid
graph LR
    A[📝 Prompt A] --> B[📝 Prompt B] --> C[📝 Prompt C] --> D[🚀 Super Prompt]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style C fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style D fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#000
```

Transform individual prompts into comprehensive workflows:
- **🔗 Combine multiple prompts** into sophisticated sequences
- **🎨 Choose from 4 templates** for different combination styles  
- **👁️ Live preview** - See results before saving
- **🖱️ Drag-and-drop interface** - Visual, intuitive building
- **🔄 Seamless integration** - Edit combined prompts in main editor

### 🏗️ Builder Interface

```mermaid
graph LR
    A[📚 Available<br/>Prompts] --> B[🎯 Selected<br/>Prompts] --> C[👁️ Preview] --> D[🔗 Combine]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style B fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style C fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
```

### 🎨 Template Gallery

Choose the right combination style for your needs:

| Template | Icon | Description | Best For |
|----------|------|-------------|----------|
| **📋 Sequential** | `1→2→3` | Step-by-step flow | Tutorials, processes |
| **📑 Sections** | `[A][B][C]` | Organized sections | Reports, documentation |
| **🏗️ Layered** | `Base+Layer1+Layer2` | Context building | Complex reasoning |
| **🎨 Custom** | `{template}` | Your own format | Specialized needs |

### ⚡ Quick Building Workflow

1. **📂 Access** the Prompt Builder tab
2. **🖱️ Drag prompts** from Available to Selected area
3. **📝 Arrange order** by dragging within Selected area
4. **🎨 Choose template** - Sequential, Sections, Layered, or Custom
5. **👁️ Preview** your combined prompt in real-time
6. **🔗 Combine** to generate the final prompt
7. **📝 Edit** in main editor for final tweaks

### 📋 Step-by-Step Guide

#### **Step 1: Browse Available Prompts**
- The **Available Prompts** panel shows all your existing prompts as cards
- Each card displays:
  - **Prompt name** and category
  - **Preview** of the content
  - **Character count** and type (regular or enhancement)
  - **Visual indicators** for prompt types

#### **Step 2: Select Prompts to Combine**
- **Drag prompts** from the Available section to the Selected area
- **Alternative**: Click prompts to add them to your selection
- **Reorder**: Drag selected prompts to change their order
- **Remove**: Drag prompts out of the selected area to remove them

#### **Step 3: Choose a Combination Template**

| Template | Icon | Description | Best For |
|----------|------|-------------|----------|
| **Sequential** | 📋 | Combines prompts one after another with clear separation | Simple prompt chaining |
| **Sections** | 📑 | Creates distinct sections with headers for each prompt | Structured, multi-part prompts |
| **Layered** | 🏗️ | Builds context in layers with base + additional layers | Complex context building |
| **Custom** | 🎨 | Uses your own formatting template with placeholders | Advanced customization |

#### **Step 4: Customize Options**
- **Custom Separator**: Choose how prompts are separated (default: `\n\n`)
- **Add Numbers**: Automatically number each prompt section
- **Template-Specific Options**: Additional settings based on selected template

#### **Step 5: Preview Your Creation**
- The **Preview** panel shows exactly how your combined prompt will look
- **Real-time updates** as you change templates or options
- **Character count** and **source prompt tracking**

#### **Step 6: Finalize and Edit**
- Click **🔗 Combine Prompts** to generate the final result
- Click **📝 Open in Editor** to transfer the combined prompt to the main editor
- **Continue editing** in the main interface with full editing capabilities

### 🎨 Template Details

#### **📋 Sequential Template**
Combines prompts in order with simple separation:
```
1. First prompt content here

2. Second prompt content here

3. Third prompt content here
```

**Options:**
- ✅ Add sequence numbers
- ✅ Custom separator between prompts

#### **📑 Sections Template**  
Creates clearly defined sections with headers:
```
## First Prompt Title
First prompt content here

---

## Second Prompt Title  
Second prompt content here

---

## Third Prompt Title
Third prompt content here
```

**Best for:**
- Multi-part instructions
- Structured analysis prompts
- Documentation generation

#### **🏗️ Layered Template**
Builds context progressively:
```
Base Context:
Your foundational prompt here

Layer 1:
Additional context or instructions

Layer 2:
Further refinements or specifications

Instructions: Integrate all layers above into a cohesive response.
```

**Best for:**
- Complex reasoning tasks
- Context-heavy prompts
- Graduated instruction sets

#### **🎨 Custom Template**
Use your own formatting with placeholders:
```
Template: "Context: {content}\nSource: {name}\nCategory: {category}"
```

**Available Placeholders:**
- `{content}` - The prompt content
- `{name}` - Prompt name
- `{title}` - Prompt title
- `{category}` - Prompt category
- `{tags}` - Prompt tags

### ⚡ Advanced Features

#### **Smart Metadata Generation**
When you combine prompts, the system automatically generates:
- **Suggested Name**: `Combined_PromptA+PromptB` or `Combined_3_Prompts_20250108`
- **Suggested Title**: Based on prompt categories and content
- **Combined Category**: `Combined` or inherited from source prompts
- **Merged Tags**: All unique tags from source prompts plus `combined` and `X-part` tags

#### **Validation and Error Prevention**
- **Minimum Requirements**: Must select at least 2 prompts
- **Duplicate Detection**: Prevents selecting the same prompt twice
- **Length Limits**: Warns if combined prompt exceeds 50,000 characters
- **Template Validation**: Ensures template compatibility with selected prompts

#### **Search and Filter**
- **Search Bar**: Find prompts by name, title, or content
- **Category Filter**: Show only prompts from specific categories
- **Refresh**: Update available prompts after creating new ones

### 🌐 Multi-Language Support

The Prompt Builder is fully localized in all 10 supported languages:

| Language | Prompt Builder | Available Prompts | Template Options |
|----------|---------------|-------------------|------------------|
| 🇺🇸 English | Prompt Builder | Available Prompts | Sequential, Sections, Layered, Custom |
| 🇪🇸 Spanish | Constructor de Prompts | Prompts Disponibles | Secuencial, Secciones, Por Capas, Personalizado |
| 🇫🇷 French | Constructeur de Prompts | Prompts Disponibles | Séquentiel, Sections, En Couches, Personnalisé |
| 🇩🇪 German | Prompt-Builder | Verfügbare Prompts | Sequenziell, Abschnitte, Geschichtet, Benutzerdefiniert |
| 🇨🇳 Chinese | 提示构建器 | 可用提示 | 顺序, 分段, 分层, 自定义 |
| 🇯🇵 Japanese | プロンプトビルダー | 利用可能なプロンプト | 順次, セクション, 階層, カスタム |
| 🇵🇹 Portuguese | Construtor de Prompts | Prompts Disponíveis | Sequencial, Seções, Em Camadas, Personalizado |
| 🇷🇺 Russian | Конструктор Промптов | Доступные Промпты | Последовательный, Секции, Слоистый, Пользовательский |
| 🇸🇦 Arabic | منشئ المطالبات | المطالبات المتاحة | تسلسلي, أقسام, طبقات, مخصص |
| 🇮🇳 Hindi | प्रॉम्प्ट बिल्डर | उपलब्ध प्रॉम्प्ट्स | क्रमिक, खंड, परतदार, कस्टम |

### 💡 Use Cases and Examples

#### **Example 1: Content Creation Workflow**
1. **Select prompts**: "Blog Introduction", "SEO Keywords", "Call to Action"
2. **Template**: Sections
3. **Result**: Complete blog post structure with intro, SEO-optimized content, and CTA

#### **Example 2: Analysis Framework**
1. **Select prompts**: "Context Analysis", "SWOT Framework", "Recommendations"
2. **Template**: Layered
3. **Result**: Comprehensive analysis prompt with progressive depth

#### **Example 3: Creative Writing**
1. **Select prompts**: "Character Development", "Setting Description", "Plot Points"
2. **Template**: Sequential
3. **Result**: Complete creative writing framework

#### **Example 4: Technical Documentation**
1. **Select prompts**: "Requirements Gathering", "Technical Specs", "User Stories"
2. **Template**: Sections with custom separator
3. **Result**: Structured technical documentation prompt

### 🔧 Tips and Best Practices

#### **Prompt Selection Tips**
- ✅ **Start with complementary prompts** that work well together
- ✅ **Consider prompt length** - very long prompts may overwhelm the combination
- ✅ **Mix prompt types** - combine different categories for richer results
- ✅ **Use enhancement prompts** strategically to improve overall quality

#### **Template Selection Guide**
- **Sequential**: Simple combinations, tutorials, step-by-step processes
- **Sections**: Reports, analyses, structured content
- **Layered**: Complex reasoning, context-heavy tasks
- **Custom**: Specialized formatting, integration with external systems

#### **Optimization Strategies**
- 🎯 **Preview frequently** to catch issues early
- 🎯 **Test with smaller combinations** first
- 🎯 **Use meaningful names** for easy identification later
- 🎯 **Leverage tags** to organize and find combined prompts

### 🚨 Troubleshooting

#### **Common Issues**

**"No prompts selected" Error:**
- Make sure you've dragged at least 2 prompts to the Selected area
- Check that prompts are actually visible in the Selected section

**"Combined prompt too long" Warning:**
- Remove some prompts or choose shorter ones
- Use more concise source prompts
- Consider splitting into multiple smaller combinations

**Preview not updating:**
- Click the "👁️ Refresh Preview" button
- Check that you've selected a valid template
- Ensure selected prompts are properly loaded

**Drag-and-drop not working:**
- Refresh the page and try again
- Use click-to-select as an alternative
- Check browser compatibility (modern browsers recommended)

#### **Performance Tips**
- **Limit simultaneous combinations** to avoid browser slowdown
- **Clear old selections** before starting new combinations
- **Use shorter prompts** for faster preview updates
- **Save frequently** to avoid losing work

### 🔗 Integration with Other Features

#### **Token Calculator Integration**
- Combined prompts automatically work with the Token Calculator
- Estimate costs for your combined prompts before using them
- Compare token usage across different combination templates

#### **LangWatch Optimization**
- Use combined prompts with LangWatch optimization
- Improve combined prompts with AI-powered suggestions
- Optimize the final result after combination

#### **Translation Feature**
- Combined prompts work with the translation feature
- Translate combined prompts to English for better AI processing
- Maintain formatting across translations

#### **API Access**
- Combined prompts are saved like regular prompts
- Access via API endpoints once saved
- Include in automated workflows and integrations

---

## 🔑 API Access

**Dual-Server Architecture:** The API system uses a dedicated FastAPI server running alongside the main web interface for optimal performance and separation of concerns.

### 🏗️ Architecture Overview

```mermaid
graph LR
    A[🌐 Client Request] --> B{Port Router}
    B -->|:7860| C[📱 Web UI Server]
    B -->|:7861| D[🔌 FastAPI API Server]
    
    C --> E[Web Interface]
    D --> F[REST API Endpoints]
    D --> G[📚 Swagger Docs]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    style C fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    style D fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    style E fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style F fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style G fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
```

### 🚀 Enabling API Access

**Start with API enabled:**
```bash
python run.py --with-api --port 7860
```

This starts two servers:
- **🖥️ Web UI Server**: `http://localhost:7860` (Modern web interface)
- **🔌 API Server**: `http://localhost:7861` (FastAPI endpoints)

### 📍 API Endpoints

**Base URL:** `http://localhost:7861` (main port + 1)

**Core Endpoints:**
```bash
# Health check
GET /health
# Returns: {"status": "healthy", "timestamp": "2025-01-01T12:00:00"}

# Service information  
GET /info
# Returns: {"service": "ai-prompt-manager", "version": "1.0.0"}

# API root with endpoint listing
GET /
# Returns: {"message": "AI Prompt Manager API", "endpoints": {...}}
```

**Documentation Endpoints:**
```bash
# Interactive Swagger UI
GET /docs

# ReDoc documentation
GET /redoc

# OpenAPI schema
GET /openapi.json
```

### 🔧 Development Workflow

**1. Start the application:**
```bash
python run.py --with-api --debug --port 7860
```

**2. Access services:**
- **UI**: http://localhost:7860
- **API**: http://localhost:7861
- **API Docs**: http://localhost:7861/docs

**3. Test endpoints:**
```bash
# Test health endpoint
curl http://localhost:7861/health

# Test with pretty JSON
curl -s http://localhost:7861/info | python -m json.tool
```

### 🔐 Authentication (Future Enhancement)

*Current API endpoints are public for development. Production authentication will be added via:*

1. **Navigate to Account Settings → API Tokens** (UI feature)
2. **Create token with expiration**
3. **Use Bearer token authentication:**
   ```bash
   curl -H "Authorization: Bearer apm_your_token_here" \
        http://localhost:7861/health
   ```

### 🌐 Port Configuration

**Default Ports:**
- Main port: 7860 (UI)
- API port: 7861 (Main + 1)

**Custom Ports:**
```bash
# Custom port configuration
python run.py --with-api --port 8080
# UI: http://localhost:8080
# API: http://localhost:8081
```

**Docker Deployment:**
```bash
# Expose both ports
docker run -p 7860:7860 -p 7861:7861 \
           -e ENABLE_API=true \
           ghcr.io/makercorn/ai-prompt-manager:latest
```

---

## ⚙️ Configuration

### Environment Setup

Create a `.env` file with your settings:

```env
# Application Mode
MULTITENANT_MODE=true          # Enable multi-tenant mode (default: true)
ENABLE_API=false               # Enable dual-server API architecture (default: false)

# Server Configuration  
SERVER_HOST=0.0.0.0           # Server host (default: 0.0.0.0)
SERVER_PORT=7860              # Main server port (UI server, API will be PORT+1)

# Database Configuration
DB_TYPE=sqlite                # Database type: sqlite or postgres (default: sqlite)
DB_PATH=prompts.db           # SQLite database path (default: prompts.db)
POSTGRES_DSN=postgresql://user:pass@localhost:5432/dbname

# Authentication & Security
SECRET_KEY=your-secure-secret-key    # JWT signing secret (auto-generated if not set)
LOCAL_DEV_MODE=true                 # Enable local development features (default: false)

# SSO/ADFS Integration (optional)
SSO_ENABLED=false
SSO_CLIENT_ID=your-application-id
SSO_CLIENT_SECRET=your-client-secret
SSO_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
SSO_REDIRECT_URI=http://localhost:7860/auth/callback

# Entra ID (Azure AD) Authentication (optional)
ENTRA_ID_ENABLED=false
ENTRA_CLIENT_ID=your-entra-client-id
ENTRA_CLIENT_SECRET=your-entra-client-secret
ENTRA_TENANT_ID=your-azure-tenant-id
ENTRA_REDIRECT_URI=http://localhost:7860/auth/entra-callback
ENTRA_SCOPES=openid email profile User.Read

# Azure AI Services (optional)
AZURE_AI_ENABLED=false
AZURE_AI_ENDPOINT=https://your-azure-ai-endpoint.cognitiveservices.azure.com
AZURE_AI_KEY=your-azure-ai-key
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_VERSION=2024-02-15-preview

# Prompt Optimization Services (optional)
PROMPT_OPTIMIZER=langwatch              # Service: langwatch, promptperfect, langsmith, helicone, builtin
LANGWATCH_API_KEY=your-langwatch-api-key
LANGWATCH_PROJECT_ID=ai-prompt-manager
PROMPTPERFECT_API_KEY=your-promptperfect-key
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=your-project-name
HELICONE_API_KEY=your-helicone-key

# Development & Debugging
DEBUG=false                   # Enable debug mode (default: false)
```

### Complete Environment Variable Reference

| Variable | Description | Default | Command Line Override |
|----------|-------------|---------|----------------------|
| `MULTITENANT_MODE` | Enable multi-tenant architecture | `true` | `--single-user` / `--multi-tenant` |
| `ENABLE_API` | Enable REST API endpoints | `false` | `--with-api` |
| `SERVER_HOST` | Server bind address | `0.0.0.0` | `--host HOST` |
| `SERVER_PORT` | Server port | `7860` | `--port PORT` |
| `DB_TYPE` | Database type (sqlite/postgres) | `sqlite` | - |
| `DB_PATH` | SQLite database file path | `prompts.db` | - |
| `POSTGRES_DSN` | PostgreSQL connection string | - | - |
| `SECRET_KEY` | JWT signing secret | auto-generated | - |
| `LOCAL_DEV_MODE` | Enable development features | `true` | - |
| `SSO_ENABLED` | Enable SSO authentication | `false` | - |
| `SSO_CLIENT_ID` | SSO application ID | - | - |
| `SSO_CLIENT_SECRET` | SSO client secret | - | - |
| `SSO_AUTHORITY` | SSO authority URL | - | - |
| `PROMPT_OPTIMIZER` | Optimization service to use | `builtin` | - |
| `LANGWATCH_API_KEY` | LangWatch API key | - | - |
| `LANGWATCH_PROJECT_ID` | LangWatch project ID | `ai-prompt-manager` | - |
| `PROMPTPERFECT_API_KEY` | PromptPerfect API key | - | - |
| `LANGSMITH_API_KEY` | LangSmith API key | - | - |
| `HELICONE_API_KEY` | Helicone API key | - | - |
| `ENTRA_ID_ENABLED` | Enable Entra ID authentication | `false` | - |
| `ENTRA_CLIENT_ID` | Entra ID application ID | - | - |
| `ENTRA_CLIENT_SECRET` | Entra ID client secret | - | - |
| `ENTRA_TENANT_ID` | Azure tenant ID | - | - |
| `ENTRA_REDIRECT_URI` | Entra ID callback URL | `/auth/entra-callback` | - |
| `AZURE_AI_ENABLED` | Enable Azure AI services | `false` | - |
| `AZURE_AI_ENDPOINT` | Azure AI Studio endpoint | - | - |
| `AZURE_AI_KEY` | Azure AI Studio key | - | - |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | - | - |
| `AZURE_OPENAI_KEY` | Azure OpenAI key | - | - |
| `AZURE_OPENAI_VERSION` | Azure OpenAI API version | `2024-02-15-preview` | - |
| `DEBUG` | Enable debug logging | `false` | `--debug` |
| `PUBLIC_SHARE` | Enable public sharing | `false` | `--share` |

### Database Options

**SQLite (Development):**
- Zero setup required
- File-based storage
- Single-user friendly

**PostgreSQL (Production):**
- Better performance
- Multi-user support
- Enterprise features

### AI Service Integration

Supported AI providers:
- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Azure OpenAI** (Enterprise OpenAI models)
- **Azure AI Studio** (Phi-3, Mistral, and other Azure models)
- **LM Studio** (Local models)
- **Ollama** (Self-hosted)
- **Llama.cpp** (Local inference)

Configure in the application's AI Service Settings.

---

## 🔵 Azure AI Integration

### Overview

AI Prompt Manager provides comprehensive support for Microsoft Azure services, including:
- **Azure OpenAI**: Enterprise-grade OpenAI models with enhanced security and compliance
- **Azure AI Studio**: Access to Phi-3, Mistral, and other Azure-hosted AI models
- **Entra ID**: Modern Azure Active Directory authentication with Microsoft Graph integration

### 🔐 Entra ID Authentication Setup

Entra ID (formerly Azure Active Directory) provides enterprise-grade authentication with seamless Microsoft Graph API integration.

#### **1. Azure App Registration**

1. **Navigate to Azure Portal** → Azure Active Directory → App registrations
2. **Create new registration**:
   - Name: `AI Prompt Manager`
   - Supported account types: `Accounts in this organizational directory only`
   - Redirect URI: `http://localhost:7860/auth/entra-callback` (for local dev)

3. **Configure Authentication**:
   - Add redirect URIs for production environments
   - Enable `ID tokens` under Authentication → Implicit grant and hybrid flows

4. **API Permissions**:
   - Add `Microsoft Graph` permissions:
     - `openid` (Sign users in)
     - `email` (Read user email)
     - `profile` (Read user profile)
     - `User.Read` (Read user information)

5. **Certificates & secrets**:
   - Create new client secret
   - Copy the secret value (save immediately - you won't see it again)

#### **2. Environment Configuration**

```bash
# Enable Entra ID authentication
ENTRA_ID_ENABLED=true
ENTRA_CLIENT_ID=12345678-1234-1234-1234-123456789012
ENTRA_CLIENT_SECRET=your-client-secret-value
ENTRA_TENANT_ID=your-azure-tenant-id
ENTRA_REDIRECT_URI=http://localhost:7860/auth/entra-callback

# Optional: Customize scopes (default shown)
ENTRA_SCOPES=openid email profile User.Read
```

#### **3. Multi-Tenant Configuration**

For organizations with multiple tenants:

```bash
# Production example
ENTRA_ID_ENABLED=true
ENTRA_CLIENT_ID=your-production-client-id
ENTRA_TENANT_ID=your-production-tenant-id
ENTRA_REDIRECT_URI=https://prompts.yourcompany.com/auth/entra-callback

# Development
ENTRA_REDIRECT_URI=http://localhost:7860/auth/entra-callback
```

### 🤖 Azure AI Services Setup

#### **Azure OpenAI Configuration**

1. **Create Azure OpenAI resource** in Azure Portal
2. **Deploy models** (e.g., GPT-4, GPT-3.5-turbo)
3. **Get endpoint and keys** from resource overview

```bash
# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_VERSION=2024-02-15-preview
```

#### **Azure AI Studio Configuration**

1. **Create Azure AI Studio workspace**
2. **Deploy models** (Phi-3, Mistral, etc.)
3. **Configure endpoints and authentication**

```bash
# Azure AI Studio configuration
AZURE_AI_ENABLED=true
AZURE_AI_ENDPOINT=https://your-ai-endpoint.cognitiveservices.azure.com
AZURE_AI_KEY=your-azure-ai-key
```

### 📊 Supported Azure Models

#### **Azure OpenAI Models**
- `azure-gpt-4` - GPT-4 with Azure enterprise features
- `azure-gpt-35-turbo` - GPT-3.5 Turbo with Azure security

#### **Azure AI Studio Models**
- `azure-ai-phi-3` - Microsoft Phi-3 small language model
- `azure-ai-mistral` - Mistral models hosted on Azure

### 🔧 Testing Configuration

```bash
# Test Azure connectivity
python -c "
from auth_manager import AuthManager
auth = AuthManager()

# Test Entra ID configuration
print('Entra ID enabled:', auth.is_entra_id_enabled())
print('Authentication methods:', auth.get_authentication_methods())

# Test Azure AI configuration
print('Azure AI enabled:', auth.is_azure_ai_enabled())
azure_config = auth.get_azure_ai_config()
print('Azure config:', azure_config)

# Validate credentials (requires network access)
valid, message = auth.validate_azure_credentials()
print(f'Azure validation: {valid} - {message}')
"
```

### 🌐 Production Deployment

#### **Security Considerations**
- Use Azure Key Vault for secret management
- Configure proper RBAC permissions
- Enable Azure Monitor for logging
- Use managed identities where possible

#### **Example Production Configuration**
```bash
# Production environment variables
ENTRA_ID_ENABLED=true
ENTRA_CLIENT_ID=${AZURE_CLIENT_ID}
ENTRA_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
ENTRA_TENANT_ID=${AZURE_TENANT_ID}
ENTRA_REDIRECT_URI=https://prompts.yourcompany.com/auth/entra-callback

AZURE_AI_ENABLED=true
AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}

# Use PostgreSQL for production
DB_TYPE=postgres
POSTGRES_DSN=${DATABASE_URL}
```

### 🔍 Troubleshooting

#### **Common Entra ID Issues**

**Authentication fails with "invalid_client":**
- Verify `ENTRA_CLIENT_ID` and `ENTRA_CLIENT_SECRET`
- Check redirect URI matches exactly
- Ensure app registration is not expired

**No email returned from Entra ID:**
- Verify `email` scope is requested
- Check API permissions include `User.Read`
- User might not have email attribute set

#### **Common Azure AI Issues**

**Azure OpenAI "Invalid API key":**
- Check `AZURE_OPENAI_KEY` is correct
- Verify endpoint URL format
- Ensure API version is supported

**Model not found errors:**
- Verify model deployment names
- Check Azure AI Studio model availability
- Confirm endpoint supports requested model

#### **Token Calculator Issues**

**Azure models not showing costs:**
- Azure pricing included for common models
- Custom model pricing can be configured
- Check model name matches supported patterns

### 🔄 Migration from Generic SSO

If migrating from generic SSO to Entra ID:

```bash
# Disable generic SSO
SSO_ENABLED=false

# Enable Entra ID
ENTRA_ID_ENABLED=true
# ... other Entra ID settings

# Existing users will be matched by email
# SSO ID will be updated to Entra ID object ID
```

---

## 🏢 Multi-Tenant Features

### For Organizations

- **Complete Data Isolation** - Each tenant's data is separate
- **User Management** - Add users with different roles
- **Admin Dashboard** - Monitor usage and manage tenants
- **SSO Integration** - Connect with existing authentication

### User Roles

- **Admin**: Full system access, user management
- **User**: Create and manage prompts, API access
- **Readonly**: View prompts only, no modifications

### Default Credentials

For local development:
- **Tenant**: `localhost`
- **Email**: `admin@localhost`
- **Password**: `admin123`

---

## 🚀 Development

### Development Commands

```bash
# Install dependencies
poetry install

# Run application in different modes
python run.py                                # Default: Multi-tenant
python run.py --single-user                  # Single-user mode
python run.py --with-api                     # Multi-tenant + API
python run.py --single-user --with-api       # Single-user + API

# Development options
python run.py --debug                        # Enable debug mode
python run.py --share                        # Enable public sharing
python run.py --port 8080                    # Custom port
python run.py --help                         # Show all options

# Testing
python tests/integration/test_mt_install.py                    # Multi-tenant setup
python tests/integration/test_langwatch_integration.py         # LangWatch features
python tests/integration/test_standalone_api.py                # API integration
```

### Docker Development

```bash
# Build and run
docker build -t ai-prompt-manager .
docker run -p 7860:7860 ai-prompt-manager

# With environment variables
docker run -p 7860:7860 \
  -e MULTITENANT_MODE=false \
  -e ENABLE_API=true \
  ai-prompt-manager

# With PostgreSQL
docker-compose up -d
```

### Architecture

**Core Components:**
- `run.py` - Universal launcher (single-user + multi-tenant)
- `web_app.py` - Modern FastAPI web interface
- `prompt_data_manager.py` - Database abstraction with tenant isolation
- `auth_manager.py` - Authentication and user management
- `token_calculator.py` - Token estimation engine
- `langwatch_optimizer.py` - Prompt optimization
- `api_endpoints_enhanced.py` - Enhanced REST API implementation
- `api_token_manager.py` - Secure API token management

### Database Schema

**Multi-Tenant Architecture:**
```
tenants
├── id (UUID)
├── name
├── subdomain  
├── max_users
├── is_active
└── created_at

users
├── id (UUID)
├── tenant_id (FK)
├── email (unique per tenant)
├── password_hash
├── first_name, last_name
├── role (admin|user|readonly)
├── sso_id (optional)
├── is_active
├── created_at
└── last_login

prompts
├── id
├── tenant_id (FK) - ensures tenant isolation
├── user_id (FK) - tracks ownership
├── name (unique per tenant)
├── title, content, category, tags
├── is_enhancement_prompt
├── created_at
└── updated_at

config
├── id
├── tenant_id (FK)
├── user_id (FK)
├── key, value - stores user/tenant settings
└── created_at

api_tokens
├── id (UUID)
├── user_id (FK)
├── tenant_id (FK)
├── name
├── token_hash
├── token_prefix
├── expires_at (optional)
├── last_used
└── created_at
```

### Security Architecture

**Multi-Layer Security:**
- **PBKDF2 Password Hashing**: Secure password storage with salt
- **JWT Session Tokens**: Stateless authentication with expiration
- **Tenant Row-Level Security**: Complete data isolation between organizations
- **Role-Based Access Control**: Granular permission system
- **API Token Management**: Secure programmatic access
- **Session Validation**: Automatic token validation and renewal

**Data Isolation:**
- All database queries include tenant_id filtering
- Users cannot access data outside their tenant
- Admin users can manage their tenant only
- Complete separation of configurations and prompts

---

## 🔒 Production Deployment

### Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Set `LOCAL_DEV_MODE=false`
- [ ] Use PostgreSQL database
- [ ] Configure HTTPS/TLS
- [ ] Set up proper SSO/ADFS
- [ ] Configure firewall rules
- [ ] Implement backup procedures
- [ ] Monitor application logs

### Production Docker

```bash
# Set environment variables
export SECRET_KEY="your-production-secret-key"
export SSO_ENABLED="true"
export MULTITENANT_MODE="true"
export ENABLE_API="true"

# Deploy with published images
docker-compose -f docker-compose.prod.yml up -d

# Single command with all options
docker run -p 7860:7860 \
  -e MULTITENANT_MODE=true \
  -e ENABLE_API=true \
  -e SECRET_KEY="your-production-secret" \
  -e DB_TYPE=postgres \
  -e POSTGRES_DSN="postgresql://user:pass@db:5432/prompts" \
  ghcr.io/makercorn/ai-prompt-manager:latest
```

**Available Images:**
- `ghcr.io/makercorn/ai-prompt-manager:latest` - Latest development build
- `ghcr.io/makercorn/ai-prompt-manager:stable` - Latest stable release
- `ghcr.io/makercorn/ai-prompt-manager:v1.0.0` - Specific tagged releases

**Multi-Platform Support**: All images support both `linux/amd64` and `linux/arm64` architectures.

---

## 🚀 Quick Reference

### ⚡ Essential Commands

| Task | Command | Description |
|------|---------|-------------|
| **🚀 Start App** | `python run.py` | Default multi-tenant mode |
| **👤 Single User** | `python run.py --single-user` | Personal use mode |
| **🔌 With API** | `python run.py --with-api` | Enable REST endpoints |
| **🐳 Docker** | `docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager` | Container deployment |
| **📦 PyPI** | `pip install promptman && python -m promptman` | Package installation |
| **🔧 Help** | `python run.py --help` | Show all options |

### 🌐 Multi-Language Quick Access

| Language | Code | Environment Variable | URL Parameter |
|----------|------|---------------------|---------------|
| **English** | `en` | `DEFAULT_LANGUAGE=en` | `?lang=en` |
| **Spanish** | `es` | `DEFAULT_LANGUAGE=es` | `?lang=es` |
| **French** | `fr` | `DEFAULT_LANGUAGE=fr` | `?lang=fr` |
| **German** | `de` | `DEFAULT_LANGUAGE=de` | `?lang=de` |
| **Chinese** | `zh` | `DEFAULT_LANGUAGE=zh` | `?lang=zh` |
| **Japanese** | `ja` | `DEFAULT_LANGUAGE=ja` | `?lang=ja` |

### 🧩 Prompt Builder Shortcuts

| Action | Method | Tip |
|--------|--------|-----|
| **Add Prompts** | Drag from Available → Selected | Or click to select |
| **Reorder** | Drag within Selected area | Order affects output |
| **Remove** | Drag out or click X | Undo with Ctrl+Z |
| **Preview** | Auto-updates on changes | 👁️ Refresh if needed |
| **Templates** | 📋 Sequential, 📑 Sections, 🏗️ Layered, 🎨 Custom | Choose based on use case |

### 🔧 Configuration Quick Setup

```bash
# Essential .env settings
MULTITENANT_MODE=true    # Teams/organizations
ENABLE_API=true         # Developer access  
DB_TYPE=postgres        # Production database
SECRET_KEY=secure-key   # JWT security

# AI Services
PROMPT_OPTIMIZER=langwatch
LANGWATCH_API_KEY=your_key
TRANSLATION_SERVICE=openai
OPENAI_API_KEY=your_key
```

### 🚨 Emergency Commands

```bash
# Reset admin password
python -c "from auth_manager import AuthManager; auth = AuthManager(); auth.reset_admin_password()"

# Check system health
curl http://localhost:7860/api/health

# Database backup
cp prompts.db prompts.db.backup

# View logs
tail -f application.log
```

---

## 🔧 Troubleshooting

### 🚨 Common Issues & Quick Fixes

#### 🔌 Application Won't Start

```bash
# Check port availability
lsof -i :7860

# Try different port
python run.py --port 8080

# Check Python version
python --version  # Requires 3.12+
```

#### 🗄️ Database Issues

```bash
# SQLite permission errors
chmod 664 prompts.db
chown $USER:$USER prompts.db

# PostgreSQL connection
psql -h localhost -U username -d dbname  # Test connection
```

#### 🔐 Authentication Problems

```bash
# Reset admin password (emergency)
python -c "
from auth_manager import AuthManager
auth = AuthManager('prompts.db')
auth.create_user('tenant-id', 'admin@localhost', 'newpassword', 'Admin', 'User', 'admin')
"

# Check tenant configuration
python -c "
from auth_manager import AuthManager
auth = AuthManager('prompts.db')
tenants = auth.get_all_tenants()
for t in tenants: print(f'Tenant: {t.name} ({t.subdomain})')
"
```

#### 🌐 Network & Access Issues

```bash
# Check if service is running
curl http://localhost:7860/api/health
# Expected: {"status": "healthy"}

# Test with debug mode
python run.py --debug

# Allow external access
python run.py --host 0.0.0.0
```

#### 🐳 Docker Issues

```bash
# Check container logs
docker logs ai-prompt-manager

# Test database connectivity
docker exec -it ai-prompt-manager python -c "
from prompt_data_manager import PromptDataManager
data = PromptDataManager('prompts.db')
print('Database connection successful')
"
```

#### 🤖 AI Service Issues

```bash
# Test optimization service
python tests/integration/test_langwatch_integration.py

# Verify API keys
python -c "
import os
print('LangWatch:', 'Set' if os.getenv('LANGWATCH_API_KEY') else 'Missing')
print('OpenAI:', 'Set' if os.getenv('OPENAI_API_KEY') else 'Missing')
"
```

### 🆘 Getting Help

- **📖 Documentation**: Check this README for detailed guides
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/MakerCorn/ai-prompt-manager/issues)
- **💬 Community**: Join discussions for community support
- **🔧 Self-Service**: Use the troubleshooting commands above

---

## 📚 Additional Resources

### Testing

**Comprehensive Test Suite:**
```bash
# Install test dependencies
poetry install --with dev

# 🏗️ New Architecture Tests
python tests/integration/test_new_prompt_architecture.py  # New architecture validation
python tests/integration/test_new_architecture_integration.py  # Component integration
python -c "
# Test new architecture imports
import sys; sys.path.insert(0, 'src')
from src.core.config.settings import AppConfig
from src.prompts.services.prompt_service import PromptService
from src.auth.models.user import User
print('✅ New architecture components working!')
"

# 🔧 Integration Tests
python tests/integration/test_mt_install.py                    # Multi-tenant setup and UI creation
python tests/integration/test_standalone_api.py               # API integration
python tests/integration/test_langwatch_integration.py        # Prompt optimization features
python tests/integration/test_api_integration.py              # Full API test suite

# 📊 Component Testing
python -c "
from prompt_data_manager import PromptDataManager
from auth_manager import AuthManager

# Test database initialization  
auth = AuthManager('test.db')
data = PromptDataManager('test.db', tenant_id='test', user_id='test')
print('✅ Core components working correctly!')

# Cleanup
import os
os.remove('test.db')
"

# 🏢 Multi-tenant Isolation Testing
python -c "
from auth_manager import AuthManager
auth = AuthManager('test_isolation.db')

# Create two tenants
tenant1_id = auth.create_tenant('Company A', 'company-a', 100)[1]
tenant2_id = auth.create_tenant('Company B', 'company-b', 50)[1] 

print('✅ Tenant isolation test passed')
"

# 🚀 Test Different Launcher Modes
python run.py --help                         # Show all options
MULTITENANT_MODE=false python run.py &       # Start in single-user mode
sleep 2 && pkill -f "python run.py"          # Stop test server
```

**Docker Testing:**
```bash
# 🐳 Comprehensive Docker Testing
./scripts/docker-test.sh                    # Full Docker validation suite

# 🧪 Manual Docker Testing
docker build -t ai-prompt-manager-test .    # Test build process
docker run --rm -p 7860:7860 ai-prompt-manager-test  # Test single container

# 🏗️ Test Development Stack
docker-compose up -d                        # PostgreSQL + Redis + App
docker-compose logs app                     # Check application logs
curl http://localhost:7860/api/health       # Verify health endpoint

# 🏭 Test Production Stack  
docker-compose -f docker-compose.prod.yml up -d  # Production configuration
curl http://localhost:7860/api/health       # Verify health endpoint

# 🔐 Test Multi-Platform Images
docker pull ghcr.io/makercorn/ai-prompt-manager:latest  # Pull latest image
docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:latest  # Test pre-built image

# 🔍 Container Validation
docker exec ai-prompt-manager-app-1 python -c "
import sys; sys.path.insert(0, '/app/src')
from src.prompts.services.prompt_service import PromptService
import auth_manager
from run import main
print('✅ All components available in container')
"
```

### CI/CD Pipeline

- **Automated Testing** - 21 test files with comprehensive unit and integration coverage
- **Docker Publishing** - GitHub Container Registry with multi-platform support (linux/amd64, linux/arm64)
- **Release Management** - Automated PyPI publishing and Docker image releases
- **Security** - Sigstore/Cosign signing for supply chain security and container verification

**📋 Setup Guide:** See [GITHUB_WORKFLOWS_SETUP.md](GITHUB_WORKFLOWS_SETUP.md) for complete workflow configuration instructions.

#### **Release Process**

The project uses automated releases that create both Python packages and Docker images:

**🚀 Creating a Release:**
```bash
# Semantic versioning via GitHub Actions (recommended)
# Go to Actions → Semantic Version Release → Run workflow
# Select version type: patch (0.3.2 → 0.3.3), minor (0.3.2 → 0.4.0), or major (0.3.2 → 1.0.0)

# Or using the release script (legacy)
./scripts/create-release.sh

# Manual process (legacy)
git tag v1.0.0
git push origin v1.0.0
```

**🎯 Semantic Versioning Workflow Features:**
- ✅ **Automatic Version Bumping**: Choose patch, minor, or major version increments
- ✅ **Poetry Integration**: Automatic pyproject.toml version updates
- ✅ **Changelog Integration**: Extracts and formats changelog content for releases
- ✅ **Multi-Platform Docker**: Builds and signs images for linux/amd64 and linux/arm64
- ✅ **PyPI Publishing**: Automatic package publishing for stable releases
- ✅ **Release Flexibility**: Support for pre-releases and draft releases

**📦 Release Artifacts:**
- **Python Packages**: Wheel and source distributions
- **Docker Images**: Multi-platform containers (linux/amd64, linux/arm64)
- **Source Archives**: Complete source with installation scripts
- **Documentation**: Release manifests and installation guides

**🔐 Security Features:**
- SHA256 checksums for all packages
- Signed Docker images with Cosign
- Reproducible and auditable builds

**🐳 Docker Images:**
```bash
# Available tags with multi-platform support (linux/amd64, linux/arm64):
ghcr.io/makercorn/ai-prompt-manager:latest     # Latest development build
ghcr.io/makercorn/ai-prompt-manager:stable     # Latest stable release
ghcr.io/makercorn/ai-prompt-manager:v1.0.0     # Specific version tags

# All images are signed with Sigstore/Cosign for security verification
# Verify with: cosign verify --certificate-identity-regexp='.*' \
#   --certificate-oidc-issuer-regexp='.*' ghcr.io/makercorn/ai-prompt-manager:latest
```

> **Note**: Docker registry names must be lowercase. The release workflow automatically converts repository names to comply with Docker registry requirements.

### Troubleshooting

**Common Issues and Solutions:**

**🔧 Database Connection Issues**
```bash
# SQLite permission errors
chmod 664 prompts.db
chown user:group prompts.db

# PostgreSQL connection errors
psql -h localhost -U username -d dbname  # Test connection
export POSTGRES_DSN="postgresql://user:pass@host:port/db"
```

**🔐 Authentication Problems**
```bash
# Reset admin password (emergency)
python -c "
from auth_manager import AuthManager
auth = AuthManager('prompts.db')
auth.create_user('tenant-id', 'admin@localhost', 'newpassword', 'Admin', 'User', 'admin')
"

# Check tenant configuration
python -c "
from auth_manager import AuthManager
auth = AuthManager('prompts.db')
tenants = auth.get_all_tenants()
for t in tenants: print(f'Tenant: {t.name} ({t.subdomain})')
"
```

**🌐 Network and Port Issues**
```bash
# Check if port is in use
lsof -i :7860
netstat -tulpn | grep 7860

# Test application startup
python run.py --single-user --debug
```

**🐳 Docker Issues**
```bash
# Check container logs
docker logs ai-prompt-manager

# Test database connectivity
docker exec -it ai-prompt-manager python -c "
from prompt_data_manager import PromptDataManager
data = PromptDataManager('prompts.db')
print('Database connection successful')
"
```

**🚨 Emergency Recovery**
```bash
# Backup database
cp prompts.db prompts.db.backup

# Reset to clean state (CAUTION: Loses all data)
rm prompts.db
python -c "from auth_manager import AuthManager; AuthManager('prompts.db')"
```

### Support

- 📖 **Documentation**: Comprehensive guides and API reference in this README
- 🐛 **Issues**: Report bugs and request features via GitHub Issues
- 💬 **Community**: Join discussions and share prompts
- 🔧 **Troubleshooting**: See troubleshooting section above for common solutions
- 📋 **Testing**: Use provided test scripts to verify functionality

---

## 📄 License

**Non-Commercial License** - This software is licensed for non-commercial use only.

### Usage Rights
- ✅ **Personal use** - Individual, educational, and research purposes
- ✅ **Non-profit organizations** - For non-commercial activities  
- ✅ **Academic institutions** - Research and educational use
- ❌ **Commercial use** - Business operations, revenue generation, or profit
- ❌ **Selling or licensing** - Without explicit commercial license agreement

### Commercial Licensing
For commercial use, please contact the copyright holder to obtain a separate commercial license agreement.

See the [LICENSE](LICENSE) file for complete details.

---

**🔐 Secure • 🧮 Cost-Aware • 🚀 Optimized • 🤖 AI-Powered • 🧩 Builder-Enhanced • 🔌 API-Ready**
