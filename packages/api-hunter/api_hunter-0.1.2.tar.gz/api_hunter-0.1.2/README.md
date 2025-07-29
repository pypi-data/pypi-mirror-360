# 🕵️‍♂️ API Hunter

**API Hunter** is a lightweight Python tool that scans staged Git files for sensitive credentials like API keys, access tokens, and private keys before you commit them.

> 🔒 Catch secrets before they leak. Simple, fast, and configurable.

---

## 🚀 Features

- ✅ Scans only files added via `git add` (i.e., staged files)
- 🔍 Detects:
  - AWS, GitHub, Google, Slack tokens
  - API keys, auth tokens, secret keys
  - Private keys and database URLs
- ⚡️ Async scanning for fast performance
- 🛠️ Custom regex patterns (add/remove/display)
- 🤖 Gemini integration for automatic regex generation (with API key anonymization)
- 🎨 Colored output for better readability
- 📊 Verbose mode to show matched patterns

---

## 📦 Installation

### From PyPI

```bash
pip install api-hunter

```

---

## 🗑️ Uninstallation

### Remove the package

```bash
pip uninstall api-hunter
```

### Remove created files and directories

The tool creates configuration files in your home directory. To completely remove all traces:

```bash
# Remove the configuration directory and all its contents
rm -rf ~/api_hunt_envs/
```

This will remove:
- Custom regex patterns (`custom_pattern.json`)
- Gemini API key configuration
- Any other configuration files created by the tool

---

## 🛠️ CLI Commands

- **Scan all staged files in git repo:**
  ```bash
  hunt
  ```
- **Scan all staged files with verbose output:**
  ```bash
  hunt -v
  ```
- **Scan a specific file:**
  ```bash
  hunt -n path/to/file.py
  ```
- **Scan a specific file with verbose output:**
  ```bash
  hunt -n path/to/file.py -v
  ```
- **Add a custom pattern:**
  ```bash
  hunt -a "my_service" "my_service_[a-zA-Z0-9]{32}"
  ```
  > **Note:** Use unique key names when adding patterns, as the remove command identifies patterns by their key name.

- **Remove a custom pattern:**
  ```bash
  hunt -r "my_service"
  ```
- **Display all custom patterns:**
  ```bash
  hunt -d
  ```
- **Configure Gemini API key:**
  ```bash
  hunt -c "your-gemini-api-key"
  ```
- **Generate and add a regex for a new API key using Gemini:**
  ```bash
  hunt -re "my_service" "sk-abc123..."
  ```
  > **Note:** The tool randomizes the digits in your API key before sending it to Gemini, so your actual key is never exposed.

---

## 💡 Example Usage

```bash
# Scan all staged files in your git repo
hunt

# Scan all staged files with verbose output (shows matched patterns)
hunt -v

# Scan a specific file
hunt -n path/to/file.py

# Scan a specific file with verbose output
hunt -n path/to/file.py -v

# Add a custom pattern
hunt -a "my_service" "my_service_[a-zA-Z0-9]{32}"

# Remove a custom pattern
hunt -r "my_service"

# Display all custom patterns
hunt -d

# Configure Gemini API key
hunt -c "your-gemini-api-key"

# Generate and add a regex for a new API key using Gemini
hunt -re "my_service" "sk-abc123..."
```

---

## 📝 Notes

- Custom patterns and Gemini API key are stored in `~/api_hunt_envs/`.
- Only files with common code/config extensions are scanned (see `api_hunt/patterns.py`).
- For Gemini integration, you need a valid Google Gemini API key.
- **Privacy:** When generating a regex for your API key using Gemini, API Hunter randomizes the digits in your key before sending it to the LLM. This ensures your actual API key is never exposed to any third party.
- **Verbose Mode:** Use `-v` flag to see the actual matched patterns in colored output (yellow for file names, green for line numbers, red for matched patterns).
- **Custom Patterns:** Use unique key names when adding custom patterns, as the remove command identifies patterns by their key name for deletion.

---

## ⚠️ False Positives & Detection Trade-offs

API Hunter uses pattern-based detection, which means it may generate **false positives** - detecting strings that look like secrets but aren't actually sensitive. This is an inherent limitation of regex-based scanning.

