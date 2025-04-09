import cloudinary
import cloudinary.uploader

class UploadFileService:
    """
    Service class for handling file uploads to Cloudinary.

    This class provides functionality to upload files to Cloudinary, configure the Cloudinary
    instance with provided credentials, and generate a URL for the uploaded image with custom settings.

    Attributes:
        cloud_name (str): The Cloudinary cloud name for the account.
        api_key (str): The API key for accessing Cloudinary services.
        api_secret (str): The API secret for accessing Cloudinary services.
    """

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Initializes the UploadFileService with Cloudinary credentials and configures the Cloudinary API.

        Args:
            cloud_name (str): The Cloudinary cloud name for the account.
            api_key (str): The API key for accessing Cloudinary services.
            api_secret (str): The API secret for accessing Cloudinary services.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username: str) -> str:
        """
        Uploads a file to Cloudinary and generates a URL for the uploaded file with custom settings.

        The file is uploaded with a public ID based on the username, and the generated URL
        is cropped and resized to a 250x250 square image.

        Args:
            file: The file to upload. This should be a file-like object (e.g., an image file).
            username (str): The username to use for naming the file's public ID.

        Returns:
            str: The URL of the uploaded image, resized to 250x250 with "fill" crop mode.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url