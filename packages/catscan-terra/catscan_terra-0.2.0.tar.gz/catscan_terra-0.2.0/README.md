# CatSCAN

**Terraform Cloud multi-workspace scanner**

CatSCAN is a simple, interactive CLI tool that uses the Terraform Cloud API to scan all workspaces in your organization and display a summary of resources currently running. It features an old-school ASCII aesthetic and a menu-driven interface for browsing your previous scan history.

---

## Features

* Fetches all workspaces from Terraform Cloud
* Downloads and parses the current state for each workspace
* Counts and summarizes resource types across workspaces
* Interactive history viewer with detailed scan records
* ASCII-art banner and menu-driven UI via Rich
* Cross-platform support (Windows, macOS/Linux)

---

## Installation

Install from PyPI:

```bash
pip install catscan-terra
```

Or install the latest development version directly from GitHub:

```bash
git clone https://github.com/cloudsifar/catscan.git
cd catscan
pip install --editable .
```

---

## Usage

Run the scanner:

```bash
catscan
```

Or via Python module:

```bash
python -m catscan
```

### Command Options

After starting, CatSCAN will prompt you to configure your Terraform Cloud organization and API token (unless set via environment variables `TFC_ORG_NAME` and `TFC_TOKEN`).

During a scan, you’ll see progress spinners and a final summary table. Options after a scan:

* **H**: View scan history
* **R**: Run another scan
* **Q**: Quit

---

## Configuration

### Environment Variables

For non-interactive or CI usage, export:

* `TFC_ORG_NAME` – your Terraform Cloud organization name
* `TFC_TOKEN` – a Terraform Cloud API token

```bash
export TFC_ORG_NAME="my-org"
export TFC_TOKEN="abcdef1234567890"
```

### Interactive Setup

If no environment variables are found, CatSCAN will prompt you to enter and optionally persist your credentials in your shell configuration (or on Windows, the user environment).

---

## Example Output

```
Found 2 workspaces

📊 Deployed Resources by Workspace (my-org)

Workspace   Resources          Status
--------    ---------          ------
prod-app    aws_instance(4)    ✅ 4
dev         aws_s3_bucket(2)   ✅ 2
---
```

---

## Contributing

I welcome suggestions and improvements! If you’re new to GitHub or pull requests don’t worry – here’s the usual workflow:

1. **Fork the repository** on GitHub to your own account.
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/<your-username>/catscan.git
   cd catscan
   ```
3. **Create a feature branch**:

   ```bash
   git checkout -b feature/my-feature
   ```
4. **Make your changes**, then **commit** them:

   ```bash
   git add .
   git commit -m "Describe your change here"
   ```
5. **Push** the branch to your fork:

   ```bash
   git push origin feature/my-feature
   ```
6. **Open a Pull Request** against `cloudsifar/catscan` via GitHub’s UI.

   * You’ll automatically be notified of comments, CI results, and merge status.
   * I review and manually merge when ready.

Feel free to open **issues** first if you want to discuss big changes or report bugs.

---

## Author

**Simon Farrell** – creator of CatSCAN and Terraform enthusiast. Follow me on [LinkedIn](https://www.linkedin.com/in/simon-farrell-cloud/) for updates.

---

## License

This project is licensed under the [MIT License](LICENSE).
