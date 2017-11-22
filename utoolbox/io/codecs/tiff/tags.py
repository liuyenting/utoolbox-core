from enum import Enum

TAG_NAME = {
    254: 'NewSubfileType',
    255: 'SubfileType',
    256: 'ImageWidth',
    257: 'ImageLength',
    258: 'BitsPerSample',
    259: 'Compression',
    262: 'PhotometricInterpretation',
    263: 'Thresholding',
    264: 'CellWidth',
    265: 'CellLength',
    266: 'FillOrder',
    269: 'DocumentName',
    270: 'ImageDescription',
    271: 'Make',
    272: 'Model',
    273: 'StripOffsets',
    274: 'Orientation',
    277: 'SamplesPerPixel',
    278: 'RowsPerStrip',
    279: 'StripByteCounts',
    280: 'MinSampleValue',
    281: 'MaxSampleValue',
    282: 'XResolution',
    283: 'YResolution',
    284: 'PlanarConfiguration',
    285: 'PageName',
    286: 'XPosition',
    287: 'YPosition',
    288: 'FreeOffsets',
    289: 'FreeByteCounts',
    290: 'GrayResponseUnit',
    291: 'GrayResponseCurve',
    292: 'T4Options',
    293: 'T6Options',
    296: 'ResolutionUnit',
    297: 'PageNumber',
    301: 'TransferFunction',
    305: 'Software',
    306: 'DateTime',
    315: 'Artist',
    316: 'HostComputer',
    317: 'Predictor',
    318: 'WhitePoint',
    319: 'PrimaryChromaticities',
    320: 'ColorMap',
    321: 'HalftoneHints',
    322: 'TileWidth',
    323: 'TileLength',
    324: 'TileOffsets',
    325: 'TileByteCounts',
    332: 'InkSet',
    333: 'InkNames',
    334: 'NumberOfInks',
    336: 'DotRange',
    337: 'TargetPrinter',
    338: 'ExtraSamples',
    339: 'SampleFormat',
    340: 'SMinSampleValue',
    341: 'SMaxSampleValue',
    342: 'TransferRange',
    512: 'JPEGProc',
    513: 'JPEGInterchangeFormat',
    514: 'JPEGInterchangeFormatLngth',
    515: 'JPEGRestartInterval',
    517: 'JPEGLosslessPredictors',
    518: 'JPEGPointTransforms',
    519: 'JPEGQTables',
    520: 'JPEGDCTables',
    521: 'JPEGACTables',
    529: 'YCbCrCoefficients',
    530: 'YCbCrSubSampling',
    531: 'YCbCrPositioning',
    532: 'ReferenceBlackWhite',
    33432: 'Copyright'
}

class CompressionOptions(Enum):
    Uncompressed = 1
    CCITT = 2
    Group3 = 3
    Group4 = 4
    LZW = 5
    JPEG = 6
    PackBits = 32773

class PhotometricOptions(Enum):
    WhiteIsZero = 0
    BlackIsZero = 1
    RGB = 2
    Palette = 3
    TransparencyMask = 4
    CMYK = 5
    YCbCr = 6
    CIELab = 8

class Tags(object):
    def __init__(self):
        pass
