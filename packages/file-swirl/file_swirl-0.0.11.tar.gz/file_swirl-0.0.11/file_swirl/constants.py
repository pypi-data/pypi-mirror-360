"""
Store all constants
"""

# Image formats
IMAGE = {
    'jpg', 'jpeg', 'png', 'tiff', 'gif', 'bmp',
    'heic', 'raw', 'svg', 'webp', 'ico', 'avif'
}

# Audio formats
AUDIO = {
    'mp3', 'wav', 'aac', 'flac', 'ogg',
    'wma', 'm4a', 'alac'
}

# Video formats
VIDEO = {
    'mp4', 'mov', 'avi', 'wmv', 'flv',
    'mkv', 'webm', 'mpg', 'mpeg',
    '3gp', 'mts', 'dav'
}

# Document formats
DOCUMENT = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx',
    'ppt', 'pptx', 'txt', 'rtf', 'md',
    'odt', 'ods', 'odp'
}

# eBook formats
EBOOK = {
    'epub', 'mobi', 'azw', 'azw3', 'ibooks'
}

# Archive formats
ARCHIVE = {
    'zip', 'rar', '7z', 'tar', 'gz',
    'bz2', 'xz', 'iso'
}

# Code & scripts
CODE = {
    'py', 'js', 'html', 'css', 'java',
    'c', 'cpp', 'cs', 'php', 'rb',
    'go', 'rs', 'swift', 'kt', 'sh',
    'pl', 'sql'
}

# Font formats
FONT = {
    'ttf', 'otf', 'woff', 'woff2', 'eot'
}

# Presentation formats (already included in DOCUMENT but singled out if preferred)
PRES = {'ppt', 'pptx', 'odp'}

# Miscellaneous / Other
MISC = {
    'exe', 'dll', 'bat', 'app', 'dmg',
    'iso', 'apk', 'crx', 'deb', 'rpm'
}

# Vector Graphic & Design formats
VECTOR = {
    'svg', 'eps', 'ai', 'psd', 'indd', 'cdr', 'sketch', 'xd'
}

# GIS / Geospatial data formats
GIS = {
    'shp', 'kml', 'kmz', 'geojson', 'gpx', 'tif', 'tiff'
}

# Scientific / Data formats
DATA = {
    'csv', 'xls', 'xlsx', 'json', 'xml', 'yaml', 'yml', 'hdf5', 'nc', 'fits'
}

# 3D Model formats
THREE_D = {
    'obj', 'fbx', 'stl', 'dae', '3ds', 'blend', 'ply', 'gltf', 'glb'
}

# CAD formats
CAD = {
    'dwg', 'dxf', 'igs', 'iges', 'step', 'stp'
}

# Backup format
BACKUP = {
    'bak', 'tmp', 'old'
}

# Combine everything into one master set
FILE_EXTENSIONS = (
    IMAGE | AUDIO | VIDEO | DOCUMENT | EBOOK | ARCHIVE |
    CODE | FONT | MISC | VECTOR | GIS | DATA | THREE_D |
    CAD | BACKUP
)

FILE_EXTENSIONS_MAP = {
    'IMAGE': IMAGE,
    'AUDIO': AUDIO,
    'VIDEO': VIDEO,
    'DOCUMENT': DOCUMENT,
    'EBOOK': EBOOK,
    'ARCHIVE': ARCHIVE,
    'CODE': CODE,
    'FONT': FONT,
    'MISC': MISC,
    'VECTOR': VECTOR,
    'GIS': GIS,
    'DATA': DATA,
    'THREE_D': THREE_D,
    'CAD': CAD,
    'BACKUP': BACKUP
}

DATE_FIELDS = [
    'DateTimeOriginal',
    'SubSecDateTimeOriginal',
    'MediaCreateDate',
    'FileModifyDate',
    'CreateDate',
    'FileAccessDate',
    'FileCreateDate',
    'Date',
]
