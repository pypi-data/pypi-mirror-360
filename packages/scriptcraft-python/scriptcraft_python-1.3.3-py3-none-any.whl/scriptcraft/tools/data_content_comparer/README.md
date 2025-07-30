# Data Content Comparer 🔍

A flexible tool for comparing data content between files using different comparison modes. Perfect for validating data changes, migrations, and updates.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This tool was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
data_content_comparer/
├── __init__.py         # Package interface and version info
├── __main__.py         # CLI entry point
├── tool.py            # Core implementation
├── utils.py           # Helper functions
├── plugins/           # Comparison mode plugins
│   ├── __init__.py
│   └── domain_old_vs_new_mode.py
├── tests/             # Test suite
│   ├── __init__.py
│   ├── test_integration.py
│   └── test_tool.py
└── README.md         # This documentation
```

---

## 🚀 Usage (Development)

### Command Line
```bash
python -m scripts.tools.data_content_comparer old.csv new.csv --mode full
```

### Python API
```python
from scripts.tools.data_content_comparer.tool import DataContentComparer

comparer = DataContentComparer()
comparer.run(
    mode="full",
    input_paths=["old.csv", "new.csv"],
    output_dir="output/comparisons",
    domain="Clinical"
)
```

Arguments:
- `mode`: Comparison mode (full, quick, summary)
- `input_paths`: List of files to compare
- `output_dir`: Directory for comparison reports
- `domain`: Optional domain context

---

## ⚙️ Features

- Multiple comparison modes
- Detailed difference reporting
- Support for various file formats
- Domain-specific comparisons
- Configurable comparison rules
- Plugin architecture
- Progress tracking
- Detailed logging

---

## 🔧 Dev Tips

- Use appropriate comparison mode
- Enable debug logging for details
- Consider file sizes for performance
- Implement custom comparison plugins
- Handle missing values properly
- Validate input data types

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
Example files in `tests/data/tools/data_content_comparer/`:
- `old_data.csv`
- `new_data.csv`
- `expected_diffs.xlsx`

---

## 🔄 Dependencies

- pandas >= 1.3.0
- numpy >= 1.20.0
- openpyxl >= 3.0.0
- Python >= 3.8
- common.base.BaseTool

---

## 🚨 Error Handling

Common errors and solutions:
1. Invalid Mode
   - Cause: Unsupported comparison mode
   - Solution: Check available modes
2. File Format Mismatch
   - Cause: Incompatible file formats
   - Solution: Convert to supported format
3. Memory Error
   - Cause: Large file comparison
   - Solution: Use chunked processing

---

## 📊 Performance

- Processing speed depends on:
  - File sizes
  - Comparison mode
  - Number of differences
- Memory usage:
  - Base: ~200MB
  - Per file: Size * 1.5
  - Peak during diff: 2-3x input size
- Optimization tips:
  - Use quick mode for large files
  - Pre-filter unnecessary columns
  - Enable chunked processing

---

## 📋 Development Checklist

### 1. File Structure ⬜
- [ ] Standard package layout
  - [ ] __init__.py with version info
  - [ ] __main__.py for CLI
  - [ ] tool.py for core functionality
  - [ ] utils.py for helpers
  - [ ] tests/ directory
  - [ ] README.md
- [ ] Clean organization
- [ ] No deprecated files

### 2. Documentation ⬜
- [ ] Version information
- [ ] Package-level docstring
- [ ] Function docstrings
- [ ] Type hints
- [ ] README.md
- [ ] API documentation
- [ ] Error code reference
- [ ] Troubleshooting guide

### 3. Code Implementation ⬜
- [ ] Core functionality
- [ ] CLI interface
- [ ] Error handling
- [ ] Input validation
- [ ] Type checking
- [ ] Performance optimization
- [ ] Security considerations

### 4. Testing ⬜
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance tests
- [ ] Edge case tests
- [ ] Error condition tests
- [ ] Test data examples

### 5. Error Handling ⬜
- [ ] Custom exceptions
- [ ] Error messages
- [ ] Error logging
- [ ] Error recovery
- [ ] Input validation

### 6. Performance ⬜
- [ ] Large dataset testing
- [ ] Memory optimization
- [ ] Progress reporting
- [ ] Chunked processing
- [ ] Performance metrics

### 7. Configuration ⬜
- [ ] Command-line arguments
- [ ] Configuration validation
- [ ] Environment variables
- [ ] Default settings
- [ ] Documentation

### 8. Packaging ⬜
- [ ] Dependencies specified
- [ ] Version information
- [ ] Package structure
- [ ] Installation tested
- [ ] Distribution tested

---

## 📋 Current Status and Future Improvements

### ✅ Completed Items
1. **Core Implementation**
   - Base tool class integration
   - Multiple comparison modes
   - Detailed difference reporting
   - Support for various file formats
   - Domain-specific comparisons

2. **Documentation**
   - Main README structure
   - Usage examples
   - Error handling guide
   - Performance metrics

3. **Testing**
   - Basic unit test structure
   - Test data organization
   - Sample test cases
   - Error case testing

### 🔄 Partially Complete
1. **Error Handling**
   - ✅ Basic error types defined
   - ✅ Error messages implemented
   - ❌ Need automatic recovery
   - ❌ Need state preservation

2. **Performance**
   - ✅ Basic metrics documented
   - ✅ Memory usage guidelines
   - ❌ Need parallel processing
   - ❌ Need chunked operations

3. **Testing**
   - ✅ Unit tests
   - ✅ Basic integration
   - ❌ Need performance tests
   - ❌ Need stress testing

### 🎯 Prioritized Improvements

#### High Priority
1. **Error Recovery**
   - Implement automatic recovery
   - Add state preservation
   - Enhance error reporting
   - Add rollback capability

2. **Performance Optimization**
   - Add parallel processing
   - Implement smart diff algorithm
   - Add memory optimization
   - Improve large file handling

3. **Testing Enhancement**
   - Add performance test suite
   - Create stress tests
   - Add edge case coverage
   - Improve test data

#### Medium Priority
4. **Documentation**
   - Add detailed API docs
   - Create troubleshooting guide
   - Add performance tuning guide
   - Document common patterns

5. **User Experience**
   - Add progress tracking
   - Improve error messages
   - Add configuration validation
   - Create interactive mode

#### Low Priority
6. **Feature Enhancements**
   - Add visualization options
   - Support more file formats
   - Add column mapping
   - Create summary reports

7. **Development Tools**
   - Add development utilities
   - Create debugging helpers
   - Add profiling support
   - Improve error messages

---

## 🤝 Contributing

1. Branch naming: `feature/comparer-[feature]`
2. Required tests:
   - Unit tests for comparison logic
   - Integration tests with sample data
3. Documentation:
   - Update README
   - Document comparison modes
   - Update error messages
4. Code review checklist in CONTRIBUTING.md 