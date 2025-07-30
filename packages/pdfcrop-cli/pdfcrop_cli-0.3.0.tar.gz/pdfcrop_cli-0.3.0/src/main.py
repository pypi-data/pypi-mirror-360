from dataclasses import dataclass
from pathlib import Path

import pymupdf as pf
import tyro
from typing_extensions import Annotated


@dataclass
class Args:
    input: Annotated[
        Path,
        tyro.conf.arg(aliases=["-i"], help="The input pdf file."),
    ]
    output: Annotated[
        Path | None, tyro.conf.arg(aliases=["-o"], help="The output path.")
    ] = None
    pages: Annotated[
        list[int] | None,
        tyro.conf.arg(help="The page numbers to crop. None denotes all pages."),
    ] = None
    margins: Annotated[
        list[int] | None,
        tyro.conf.arg(
            help="The margins to reserve. None denotes all 0. If one number is given, it will be applied to four borders."
        ),
    ] = None
    reverse_mode: Annotated[
        bool,
        tyro.conf.arg(
            help="Crop space with length of margins from outside border.",
        ),
    ] = False


def crop_page(p: pf.Page, margins: list[int], reverse_mode: bool) -> pf.Page:
    if reverse_mode:
        w, h = p.rect.width, p.rect.height
        x0, y0, x1, y1 = *margins[:2], w - margins[2], h - margins[3]
    else:
        blocks = p.get_text("dict")["blocks"]
        shapes = p.get_drawings()
        coordinates = []

        for b in blocks:
            coordinates.append(b["bbox"])

        for s in shapes:
            coordinates.append((s["rect"].x0, s["rect"].y0, s["rect"].x1, s["rect"].y1))

        x0 = min([p[0] for p in coordinates]) - margins[0]
        y0 = min([p[1] for p in coordinates]) - margins[2]
        x1 = max([p[2] for p in coordinates]) + margins[1]
        y1 = max([p[3] for p in coordinates]) + margins[3]

    p.set_cropbox(pf.Rect(x0, y0, x1, y1))

    return p


def main():
    args = tyro.cli(Args)
    assert args.margins is None or len(args.margins) in (1, 4), (
        "margins number must be 1 or 4"
    )
    if args.margins is None:
        margins = [0] * 4
    elif len(args.margins) == 1:
        margins = margins * 4
    elif len(args.margins) == 4:
        margins = args.margins

    # breakpoint()
    doc = pf.open(str(args.input))
    for i, p in enumerate(doc.pages()):
        if args.pages is None or i in args.pages:
            crop_page(p, margins, args.reverse_mode)

    if args.output is None:
        output_path = args.input.with_name(args.input.stem + "_cropped.pdf")
    else:
        output_path = args.output

    doc.save(output_path, deflate=True, garbage=4, clean=True)


if __name__ == "__main__":
    main()
