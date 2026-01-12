import uuid
from .supabase import supabase

def upload_image(file, folder: str):
    """
    Uploads image to Supabase Storage and returns public URL
    """
    ext = file.name.split('.')[-1]
    filename = f"{folder}/{uuid.uuid4()}.{ext}"

    # Upload
    supabase.storage.from_("media").upload(
        filename,
        file.read(),
        file_options={
            "content-type": file.content_type
        }
    )

    # Get public URL
    public_url = supabase.storage.from_("media").get_public_url(filename)

    return public_url
