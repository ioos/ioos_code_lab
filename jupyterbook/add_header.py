from pathlib import Path

path = Path(__file__).absolute().parent


def add_header(fname):
    ioos_ui_components_min_js = """\n<script src="https://dgd6r9iiqa8y9.cloudfront.net/ioos-ui-components.min.js"></script>\n"""
    ioos_header = """\n<ioos-header variant="compact" theme="auto"></ioos-header>\n"""

    with open(fname) as f:
        lines = f.readlines()

    with open(fname, "w") as out:
        for line in lines:
            if line.strip().startswith("<title"):
                line = line + f"\n{ioos_ui_components_min_js}"
            if line.strip().startswith("<body"):
                line = line + f"\n{ioos_header}"
            out.write(line)


if "__main__" == __name__:
    for fname in path.glob("_build/html/**/*.html"):
        add_header(fname)
