from markdown_pdf import MarkdownPdf, Section
import base64
import pdfkit

# def generate_image(document_text, client):
#     print("requesting image generation")
#     response = client.responses.create(
#         model="gpt-5",
#         input=f"Generate an image of cv with following text:\n{document_text}",
#         tools=[{"type": "image_generation"}],
#     )
#     image_data = [
#         output.result
#         for output in response.output
#             if output.type == "image_generation_call"
#     ]
#     if image_data:
#         path = get_path("generated_image", "png")
#         image_base64 = image_data[0]
#         with open(path, "wb") as f:
#             f.write(base64.b64decode(image_base64))
#         print(f"saving image as {path}")
#     else:
#         print("image generation failed")


# def save_markdown_as_pdf(markdown_text):
#     path = get_path("from_markdown", "pdf")
#     pdf = MarkdownPdf()
#     pdf.add_section(Section(markdown_text))
#     pdf.save("path")
#     print(f"saving document as {path}")


def save_html_as_pdf(path, html_text):
    pdfkit.from_string(html_text, path)
    print(f"saving document as {path}")

def create_shortcut(path, target):
    with open(path, 'w') as f:
        content = f"[InternetShortcut]\nURL={target}\n"
        f.write(content)
    print(f"creating shortcut {path}")
