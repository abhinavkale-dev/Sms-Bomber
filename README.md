# SMS Bomber

A cross-platform tool for sending multiple SMS verification requests to a target phone number.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/python-3.6%2B-green)

## 📱 Example

![SMS Bomber in action](Example.jpeg)

*Screenshot showing SMS Bomber sending verification requests to a target number*

## ⚠️ Disclaimer

This tool is provided for **EDUCATIONAL PURPOSES ONLY**. SMS bombing can be considered harassment and may be illegal in many jurisdictions. The authors and contributors are not responsible for any misuse of this software.

- **DO NOT** use this on phone numbers without explicit permission
- **DO NOT** use this tool to harass, annoy, or harm others
- **DO NOT** use this tool for any malicious purposes

## 📋 Features

- Send SMS verification requests in configurable batches
- Cross-platform compatibility (Windows, macOS, Linux)
- Multi-threaded for improved performance
- Batch processing with cooldown periods to avoid rate limiting
- Automatic browser fingerprint randomization
- Detailed progress tracking and statistics
- **Multi-site support** - Rotates between multiple Indian websites for OTP requests

## 🌐 Supported Sites

The script currently supports the following Indian websites (processed in sequence):
- Flipkart
- Myntra
- Cleartrip
- Meesho

Sites are processed in a specific order (Flipkart → Myntra → Cleartrip → Meesho), ensuring a consistent rotation pattern for each attempt.

More sites can be easily added by following the template in the `SUPPORTED_SITES` list and adding them to the `SITE_SEQUENCE` list.

## 🔄 How It Works

1. The script opens multiple Chrome browser instances
2. Each browser processes sites in a specific sequence (Flipkart → Myntra → Cleartrip → Meesho)
3. For each site, it navigates to the login page
4. It enters the target phone number in the login field
5. It clicks the appropriate button to send a verification SMS
6. It verifies if the OTP was actually sent by checking for confirmation messages
7. After completing a batch, it takes a cooldown period
8. It repeats this process for the configured number of batches

## 🔧 Requirements

- Python 3.6 or higher
- Chrome browser installed
- Internet connection
- For Python 3.12+: setuptools package (included in requirements.txt)

## 📦 Installation

1. Clone the repository or download the source code:

```bash
git clone https://github.com/abhinavkale-dev/Sms-Bomber.git
cd sms_bomber
```

2. Create and activate a virtual environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Open `sms_bomber.py` in a text editor and modify these variables at the top of the file:

```python
# Configure these variables
PHONE_NUMBER = "1234567890"  # <-- Put the target phone number here
BATCH_SIZE = 40              # <-- Number of SMS to send per batch (optimized for reliability)
NUMBER_OF_BATCHES = 3        # <-- Number of batches to send
MAX_CONCURRENT_BROWSERS = 8  # <-- Number of parallel browsers per batch (balanced for stability)
BATCH_COOLDOWN = (90, 120)   # <-- Cooldown between batches in seconds (min, max)
```

### Headless Mode

By default, the script runs with visible browser windows. If you want to run in headless mode for better performance (no visible browser windows), uncomment this line in the `generate_fingerprint_options()` function:

```python
# Headless mode for better performance (uncomment if needed)
# options.add_argument('--headless')
```

Note that some websites might detect and block headless browsers, so visible mode is often more reliable but uses more system resources.