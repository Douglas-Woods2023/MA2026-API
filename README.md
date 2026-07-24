# MA2026 - Minisoft Account 2026 CLI Tool

**MA2026** is a command-line client for the Minisoft Account 2026 authentication system. It provides a simple interface to manage user accounts, including registration, login, TOTP (two-factor authentication), password changes, token revocation, and account deletion.

---

## Features

- **User Registration** – Create a new account with username, password, and optional email.
- **Login** – Authenticate and obtain an access token.
- **Profile** – View user information (without password).
- **TOTP (2FA)** – Enable and verify time-based one-time passwords.
- **Change Password** – Update your password and automatically revoke all existing tokens.
- **Revoke Tokens** – Invalidate all active tokens for a user (requires password).
- **Delete Account** – Permanently remove the account.
- **Logout** – Invalidate a single token.

All commands communicate with a MA2026-compatible server over HTTP/HTTPS.

---

## Requirements

- Python 3.6 or later
- `requests` library (install via `pip install requests`)

---

## Installation

1. Download `ma2026.py` to your local machine.
2. Make it executable (Unix-like systems):
   ```bash
   chmod +x ma2026.py
   ```
3. Optionally, place it in a directory listed in your `PATH` so you can run it as `ma2026`.

---

## Usage

```
ma2026.py <command> [options]
```

Global options:
- `-s, --server <url>` – Override the default server URL (default: `http://uk.frp.one:20017`).
- `-v, --verbose` – Show additional information (e.g., user details on login).

---

## Commands

### `register`
Create a new user account.

```
ma2026.py register -u USERNAME -p PASSWORD [-e EMAIL]
```

- `-u, --username` – Required. Unique username.
- `-p, --password` – Required. Password (minimum 6 characters recommended).
- `-e, --email` – Optional. Email address.

**Example**:
```bash
ma2026.py register -u john_doe -p secure123 -e john@example.com
```

---

### `login`
Authenticate and obtain an access token.

```
ma2026.py login -u USERNAME -p PASSWORD
```

- `-u, --username` – Required.
- `-p, --password` – Required.

**Output**: Prints `Token: <token>` on success. Use `-v` to also display user profile.

**Example**:
```bash
ma2026.py login -u john_doe -p secure123
```

---

### `profile`
Retrieve user profile information (excluding password). Requires a valid token.

```
ma2026.py profile -u USERNAME -t TOKEN
```

- `-u, --username` – Required.
- `-t, --token` – Required. The access token obtained via login.

**Example**:
```bash
ma2026.py profile -u john_doe -t eyJhbGciOiJIUzI1NiIs...
```

---

### `totp-enable`
Generate a TOTP secret and provisioning URI for two-factor authentication. Requires a valid token.

```
ma2026.py totp-enable -u USERNAME -t TOKEN
```

- `-u, --username` – Required.
- `-t, --token` – Required.

**Output**: Prints `Secret:` (Base32 key) and `URI:` (otpauth:// URL for QR code generation).

**Example**:
```bash
ma2026.py totp-enable -u john_doe -t <token>
```

---

### `totp-verify`
Verify a TOTP code (6 digits) for a user. This does **not** require a token.

```
ma2026.py totp-verify -u USERNAME -c CODE
```

- `-u, --username` – Required.
- `-c, --code` – Required. The 6-digit TOTP code.

**Example**:
```bash
ma2026.py totp-verify -u john_doe -c 123456
```
---

### `totp-disable`
Clear the TOTP key used for two-factor authentication. A valid token is required.
```
ma2026.py totp-disable -u USERNAME -t TOKEN
```
- `-u, --username` – Required.
- `-t, --token` – Required.

**Example**:
```bash
ma2026.py totp-disable -u john_doe -t <token>
```

---

### `change-password`
Change the user's password. On success, **all existing tokens are automatically revoked**.

```
ma2026.py change-password -u USERNAME -o OLD_PASSWORD -n NEW_PASSWORD
```

- `-u, --username` – Required.
- `-o, --old_password` – Required. Current password.
- `-n, --new_password` – Required. New password.

**Example**:
```bash
ma2026.py change-password -u john_doe -o oldpass -n newpass456
```

---

### `revoke-tokens`
Revoke **all** active tokens for a user. Requires the user's password (not the token) to prevent abuse.

```
ma2026.py revoke-tokens -u USERNAME -p PASSWORD
```

- `-u, --username` – Required.
- `-p, --password` – Required. The user's password.

**Example**:
```bash
ma2026.py revoke-tokens -u john_doe -p secure123
```

---

### `delete`
Permanently delete the user account. This action is **irreversible**. Requires password confirmation.

```
ma2026.py delete -u USERNAME -p PASSWORD
```

- `-u, --username` – Required.
- `-p, --password` – Required. Password for confirmation.

**Example**:
```bash
ma2026.py delete -u john_doe -p secure123
```

---

### `logout`
Invalidate a single token (log out a specific session). Requires the token itself.

```
ma2026.py logout -t TOKEN
```

- `-t, --token` – Required. The token to revoke.

**Example**:
```bash
ma2026.py logout -t eyJhbGciOiJIUzI1NiIs...
```

---

### `verify-password`
Verify if a given password is correct for a user. This command does **not** require a token.

```
ma2026.py verify-password -u USERNAME -p PASSWORD
```

- `-u, --username` – Required.
- `-p, --password` – Required.

**Example**:
```bash
ma2026.py verify-password -u john_doe -p mypassword123
```

---

## Server Configuration

By default, MA2026 connects to `http://uk.frp.one:20017`. You can override this using the `--server` option on any command. For persistent changes, you can set an environment variable `MA2026_SERVER` or modify the `DEFAULT_SERVER` constant in the script.

---

## Error Handling

- The tool prints error messages to `stderr` and returns a non-zero exit code on failure.
- Exit codes:
  - `0` – Success
  - `1` – General error (network, authentication, etc.)

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome! Please submit issues and pull requests via the project repository.

---

## Disclaimer

MA2026 is part of the Minisoft ecosystem and is intended for use with compatible servers. Use at your own risk; the authors are not responsible for any data loss or security incidents resulting from misuse.
