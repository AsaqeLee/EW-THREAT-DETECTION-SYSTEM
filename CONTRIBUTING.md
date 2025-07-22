# Contributing to EW Threat Detection System

Thank you for your interest in contributing to the EW Threat Detection System! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Modern web browser

### Setting up the development environment
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone git@github.com:YOUR_USERNAME/EW-THREAT-DETECTION-SYSTEM.git
   cd EW-THREAT-DETECTION-SYSTEM
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## 📝 How to Contribute

### Reporting Bugs
- Use the bug report template
- Include detailed steps to reproduce
- Provide system information
- Add screenshots if applicable

### Suggesting Features
- Use the feature request template
- Explain the use case clearly
- Consider implementation complexity
- Discuss alternatives

### Code Contributions

#### Branch Naming Convention
- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `docs/description` - for documentation updates
- `refactor/description` - for code refactoring

#### Coding Standards
- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Write comments for complex logic

#### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove)
- Keep the first line under 50 characters
- Add detailed description if needed

Example:
```
Add anomaly detection for sensor data

- Implement Z-score based detection
- Add IQR method for outlier identification
- Update UI to display anomalous sensors
```

#### Testing
- Test your changes thoroughly
- Ensure existing functionality still works
- Add comments explaining test scenarios
- Test on different browsers if UI changes

## 🔍 Code Review Process

1. Create a pull request with a clear description
2. Fill out the PR template completely
3. Ensure all checks pass
4. Respond to reviewer feedback promptly
5. Update documentation if needed

## 📚 Areas for Contribution

### High Priority
- [ ] Unit tests for core algorithms
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] Error handling improvements

### Medium Priority
- [ ] Additional location algorithms
- [ ] Data export functionality
- [ ] Real-time data streaming
- [ ] 3D visualization

### Low Priority
- [ ] Internationalization
- [ ] Theme customization
- [ ] Advanced analytics
- [ ] Machine learning integration

## 🎯 Project Goals

- Maintain high code quality
- Ensure system reliability
- Provide excellent user experience
- Keep documentation up-to-date
- Foster an inclusive community

## 📞 Getting Help

- Open an issue for questions
- Check existing issues and discussions
- Review the README for basic information

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎖️
