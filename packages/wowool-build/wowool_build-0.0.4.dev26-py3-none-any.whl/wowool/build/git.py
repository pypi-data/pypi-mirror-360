from logging import getLogger
from os import getcwd
from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Optional, Union
from os import environ

logger = getLogger(__name__)


def _get_repository_path(fp_repo: Optional[Union[str, Path]] = None) -> Path:
    if fp_repo is None:
        return Path(getcwd())
    else:
        return Path(fp_repo).parent if Path(fp_repo).is_file() else Path(fp_repo)


def increment_version(version: str) -> str:
    try:
        parts = version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    except ValueError:
        return version


def make_version(tag: str, nr_commits: int, has_changes: bool):
    postfix = environ.get("WOWOOL_VERSION_POSTFIX", f".dev{nr_commits}+dirty")
    if "dev0" in tag:
        tag = tag.replace(".dev0", "")
        version = f"{tag}.dev{nr_commits}" if has_changes == 0 else f"{tag}{postfix}"
        return version
    else:
        if has_changes == 0:
            if nr_commits == 0:
                return tag
            else:
                tag = increment_version(tag)
                if "WOWOOL_VERSION_POSTFIX" not in environ:
                    version = f"{tag}.dev{nr_commits}"
                else:
                    version = f"{tag}{postfix}"
                return version
        else:
            tag = increment_version(tag)
            version = f"{tag}{postfix}"
            return version


def run_safe(cmd: str, capture_output: bool = True, cwd: Optional[Union[str, Path]] = None) -> str:
    try:
        res = run(cmd, shell=True, check=True, cwd=cwd, capture_output=capture_output)
        return res.stdout.decode("utf-8").strip()
    except CalledProcessError as ex:
        logger.error(f"Error running command: {cmd}")
        logger.error(ex)
        print(ex.stderr.decode("utf-8"))
        print(ex.stderr.decode("utf-8"))
        raise ex


def get_version_info(fp_repo: Optional[Union[str, Path]] = None) -> dict:
    tag = run_safe('''git describe --tags --abbrev=0 --match "[0-9]*.[0-9]*.[0-9.]*"''', cwd=fp_repo)
    nr_commits_result = run_safe(f"git log {tag}..HEAD --oneline", cwd=fp_repo)
    nr_commits = len(nr_commits_result.splitlines())
    has_changes = run("git diff --quiet --exit-code HEAD", shell=True).returncode != 0
    return {"tag": tag, "nr_commits": nr_commits, "has_changes": has_changes}


def get_version(fp_repo: Optional[Union[str, Path]] = None) -> str:
    """
    Get the version from the git history of the given repository folder

    :param fp_repo: Optional repository folder. If not provided, the current
                    working directory is used
    """

    fp_repo = _get_repository_path(fp_repo)
    fn_version = fp_repo / "version.txt"
    if fn_version.is_file():
        version = fn_version.read_text().strip()
        return version

    _git_info = get_version_info(fp_repo)
    return make_version(_git_info["tag"], _git_info["nr_commits"], _git_info["has_changes"])


def move_tag_to_head(tag_name: str, fp_repo: Optional[Union[str, Path]] = None, force: bool = True) -> bool:
    """
    Move a git tag to the current HEAD commit.

    This function deletes the existing tag (if it exists) and creates a new tag
    pointing to the current HEAD commit. Useful for updating tags like "latest"
    to always point to the most recent commit.

    Args:
        tag_name (str): Name of the tag to move
        fp_repo (Optional[Union[str, Path]]): Repository path. If None, uses current directory
        force (bool): If True, forcibly move the tag even if it already exists

    Returns:
        bool: True if tag was moved successfully, False otherwise

    Example:
        >>> move_tag_to_head("latest")
        True
        >>> move_tag_to_head("v1.0.0", "/path/to/repo", force=True)
        True
    """
    fp_repo = _get_repository_path(fp_repo)

    try:
        # Check if tag already exists
        tag_exists = False
        try:
            run_safe(f"git rev-parse {tag_name}", cwd=fp_repo)
            tag_exists = True
            logger.info(f"Tag '{tag_name}' already exists")
        except CalledProcessError:
            logger.info(f"Tag '{tag_name}' does not exist, will create it")

        # If tag exists and we're forcing, delete it first
        if tag_exists:
            if force:
                logger.info(f"Deleting existing tag '{tag_name}'")
                run_safe(f"git tag -d {tag_name}", cwd=fp_repo)
            else:
                logger.error(f"Tag '{tag_name}' already exists and force=False")
                return False

        # Create the tag at HEAD
        logger.info(f"Creating tag '{tag_name}' at HEAD")
        run_safe(f"git tag {tag_name}", cwd=fp_repo)

        logger.info(f"✅ Successfully moved tag '{tag_name}' to HEAD")
        return True

    except CalledProcessError as e:
        logger.error(f"❌ Failed to move tag '{tag_name}': {e}")
        return False


