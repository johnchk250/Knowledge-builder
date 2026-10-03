"""Read-only, bounded detail renders from immutable PDF source pages."""
import math
import fitz


def detail_png(store, evidence_id, region):
    try:
        coordinates = [float(value) for value in region.split(',')]
    except (ValueError, AttributeError):
        raise ValueError('Region must contain four normalized coordinates') from None
    if (len(coordinates) != 4 or not all(math.isfinite(v) for v in coordinates)
            or not 0 <= coordinates[0] < coordinates[2] <= 1
            or not 0 <= coordinates[1] < coordinates[3] <= 1
            or min(coordinates[2]-coordinates[0], coordinates[3]-coordinates[1]) < .002):
        raise ValueError('Invalid source region')
    rows = store.rows('SELECT e.page,d.sha256,d.media_type FROM evidence e '
                      'JOIN documents d ON d.id=e.document_id WHERE e.id=?', (evidence_id,))
    if not rows or rows[0]['media_type'] != 'application/pdf':
        raise ValueError('PDF evidence not found')
    row = rows[0]
    with fitz.open(store.root/'originals'/row['sha256']) as document:
        number = row['page']
        if not isinstance(number, int) or not 1 <= number <= len(document):
            raise ValueError('Source page not found')
        page = document[number-1]
        bounds = page.rect
        clip = fitz.Rect(coordinates[0]*bounds.width, coordinates[1]*bounds.height,
                         coordinates[2]*bounds.width, coordinates[3]*bounds.height)
        scale = min(8, 1800/max(clip.width, clip.height))
        return page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip,
                               colorspace=fitz.csRGB, alpha=False).tobytes('png')
