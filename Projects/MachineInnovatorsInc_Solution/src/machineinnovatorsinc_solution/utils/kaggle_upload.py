"""Kaggle Dataset upload utility.

Provides a single public function, :func:`push_directory_to_kaggle`, that
uploads a local directory to a Kaggle Dataset (creating it on the first call,
then adding a new version on subsequent calls).

The function is a **no-op** when the ``kaggle`` CLI is not installed, so local
runs that do not set a ``kaggle_dataset_slug`` in their config are completely
unaffected.

Authentication
--------------
The Kaggle CLI requires valid credentials **before** any API call.  Provide
them via **one** of the following methods (in order of preference):

1. **Environment variables** (recommended for CI/CD and Kaggle kernels)::

       export KAGGLE_USERNAME=your-username
       export KAGGLE_KEY=your-api-key

   On a Kaggle kernel these are injected automatically — no extra setup needed.
   On GitHub Actions, store them as repository secrets and expose them in your
   workflow::

       env:
         KAGGLE_USERNAME: ${{ secrets.KAGGLE_USERNAME }}
         KAGGLE_KEY: ${{ secrets.KAGGLE_KEY }}

2. **Credentials file** (convenient for local development)::

       mkdir -p ~/.kaggle
       echo '{"username":"your-username","key":"your-api-key"}' > ~/.kaggle/kaggle.json
       chmod 600 ~/.kaggle/kaggle.json

Get your API key at https://www.kaggle.com/settings → API → "Create New Token".

Prerequisites
-------------
``pip install kaggle``
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import warnings
from pathlib import Path

_KAGGLE_JSON = Path.home() / ".kaggle" / "kaggle.json"


def _check_kaggle_credentials() -> None:
    """Raise ``EnvironmentError`` when no Kaggle credentials can be found.

    Checks (in order):

    1. ``KAGGLE_USERNAME`` **and** ``KAGGLE_KEY`` environment variables.
    2. ``~/.kaggle/kaggle.json`` credentials file.

    Raises
    ------
    EnvironmentError
        If neither source of credentials is available, with a message that
        explains exactly how to fix the problem.
    """
    has_env = bool(os.environ.get("KAGGLE_USERNAME")) and bool(os.environ.get("KAGGLE_KEY"))
    has_file = _KAGGLE_JSON.exists()

    if not has_env and not has_file:
        raise EnvironmentError(
            "Kaggle credentials not found. Provide them via one of:\n"
            "  1. Environment variables (recommended for CI/Kaggle kernels):\n"
            "       export KAGGLE_USERNAME=your-username\n"
            "       export KAGGLE_KEY=your-api-key\n"
            "  2. Credentials file (local development):\n"
            f"       echo '{{\"username\":\"...\",\"key\":\"...\"}}' > {_KAGGLE_JSON}\n"
            f"       chmod 600 {_KAGGLE_JSON}\n"
            "Get your API key at: https://www.kaggle.com/settings → API → Create New Token"
        )


def push_directory_to_kaggle(
    directory: Path | str,
    slug: str,
    *,
    version_notes: str = "automated upload",
) -> None:
    """Upload a local directory to a Kaggle Dataset.

    On the **first call** (dataset does not yet exist on Kaggle) this creates a
    new public dataset.  On **subsequent calls** it creates a new version of the
    existing dataset.

    The function writes a ``dataset-metadata.json`` file into *directory*
    (overwriting any previous one) before invoking the Kaggle CLI, as required
    by the Kaggle API.

    If the ``kaggle`` CLI executable is not available the function emits a
    :class:`RuntimeWarning` and returns without raising, so pipelines that
    run locally without Kaggle credentials are not broken.

    Parameters
    ----------
    directory : Path | str
        Local directory whose contents will be uploaded.  The directory must
        exist and be non-empty.
    slug : str
        Kaggle dataset identifier in ``"username/dataset-slug"`` format,
        e.g. ``"jdoe/tweet-eval-processed"``.
    version_notes : str, optional
        Short description attached to the new dataset version.  Defaults to
        ``"automated upload"``.

    Raises
    ------
    ValueError
        If *slug* does not contain exactly one ``/`` separator.
    FileNotFoundError
        If *directory* does not exist.
    subprocess.CalledProcessError
        If the ``kaggle`` CLI exits with a non-zero status.

    Examples
    --------
    >>> push_directory_to_kaggle(
    ...     Path("/kaggle/working/data/processed/tweet_eval_sentiment"),
    ...     slug="jdoe/tweet-eval-processed",
    ...     version_notes="epoch 3 run",
    ... )
    """
    if shutil.which("kaggle") is None:
        warnings.warn(
            "kaggle CLI not found — skipping Kaggle upload. "
            "Install with: pip install kaggle",
            RuntimeWarning,
            stacklevel=2,
        )
        return

    _check_kaggle_credentials()

    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Upload directory does not exist: {directory}")

    parts = slug.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError(
            f"Invalid Kaggle slug '{slug}'. Expected format: 'username/dataset-slug'."
        )
    username, dataset_slug = parts

    # Write the metadata file required by the Kaggle API
    metadata = {
        "title": dataset_slug.replace("-", " ").title(),
        "id": slug,
        "licenses": [{"name": "CC0-1.0"}],
    }
    metadata_path = directory / "dataset-metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # Determine whether the dataset already exists
    check = subprocess.run(
        ["kaggle", "datasets", "list", "--user", username, "--search", dataset_slug],
        capture_output=True,
        text=True,
    )
    already_exists = dataset_slug in check.stdout

    if already_exists:
        print(
            f"📤 Uploading new version of Kaggle dataset '{slug}' "
            f"from {directory.as_posix()}",
            flush=True,
        )
        cmd = [
            "kaggle", "datasets", "version",
            "--path", str(directory),
            "--message", version_notes,
            "--dir-mode", "zip",
        ]
    else:
        print(
            f"📤 Creating new Kaggle dataset '{slug}' "
            f"from {directory.as_posix()}",
            flush=True,
        )
        cmd = [
            "kaggle", "datasets", "create",
            "--path", str(directory),
            "--dir-mode", "zip",
        ]

    subprocess.run(cmd, check=True)
    print(
        f"✅ Kaggle upload complete: https://www.kaggle.com/datasets/{slug}",
        flush=True,
    )
