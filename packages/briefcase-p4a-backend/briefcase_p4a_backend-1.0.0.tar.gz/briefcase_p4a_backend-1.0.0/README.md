# Briefcase P4A Backend

**Python-for-Android (P4A) backend for Briefcase** - Build Android APKs using python-for-android directly within Briefcase's build pipeline.

## Features

- **Direct P4A Integration**: Uses python-for-android without Gradle or Buildozer
- **Briefcase SDK Integration**: Uses Briefcase's Android SDK management system
- **Python 3.13 Compatibility**: Automatically patches pyjnius 1.6.1 for Python 3.13+ compatibility
- **Framework Agnostic**: Works with Kivy, console apps, and other Python frameworks

## Installation

```bash
pip install git+https://github.com/pyCino/briefcase-p4a-backend.git
```

## Usage

1. **Create a new Briefcase project:**
```bash
briefcase new -t https://github.com/pyCino/briefcase-p4a-template.git --template-branch main
# Choose any GUI framework when prompted
```

2. **Configure for P4A backend in `pyproject.toml`:**
```toml
[tool.briefcase.app.yourapp.android]
build_backend = "briefcase_p4a_backend"
```

3. **Build your Android APK:**
```bash
briefcase create android p4a
briefcase build android p4a
```

## How It Works

The P4A backend integrates with Briefcase's existing Android toolchain:

1. **Briefcase Integration**: Registers as `android.p4a` format in Briefcase
2. **Template System**: Uses cookiecutter templates for project structure  
3. **SDK Management**: Leverages Briefcase's Android SDK manager for tools
4. **Python 3.13 Support**: Automatically applies compatibility patches to pyjnius 1.6.1 when using Python 3.13+
6. **APK Generation**: Runs python-for-android with appropriate arguments and handles APK output


## Requirements

- Python 3.8+
- Briefcase 0.3.23+
- Linux (tested on Ubuntu 25.04+)

## Configuration Options

### Basic Configuration
```toml
[tool.briefcase.app.yourapp.android]
# Required: Use P4A backend
build_backend = "briefcase_p4a_backend"
```

### Advanced Options
```toml
[tool.briefcase.app.yourapp.android]
build_backend = "briefcase_p4a_backend"

# Target architectures (defaults to armeabi-v7a, arm64-v8a)
android_archs = ["arm64-v8a"]

# API levels
android_sdk_version = "33"
android_min_sdk_version = "21"

# Custom Android activity (optional)
android_activity = "org.kivy.android.PythonActivity"
```

## Python 3.13 Compatibility

For Python 3.13+, this backend automatically:
- Uses local pyjnius recipe with compatibility patches applied to stable version 1.6.1
- Patches are based on official pyjnius GitHub commit for Python 3.13 `long` type fixes
- No manual intervention required - patches apply automatically when needed

## Troubleshooting

### Common Issues

**"APK not found after build"**
The backend searches multiple locations for the generated APK. Check build logs for details.

### Debug Commands

```bash
# Verbose build
briefcase build android p4a -v

# Clean build
briefcase build android p4a --clean
```

## Supported frameworks

- **Kivy**: Full support with kivy>=2.3.1
- **Other Frameworks**: Any Python framework compatible with python-for-android

## Development

```bash
# Clone and install
git clone https://github.com/pyCino/briefcase-p4a-backend.git
cd briefcase-p4a-backend
pip install -e .

# Test with sample app
briefcase new  # Create test project
# Add build_backend = "briefcase_p4a_backend" to pyproject.toml
briefcase create android p4a
briefcase build android p4a
```

## Related Projects

- [Briefcase](https://github.com/beeware/briefcase) - Cross-platform Python app packaging
- [Python-for-Android](https://github.com/kivy/python-for-android) - Android build system
- [Kivy](https://github.com/kivy/kivy) - Cross-platform GUI framework

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Al pyCino** - Simplifying Android development with Python 