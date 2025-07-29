"""Initialize user configuration for cli-git."""

from typing import Annotated

import typer

from cli_git.utils.config import ConfigManager
from cli_git.utils.gh import (
    GitHubError,
    check_gh_auth,
    get_current_username,
    get_user_organizations,
    mask_token,
    run_gh_auth_login,
    validate_github_token,
)
from cli_git.utils.validators import ValidationError, validate_prefix, validate_slack_webhook_url


def mask_webhook_url(url: str) -> str:
    """Mask Slack webhook URL for display.

    Args:
        url: Slack webhook URL to mask

    Returns:
        Masked URL for display
    """
    if not url:
        return ""

    # https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX
    # -> https://hooks.slack.com/services/XXX.../XXX.../XXX...
    parts = url.split("/")
    if len(parts) >= 7 and "hooks.slack.com" in url:
        # Mask the tokens (parts[4] = T..., parts[5] = B..., parts[6] = XXX...)
        parts[4] = parts[4][:3] + "..." if len(parts[4]) > 3 else parts[4]
        parts[5] = parts[5][:3] + "..." if len(parts[5]) > 3 else parts[5]
        parts[6] = parts[6][:3] + "..." if len(parts[6]) > 3 else parts[6]
    return "/".join(parts)


def ensure_github_auth() -> None:
    """Ensure GitHub CLI is authenticated.

    Raises:
        typer.Exit: If authentication fails
    """
    if not check_gh_auth():
        typer.echo("🔐 GitHub CLI is not authenticated")
        if typer.confirm("Would you like to login now?", default=True):
            typer.echo("📝 Starting GitHub authentication...")
            if run_gh_auth_login():
                typer.echo("✅ GitHub authentication successful!")
            else:
                typer.echo("❌ GitHub login failed")
                raise typer.Exit(1)
        else:
            typer.echo("   Please run: gh auth login")
            raise typer.Exit(1)


def select_organization(orgs: list[str]) -> str:
    """Select organization from list interactively.

    Args:
        orgs: List of available organizations

    Returns:
        Selected organization name or empty string for personal account
    """
    if not orgs:
        typer.echo("\n📋 No organizations found. Using personal account.")
        return ""

    typer.echo("\n📋 Your GitHub organizations:")
    for i, org in enumerate(orgs, 1):
        typer.echo(f"   {i}. {org}")
    typer.echo("   0. No organization (use personal account)")

    while True:
        choice = typer.prompt("\nSelect organization number", default="0")
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return ""
            elif 1 <= choice_num <= len(orgs):
                return orgs[choice_num - 1]
            else:
                typer.echo("Invalid choice. Please try again.")
        except ValueError:
            typer.echo("Please enter a number.")


def collect_slack_config() -> str:
    """Collect Slack webhook URL from user.

    Returns:
        Valid Slack webhook URL or empty string
    """
    typer.echo("\n🔔 Slack Integration (optional)")
    typer.echo("   Enter webhook URL to receive sync failure notifications")

    while True:
        slack_webhook_url = typer.prompt("Slack webhook URL (optional)", default="")
        try:
            validate_slack_webhook_url(slack_webhook_url)
            return slack_webhook_url
        except ValidationError as e:
            typer.echo(str(e))
            typer.echo("   Press Enter to skip or enter a valid URL")


def collect_github_token() -> str:
    """Collect GitHub Personal Access Token from user.

    Returns:
        Valid GitHub token or empty string
    """
    typer.echo("\n🔑 GitHub Personal Access Token (선택사항)")
    typer.echo("   태그 동기화를 위해 필요한 권한:")
    typer.echo("   - repo (전체 저장소 접근)")
    typer.echo("   - workflow (워크플로우 파일 수정)")
    typer.echo("")
    typer.echo("   토큰 생성: https://github.com/settings/tokens/new")
    typer.echo("   토큰이 없으면 Enter를 누르세요 (태그 동기화가 작동하지 않을 수 있음)")

    while True:
        github_token = typer.prompt("GitHub Personal Access Token", default="", hide_input=True)
        if not github_token:
            typer.echo("   ⚠️  토큰 없이 계속합니다. 태그 동기화가 실패할 수 있습니다.")
            return ""
        elif validate_github_token(github_token):
            typer.echo("   ✓ 토큰이 유효합니다.")
            return github_token
        else:
            typer.echo("   ❌ 유효하지 않은 토큰입니다. 다시 시도하거나 Enter를 눌러 건너뛰세요.")


def collect_mirror_prefix() -> str:
    """Collect default mirror prefix from user.

    Returns:
        Valid mirror prefix
    """
    while True:
        default_prefix = typer.prompt("\nDefault mirror prefix", default="mirror-")
        try:
            validate_prefix(default_prefix)
            return default_prefix
        except ValidationError as e:
            typer.echo(str(e))


def show_init_success(
    username: str, default_org: str, slack_webhook_url: str, github_token: str, default_prefix: str
) -> None:
    """Show initialization success message.

    Args:
        username: GitHub username
        default_org: Default organization
        slack_webhook_url: Slack webhook URL
        github_token: GitHub token
        default_prefix: Mirror prefix
    """
    typer.echo()
    typer.echo("✅ Configuration initialized successfully!")
    typer.echo(f"   GitHub username: {username}")
    if default_org:
        typer.echo(f"   Default organization: {default_org}")
    if slack_webhook_url:
        typer.echo(f"   Slack webhook: {mask_webhook_url(slack_webhook_url)}")
    if github_token:
        typer.echo(f"   GitHub token: {mask_token(github_token)}")
    typer.echo(f"   Mirror prefix: {default_prefix}")
    typer.echo()
    typer.echo("Next steps:")
    typer.echo("- Run 'cli-git info' to see your configuration")
    typer.echo("- Run 'cli-git private-mirror <repo-url>' to create your first mirror")


def init_command(
    force: Annotated[bool, typer.Option("--force", "-f", help="Force reinitialization")] = False,
) -> None:
    """Initialize cli-git configuration with GitHub account information."""
    # Ensure GitHub CLI is authenticated
    ensure_github_auth()

    # Get current GitHub username
    try:
        username = get_current_username()
    except GitHubError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(1)

    # Initialize config manager
    config_manager = ConfigManager()
    config = config_manager.get_config()

    # Check if already initialized
    if config["github"]["username"] and not force:
        typer.echo("⚠️  Configuration already exists")
        typer.echo(f"   Current user: {config['github']['username']}")
        if config["github"]["default_org"]:
            typer.echo(f"   Default org: {config['github']['default_org']}")
        typer.echo("   Use --force to reinitialize")
        return

    # Get user organizations and select one
    try:
        orgs = get_user_organizations()
        default_org = select_organization(orgs)
    except GitHubError:
        # Fallback to manual input
        default_org = typer.prompt("\nDefault organization (optional)", default="")

    # Collect configuration from user
    slack_webhook_url = collect_slack_config()
    github_token = collect_github_token()
    default_prefix = collect_mirror_prefix()

    # Update configuration
    updates = {
        "github": {
            "username": username,
            "default_org": default_org,
            "slack_webhook_url": slack_webhook_url,
            "github_token": github_token,
        },
        "preferences": {"default_prefix": default_prefix},
    }
    config_manager.update_config(updates)

    # Show success message
    show_init_success(username, default_org, slack_webhook_url, github_token, default_prefix)
