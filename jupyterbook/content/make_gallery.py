import glob
import os

import nbformat
from nbconvert.exporters import markdown

SITE_DIR = "."
IMAGE_DIR = os.path.join(SITE_DIR, "images")


def extract_notebook_info(nb_path):
    title = "No title"
    image = "images/placeholder.png"
    exporter = markdown.MarkdownExporter()
    output, resources = exporter.from_filename(nb_path)
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("#"):
            title = line.strip("#").strip()
            break

    images = sorted(resources["outputs"])
    if images:
        img_file = images[-1]
        thumb_name = os.path.join(
            IMAGE_DIR,
            os.path.splitext(os.path.basename(nb_path))[0]
            + os.path.splitext(img_file)[-1],
        )

        with open(os.path.join(thumb_name), "wb") as thumb:
            thumb.write(resources["outputs"][img_file])

        image = os.path.relpath(thumb_name, SITE_DIR)
    link = f"./{nb_path.replace('.ipynb', '.html')}"
    return title, image, link


def make_gallery_entry(nb_path):
    title, image, link = extract_notebook_info(nb_path)
    nb = nbformat.read(nb_path, as_version=4)
    return f"""\
    :::{{grid-item-card}} {title}
    :margin: 3 0 0 0
    :link: {link}
    :link-type: url
    :text-align: center
    :shadow: md

    {{bdg-primary}}`{nb_path.split("/")[1].replace("_", " ").title().strip("Notebooks").strip()}`
    {{bdg-secondary}}`ERDDAP`
    {{bdg-info}}`{nb["metadata"]["language_info"]["name"]}`
    ^^^

    <img src="{image}"/>
    :::
    """


for nb_path in sorted(glob.glob("code_gallery/**/*.ipynb")):
    print(make_gallery_entry(nb_path))
