# Release Consistency Checker 🔄

Compare data files between different releases to ensure consistency and identify changes. Perfect for validating data migrations and updates.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
release_consistency_checker_distributable/
├── input/                  # Place your R5 and R6 files here
├── output/                # Comparison reports
├── logs/                  # Detailed execution logs
├── scripts/               # Core implementation (no need to modify)
├── embed_py311/          # Embedded Python environment
├── config.bat            # Configuration settings
└── run.bat              # Start the checker
```

---

## 🚀 Quick Start

1. **Place your files** in the `input/` folder:
   - Previous release (e.g., `R5_data.xlsx`)
   - New release (e.g., `R6_data.xlsx`)
2. **Double-click `run.bat`**
3. **Check results** in the `output/` folder:
   - `comparison_report.xlsx`: Detailed changes
   - `summary.txt`: Quick overview

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Excel files must be:
  - .xlsx format
  - Not password protected
  - Have consistent column names
  - Contain version identifiers

---

## ⚙️ Configuration

Default settings work for most cases, but you can customize:

1. **Comparison Settings**
   - Comparison mode (strict vs. relaxed)
   - Column matching rules
   - Data type validation level

2. **Input Settings**
   - File naming patterns
   - Required columns
   - Domain configurations

3. **Output Settings**
   - Report detail level
   - Error highlighting
   - Log verbosity

---

## 📊 Example Usage

### Basic Comparison
1. Copy your R5 and R6 files to `input/`
2. Run the checker
3. Review the comparison report

### Domain-Specific Checks
1. Place files in domain-specific folders
2. Edit domain settings in config
3. Run the checker
4. Check domain-specific reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Files Not Found"**
   - Symptom: Checker can't find input files
   - Solution: Verify file names match config

2. **"Column Mismatch"**
   - Symptom: Different columns in R5 vs R6
   - Solution: Check column naming consistency

3. **"Type Mismatch"**
   - Symptom: Data type changes between versions
   - Solution: Verify data consistency

### Error Messages

- `[RC001]`: Missing input files
- `[RC002]`: Column structure changed
- `[RC003]`: Data type inconsistency
- `[RC004]`: Value distribution change

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (2.1.0)
- Added support for multiple domains
- Improved change detection
- Better handling of data type changes
- Enhanced reporting format

### Known Issues
- Large files (>2GB) may be slow
- Some special characters cause issues
- Limited support for non-Excel formats
- Workaround: Convert to .xlsx first

--- 