# Contributing to Kehua WiseSolar

Thank you for your interest in contributing! This project is open to everyone.

## How to Contribute

### Reporting Bugs
- Open an [issue](../../issues) with a clear description of the problem
- Include your Home Assistant version and integration version
- Add relevant log entries from Home Assistant (`Settings → System → Logs`)

### Suggesting Features
- Open an [issue](../../issues) with the `enhancement` label
- Describe the feature and why it would be useful

### Submitting Code

1. **Fork** this repository
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make your changes** and test them on a real Home Assistant instance
4. **Commit** with a clear message:
   ```bash
   git commit -m "Add support for battery sensors"
   ```
5. **Push** your branch and open a **Pull Request**

### Development Setup

1. Clone the repo into your Home Assistant `custom_components` directory:
   ```bash
   cd /config/custom_components/
   git clone https://github.com/YOUR_USER/kehua_wisesolar.git
   ```
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration → Kehua WiseSolar**

### Code Guidelines

- Follow existing code style and patterns
- Add docstrings to new functions and classes
- Test your changes with a real Kehua inverter if possible
- Keep pull requests focused on a single feature or fix

### API Notes

This integration communicates with the Kehua Energy Cloud API (`energy.kehua.com`). If you're investigating new endpoints or data fields, the WiseSolar+ Android app (package `com.kehua.wisesolarpro`) is a useful reference.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
