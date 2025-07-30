#!/usr/bin/env python3
"""Script to create and populate OpenAI vector store with Rasa documentation."""

import json
import sys
from pathlib import Path
from typing import Dict, List

import openai
import structlog

structlogger = structlog.get_logger()

# Configuration
DOCS_DIR = "rasa_docs_md"
FILE_IDS_FILE = "file_ids.json"
MARKDOWN_TO_URL_FILE = "markdown_to_url.json"
ASSISTANT_NAME = "Rasa Docs Assistant"


def load_url_mapping() -> Dict[str, str]:
    """Load the markdown filename to URL mapping."""
    markdown_to_url_file = Path(MARKDOWN_TO_URL_FILE)

    if not markdown_to_url_file.exists():
        raise FileNotFoundError(
            f"URL mapping file {markdown_to_url_file} not found. "
            "Please run scrape_rasa_docs.py first."
        )

    with open(markdown_to_url_file, "r") as f:
        return json.load(f)


def get_markdown_files(docs_dir: str = DOCS_DIR) -> List[Path]:
    """Get all markdown files in the docs directory."""
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        raise FileNotFoundError(f"Documentation directory {docs_dir} not found")

    md_files = list(docs_path.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No markdown files found in {docs_dir}")

    structlogger.info("vector_store.found_files", count=len(md_files))
    return md_files


def load_or_upload_files(client: openai.OpenAI) -> List[Dict[str, str]]:
    """Load existing file IDs or upload files to OpenAI."""
    file_ids_file = Path(FILE_IDS_FILE)

    if file_ids_file.exists():
        structlogger.info("vector_store.loading_existing_files")
        with open(file_ids_file, "r") as f:
            return json.load(f)

    return upload_files(client)


def upload_files(client: openai.OpenAI) -> List[Dict[str, str]]:
    """Upload markdown files to OpenAI."""
    structlogger.info("vector_store.uploading_files")

    md_files = get_markdown_files()
    uploaded_files = []

    for md_file in md_files:
        try:
            with open(md_file, "rb") as f:
                uploaded = client.files.create(file=f, purpose="assistants")

            file_info = {"file_id": uploaded.id, "file_name": md_file.name}
            uploaded_files.append(file_info)

            structlogger.info(
                "vector_store.file_uploaded",
                file_name=md_file.name,
                file_id=uploaded.id,
            )

        except Exception as e:
            structlogger.error(
                "vector_store.upload_failed", file_name=md_file.name, error=str(e)
            )
            raise

    # Save file IDs for future use
    with open(FILE_IDS_FILE, "w") as f:
        json.dump(uploaded_files, f, indent=2)

    structlogger.info("vector_store.upload_complete", count=len(uploaded_files))
    return uploaded_files


def prepare_files_with_metadata(files: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Prepare files with URL metadata."""
    url_mapping = load_url_mapping()

    files_with_metadata = []
    for file_info in files:
        file_name = file_info["file_name"]
        url = url_mapping.get(file_name, "")

        if not url:
            structlogger.warning("vector_store.missing_url", file_name=file_name)

        files_with_metadata.append(
            {"file_id": file_info["file_id"], "file_name": file_name, "url": url}
        )

    return files_with_metadata


def create_vector_store(
    client: openai.OpenAI, files_with_metadata: List[Dict[str, str]]
) -> str:
    """Create vector store and add files."""
    try:
        # Create vector store
        structlogger.info("vector_store.creating")
        vector_store = client.vector_stores.create(name=ASSISTANT_NAME)

        # Add files to vector store
        for file_meta in files_with_metadata:
            try:
                client.vector_stores.files.create(
                    vector_store_id=vector_store.id,
                    file_id=file_meta["file_id"],
                    attributes={"url": file_meta["url"]},
                )

                structlogger.info(
                    "vector_store.file_added",
                    file_name=file_meta["file_name"],
                    url=file_meta["url"],
                )

            except Exception as e:
                structlogger.error(
                    "vector_store.file_add_failed",
                    file_name=file_meta["file_name"],
                    error=str(e),
                )
                # Continue with other files

        structlogger.info(
            "vector_store.created",
            vector_store_id=vector_store.id,
            files_count=len(files_with_metadata),
        )

        return vector_store.id

    except Exception as e:
        structlogger.error("vector_store.creation_failed", error=str(e))
        raise


def run_vector_store_creation() -> str:
    """Run the complete vector store creation process."""
    client = openai.OpenAI()

    try:
        # Load or upload files
        files = load_or_upload_files(client)

        # Prepare files with metadata
        files_with_metadata = prepare_files_with_metadata(files)

        # Create vector store
        vector_store_id = create_vector_store(client, files_with_metadata)

        print("\n🎉 Vector store created successfully!")
        print(f"Vector store ID: {vector_store_id}")
        print(f"Files processed: {len(files_with_metadata)}")

        return vector_store_id

    except Exception as e:
        structlogger.error("vector_store.process_failed", error=str(e))
        print(f"\n❌ Vector store creation failed: {e}")
        raise


def setup_logging():
    """Setup basic logging."""
    import logging.config

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {"": {"handlers": ["default"], "level": "INFO", "propagate": False}},
    }

    logging.config.dictConfig(logging_config)


def main():
    """Main entry point for the script."""
    setup_logging()

    try:
        run_vector_store_creation()
        return 0

    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
        return 1

    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
