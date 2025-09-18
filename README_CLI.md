# GDPR Tool CLI - Complete Guide

A comprehensive command-line interface for the GDPR compliance tool that provides file upload, processing, and masking map export capabilities with automatic installation and setup.

## 🚀 Quick Start

```bash
# 1. Run the CLI - it will auto-install itself on first run
./gdpr-cli help

# 2. Use from anywhere after installation
gdpr-cli list-products
gdpr-cli mask /path/to/file.txt --product "Generic"
```

## 📋 Features

- **File Upload**: Upload files with automatic product detection
- **File Processing**: Process files with product-specific masking rules
- **Masking Map Export**: Export masking maps alongside processed files
- **Output Management**: Organized output to `/var/tmp/cli_masking/`
- **Database Integration**: Full integration with existing database and services
- **Global Installation**: Run from anywhere on the server
- **Auto Installation**: Automatic setup and installation on first run
- **Zero Configuration**: No manual setup required

## 🛠️ Installation & Setup

### Option 1: Direct CLI Usage (Recommended)
```bash
# Just run the CLI - it will auto-install itself
./gdpr-cli help

# After first run, CLI is installed globally
cd /tmp
gdpr-cli list-products
```

### Option 2: Automated Setup Script
```bash
# Use the setup script for system-wide installation
./setup-gdpr-cli.sh

# Run CLI (already installed globally)
gdpr-cli help
```

### Option 3: Manual Environment Setup
```bash
# Manual environment setup only
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Use from project directory
./gdpr-cli list-products
```

## 📖 Usage

### CLI Commands
```bash
# Mask a file (upload + process)
gdpr-cli mask /path/to/file.txt --product "Generic"

# List available products
gdpr-cli list-products

# List uploaded files
gdpr-cli list-files

# Show help
gdpr-cli help
```

## 🎯 Examples

### Example: Mask a log file
```bash
# Mask a log file
gdpr-cli mask /var/log/application.log --product "WebApp"

# Output:
# ✅ File masked successfully!
#    File ID: abc123
#    Original: application.log
#    Processed: application_masked.log
#    Output: /var/tmp/cli_masking/WebApp_20241201_143022_application_masked.log
#    Masking Map: /var/tmp/cli_masking/WebApp_20241201_143022_masking_map.json
#    Status: DONE
```

### Example: List available products
```bash
gdpr-cli list-products

# Output:
# 📋 Available Products:
#    1: Generic
#    2: GSX 9000
#    3: C3 Call Controller
#    4: G9 Media Gateway
#    5: SBC 7000
#    6: C20 Call Controller
#    7: Application Server
#    8: EMS
#    9: RAMP
#    10: PSX
#    11: RA
```

## 📁 Output Structure

Processed files and masking maps are saved to `/var/tmp/cli_masking/` with organized naming:

```
/var/tmp/cli_masking/
├── Generic_20241201_143022_application_masked.log
├── Generic_20241201_143022_masking_map.json
├── Database_20241201_150315_users_masked.csv
└── Database_20241201_150315_masking_map.json
```

### File Naming Convention
- `{product_name}_{timestamp}_{original_filename}`
- `{product_name}_{timestamp}_masking_map.json`

### Masking Map Format
```json
{
  "file_id": "file_123",
  "product_name": "Generic",
  "export_timestamp": "2024-12-01T14:30:22.123456",
  "total_mappings": 150,
  "mappings": [
    {
      "id": 1,
      "original_value": "192.168.1.1",
      "masked_value": "192.168.0.1",
      "category": "IPV4_ADDR",
      "created_at": "2024-12-01T14:30:22.123456"
    }
  ]
}
```

## 🔧 How It Works

### Virtual Environment Handling
The CLI automatically:
- ✅ **Detects** if a virtual environment is already active
- ✅ **Activates** the backend `.venv` if needed
- ✅ **Sets up** the environment if it doesn't exist
- ✅ **Provides clear error messages** if setup is incomplete

### Global Installation
The CLI can be installed to run from anywhere:
- ✅ **User Installation**: `~/.local/bin/gdpr-cli` (no sudo required)
- ✅ **System Installation**: `/usr/local/bin/gdpr-cli` (requires sudo)
- ✅ **Symlink Resolution**: Automatically finds project directory
- ✅ **Path Independence**: Works from any directory

### Integration with Existing System
The CLI integrates seamlessly with the existing GDPR tool:
- ✅ **Database**: Uses the same database and models
- ✅ **Services**: Leverages existing FileService, MaskingMapService, and ProcessingConfig
- ✅ **Processing**: Uses the same processing pipeline as the web interface
- ✅ **Authentication**: Creates a dedicated CLI user for operations
- ✅ **Storage**: Uses the same file storage system

## 🛠️ Troubleshooting

### Common Issues

#### 1. Command Not Found
```bash
# Check if symlink exists
ls -la ~/.local/bin/gdpr-cli

# Check PATH
echo $PATH | grep -o '/home/.*/.local/bin'

# Manually add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

#### 2. Virtual Environment Issues
```bash
# Check if venv exists
ls -la backend/.venv/bin/activate

# The CLI will auto-setup on first run
./gdpr-cli help
```

#### 3. Database Connection Error
- Ensure the database is running
- Check database configuration in `backend/app/settings.py`

#### 4. Product Not Found
```bash
# List available products
gdpr-cli list-products

# Ensure the product exists in the database
```

#### 5. Permission Denied
```bash
# Ensure write permissions to /var/tmp/cli_masking/
sudo mkdir -p /var/tmp/cli_masking
sudo chmod 777 /var/tmp/cli_masking

# Or run with appropriate user permissions
```

### Debug Mode
For detailed logging, set the log level in `backend/app/settings.py`:
```python
LOG_LEVEL = "DEBUG"
```

## 🔄 Updating

To update the CLI:
1. Update the project code
2. The symlinks will automatically point to the updated version
3. No need to reinstall unless you move the project directory

## 📋 Uninstallation

### Remove User Installation
```bash
rm ~/.local/bin/gdpr-cli
# Remove from ~/.bashrc manually if desired
```

### Remove System Installation
```bash
sudo rm /usr/local/bin/gdpr-cli
```

## 🎯 Best Practices

1. **Run `./gdpr-cli help`** for first-time auto-installation
2. **Use the setup script** for system-wide installation if needed
3. **Always test** after installation from different directories
4. **Keep the project directory** in a stable location
5. **Use descriptive product names** for better organization
6. **The CLI auto-installs** - no manual setup required

## 🔗 Related Files

- `gdpr-cli` - Main CLI script with auto-installation
- `setup-gdpr-cli.sh` - Automated system installation script
- `backend/cli.py` - Python CLI implementation
- `backend/requirements.txt` - Python dependencies

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Run `gdpr-cli help` for command reference
3. Check the logs in `backend/app/logs/`
4. Ensure all dependencies are installed correctly
