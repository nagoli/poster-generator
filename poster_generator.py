
import reportlab
from PIL import Image
import reportlab.lib.pagesizes as pagesizes
from reportlab.pdfgen import canvas
import os
import argparse



def make_poster_pdf(image_file, output_pdf, horizontal_tile_nb=2, format="A4", orientation="portrait", margin = 70):
    """
        Generate a PDF poster from an image file and save it to output_pdf.

        Args:
            image_file (str): The path to the image file.
            output_pdf (str): The path to the output PDF file.
            horizontal_tile_nb (int, optional): The number of horizontal tiles in the poster. Defaults to 2.
            format (str, optional): The paper format of the PDF. Defaults to "A4".
            orientation (str, optional): The orientation of the PDF. Defaults to "portrait".
            margin (int, optional): The margin size in pixels. Defaults to 70.

        Raises:
            ValueError: Raised if the paper format is unknown or if the image format is unknown.

        Returns:
            None
    """
   
    # manage pdf page attributes
   
    if not hasattr(pagesizes, format) :
        raise ValueError(f"Unknown paper format: {format}")
    page_size = getattr(pagesizes,format)
    if orientation == "portrait":
        page_size = pagesizes.portrait(page_size)
    else :
        page_size = pagesizes.landscape(page_size)


    # Load the image
    # check if extention is svg and convert it to png
    if image_file.endswith(".svg") : 
        import svglib
        drawing = svglib.svglib.svg2rlg(image_file)
        img = reportlab.graphics.renderPM.drawToPIL(drawing,  dpi=300*horizontal_tile_nb)
    elif image_file.endswith(".jpg") or image_file.endswith(".jpeg")  or image_file.endswith(".png") or image_file.endswith(".tiff") or image_file.endswith(".tif") or image_file.endswith(".bmp") or image_file.endswith(".gif") :
        img = Image.open(image_file)
        img = img.convert('RGB')  
    else : 
        raise ValueError(f"Unknown image format: {image_file}")

    # Calculate tile size
    img_width, img_height = img.size
   
    grid_tile_width = page_size[0] - 2*margin
    grid_tile_height = page_size[1] - 2*margin
    h_tile_nb = horizontal_tile_nb
    poster_width = h_tile_nb * grid_tile_width
    min_poster_height = poster_width * img_height / img_width
    quotient, remainder = divmod(min_poster_height, grid_tile_height)
    if remainder == 0:
        v_tile_nb = int(quotient)
    else:
        v_tile_nb = int(quotient) + 1
    poster_height = v_tile_nb * grid_tile_height
    
    tile_width = img_width // h_tile_nb
    tile_height = tile_width * grid_tile_height // grid_tile_width

    
    # Create a PDF
    c = canvas.Canvas(output_pdf, pagesize=page_size)
    c.setFont("Helvetica", 10)
            
    # Crop and add each tile to the PDF
    for i in range(h_tile_nb):
        for j in range(v_tile_nb):
            # Define crop area
            left = i * tile_width
            upper = j * tile_height
            right = left + tile_width
            lower = upper + tile_height

            tmp_grid_tile_height = grid_tile_height
            

            # Crop the image
            crop_img = img.crop((left, upper, right, lower))

            # Save cropped image temporarily
            #os.makedirs("tmp", exist_ok=True)
            temp_img_path = f"temp_{i}_{j}.jpg"
            crop_img.save(temp_img_path, 'JPEG')

            # Add image to PDF
            c.drawImage(temp_img_path, margin, margin, width=grid_tile_width, height=grid_tile_height)
            if (lower > img_height):
                c.setFillColor('white')
                c.setStrokeColor('white')
                h_to_correct = grid_tile_height*(lower-img_height)/tile_height
                c.rect(margin, margin, grid_tile_width, h_to_correct, fill=True, stroke=True)
                
            c.setFillColor('black')
            c.setStrokeColor('black')
            
            # draw corners guide and numbering
            c.line(0,margin,margin,margin)
            c.line(margin,0,margin,margin)
            c.line(0,page_size[1]-margin,margin,page_size[1]-margin)
            c.line(margin,page_size[1],margin, page_size[1]-margin)
            c.line(page_size[0]-margin,0,page_size[0]-margin,margin)
            c.line(page_size[0],margin,page_size[0]-margin,margin)
            c.line(page_size[0],page_size[1]-margin,page_size[0]-margin,page_size[1]-margin)
            c.line(page_size[0]-margin,page_size[1],page_size[0]-margin,page_size[1]-margin)
            
            #add legend text in the corner 
            c.setFont("Courier", 14)
            c.setFillColor('black')
            legend = f"{j+1},{i+1}"
            left_padding=margin-30
            top_padding=page_size[1]-margin+7
            bottom_padding=margin-14
            right_padding=page_size[0]-margin+5
            c.drawString(left_padding,bottom_padding,legend)
            c.drawString(left_padding,top_padding,legend)
            c.drawString(right_padding,bottom_padding,legend)
            c.drawString(right_padding,top_padding,legend)
            
            
            c.setFont("Courier", 10)
            c.setFillColor('grey')
            legend = f"({v_tile_nb},{h_tile_nb})"
            h_shift = 2
            v_shift = 14
            c.drawString(left_padding-h_shift,bottom_padding-v_shift,legend)
            c.drawString(left_padding-h_shift,top_padding+v_shift+2,legend)
            c.drawString(right_padding-h_shift,bottom_padding-v_shift,legend)
            c.drawString(right_padding-h_shift,top_padding+v_shift+2,legend)
            
            #draw cut lines
            
            
            c.line(margin, 0, margin, page_size[1])
            c.line(0, margin, page_size[0], margin)
            c.line(page_size[0]-margin, 0, page_size[0]-margin, page_size[1])
            c.line(0, page_size[1]-margin, page_size[0], page_size[1]-margin)
            
            c.showPage()

            # Delete temporary image
            os.remove(temp_img_path)

    # Save the PDF
    c.save()
    print(f"""Poster created as : {output_pdf}
   > {h_tile_nb}x{v_tile_nb} in format {format}  {orientation} and margin {margin}px""")


