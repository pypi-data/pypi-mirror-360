import barcode
from barcode.writer import ImageWriter
import os
import PyPDF2
import shutil
import qrcode
from qrcode import constants


def get_file_size(file_path: str) -> int:
    """Function to get file size

    Args:
        file_path (str): Path of the file

    Returns:
        int: Size of the file in bytes

    """
    return os.path.getsize(file_path)

def get_file_extension(file_path: str) -> str:
    """Function to get file extension

    Args:
        file_path (str): Path of the file

    Returns:
        str: Extension of the file
    """
    return os.path.splitext(file_path)[1]

def get_file_name(file_path: str) -> str:
    """Function to get file name wwithout the folder structure.

    Args:
        file_path (str): Path of the file

    Returns:
        str: Name of the file
    """
    return os.path.basename(file_path)

def get_file_name_without_extension(file_path: str) -> str:
    """Function to get file name wwithout the folder structure.

    Args:
        file_path (str): Path of the file

    Returns:
        str: Name of the file
    """
    return os.path.splitext(os.path.basename(file_path))[0]

def get_number_of_pages_of_pdf(file_path: str) -> int:
    """Function to get number of pages

    Args:
        file_path (str): _description_

    Returns:
        int: Number of pages
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at the location {file_path}, Check if the file exists")
    
    if get_file_extension(file_path) != ".pdf":
        raise Exception("File is not a PDF file")
    
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)    
    except Exception as e:
        raise Exception(f"Error reading PDF file: Check if the file is a valid PDF file or corrupted {e}")

def delete_file(file_path: str) -> None:
    """Function to delete file

    Args:
        file_path (str): Path of the file
    """
    
    if os.path.exists(file_path):
        os.remove(file_path)

def rename_pdf_file_with_page_number(file_path: str,add_page_name_at_start:bool=True,keep_original_file_name:bool=False) -> str:
    """Function to rename a PDF file with page number

    Args:
        file_path (str): Path of the file
        add_page_name_at_start (bool, optional): If True, the page number will be added at the start of the file name else at the end. Defaults to True.
        keep_original_file_name (bool, optional): If True, the original file name will be kept else deleted. Defaults to False.

    Returns:
        str: Path of the new file
    """
    
    numnber_of_pages = get_number_of_pages_of_pdf(file_path)

    old_file_name_without_extension = get_file_name_without_extension(file_path)
    
    if add_page_name_at_start:
        new_file_name = f"{numnber_of_pages}_{old_file_name_without_extension}.pdf"
    else:
        new_file_name = f"{old_file_name_without_extension}_{numnber_of_pages}.pdf"

    new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)

    # Delete the old file if it exists

    delete_file(file_path=new_file_path)

    if keep_original_file_name == False:
        os.rename(file_path, new_file_path)
    else:
        shutil.copy2(file_path, new_file_path)

    return new_file_path


def generate_barcode(value,path,barcode_value_to_be_printed:bool=False) -> str:
    """Function to generate a barcode

    Args:
        value (_type_): Value of the barcode
        path (_type_): Path to save the barcode
        barcode_value_to_be_printed (bool, optional): Wether to print the value of barocde at bottom. Defaults to False.

    Raises:
        Exception: _description_

    Returns:
        str: Barcode path
    """
    barcode_string = value

    if isinstance(barcode_string, int) or isinstance(barcode_string, float):
        barcode_string = str(barcode_string)

    if barcode_string == "":
        raise Exception("Barcode value cannot be empty")

    file_path = os.path.dirname(path)

    os.makedirs(file_path, exist_ok=True)

    code128_class = barcode.get_barcode_class('code128')

    sample_barcode = code128_class(barcode_string, writer=ImageWriter())

    barcode_path = sample_barcode.save(path,options={"write_text": barcode_value_to_be_printed})

    return barcode_path

def generate_qr_code(value,path,config:dict={}) -> str:
    """
    Function to generate a QR code.

    Args:
        value (str): The data or text to encode in the QR code.
        path (str): The file path where the generated QR code image will be saved.
        
        config (dict, optional): Configuration for QR code generation. Defaults to {}.

        General Configuration:
            version (int, optional): Controls the size of the QR Code (1 is the smallest, 40 is the largest). Defaults to 1.
            error_correction (int, optional): Level of error correction. Defaults to 1 (Low).
                
                    - 1: Low (7% of codewords can be restored).
                    
                    - 2: Medium (15% of codewords can be restored).
                    
                    - 3: High (25% of codewords can be restored).
                    
                    - 4: Very High (30% of codewords can be restored).

        Display Configuration:
            box_size (int, optional): The size of each box in the QR code grid. Defaults to 10.
            border (int, optional): The width of the border (minimum is 4). Defaults to 4.
            fit (bool, optional): Whether to adjust the QR Code size to fit the data. Defaults to True.

        Color Configuration:
            fill_color (str, optional): The color of the QR code. Defaults to "black".
            back_color (str, optional): The background color of the QR code. Defaults to "white".


        Example:
            config = {
                "version": 1,
                "error_correction": 2,
                "box_size": 10,
                "border": 4,
                "fit": True,
                "fill_color": "blue",
                "back_color": "yellow"
            }

    Returns:
        str: The file path where the QR code image was saved.
    """

    qr = qrcode.QRCode(
        version=config.get("version",1),
        error_correction=config.get("error_correction",constants.ERROR_CORRECT_L),
        box_size=config.get("box_size",10),
        border=config.get("border",4),
    )

    qr.add_data(value)

    qr.make(fit=config.get("fit",True))

    img = qr.make_image(fill_color=config.get("fill_color","black"), back_color=config.get("back_color","white"))

    file_path = os.path.dirname(path)

    os.makedirs(file_path, exist_ok=True)

    if get_file_extension(path) != ".png":
        path = f"{path}.png"

    img.save(path)


if __name__ == "__main__":
    barcode_path = generate_qr_code(value="Hello World",path='new/sample_qrcode') 

    print(barcode_path)