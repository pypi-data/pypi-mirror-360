# Data Content Comparer 🔍

Compare data files to identify differences, changes, and inconsistencies. Perfect for validating data updates and ensuring data consistency.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
data_content_comparer_distributable/
├── input/                  # Place your files to compare here
├── output/                # Comparison reports
├── logs/                  # Detailed execution logs
├── scripts/               # Core implementation (no need to modify)
├── embed_py311/          # Embedded Python environment
├── config.bat            # Configuration settings
└── run.bat              # Start the comparer
```

---

## 🚀 Quick Start

1. **Place your files** in the `input/` folder:
   - Old/reference file
   - New/comparison file
2. **Double-click `run.bat`**
3. **Check results** in the `output/` folder:
   - `differences.xlsx`: Detailed comparison
   - `summary.txt`: Quick overview
   - `visualizations/`: Difference charts

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 500MB free disk space
- Files must be:
  - Excel (.xlsx) or CSV
  - Not password protected
  - Have matching column names
  - Under 1GB each

---

## ⚙️ Configuration

Default settings work for most cases, but you can customize:

1. **Comparison Settings**
   - Comparison mode (full, quick, summary)
   - Column matching rules
   - Difference thresholds
   - Missing value handling

2. **Input Settings**
   - File naming patterns
   - Required columns
   - Data type validation

3. **Output Settings**
   - Report format
   - Visualization options
   - Log detail level

---

## 📊 Example Usage

### Basic Comparison
1. Copy old and new files to `input/`
2. Run the comparer
3. Check difference report

### Advanced Comparison
1. Edit config.bat to set:
   - Comparison mode
   - Column rules
   - Output preferences
2. Run the comparer
3. Check detailed reports

---

## 🔎 Troubleshooting

### Common Issues

1. **"Files Not Found"**
   - Symptom: Can't find input files
   - Solution: Verify files are in input folder

2. **"Column Mismatch"**
   - Symptom: Different columns in files
   - Solution: Check column names match

3. **"Memory Error"**
   - Symptom: Process stops
   - Solution: Use quick mode for large files

### Error Messages

- `[DC001]`: Missing input files
- `[DC002]`: Invalid file format
- `[DC003]`: Column mismatch
- `[DC004]`: Processing error

---

## 📞 Support

- Check `logs/run_log.txt` for detailed error information
- Contact: data.support@organization.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

---

## 📝 Release Notes

### Current Version (1.5.0)
- Added quick comparison mode
- Improved difference detection
- Better memory handling
- Enhanced reporting format

### Known Issues
- Maximum 1GB per input file
- Some Excel formulas may be lost
- Special characters in headers cause issues
- Workaround: Use simple column names

--- 