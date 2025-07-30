# YNAB Bulk Rename

A command-line tool to bulk rename YNAB (You Need A Budget) payees that match a specific pattern.

## Description

This CLI tool finds payees that match a regex pattern and renames them by removing the matched pattern. By default, it targets payees starting with "CARTE DD/MM " (where DD/MM is a date) and removes this prefix, but you can customize the pattern for your needs.

## Installation

Install from PyPI:
```bash
pip install ynab-bulk-rename
```

Or install from source:
```bash
pip install -e .
```

## Setup

1. Get your YNAB API token:
   - Go to https://app.ynab.com/settings/developer
   - Generate a new Personal Access Token
   - Set it as an environment variable (see below)

## Usage

### Basic Commands

```bash
# Set your YNAB token (required)
export YNAB_TOKEN='your_actual_token_here'

# Dry run with default pattern (shows what would be changed)
ynab-bulk-rename your_budget_id

# Actually perform the rename operations
ynab-bulk-rename your_budget_id --no-dry-run

# Use a custom pattern
ynab-bulk-rename your_budget_id --pattern "^PAYMENT \d{2}/\d{2} "

# Custom pattern with actual rename
ynab-bulk-rename your_budget_id --pattern "^MERCHANT_PREFIX " --no-dry-run
```

### Command Line Arguments

```
positional arguments:
  budget_id             YNAB budget ID to work with

optional arguments:
  -h, --help            show this help message and exit
  --pattern PATTERN, -p PATTERN
                        Regex pattern to match payees (default: '^CARTE \d{2}/\d{2} ')
  --no-dry-run          Actually perform the rename operations (default: dry run only)
  --skip-pause          Skip the pause between API calls (default: pause when ≥199 payees)
  --version             show program's version number and exit
```

### Examples

```bash
# Example 1: Default pattern (dry run)
ynab-bulk-rename fedd1ee2-8048-4e69-95e5-cf2cab422dc5

# Example 2: Actually rename with default pattern
ynab-bulk-rename fedd1ee2-8048-4e69-95e5-cf2cab422dc5 --no-dry-run

# Example 3: Custom pattern for different card format
ynab-bulk-rename fedd1ee2-8048-4e69-95e5-cf2cab422dc5 --pattern "^CARD \d{4} "

# Example 4: Remove merchant prefixes
ynab-bulk-rename fedd1ee2-8048-4e69-95e5-cf2cab422dc5 --pattern "^MERCHANT " --no-dry-run

# Example 5: Skip pauses for faster processing (use with caution)
ynab-bulk-rename fedd1ee2-8048-4e69-95e5-cf2cab422dc5 --no-dry-run --skip-pause

# Example 6: One-time usage with environment variable
YNAB_TOKEN='your_token' ynab-bulk-rename your_budget_id --no-dry-run
```

## Environment Variables

- **YNAB_TOKEN** (required): Your YNAB Personal Access Token
  - Get it from: https://app.ynab.com/settings/developer
  - Keep it secure - never commit it to version control!

## Example Output

**Small batch (under rate limit):**
```
🎯 Budget ID: fedd1ee2-8048-4e69-95e5-cf2cab422dc5
🔍 Pattern: ^CARTE \d{2}/\d{2} 
🏃 Mode: ACTUAL RENAME
--------------------------------------------------
Fetching payees...
Found 5 payees matching the pattern:
⚡ No pauses needed - 5 payees is under rate limit (199)

  - CARTE 15/12 GROCERY STORE -> GROCERY STORE
Successfully renamed payee to: GROCERY STORE
  - CARTE 16/12 GAS STATION -> GAS STATION
Successfully renamed payee to: GAS STATION
  - CARTE 17/12 RESTAURANT -> RESTAURANT
Successfully renamed payee to: RESTAURANT

✅ Successfully processed 5 payees!
```

**Large batch (with rate limiting):**
```
🎯 Budget ID: fedd1ee2-8048-4e69-95e5-cf2cab422dc5
🔍 Pattern: ^CARTE \d{2}/\d{2} 
🏃 Mode: ACTUAL RENAME
--------------------------------------------------
Fetching payees...
Found 200 payees matching the pattern:
⚠️  YNAB API Rate Limit: 200 requests/hour
⏱️  Estimated completion time: ~1h 6m
    (20 second pause between each rename to stay within limits)

  - CARTE 15/12 GROCERY STORE -> GROCERY STORE
Successfully renamed payee to: GROCERY STORE
    ⏳ Pausing for 20 seconds... (1/200 completed)
  - CARTE 16/12 GAS STATION -> GAS STATION
...
```

## Safety Features

- **Dry Run Mode**: By default, the tool only shows what would be changed without making actual changes
- **Error Handling**: Includes proper error handling for API requests and invalid regex patterns
- **Pattern Validation**: Validates regex patterns before processing
- **Intelligent Rate Limiting**: Automatically skips pauses when processing <199 payees (within rate limit)
- **Manual Pause Control**: `--skip-pause` option to override rate limiting (use with caution)
- **Graceful Interruption**: Can be cancelled safely with Ctrl+C

## Performance Notes

⚠️ **Rate Limiting**: The YNAB API has a rate limit of 200 requests per hour.

### Automatic Optimization:
- **≤198 payees**: No pauses needed (instant processing)
- **≥199 payees**: 20-second pauses between operations
- **Manual override**: `--skip-pause` skips all pauses (use carefully)

### Timing Examples:
- **1-198 payees**: Instant (no pauses)
- **199+ payees**: ~20 seconds per payee after the first
- **Example**: 5 payees = instant, 250 payees = ~1 hour 20 minutes

The tool will show the processing strategy before starting operations.

## Regex Pattern Examples

- `^CARTE \d{2}/\d{2} ` - Matches "CARTE 15/12 STORE" → "STORE"
- `^PAYMENT \d{4} ` - Matches "PAYMENT 1234 DESC" → "DESC"
- `^MERCHANT ` - Matches "MERCHANT STORE NAME" → "STORE NAME"
- `^CARD\*\d{4} ` - Matches "CARD*1234 PURCHASE" → "PURCHASE"

## Requirements

- Python 3.10+
- requests library
- Valid YNAB API token
- YNAB budget with payees to rename