def generate_output_filename(input_file, output_name=None):
    """
    Generate the output file name based on the input file and optional output name.

    Parameters:
        input_file (str): The path of the input file.
        output_name (str, optional): The desired name for the output file. If not provided or empty, a new name will be generated based on the input file.

    Returns:
        str: The output file name with the extension ".pdf" added if needed.
    """
    # Check if output_name is None or empty
    if output_name is None or output_name.strip() == "":
        # If it's None or empty, create a new name based on the input_file
        root, _ = os.path.splitext(input_file)
        output_name = f"{root}_poster.pdf"
    else:
        # Check if output_name is an absolute path
        if not os.path.isabs(output_name):
            # If it's not an absolute path, create a new path by joining the input_file's directory with output_name
            input_directory = os.path.dirname(input_file)
            output_name = os.path.join(input_directory, output_name)

        # Check if the extension is already ".pdf," and add it if not
        root, ext = os.path.splitext(output_name)
        if not ext or ext.lower() != ".pdf":
            output_name += ".pdf"

    return output_name


def main():
    """
    Generate a poster from an image that can be printed on common printers. In practice it make a pdf that upsize the image and split it on several pages

    Parameters:
        image_file (str): Path to the input image file
        grid_width (int): Grid width -- the number of pages in the width of your poster
        output (str, optional): Name for the output PDF file
        format (str, optional): Paper format (default: page_size)
        orientation (str, optional): Page orientation portrait or landscape (default: portrait)
        margin (int, optional): Margin in pixels (default: 70)

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="Generate a poster from an image that can be printed on common printers. In practice it make a pdf that upsize the image and split it on several pages")
    parser.add_argument("image_file", help="Path to the input image file")
    parser.add_argument("grid_width", type=int, help="Grid width -- the number of pages in the width of your poster")
    parser.add_argument("-output",  nargs="?", default="", help="Name for the output PDF file")
    parser.add_argument("-format", nargs="?", default="A4", help="Paper format (default: page_size)")
    parser.add_argument("-orientation", nargs="?", default="portrait", help="Page orientation portrait or landscape (default: portrait)")
    parser.add_argument("-margin", type=int, nargs="?", default=70, help="Margin in pixels (default: 70)")

    args = parser.parse_args()
    
    output_file = generate_output_filename(args.image_file, args.output)
    
    make_poster_pdf(
        image_file=args.image_file, 
        output_pdf=output_file, 
        horizontal_tile_nb=args.grid_width, 
        format=args.format, 
        orientation=args.orientation, 
        margin=args.margin)
    

if __name__ == "__main__":
    main()
    
