import os


class EnvironmentVariables:
    """
    Environment variables used by the supervisor package. These are consolidated
    here to have a single source of truth.
    """

    @property
    def run_id(self) -> str:
        """
        Returns:
          (str) The service provider's (Opus or Robocorp) unique ID for this run
        """
        # RC_PROCESS = Robocorp Cloud Process
        # THOUGHTFUL = Opus
        return os.environ.get("RC_PROCESS_RUN_ID") or os.environ.get(
            "THOUGHTFUL_RUN_ID"
        )

    @property
    def callback_url(self) -> str:
        """
        Returns:
          (str) The Fabric endpoint that can receive streaming updates
        """
        return os.environ.get("SUPERVISOR_CALLBACK_URL") or os.environ.get(
            "THOUGHTFUL_CALLBACK_URL"
        )

    @property
    def s3_bucket_uri(self) -> str:
        """
        Returns:
          (str) The location in AWS S3 to which Supervisor should upload
          artifacts to
        """
        return os.environ.get("SUPERVISOR_ARTIFACT_UPLOAD_URI")
