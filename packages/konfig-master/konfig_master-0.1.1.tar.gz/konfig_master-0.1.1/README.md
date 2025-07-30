# Konfig ✨

**A dead-simple, yet powerful Python library for managing application configuration from multiple sources.**

---

## Why Konfig?

Application configuration can be messy. You might have settings in **JSON**, environment-specific overrides in **YAML**, and secrets in **environment variables**.

**Konfig** brings sanity to this chaos by providing a single, unified object to access all your settings without the boilerplate.

Our philosophy is simple: **Stop worrying about how to load your config, and just use it.**

---

## Key Features 🚀

- **Multi-Format Support:** Natively loads **JSON**, **YAML**, and **TOML** files with zero configuration.
- **Unified Access:** Access nested values using standard dictionary syntax or convenient dot notation (`config.get('database.host')`).
- **Environment Variable Overrides:** Seamlessly override file settings with environment variables — perfect for Docker and production deployments.
- **Schema Validation:** Use **Pydantic** models to validate your configuration on load, ensuring data integrity and catching errors early.
- **Lightweight & Simple:** Designed with a minimal, intuitive API to be effective without being complex.

---

## Installation ⚙️

Install Konfig directly from **PyPI**:

```bash
pip install konfig-master
```

---

## Quickstart

Get up and running in less than a minute.

### 1️⃣ Create a configuration file (e.g., `settings.yaml`):

```yaml
# settings.yaml
database:
  host: localhost
  port: 5432
  user: "admin"

logging:
  level: "INFO"
```

### 2️⃣ Load and use it in your Python code:

```python
from konfig_master import load

# Load the configuration
config = load('settings.yaml')

# Access values easily
db_host = config.get('database.host')
log_level = config.get('logging.level')

print(f"Connecting to {db_host} with log level {log_level}...")
# Output: Connecting to localhost with log level INFO...
```

---

## Usage

### Accessing Values

✅ **Dictionary-style (strict for known keys):**

```python
port = config['database']['port']  # Raises KeyError if not found
```

✅ **Dot notation `.get()` (safe for optional keys):**

```python
host = config.get('database.host')  # Returns None if not found
timeout = config.get('database.timeout', default=30)  # Provides default if missing
```

---

### Working with Different Formats

Konfig automatically detects file formats (`.json`, `.toml`, `.yaml`) with **no code changes**:

```python
config_json = load('settings.json')
config_toml = load('settings.toml')
```

---

## Advanced Usage

### Environment Variable Overrides

Konfig allows overriding configuration values with environment variables — essential for **Docker** and **Kubernetes**.

1. Export environment variables:

```bash
export MYAPP_DATABASE_PORT=8000
export MYAPP_LOGGING_LEVEL="DEBUG"
```

2. Load configuration with a prefix:

```python
from konfig_master import load

config = load('settings.yaml', env_prefix='MYAPP')

print(config.get('database.port'))    # 8000 (from env)
print(config.get('logging.level'))    # DEBUG (from env)
print(config.get('database.host'))    # localhost (from file)
```

---

### Schema Validation with Pydantic

Validate your configuration upfront to avoid runtime surprises.

```python
from pydantic import BaseModel, Field

class DatabaseConfig(BaseModel):
    host: str
    port: int = Field(gt=1024)  # Must be greater than 1024
    user: str

class Settings(BaseModel):
    database: DatabaseConfig
    logging: dict
```

```python
from konfig_master import load
from pydantic import ValidationError

try:
    config = load('settings.yaml', model=Settings)
    print("Configuration loaded and validated successfully!")
    print(f"Validated Port: {config.database.port}")

except ValidationError as e:
    print("Configuration error!")
    print(e)
```

If the config file contains an invalid value (e.g., port `80`), Konfig will catch this and raise a **ValidationError**.

---

## Contributing 🤝

We welcome contributions!

1. Fork the repository.
2. Create your feature branch:

   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. Commit your changes:

   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

4. Push to the branch:

   ```bash
   git push origin feature/AmazingFeature
   ```

5. Open a **Pull Request**.

---

## License

This project is licensed under the **MIT License**.

---

✨ _Konfig: Load Less. Do More._
