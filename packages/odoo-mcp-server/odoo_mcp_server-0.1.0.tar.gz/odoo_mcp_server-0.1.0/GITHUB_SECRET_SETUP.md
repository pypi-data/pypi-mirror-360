# Setting up GitHub Secrets for PyPI Publishing

Follow these steps to securely add your PyPI token to GitHub:

## 1. First, Secure Your Token

**IMPORTANT**: Since you shared your token publicly, you should:
1. Go to https://pypi.org/manage/account/token/
2. Revoke the token you shared
3. Create a new token with scope "Entire account" or just for "mcp-server-odoo"
4. Copy the new token (it will start with `pypi-`)

## 2. Add Token to GitHub Repository

1. Go to your repository: https://github.com/vzeman/mcp-server-odoo
2. Click on **Settings** (in the repository navigation)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add the secret:
   - **Name**: `PYPI_API_TOKEN`
   - **Secret**: Paste your complete PyPI token (including the `pypi-` prefix)
6. Click **Add secret**

## 3. Test the Workflow

### Option A: Manual Trigger (Recommended for First Test)
1. Go to the **Actions** tab in your repository
2. Click on "Publish to PyPI" workflow
3. Click **Run workflow**
4. Leave "Publish to Test PyPI" unchecked
5. Click **Run workflow** (green button)

### Option B: Create a Release
1. Go to the **Releases** section of your repo
2. Click **Create a new release**
3. Create a new tag `v0.1.0`
4. Fill in release notes
5. Click **Publish release**

## 4. Monitor the Publishing

1. Go to the **Actions** tab
2. Click on the running workflow
3. Watch the logs to ensure successful publishing
4. Once complete, check https://pypi.org/project/mcp-server-odoo/

## 5. Verify Installation

After successful publishing, test the installation:
```bash
pip install mcp-server-odoo
```

## Troubleshooting

If the workflow fails:
- Check that the secret name is exactly `PYPI_API_TOKEN`
- Ensure the token includes the `pypi-` prefix
- Verify the token has upload permissions
- Check the workflow logs for specific error messages

## Security Best Practices

1. Never commit tokens to your repository
2. Use GitHub Secrets for all sensitive data
3. Regularly rotate your API tokens
4. Use scoped tokens when possible (limit to specific projects)
5. Enable 2FA on your PyPI account