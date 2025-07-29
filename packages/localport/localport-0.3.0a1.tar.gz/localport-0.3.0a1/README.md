# LocalPort

> **🚧 ALPHA RELEASE - Universal port forwarding manager with intelligent health monitoring**

**⚠️ This is alpha software under active development. While core functionality is working and tested, expect breaking changes and incomplete features. Please report issues and provide feedback!**

LocalPort is a modern Python CLI tool that simplifies port forwarding across different technologies (kubectl, SSH) while providing enterprise-grade features like automatic health monitoring, intelligent restart policies, and daemon-mode operation.

## ✨ Why LocalPort?

- **🔄 Universal**: Works with kubectl, SSH, and more - one tool for all your port forwarding needs
- **🏥 Self-Healing**: Automatic health monitoring with intelligent restart policies and exponential backoff
- **⚡ Hot Reload**: Configuration changes applied instantly in daemon mode
- **🎯 Production Ready**: Daemon mode for background operation with comprehensive monitoring
- **🎨 Beautiful CLI**: Rich terminal interface with clean output and progressive verbosity
- **🔧 Flexible**: YAML configuration with environment variable support and validation

## 🚀 Quick Start

### Installation

#### Current Release (Test PyPI)
> **Note**: LocalPort is currently in testing phase and not yet published to production PyPI. Install from Test PyPI for now.

```bash
# Install latest test version with pipx (recommended)
pipx install --index-url https://test.pypi.org/simple/ --pip-args="--extra-index-url https://pypi.org/simple/" localport

# Install with optional dependencies for advanced health checks
pipx install --index-url https://test.pypi.org/simple/ --pip-args="--extra-index-url https://pypi.org/simple/" "localport[kafka,postgres]"

# Alternative: Install with UV
uv tool install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ localport
```

#### Future Stable Release (PyPI)
```bash
# Will be available once testing is complete:
pipx install localport                    # Coming soon
uv tool install localport                 # Coming soon
```

#### Development Installation (GitHub)
```bash
# Install latest from GitHub
pipx install git+https://github.com/dawsonlp/localport.git

# Install specific version/tag
pipx install git+https://github.com/dawsonlp/localport.git@v0.1.0

# Development: Install from source
git clone https://github.com/dawsonlp/localport.git
cd localport && ./scripts/setup-dev.sh
```

### 5-Minute Setup

1. **Create a configuration file** (`localport.yaml`):

```yaml
version: "1.0"

services:
  # Forward PostgreSQL from Kubernetes
  - name: postgres
    technology: kubectl
    local_port: 5432
    remote_port: 5432
    connection:
      resource_name: postgres
      namespace: default
    tags: [database]

  # Forward Redis via SSH tunnel
  - name: redis
    technology: ssh
    local_port: 6379
    remote_port: 6379
    connection:
      host: redis.example.com
      user: deploy
    tags: [cache]
```

2. **Start your services**:

```bash
# Start all services
localport start --all

# Start specific services
localport start postgres redis

# Start services by tag
localport start --tag database
```

3. **Check status**:

```bash
localport status
```

4. **Use your forwarded services**:

```bash
# Connect to PostgreSQL
psql -h localhost -p 5432 -U postgres

# Connect to Redis
redis-cli -h localhost -p 6379
```

That's it! Your services are now accessible locally with automatic health monitoring and restart capabilities.

## 📖 Documentation

### Getting Started
- **[Getting Started Guide](docs/getting-started.md)** - Step-by-step setup for new users
- **[Configuration Guide](docs/configuration.md)** - Complete configuration reference
- **[CLI Reference](docs/cli-reference.md)** - All commands and options

### User Guides
- **[User Guide](docs/user-guide.md)** - Common workflows and best practices
- **[Troubleshooting](docs/troubleshooting.md)** - Solutions for common issues
- **[Examples](docs/examples/)** - Real-world configuration examples

## 🎯 Core Features

### Service Management
```bash
# Start services
localport start postgres redis              # Specific services
localport start --tag database             # By tag
localport start --all                      # All services

# Monitor services
localport status                           # Current status
localport status --watch                   # Live monitoring
localport logs postgres                    # Service logs

# Stop services
localport stop postgres redis              # Specific services
localport stop --all                      # All services
```

### Daemon Mode (Background Operation)
```bash
# Start daemon for background operation
localport daemon start --auto-start

# Check daemon status
localport daemon status

# Reload configuration without restart
localport daemon reload

# Stop daemon
localport daemon stop
```

### Configuration Management
```bash
# Validate configuration
localport config validate

# Export configuration
localport config export --format json

# Export specific services
localport config export --tag database --output backup.yaml
```

