import enum


class Compression(enum.Enum):
    """Different compression formats that are understood by file readers"""
    NONE = 'none'
    GZIP = 'gzip'
    TAR_GZIP = 'tar.gzip'
    ZIP = 'zip'


def file_extension(compression: Compression) -> str:
    """Gives the file extension for the compression"""
    return {Compression.NONE: None,
            Compression.ZIP: 'zip',
            Compression.GZIP: 'gz',
            Compression.TAR_GZIP: 'tar.gz'}[compression]


def compressor(compression: Compression) -> str:
    """
    Maps compression methods to command line programs that can pack files.
    The list of files which shall be compressed must be given after the command.
    The compressed file will be send to stdout

    Example:
        command = f'{compressor(Compression.GZIP)} my_file_to_compress.txt > my_compressed_file.txt.gz'

    Args:
        compression: the compression to be used

    Returns:
        The compress command without the files to be compressed
    """
    if compression not in [Compression.ZIP, Compression.GZIP, Compression.TAR_GZIP]:
        raise ValueError('The arg compression must be of enum value ZIP, GZIP or TAR_GZIP')

    return {Compression.ZIP: 'zip -',
            Compression.GZIP: 'gzip -c',
            Compression.TAR_GZIP: 'tar -czf -'}[compression]


def uncompressor(compression: Compression) -> str:
    """
    Maps compression methods to command line programs that can unpack the respective
    files
    """
    return {Compression.NONE: 'cat',
            Compression.ZIP: 'unzip -p',
            Compression.GZIP: 'gunzip -d -c',
            Compression.TAR_GZIP: 'tar -xOzf'}[compression]
