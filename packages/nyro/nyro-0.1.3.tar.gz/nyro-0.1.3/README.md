# Nyro - Unified Redis Operations Package
**♠️🌿🎸🧵 G.Music Assembly Consolidation**

> *Transforming 13+ scattered bash scripts into unified Python harmony*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Status](https://img.shields.io/badge/status-ready-green.svg)

## 🎯 What is Nyro?

Nyro is a **complete Python package** that consolidates 13+ bash Redis scripts into a unified, musical, and intuitive interface. Born from Jerry's ⚡ G.Music Assembly vision, it replaces fragmented workflows with harmonic development experiences.

### 🔄 Before vs After

**Before:** 13+ separate bash scripts
```bash
./menu.sh              # Interactive menu
./set-key.sh key val    # Set operations  
./get-key.sh key        # Get operations
./del-key.sh key        # Delete operations
./scan-garden.sh "*"    # Key scanning
./stream-add.sh ...     # Stream operations
./redis-mobile.sh       # Mobile interface
# ... and 6 more scripts
```

**After:** One unified Python package
```bash
nyro interactive        # All menus unified
nyro set key val       # All operations unified
nyro get key           # Clean, consistent interface
nyro scan --garden     # Enhanced with categories
nyro stream diary add  # Logical grouping
# + Musical session tracking!
```

## 🚀 Quick Start

### One-Command Installation
```bash
curl -sSL https://raw.githubusercontent.com/gerico1007/nyro/main/QUICK_SETUP.sh | bash
```

### Manual Installation
```bash
git clone https://github.com/gerico1007/nyro.git
cd nyro
pip install -e .
nyro init
# Edit .env with your Redis credentials
nyro test
nyro interactive
```

## ✨ Key Features

### 🔧 **Unified Operations**
- **Multi-database support** - Route operations across multiple Upstash Redis instances
- **Profile management** - Seamless credential switching
- **Both REST & CLI** - Works with Upstash REST API and direct Redis CLI
- **Interactive menus** - All bash menus consolidated into one interface

### 🎼 **Musical Integration** 
- **Session tracking** - Development sessions become musical compositions
- **ABC notation export** - Generate playable music from your work
- **Team harmonics** - Different roles create distinct musical voices  
- **Rhythmic patterns** - Code patterns translate to musical motifs

### 🏗️ **Architecture**
- **Profile-based** - Easy switching between Redis instances
- **Massive data handling** - Chunked operations for large payloads
- **Security synthesis** - Proper authentication and validation
- **Four-perspective testing** - ♠️🌿🎸🧵 Assembly validation

## 📦 Package Structure

```
nyro/
├── core/              # Redis operations
│   ├── client.py     # Unified Redis client
│   ├── profiles.py   # Multi-database management
│   └── operations.py # Advanced operations
├── cli/               # Command interface
│   ├── main.py       # CLI entry point
│   └── interactive.py # Interactive menus
├── musical/           # Musical integration
│   ├── ledger.py     # Session tracking
│   └── composer.py   # Harmonic generation
└── testing/           # Validation framework
```

## 🎯 Commands Reference

### Basic Operations
```bash
nyro set key value              # Set Redis key
nyro get key                    # Get Redis key  
nyro del key                    # Delete Redis key
nyro scan "pattern*"            # Scan keys with pattern
nyro test                       # Test connection
```

### Advanced Features
```bash
nyro interactive                # Interactive CLI mode
nyro scan --garden             # Categorized key scanning
nyro list push mylist item     # List operations
nyro stream diary add          # Stream operations  
nyro profiles list             # Profile management
nyro music summary             # Musical session summary
```

### Profile Management
```bash
nyro profiles list             # List all profiles
nyro profiles switch secondary # Switch to profile
nyro --profile test interactive # Use specific profile
```

## 🔧 Configuration

### Environment Setup
```env
# Primary Redis database
KV_REST_API_URL=https://your-redis.upstash.io
KV_REST_API_TOKEN=your_token_here

# Additional profiles
PROFILE_SECONDARY_URL=https://secondary-redis.upstash.io
PROFILE_SECONDARY_TOKEN=secondary_token

# Alternative: Redis CLI
REDIS_URL=rediss://user:pass@host:6380
```

### Multiple Profiles
Nyro supports unlimited Redis databases through profile configuration:

```bash
# List available profiles
nyro profiles list

# Switch between databases
nyro profiles switch production
nyro profiles switch testing

# Use temporary profile
nyro --profile staging interactive
```

## 🎼 Musical Features

Nyro includes **unique musical session tracking**:

```bash
# Enable musical logging
nyro --musical interactive

# View session compositions
nyro music summary

# Export ABC notation
nyro music export

# Musical patterns for team members:
# ♠️ Nyro: Structural patterns (X-x-X-x-)
# 🌿 Aureon: Flowing patterns (~~o~~o~~)  
# 🎸 JamAI: Harmonic patterns (G-D-A-E-)
# 🧵 Synth: Terminal patterns (|-|-|-|-)
```

## 🧪 Testing

### Quick Test
```bash
nyro test                      # Test connection
```

### Comprehensive Testing
```bash
python -m testing.test_framework  # Full Assembly tests
```

### Interactive Testing
```bash
nyro interactive
# Choose option 9: "Quick Scan & Test"
```

## 📊 Migration Guide

### From Bash Scripts
Replace your existing bash scripts with Nyro commands:

| Old Bash Script | New Nyro Command |
|----------------|------------------|
| `./menu.sh` | `nyro interactive` |
| `./set-key.sh key val` | `nyro set key val` |
| `./get-key.sh key` | `nyro get key` |
| `./del-key.sh key` | `nyro del key` |
| `./scan-garden.sh "*"` | `nyro scan --garden` |
| `./stream-add.sh stream field val` | `nyro stream diary add` |
| `./push-list.sh list item` | `nyro list push list item` |
| `./redis-mobile.sh` | `nyro interactive` |

### Environment Migration
Your existing `.env` files work with Nyro! Just ensure variables follow the pattern:
- `KV_REST_API_URL` and `KV_REST_API_TOKEN` for default profile
- `PROFILE_NAME_URL` and `PROFILE_NAME_TOKEN` for additional profiles

## 🏆 Benefits

### For Developers
- **80% less code** - 13+ scripts → 1 package
- **Consistent interface** - No more remembering different script syntaxes
- **Better error handling** - Clear messages and guidance
- **Type safety** - Python types vs bash string handling
- **Testing support** - Comprehensive test framework

### For Teams  
- **Musical collaboration** - Sessions become shared compositions
- **Profile sharing** - Easy credential management
- **Garden metaphors** - Redis operations as botanical exploration
- **Assembly methodology** - Four-perspective development validation

### For Operations
- **Cross-platform** - Works on Linux, macOS, Windows
- **Docker support** - Container-ready installation
- **Security synthesis** - Proper authentication handling
- **Massive data support** - Chunked operations for large payloads

## 🤝 Contributing

**We welcome contributions through detailed enhancement requests!**

### 🎯 **How to Collaborate**
The primary way to contribute to Nyro is by **creating detailed enhancement requests as issues** in our GitHub repository:

1. **Visit**: https://github.com/gerico1007/nyro/issues/new
2. **Use our template**: See `CONTRIBUTING.md` for the comprehensive enhancement request format
3. **Engage**: Participate in discussions and help refine ideas

### 🎼 **Types of Contributions Welcome**
- **Feature Enhancements**: New Redis operations, CLI improvements
- **Musical Integration**: ABC notation features, rhythmic patterns
- **Documentation**: Tutorials, examples, installation guides
- **Testing**: Framework improvements, new test scenarios
- **Platform Support**: Docker, cloud deployments, mobile optimizations

### 📋 **Enhancement Request Template**
See `CONTRIBUTING.md` for our detailed template that includes:
- Feature description and motivation
- Musical integration possibilities
- Impact assessment and testing considerations
- Assembly perspective alignment (♠️🌿🎸🧵)

### 🎵 **Assembly Methodology**
Nyro follows the **♠️🌿🎸🧵 G.Music Assembly** approach:

- **♠️ Nyro**: Structural analysis and architecture
- **🌿 Aureon**: Emotional flow and user experience  
- **🎸 JamAI**: Creative solutions and musical integration
- **🧵 Synth**: Terminal orchestration and security

### Development Setup
```bash
git clone https://github.com/gerico1007/nyro.git
cd nyro
pip install -e .[dev]
python -m testing.test_framework
```

**For detailed contribution guidelines, see `CONTRIBUTING.md`**

## 📄 License

MIT License - See LICENSE file for details.

## 🎵 Musical Innovation

Nyro pioneered **musical development documentation** - the first package to transform coding sessions into musical compositions. Each development activity becomes a note, each team member a voice, each session a melody.

> *"Every line of code is a note, every function a phrase, every feature a movement. Together, development teams create symphonies of software."*

## 📞 Support

### 🎯 **Getting Help**
- **🐛 Bug Reports**: [Create an issue](https://github.com/gerico1007/nyro/issues/new?template=bug_report.md)
- **💡 Enhancement Requests**: [Suggest improvements](https://github.com/gerico1007/nyro/issues/new?template=enhancement_request.md)
- **📚 Documentation**: Browse our comprehensive guides below

### 📖 **Documentation**
- **Installation Guide**: See `INSTALLATION.md`
- **Contributing**: See `CONTRIBUTING.md` for detailed collaboration guide
- **Assembly Documentation**: See `CLAUDE.md`  
- **Testing Ledger**: See `testing/ASSEMBLY_LEDGER.md`
- **Musical Enhancement**: See `ECHOTHREADS_ENHANCEMENT_PROPOSAL.md`

### 🤝 **Community Collaboration**
**Primary collaboration method**: Create detailed enhancement requests as issues in [gerico1007/nyro](https://github.com/gerico1007/nyro/issues/new)

---

**🎼 Transform your Redis operations into musical harmony**  
*Built with ♠️🌿🎸🧵 G.Music Assembly methodology*  
*Jerry's ⚡ vision of unified development experiences*