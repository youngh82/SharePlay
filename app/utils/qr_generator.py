"""QR code generator"""
import qrcode
import io
import base64


def generate_qr_code(data: str, size: int = 10) -> str:
    """
    Generate a QR code as a base64-encoded PNG image.
    
    Args:
        data: Data to encode in the QR code (usually the room URL)
        size: Size of the QR code (default: 10)
        
    Returns:
        Base64-encoded PNG image string (data URI format)
    """
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    
    return f"data:image/png;base64,{img_base64}"