def push_tag_to_remote(tag_name: str, remote: str = "origin", fp_repo: Optional[Union[str, Path]] = None, force: bool = True) -> bool:
    """
    Push a tag to the remote repository.

    Args:
        tag_name (str): Name of the tag to push
        remote (str): Name of the remote (default: "origin")
        fp_repo (Optional[Union[str, Path]]): Repository path. If None, uses current directory
        force (bool): If True, force push the tag (overwrites existing tag on remote)

    Returns:
        bool: True if tag was pushed successfully, False otherwise

    Example:
        >>> push_tag_to_remote("latest")
        True
        >>> push_tag_to_remote("v1.0.0", "upstream", force=True)
        True
    """
    fp_repo = _get_repository_path(fp_repo)

    try:
        # Construct the push command
        push_cmd = f"git push {remote} {tag_name}"
        if force:
            push_cmd = f"git push --force {remote} {tag_name}"

        logger.info(f"Pushing tag '{tag_name}' to remote '{remote}'")
        run_safe(push_cmd, cwd=fp_repo)

        logger.info(f"✅ Successfully pushed tag '{tag_name}' to {remote}")
        return True

    except CalledProcessError as e:
        logger.error(f"❌ Failed to push tag '{tag_name}' to {remote}: {e}")
        return False


def move_and_push_tag(tag_name: str, remote: str = "origin", fp_repo: Optional[Union[str, Path]] = None, force: bool = True) -> bool:
    """
    Move a tag to HEAD and push it to remote in one operation.

    This is a convenience function that combines moving a tag to the current HEAD
    and pushing it to the remote repository.

    Args:
        tag_name (str): Name of the tag to move and push
        remote (str): Name of the remote (default: "origin")
        fp_repo (Optional[Union[str, Path]]): Repository path. If None, uses current directory
        force (bool): If True, force operations (overwrite existing tag)

    Returns:
        bool: True if both operations succeeded, False otherwise

    Example:
        >>> move_and_push_tag("latest")
        True
        >>> move_and_push_tag("v1.0.0", "upstream")
        True
    """
    # First move the tag to HEAD
    if not move_tag_to_head(tag_name, fp_repo, force):
        return False

    # Then push it to remote
    if not push_tag_to_remote(tag_name, remote, fp_repo, force):
        return False

    logger.info(f"✅ Successfully moved and pushed tag '{tag_name}' to {remote}")
    return True


def git_hash(fp_repo: Optional[Union[str, Path]] = None) -> str:
    fp_repo = _get_repository_path(fp_repo)
    result = run("git rev-parse HEAD", capture_output=True, shell=True, check=True, cwd=fp_repo)
    git_hash_rev = result.stdout.decode().strip()
    return git_hash_rev


def ensure_release_exists(repo: str, version: str, create_if_missing: bool = True) -> bool:
    """
    Check if a GitHub release exists and optionally create it if it doesn't.

    Args:
        repo (str): GitHub repository in format 'username/repo'
        version (str): Release tag version
        create_if_missing (bool): If True, create the release if it doesn't exist

    Returns:
        bool: True if release exists or was created, False if it doesn't exist and wasn't created

    Raises:
        requests.HTTPError: If there's an error with the GitHub API
        ValueError: If GITHUB_TOKEN is not set
    """
    import requests

    GITHUB_TOKEN = environ.get("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable is required for GitHub API access")

    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

    # Check if release exists
    release_url = f"https://api.github.com/repos/{repo}/releases/tags/{version}"
    release_resp = requests.get(release_url, headers=headers)

    if release_resp.status_code == 200:
        release_data = release_resp.json()
        logger.info(f"✅ Release '{version}' already exists (ID: {release_data['id']})")
        return True
    elif release_resp.status_code == 404:
        if create_if_missing:
            logger.info(f"⚠️ Release '{version}' not found. Creating it...")
            return _create_release(repo, version, headers)
        else:
            logger.warning(f"❌ Release '{version}' not found and create_if_missing=False")
            return False
    else:
        # Some other error occurred
        release_resp.raise_for_status()
        return False


def _create_release(repo: str, version: str, headers: dict) -> bool:
    """
    Create a new GitHub release.

    Args:
        repo (str): GitHub repository in format 'username/repo'
        version (str): Release tag version
        headers (dict): HTTP headers for GitHub API

    Returns:
        bool: True if release was created successfully

    Raises:
        requests.HTTPError: If there's an error creating the release
    """
    import requests

    # Create the release
    create_url = f"https://api.github.com/repos/{repo}/releases"

    # Prepare release data
    release_data = {
        "tag_name": version,
        "name": version,
        "body": f"Release {version}",
        "draft": False,
        "prerelease": version != "latest" and ("dev" in version or "alpha" in version or "beta" in version or "rc" in version),
    }

    create_resp = requests.post(create_url, headers=headers, json=release_data)

    if create_resp.status_code == 201:
        created_release = create_resp.json()
        logger.info(f"✅ Successfully created release '{version}' (ID: {created_release['id']})")
        return True
    else:
        logger.error(f"❌ Failed to create release '{version}': {create_resp.status_code} {create_resp.text}")
        create_resp.raise_for_status()
        return False


