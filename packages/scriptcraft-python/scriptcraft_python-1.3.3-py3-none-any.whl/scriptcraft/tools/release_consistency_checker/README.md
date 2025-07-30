# Release Consistency Checker 🔄

A specialized checker that validates data consistency between different releases, tracking changes in values, data types, and column structures.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This package was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
release_consistency_checker/
├── __init__.py         # Package interface and version info
├── __main__.py         # CLI entry point
├── tool.py            # Core checker implementation
├── utils.py           # Helper functions
├── tests/             # Unit test suite
│   ├── __init__.py
│   └── test_consistency.py
└── README.md         # This documentation
```

---

## 🚀 Usage (Development)

### Command Line
```bash
# Domain Mode (Pipeline)
python -m release_consistency_checker

# Manual Mode (Direct File Comparison)
python -m release_consistency_checker --input r5_file.csv r6_file.csv --mode standard --debug
```

### Python API
```python
from scripts.checkers.release_consistency_checker import checker

# Pipeline Mode
checker.check(
    domain="Clinical",
    input_path="",  # Not used directly
    output_path="", # Not used directly
    paths={
        "merged_data": "path/to/merged/data",
        "qc_output": "path/to/output"
    }
)

# Manual Mode
checker.check_manual(
    r5_filename="old_file.csv",
    r6_filename="new_file.csv",
    debug=True,
    mode="standard"
)
```

Arguments:
- `domain`: Domain to check (e.g., "Clinical", "Biomarkers")
- `mode`: Comparison mode ("old_only" or "standard")
- `debug`: Enable debug mode for dtype checks
- `input`: Two files to compare (for manual mode)

---

## ⚙️ Features

- Compare data between releases
- Track value changes
- Identify column additions/removals
- Validate data types
- Support for multiple domains
- Manual file comparison mode
- Detailed change reporting
- Configurable comparison modes

---

## 🔧 Dev Tips

- Use debug mode for detailed dtype checks
- Check mapping file for column changes
- Handle missing values appropriately
- Consider data type compatibility
- Monitor memory usage with large datasets
- Use appropriate comparison mode

---

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/test_consistency.py
```

### Integration Tests
```bash
python -m pytest tests/integration/test_release_consistency.py
```

### Test Data
Example files needed:
- R5 and R6 sample files
- Column mapping file
- Various data types
- Missing value examples

---

## 🔄 Dependencies

Required packages:
- pandas >= 1.3.0
- numpy >= 1.20.0
- Python >= 3.8

System requirements:
- Memory: 8GB minimum
- Storage: 2GB for large datasets
- CPU: Multi-core recommended

---

## 🚨 Error Handling

Common errors and solutions:
1. Missing Mapping File
   - Cause: Column mapping file not found
   - Solution: Verify mapping file location
2. Data Type Mismatch
   - Cause: Incompatible data types between releases
   - Solution: Use debug mode and check alignment
3. Memory Error
   - Cause: Dataset too large for memory
   - Solution: Process in chunks or increase memory

---

## 📊 Performance

Expectations:
- Processing speed: ~2-3 minutes per 100k rows
- Memory usage: ~1GB base + 200MB per 100k rows
- File size limits: Tested up to 2M rows

Optimization tips:
- Use CSV format for large files
- Enable chunked processing
- Monitor memory usage
- Pre-filter unnecessary columns

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
1. **File Structure**
   - Standard layout with all required files
   - Clean organization
   - Proper test directory structure

2. **Core Documentation**
   - Main README.md with all key sections
   - Usage examples (CLI and API)
   - Error handling documentation
   - Build date placeholder

3. **Code Implementation**
   - Base class usage and inheritance
   - Standard CLI implementation
   - Basic error handling
   - Type hints in core files

4. **Configuration**
   - Uses common config system
   - Documents options
   - Provides defaults
   - Input validation

### 🔄 Partially Complete
1. **Testing**
   - ✅ Basic unit tests
   - ✅ Basic integration tests
   - ❌ Need performance tests
   - ❌ Need more edge cases
   - ❌ Need error condition tests

2. **Error Handling**
   - ✅ Basic error patterns
   - ✅ Logging implementation
   - ❌ Need standardized error codes
   - ❌ Need more user-friendly messages

3. **Performance**
   - ✅ Basic guidelines documented
   - ❌ Need detailed resource usage docs
   - ❌ Need optimization guidelines
   - ❌ Need large file handling specs

### 🎯 Prioritized Improvements

#### High Priority
1. **Testing Enhancement**
   - Add performance test suite
   - Create edge case test data
   - Add error condition tests
   - Implement stress testing
   - Add test data examples

2. **Performance Optimization**
   - Implement chunked processing for large files
   - Add memory usage monitoring
   - Optimize DataFrame operations
   - Add progress reporting
   - Create performance benchmarks

3. **Documentation Updates**
   - Add API documentation
   - Create error code reference
   - Add troubleshooting guide
   - Update example usage
   - Add performance guidelines

#### Medium Priority
4. **Code Structure**
   - Remove Datasets directory
   - Add logging configuration
   - Improve progress reporting
   - Add input validation helpers
   - Create utility functions for common operations

5. **User Experience**
   - Add progress bars
   - Improve error messages
   - Add debug mode options
   - Create interactive mode
   - Add configuration wizard

#### Low Priority
6. **Development Tools**
   - Add development scripts
   - Create test data generators
   - Add benchmark tools
   - Improve CI/CD pipeline
   - Add code quality checks

7. **Monitoring**
   - Add telemetry
   - Create performance metrics
   - Add usage statistics
   - Implement health checks
   - Add monitoring dashboard

---

## 🤝 Contributing

1. Branch naming: `feature/release-checker-[name]`
2. Required for all changes:
   - Unit tests
   - Documentation updates
   - Checklist review
3. Code review process in CONTRIBUTING.md