### Why False Positives Occur
- Pattern matching can't distinguish between real API keys and similar-looking strings
- Some legitimate code may contain strings that match secret patterns
- Generic patterns (like `api_key`) may catch variable names or example values

### The Trade-off: Detection vs. Privacy
We prioritize **detection over precision** because:
- **Better safe than sorry:** It's better to catch a false positive than miss a real secret
- **Manual review:** You can quickly verify if a detected pattern is actually sensitive
- **Privacy protection:** Pattern-based detection keeps your actual secrets local

### Alternative: LLM-Based Filtering
While we could use an LLM to filter out false positives, this would require:
- Sending your detected patterns to an external service
- **Risk of exposing real secrets** to third-party LLMs
- Additional API costs and latency

**Our approach:** Keep detection local and let you manually review results, ensuring your secrets never leave your machine.

---

## 🔍 Default Detection Patterns

API Hunter comes with built-in patterns to detect various types of secrets:

### Cloud Services
- **AWS:** Access Keys (`AKIA[0-9A-Z]{16}`), Secret Keys (`[0-9a-zA-Z/+]{40}`)
- **Google:** API Keys (`AIza[0-9A-Za-z\-_]{35}`)
- **Azure:** Generic keys (`[a-f0-9]{32}` or `[A-Za-z0-9+/=]{40,}`)
- **DigitalOcean:** API Tokens (`dop_v1_[0-9a-f]{64}`)

### Development Platforms
- **GitHub:** Personal Access Tokens (`gh[opusr]_[0-9a-zA-Z]{36}`)
- **Slack:** Bot/App Tokens (`xox[boaprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}`)

### AI Services
- **OpenAI:** API Keys (`sk-[a-zA-Z0-9]{48}`, `sk-proj-[a-zA-Z0-9]{48}`)
- **Claude:** API Keys (`sk-ant-api03-[a-zA-Z0-9\-_]{95}`)

### Database & Backend
- **Supabase:** JWT Tokens (`eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+`), Service Keys (`sbp_[a-zA-Z0-9]{40}`)
- **MongoDB Atlas:** Connection Strings (`mongodb\+srv:\/\/[^:\s]+:[^@\s]+@[^\/\s]+`)

### Payment Services
- **Stripe:** Live/Test Keys (`sk_live_[0-9a-zA-Z]{24}`, `sk_test_[0-9a-zA-Z]{24}`, etc.)
- **Square:** API Keys (`sq0[a-z]{3}-[0-9a-zA-Z\-_]{22,43}`)
- **Shopify:** Access Tokens (`shpat_[0-9a-fA-F]{32}`, etc.)

### Communication Services
- **Twilio:** Account/Service Keys (`SK[0-9a-fA-F]{32}`, `AC[0-9a-fA-F]{32}`)
- **SendGrid:** API Keys (`SG\.[0-9a-zA-Z\-_]{22}\.[0-9a-zA-Z\-_]{43}`)
- **Mailgun:** API Keys (`key-[0-9a-zA-Z]{32}`)

### Generic Patterns
- **API Keys:** `api_key`, `apiKey`, `API_KEY` with values
- **Secret Keys:** `secret_key`, `secretKey`, `SECRET_KEY` with values
- **Access Tokens:** `access_token`, `accessToken`, `ACCESS_TOKEN` with values
- **Auth Tokens:** `auth_token`, `authToken`, `AUTH_TOKEN` with values
- **Bearer Tokens:** `Bearer [token]` format
- **Private Keys:** RSA, EC, DSA, OpenSSH, PGP private key headers

### Supported File Extensions
- **Code:** `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.go`, `.rb`, `.php`, `.cs`, `.cpp`, `.c`, `.h`, `.hpp`
- **Scripts:** `.sh`, `.bash`, `.zsh`, `.fish`
- **Config:** `.yml`, `.yaml`, `.json`, `.xml`, `.env`, `.config`, `.conf`, `.ini`
- **Docs:** `.txt`, `.md`, `.rst`
- **Infrastructure:** `.sql`, `.tf`, `.tfvars`
