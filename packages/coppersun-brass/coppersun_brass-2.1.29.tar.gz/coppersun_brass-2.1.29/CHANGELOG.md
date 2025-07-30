# Changelog

All notable changes to Copper Sun Brass will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.29] - 2025-07-07

### 🔒 MAJOR SECURITY ENHANCEMENT
- **Complete API Key Security Implementation** - Comprehensive security overhaul for API key storage and management
- **Pure Python Encryption** - PBKDF2HMAC + XOR cipher with HMAC authentication using only stdlib 
- **Machine-Specific Key Derivation** - Prevents cross-machine decryption and unauthorized access
- **Secure Configuration Hierarchy** - Environment variables → global config → project config → defaults
- **Encrypted Global Storage** - `~/.config/coppersun-brass/` with 600/700 file permissions

### 🛠️ New CLI Security Commands
- **`brass config audit`** - Comprehensive security analysis with actionable recommendations
- **`brass config show`** - Configuration hierarchy visualization and debugging
- **`brass migrate`** - Automated migration from legacy configurations with dry-run support

### 🔄 Migration & Compatibility
- **Automatic Legacy Detection** - Migration needs identified during `brass init`
- **Safe Migration Process** - Backup creation and comprehensive validation
- **Backward Compatibility** - Seamless transition from existing configurations
- **Complete Cleanup** - Enhanced `brass uninstall` removes all API key locations

### 🧪 Quality Assurance
- **100% Test Coverage** - All 4 migration scenarios validated and passing
- **Blood Oath Compliance** - Zero new dependencies, pure Python implementation
- **Production Validation** - Real-world testing with comprehensive CLI verification

### 🐛 Additional Fixes
- **Fixed invalid regex pattern** in content safety (VAL.7.6.2) - URL encoding pattern correction
- **Enhanced Claude API configuration** - Improved .env file search paths (VAL.7.6.4)  
- **Database access failure resolution** - Shared DCPAdapter implementation (VAL.7.6.1)
- **Branding consistency** - Complete "Copper Sun Brass" naming alignment

### 📚 Documentation
- **Complete implementation reports** with technical details and success metrics
- **Lessons learned documentation** for future security implementations
- **Updated deployment procedures** and packaging guidelines

## [2.0.14] - 2025-07-01

### Fixed
- 🔧 **CRITICAL**: Fixed Scout intelligence persistence pipeline - Scout analysis now properly saves observations to SQLite database and generates JSON files for Claude Code
- 📦 **CRITICAL**: Added missing `anthropic` dependency to setup.py that was causing CLI integration failures in production
- 📦 Fixed version conflicts between setup.py and requirements.txt 
- 🔧 Fixed CLI integration gap that prevented observations from being stored after analysis

### Added
- ⚖️ `brass legal` command for accessing legal documents and license information
- 💾 Persistent intelligence storage system now fully operational
- 📊 JSON output files (analysis_report.json, todos.json, project_context.json) for Claude Code integration
- 🛠️ Shell completion support for enhanced CLI user experience
- 📈 Progress indicators for long-running operations
- 🗑️ `brass uninstall` command for secure credential removal

### Improved
- 🎯 Scout agent now delivers 100% persistent intelligence (previously 0% due to integration gap)
- 🔍 Complete multi-agent pipeline restored (Scout, Watch, Strategist, Planner working in concert)
- 📁 .brass/ directory now populated with actionable intelligence files
- 🚀 Claude Code integration fully functional with persistent memory across sessions

## [2.0.0] - 2025-06-18

### Changed
- 🚀 **Major Rebrand**: DevMind is now Copper Alloy Brass
- Package renamed from `devmind` to `coppersun_brass`
- CLI command changed from `devmind` to `brass`
- Context directory renamed from `.devmind/` to `.brass/`
- License format updated from `DEVMIND-XXXX` to `BRASS-XXXX`
- Environment variables renamed from `DEVMIND_*` to `BRASS_*`

### Added
- Comprehensive migration tool (`brass-migrate`)
- Backward compatibility for old licenses
- Detailed developer environment guide
- Professional documentation structure
- Docker and Kubernetes deployment support
- Enhanced error messages and logging

### Improved
- Reorganized code into standard Python package structure
- Cleaned up development artifacts
- Enhanced documentation with clear user/developer separation
- Better test organization and coverage
- Streamlined installation process

### Compatibility
- ✅ Old license keys automatically converted
- ✅ Environment variables support fallback
- ✅ Configuration files auto-migrate
- ⚠️ Python imports must be updated

### Migration
See [Migration Guide](docs/migration-from-devmind.md) for upgrade instructions.

---

## [1.0.0] - 2025-06-16 (Final DevMind Release)

### Added
- Four specialized agents (Watch, Scout, Strategist, Planner)
- Development Context Protocol (DCP)
- ML-powered code analysis
- Real-time project monitoring
- Strategic planning capabilities
- Claude API integration

### Notes
This was the final release under the DevMind brand.