def ensure_latest_release(repo: str) -> bool:
    """
    Ensure that a 'latest' release tag exists in the GitHub repository.

    This is a convenience function specifically for the 'latest' tag commonly
    used for documentation and development builds.

    Args:
        repo (str): GitHub repository in format 'username/repo'

    Returns:
        bool: True if 'latest' release exists or was created successfully

    Example:
        >>> ensure_latest_release("wowool/my-project")
        True
    """
    return ensure_release_exists(repo, "latest", create_if_missing=True)


def upload_raw(repo: str, version: str, file_path: Path, overwrite: bool = False):
    """
    Upload the raw version of the package to the repository
    repo = your-username/your-repo

    Args:
        repo: GitHub repository in format 'username/repo'
        version: Release tag version
        file_path: Path to the file to upload
        overwrite: If True, overwrite existing asset with same name
    """
    import requests

    GITHUB_TOKEN = environ.get("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable is required for GitHub API access")

    file_name = file_path.name

    # ==== STEP 0: Ensure the release exists ====
    if not ensure_release_exists(repo, version, create_if_missing=True):
        raise RuntimeError(f"Failed to ensure release '{version}' exists")

    # ==== STEP 1: Get the release info ====
    release_url = f"https://api.github.com/repos/{repo}/releases/tags/{version}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    release_resp = requests.get(release_url, headers=headers)
    release_resp.raise_for_status()
    release_data = release_resp.json()
    upload_url = release_data["upload_url"].split("{")[0]
    print(f"✅ Found release: {release_data['name']} (ID: {release_data['id']})")

    # ==== STEP 2: Check for existing asset with same name ====
    if overwrite:
        for asset in release_data.get("assets", []):
            if asset["name"] == file_name:
                print(f"Found existing asset '{file_name}' - deleting it first")
                delete_url = f"https://api.github.com/repos/{repo}/releases/assets/{asset['id']}"
                delete_resp = requests.delete(delete_url, headers=headers)
                delete_resp.raise_for_status()
                print("✅ Successfully deleted existing asset")
                break

    # ==== STEP 3: Upload the asset ====
    with open(file_path, "rb") as f:
        headers.update({"Content-Type": "application/gzip"})
        params = {"name": file_name}
        upload_resp = requests.post(upload_url, headers=headers, params=params, data=f)
        upload_resp.raise_for_status()

    print(f"✅ Uploaded: {upload_resp.json()['browser_download_url']}")


def download_raw(repo: str, version: str, file_name: str, output_path: Path):
    """
    Download a raw asset from a GitHub release

    Args:
        repo: GitHub repository in format 'username/repo'
        version: Release tag version
        file_name: Name of the asset to download
        output_path: Path where to save the downloaded file
    """
    import requests

    headers = {"Accept": "application/vnd.github.v3+json"}
    if environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {environ.get('GITHUB_TOKEN')}"

    # GITHUB_TOKEN = environ.get("GITHUB_TOKEN")
    # headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN is not None else {}

    # ==== STEP 1: Get the release info ====
    release_url = f"https://api.github.com/repos/{repo}/releases/tags/{version}"
    release_resp = requests.get(release_url, headers=headers)
    release_resp.raise_for_status()
    release_data = release_resp.json()
    print(f"📦 Found release: {release_data['name']} (ID: {release_data['id']})")

    # ==== STEP 2: Find the asset ====
    asset_id = None
    for asset in release_data.get("assets", []):
        if asset["name"] == file_name:
            asset_id = asset["id"]
            print(f"📄 Found asset: {file_name} (ID: {asset_id})")
            break

    if not asset_id:
        available_assets = ", ".join([asset["name"] for asset in release_data.get("assets", [])])
        raise ValueError(f"Asset '{file_name}' not found in release. Available assets: {available_assets}")

    # ==== STEP 3: Download the asset ====
    download_url = f"https://api.github.com/repos/{repo}/releases/assets/{asset_id}"
    download_headers = headers.copy()
    download_headers.update({"Accept": "application/octet-stream"})

    print(f"Downloading from: {download_url}")
    download_resp = requests.get(download_url, headers=download_headers, stream=True)
    download_resp.raise_for_status()

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    with open(output_path, "wb") as f:
        for chunk in download_resp.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Downloaded {file_name} to {output_path}")
    return output_path
