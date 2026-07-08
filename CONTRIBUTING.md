# Contributing

Thank you for your interest in this project! Contributions, corrections, and
extensions are very welcome.

## Ways to contribute

- **Bug reports** — if the code gives wrong results or crashes, open an issue
  with your Python version, OS, and the full error message.
- **Improvements** — better comments, cleaner plots, performance tweaks.
- **Extensions** — ideas listed in README.md (GHZ test, Mermin, loophole analysis).
- **Corrections** — if you spot a physics or maths mistake, please open an issue
  before a pull request so we can discuss it.

## How to submit a pull request

1. Fork the repository and create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes, keeping the same code style (PEP 8, docstrings on all functions).
3. Run the experiment locally and confirm the output looks correct:
   ```bash
   python bell_test.py
   ```
4. Open a pull request with a clear description of what changed and why.

## Code style

- Follow PEP 8.
- Every public function must have a docstring.
- Keep comment blocks that explain the physics — this is an educational project.
- Do not add external dependencies beyond those in `requirements.txt` unless
  there is a very strong reason; open an issue first.

## Disclaimer

This is a personal learning project. Any contributions you make are also
contributed under the Apache 2.0 licence. Views and code in this repository
do not represent IBM or any other organisation.