## 🔧 Configuration

### Basic Configuration

```yaml
version: "1.0"

services:
  - name: postgres
    technology: kubectl
    local_port: 5432
    remote_port: 5432
    connection:
      resource_name: postgres
      namespace: default
```

### Advanced Configuration with Health Monitoring

```yaml
version: "1.0"

# Global defaults
defaults:
  health_check:
    type: tcp
    interval: 30
    timeout: 5.0
    failure_threshold: 3
  restart_policy:
    enabled: true
    max_attempts: 5
    backoff_multiplier: 2.0

services:
  - name: postgres
    technology: kubectl
    local_port: 5432
    remote_port: 5432
    connection:
      resource_type: service
      resource_name: postgres
      namespace: default
      context: ${KUBE_CONTEXT:minikube}
    enabled: true
    tags: [database, essential]
    description: "PostgreSQL database"
    health_check:
      type: postgres
      config:
        database: postgres
        user: postgres
        password: ${POSTGRES_PASSWORD}
    restart_policy:
      max_attempts: 3
      initial_delay: 2
```

**Supported Health Check Types:**
- **TCP**: Basic connectivity testing
- **HTTP/HTTPS**: Web service health endpoints
- **Kafka**: Message broker connectivity (requires `kafka-python`)
- **PostgreSQL**: Database connectivity (requires `psycopg`)

## 🛠️ Supported Technologies

### Kubernetes (kubectl)
```yaml
- name: service-name
  technology: kubectl
  connection:
    resource_type: service        # service, deployment, pod
    resource_name: my-service
    namespace: default
    context: minikube            # optional
```

### SSH Tunnels
```yaml
- name: service-name
  technology: ssh
  connection:
    host: remote-server.com
    user: deploy
    port: 22                     # optional, default 22
    key_file: ~/.ssh/id_rsa     # optional
    password: secret             # optional (not recommended)
```

## 🌟 Advanced Features

### Hot Configuration Reloading (Daemon Mode)

When running in daemon mode, LocalPort automatically detects configuration changes and applies them without restarting services:

```bash
# Start daemon mode first
localport daemon start --auto-start

# Edit your localport.yaml file
vim localport.yaml

# Changes are automatically applied in daemon mode!
# Check what changed:
localport daemon status
localport status
```

> **Note**: Hot reloading only works in daemon mode. For standalone commands, you'll need to restart services manually after configuration changes.

### Multiple Output Formats

```bash
# Table format (default)
localport status

# JSON for scripting
localport status --output json

# Text for simple parsing
localport status --output text
```

### Environment Variables

Use environment variable substitution for sensitive data:

```yaml
connection:
  host: ${DB_HOST:localhost}
  user: ${DB_USER}
  password: ${DB_PASSWORD}
  key_file: ${SSH_KEY_FILE:~/.ssh/id_rsa}
```

## 🚀 Development

### Requirements

- Python 3.13+
- UV (for dependency management)
- Virtual environment support

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/localport.git
cd localport

# Setup development environment
./scripts/setup-dev.sh

# Activate virtual environment
source .venv/bin/activate

# Install in development mode
uv pip install -e .

# Run tests
uv run pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📊 Status

🎯 **Alpha Release 0.3.0** - Core functionality working with daemon mode and health monitoring!

**Current Progress:**
- ✅ Core Infrastructure (100% complete)
- ✅ kubectl Port Forwarding (100% complete)
- ✅ Process Persistence (100% complete)
- ✅ ConnectionInfo Value Objects (100% complete)
- ✅ Health Monitoring Framework (100% complete)
- ✅ Configuration Management (100% complete)
- ✅ Daemon Mode (100% complete)
- ✅ Basic Testing Suite (100% complete)
- ✅ Hybrid Verbosity System (100% complete)
- 🚧 SSH Tunnels (planned for 0.4.0)
- 🚧 Advanced Health Checks (in progress)
- 🚧 Documentation (in progress)

**Known Issues:**
- **PostgreSQL Health Check**: Requires password configuration (see [Configuration Guide](docs/configuration.md))
- **Kafka Health Check**: May be too aggressive in failure detection
- **SSH Tunnels**: Not yet implemented

**Recent Improvements:**
- ✅ Daemon startup detection and verification
- ✅ Health check interface standardization
- ✅ Progressive verbosity system (-v, -vv, --debug)
- ✅ Clean CLI output by default

## 🔗 Links

- [Requirements](localport.md) - Detailed project requirements
- [Implementation Design](implementation_design_python.md) - Technical architecture and implementation guide
- [Development Guide](docs/development.md) - Development setup and contribution guidelines (coming soon)
