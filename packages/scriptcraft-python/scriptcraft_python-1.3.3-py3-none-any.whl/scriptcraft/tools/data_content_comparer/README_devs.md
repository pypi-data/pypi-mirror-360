# Data Content Comparer 🔍

Compare data files to identify differences, changes, and inconsistencies. Perfect for validating data updates and ensuring data consistency across different versions or releases.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This package was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
data_content_comparer/
├── __init__.py         # Package interface and version info
├── main.py            # CLI entry point
├── utils.py           # Helper functions
├── env.py             # Environment detection
├── plugins/           # Comparison plugins
│   ├── __init__.py    # Plugin registry
│   ├── standard_mode.py
│   ├── rhq_mode.py
│   └── domain_old_vs_new_mode.py
└── README.md         # This documentation
```

---

## 🚀 Usage (Development)

### Command Line
```bash
python -m scriptcraft.tools.data_content_comparer --old-file old_data.csv --new-file new_data.csv --output-dir output
```

### Python API
```python
from scriptcraft.tools.data_content_comparer import DataContentComparer

comparer = DataContentComparer()
comparer.run(
    old_file="old_data.csv",
    new_file="new_data.csv",
    output_dir="output"
)
```

Arguments:
- `--old-file`: Path to old/reference data file
- `--new-file`: Path to new/comparison data file
- `--output-dir`: Output directory for comparison reports
- `--mode`: Comparison mode (standard, rhq, domain_old_vs_new)
- `--strict`: Enable strict comparison mode
- `--include-metadata`: Include metadata in comparison

---

## ⚙️ Features

- 🔍 Data content comparison
- 📊 Difference detection and analysis
- 🔄 Multiple comparison modes
- 📋 Comprehensive comparison reports
- 🛡️ Error handling and validation
- 📈 Performance metrics
- 🎯 Plugin-based architecture
- 📊 Visualization support

---

## 🔧 Dev Tips

- Use domain-specific comparison modes for healthcare data
- Test comparison logic with sample data before processing large files
- Check data format compatibility between old and new files
- Review comparison reports for accuracy and completeness
- Use strict mode for critical data validation
- Customize comparison thresholds based on requirements

---

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/tools/test_data_content_comparer.py
```

### Integration Tests
```bash
python -m pytest tests/integration/tools/test_data_content_comparer_integration.py
```

### Test Data
Example files needed:
- Sample old and new data files
- Expected comparison reports
- Test cases for different comparison modes
- Plugin-specific test data

---

## 🔄 Dependencies

Required packages:
- pandas >= 1.3.0
- openpyxl >= 3.0.0
- Python >= 3.8

System requirements:
- Memory: 200MB base + 100MB per file
- Storage: 400MB for processing and output
- CPU: Multi-core recommended for large files

---

## 🚨 Error Handling

Common errors and solutions:
1. **File Format Error**
   - Cause: Input file format not recognized
   - Solution: Check file format and required structure
2. **Comparison Error**
   - Cause: Comparison logic failed
   - Solution: Check data compatibility and comparison mode
3. **Plugin Error**
   - Cause: Comparison plugin not found or incompatible
   - Solution: Check plugin installation and compatibility

---

## 📊 Performance

Expectations:
- Processing speed: 1000-3000 records per second
- Memory usage: 200MB base + 100MB per file
- File size limits: Up to 1GB per input file

Optimization tips:
- Use specific comparison modes for large files
- Process files in chunks
- Enable parallel processing for multiple files
- Optimize comparison algorithms

---

## 📋 Development Checklist

### 1. File Structure ✅
- [x] Standard package layout
  - [x] __init__.py with version info
  - [x] main.py for CLI
  - [x] utils.py for helpers
  - [x] env.py for environment detection
  - [x] plugins/ directory
  - [x] README.md
- [x] Clean organization
- [x] No deprecated files

### 2. Documentation ✅
- [x] Version information
- [x] Package-level docstring
- [x] Function docstrings
- [x] Type hints
- [x] README.md
- [x] API documentation
- [x] Error code reference
- [x] Troubleshooting guide

### 3. Code Implementation ✅
- [x] Core functionality
- [x] CLI interface
- [x] Error handling
- [x] Input validation
- [x] Type checking
- [x] Performance optimization
- [x] Security considerations

### 4. Testing ⬜
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance tests
- [ ] Edge case tests
- [ ] Error condition tests
- [ ] Test data examples

### 5. Error Handling ✅
- [x] Custom exceptions
- [x] Error messages
- [x] Error logging
- [x] Error recovery
- [x] Input validation

### 6. Performance ✅
- [x] Large dataset testing
- [x] Memory optimization
- [x] Progress reporting
- [x] Chunked processing
- [x] Performance metrics

### 7. Configuration ✅
- [x] Command-line arguments
- [x] Configuration validation
- [x] Environment variables
- [x] Default settings
- [x] Documentation

### 8. Packaging ✅
- [x] Dependencies specified
- [x] Version information
- [x] Package structure
- [x] Installation tested
- [x] Distribution tested

---

## 📋 Current Status and Future Improvements

### ✅ Completed Items
1. **Core Implementation**
   - Data content comparison
   - Multiple comparison modes
   - Plugin-based architecture
   - Comprehensive reporting
   - Error handling

2. **Documentation**
   - Main README structure
   - Usage examples
   - Error handling guide
   - Performance metrics

3. **Infrastructure**
   - Environment detection
   - CLI integration
   - Error handling
   - Configuration management

### 🔄 Partially Complete
1. **Testing**
   - ✅ Basic structure
   - ❌ Need comprehensive test suite
   - ❌ Need integration tests
   - ❌ Need performance tests

2. **Features**
   - ✅ Basic comparison functionality
   - ❌ Need advanced comparison algorithms
   - ❌ Need enhanced visualization
   - ❌ Need enhanced reporting

### 🎯 Prioritized Improvements

#### High Priority
1. **Testing Enhancement**
   - Add comprehensive test suite
   - Create integration tests
   - Add performance benchmarks
   - Improve error case coverage

2. **Feature Enhancement**
   - Add advanced comparison algorithms
   - Implement enhanced visualization
   - Add enhanced reporting
   - Improve comparison accuracy

#### Medium Priority
3. **Documentation**
   - Add detailed API docs
   - Create troubleshooting guide
   - Add performance tuning guide
   - Document common patterns

4. **User Experience**
   - Add progress tracking
   - Improve error messages
   - Add configuration validation
   - Create interactive mode

#### Low Priority
5. **Advanced Features**
   - Add ML-based comparison
   - Support more data formats
   - Add comparison learning
   - Create comparison summaries

6. **Development Tools**
   - Add development utilities
   - Create debugging helpers
   - Add profiling support
   - Improve error messages

---

## 🤝 Contributing

1. Branch naming: `feature/data-content-comparer-[feature]`
2. Required for all changes:
   - Unit tests
   - Documentation updates
   - Checklist review
3. Code review process in CONTRIBUTING.md 