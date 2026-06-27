import fitz  # PyMuPDF
from fastapi import UploadFile, HTTPException
import io


async def extract_text(file: UploadFile) -> str:
    """
    Extracts text from PDF and TXT files.

    Args:
        file (UploadFile): The uploaded file.

    Returns:
        str: Extracted text content.

    Raises:
        HTTPException: If the file type is not supported.
    """
    content_type = file.content_type
    filename = file.filename or ""

    if content_type == "application/pdf" or filename.endswith(".pdf"):
        try:
            # Read file content into bytes
            file_bytes = await file.read()
            # Open PDF from bytes
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")

    elif content_type == "text/plain" or filename.endswith(".txt"):
        try:
            content = await file.read()
            return content.decode("utf-8")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing TXT: {str(e)}")

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Please upload PDF or TXT files.",
        )
