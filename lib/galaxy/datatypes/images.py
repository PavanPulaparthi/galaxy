"""
Image classes
"""
import base64
import logging
import zipfile
from urllib.parse import quote_plus

from galaxy.datatypes.binary import Binary
from galaxy.datatypes.text import Html as HtmlFromText
from galaxy.util import nice_size
from galaxy.util.image_util import check_image_type
from . import data
from .sniff import build_sniff_from_prefix
from .xml import GenericXml

log = logging.getLogger(__name__)

# TODO: Uploading image files of various types is supported in Galaxy, but on
# the main public instance, the display_in_upload is not set for these data
# types in datatypes_conf.xml because we do not allow image files to be uploaded
# there.  There is currently no API feature that allows uploading files outside
# of a data library ( where it requires either the upload_paths or upload_directory
# option to be enabled, which is not the case on the main public instance ).  Because
# of this, we're currently safe, but when the api is enhanced to allow other uploads,
# we need to ensure that the implementation is such that image files cannot be uploaded
# to our main public instance.


class Image(data.Data):
    """Class describing an image"""
    edam_data = 'data_2968'
    edam_format = "format_3547"
    file_ext = ''

    def __init__(self, **kwd):
        super().__init__(**kwd)
        self.image_formats = [self.file_ext.upper()]

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            dataset.peek = 'Image in %s format' % dataset.extension
            dataset.blurb = nice_size(dataset.get_size())
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def sniff(self, filename):
        """Determine if the file is in this format"""
        return check_image_type(filename, self.image_formats)

    def handle_dataset_as_image(self, hda):
        dataset = hda.dataset
        name = hda.name or ''
        with open(dataset.file_name, "rb") as f:
            base64_image_data = base64.b64encode(f.read()).decode("utf-8")
        return f"![{name}](data:image/{self.file_ext};base64,{base64_image_data})"


class Jpg(Image):
    edam_format = "format_3579"
    file_ext = "jpg"

    def __init__(self, **kwd):
        super().__init__(**kwd)
        self.image_formats = ['JPEG']


class Png(Image):
    edam_format = "format_3603"
    file_ext = "png"


class Tiff(Image):
    edam_format = "format_3591"
    file_ext = "tiff"


class Hamamatsu(Image):
    file_ext = "vms"


class Mirax(Image):
    file_ext = "mrxs"


class Sakura(Image):
    file_ext = "svslide"


class Nrrd(Image):
    file_ext = "nrrd"


class Bmp(Image):
    edam_format = "format_3592"
    file_ext = "bmp"


class Gif(Image):
    edam_format = "format_3467"
    file_ext = "gif"


class Im(Image):
    edam_format = "format_3593"
    file_ext = "im"


class Pcd(Image):
    edam_format = "format_3594"
    file_ext = "pcd"


class Pcx(Image):
    edam_format = "format_3595"
    file_ext = "pcx"


class Ppm(Image):
    edam_format = "format_3596"
    file_ext = "ppm"


class Psd(Image):
    edam_format = "format_3597"
    file_ext = "psd"


class Xbm(Image):
    edam_format = "format_3598"
    file_ext = "xbm"


class Xpm(Image):
    edam_format = "format_3599"
    file_ext = "xpm"


class Rgb(Image):
    edam_format = "format_3600"
    file_ext = "rgb"


class Pbm(Image):
    edam_format = "format_3601"
    file_ext = "pbm"


class Pgm(Image):
    edam_format = "format_3602"
    file_ext = "pgm"


class Eps(Image):
    edam_format = "format_3466"
    file_ext = "eps"


class Rast(Image):
    edam_format = "format_3605"
    file_ext = "rast"


class Pdf(Image):
    edam_format = "format_3508"
    file_ext = "pdf"

    def sniff(self, filename):
        """Determine if the file is in pdf format."""
        with open(filename, 'rb') as fh:
            return fh.read(4) == b"%PDF"


def create_applet_tag_peek(class_name, archive, params):
    text = """
<object classid="java:{}"
      type="application/x-java-applet"
      height="30" width="200" align="center" >
      <param name="archive" value="{}"/>""".format(class_name, archive)
    for name, value in params.items():
        text += f"""<param name="{name}" value="{value}"/>"""
    text += """
<object classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93"
        height="30" width="200" >
        <param name="code" value="{}" />
        <param name="archive" value="{}"/>""".format(class_name, archive)
    for name, value in params.items():
        text += f"""<param name="{name}" value="{value}"/>"""
    text += """<div class="errormessage">You must install and enable Java in your browser in order to access this applet.<div></object>
</object>
"""
    return """<div><p align="center">%s</p></div>""" % text


class Gmaj(data.Data):
    """Class describing a GMAJ Applet"""
    edam_format = "format_3547"
    file_ext = "gmaj.zip"
    copy_safe_peek = False

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            if hasattr(dataset, 'history_id'):
                params = {
                    "bundle": "display?id=%s&tofile=yes&toext=.zip" % dataset.id,
                    "buttonlabel": "Launch GMAJ",
                    "nobutton": "false",
                    "urlpause": "100",
                    "debug": "false",
                    "posturl": "history_add_to?%s" % "&".join("{}={}".format(x[0], quote_plus(str(x[1]))) for x in [('copy_access_from', dataset.id), ('history_id', dataset.history_id), ('ext', 'maf'), ('name', 'GMAJ Output on data %s' % dataset.hid), ('info', 'Added by GMAJ'), ('dbkey', dataset.dbkey)])
                }
                class_name = "edu.psu.bx.gmaj.MajApplet.class"
                archive = "/static/gmaj/gmaj.jar"
                dataset.peek = create_applet_tag_peek(class_name, archive, params)
                dataset.blurb = 'GMAJ Multiple Alignment Viewer'
            else:
                dataset.peek = "After you add this item to your history, you will be able to launch the GMAJ applet."
                dataset.blurb = 'GMAJ Multiple Alignment Viewer'
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek(self, dataset):
        try:
            return dataset.peek
        except Exception:
            return "peek unavailable"

    def get_mime(self):
        """Returns the mime type of the datatype"""
        return 'application/zip'

    def sniff(self, filename):
        """
        NOTE: the sniff.convert_newlines() call in the upload utility will keep Gmaj data types from being
        correctly sniffed, but the files can be uploaded (they'll be sniffed as 'txt').  This sniff function
        is here to provide an example of a sniffer for a zip file.
        """
        if not zipfile.is_zipfile(filename):
            return False
        contains_gmaj_file = False
        with zipfile.ZipFile(filename, "r") as zip_file:
            for name in zip_file.namelist():
                if name.split(".")[1].strip().lower() == 'gmaj':
                    contains_gmaj_file = True
                    break
        if not contains_gmaj_file:
            return False
        return True


class Analyze75(Binary):
    """
        Mayo Analyze 7.5 files
        http://www.imzml.org
    """
    file_ext = 'analyze75'
    composite_type = 'auto_primary_file'

    def __init__(self, **kwd):
        super().__init__(**kwd)

        """The header file. Provides information about dimensions, identification, and processing history."""
        self.add_composite_file(
            'hdr',
            description='The Analyze75 header file.',
            is_binary=True)

        """The image file.  Image data, whose data type and ordering are described by the header file."""
        self.add_composite_file(
            'img',
            description='The Analyze75 image file.',
            is_binary=True)

        """The optional t2m file."""
        self.add_composite_file(
            't2m',
            description='The Analyze75 t2m file.',
            optional=True,
            is_binary=True)

    def generate_primary_file(self, dataset=None):
        rval = ['<html><head><title>Analyze75 Composite Dataset.</title></head><p/>']
        rval.append('<div>This composite dataset is composed of the following files:<p/><ul>')
        for composite_name, composite_file in self.get_composite_files(dataset=dataset).items():
            fn = composite_name
            opt_text = ''
            if composite_file.optional:
                opt_text = ' (optional)'
            if composite_file.get('description'):
                rval.append('<li><a href="{}" type="text/plain">{} ({})</a>{}</li>'.format(fn, fn, composite_file.get('description'), opt_text))
            else:
                rval.append(f'<li><a href="{fn}" type="text/plain">{fn}</a>{opt_text}</li>')
        rval.append('</ul></div></html>')
        return "\n".join(rval)


@build_sniff_from_prefix
class Nifti1(Binary):
    """
        Nifti1 format
        https://nifti.nimh.nih.gov/pub/dist/src/niftilib/nifti1.h
    """
    file_ext = 'nii1'

    def sniff_prefix(self, file_prefix):
        """Determine if the file is in Nifti1 format.
        >>> from galaxy.datatypes.sniff import get_test_fname
        >>> fname = get_test_fname('T1_top_350bytes.nii')
        >>> Nifti1().sniff( fname )
        True
        >>> fname = get_test_fname('2.txt')
        >>> Nifti1().sniff( fname )
        False
        """
        magic = file_prefix.contents_header_bytes[344:348]
        if magic == b'n+1\0':
            return True
        return False


@build_sniff_from_prefix
class Nifti2(Binary):
    """
        Nifti2 format
        https://brainder.org/2015/04/03/the-nifti-2-file-format/
    """
    file_ext = 'nii2'

    def sniff_prefix(self, file_prefix):
        """Determine if the file is in Nifti2 format.
        >>> from galaxy.datatypes.sniff import get_test_fname
        >>> fname = get_test_fname('avg152T1_LR_nifti2_top_100bytes.nii')
        >>> Nifti2().sniff( fname )
        True
        >>> fname = get_test_fname('2.txt')
        >>> Nifti2().sniff( fname )
        False
        """
        magic = file_prefix.contents_header_bytes[4:8]
        if magic in [b'n+2\0', b'ni2\0']:
            return True
        return False


@build_sniff_from_prefix
class Gifti(GenericXml):
    """Class describing a Gifti format"""
    file_ext = "gii"

    def sniff_prefix(self, file_prefix):
        """Determines whether the file is a Gifti file

        >>> from galaxy.datatypes.sniff import get_test_fname
        >>> fname = get_test_fname('Human.colin.R.activations.label.gii')
        >>> Gifti().sniff(fname)
        True
        >>> fname = get_test_fname('interval.interval')
        >>> Gifti().sniff(fname)
        False
        >>> fname = get_test_fname('megablast_xml_parser_test1.blastxml')
        >>> Gifti().sniff(fname)
        False
        >>> fname = get_test_fname('tblastn_four_human_vs_rhodopsin.blastxml')
        >>> Gifti().sniff(fname)
        False
        """
        handle = file_prefix.string_io()
        line = handle.readline()
        if not line.strip().startswith('<?xml version="1.0"'):
            return False
        line = handle.readline()
        if line.strip() == '<!DOCTYPE GIFTI SYSTEM "http://www.nitrc.org/frs/download.php/1594/gifti.dtd">':
            return True
        line = handle.readline()
        if line.strip().startswith('<GIFTI'):
            return True
        return False


class Html(HtmlFromText):
    """Deprecated class. This class should not be used anymore, but the galaxy.datatypes.text:Html one.
    This is for backwards compatibilities only."""


class Laj(data.Text):
    """Class describing a LAJ Applet"""
    file_ext = "laj"
    copy_safe_peek = False

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            if hasattr(dataset, 'history_id'):
                params = {
                    "alignfile1": "display?id=%s" % dataset.id,
                    "buttonlabel": "Launch LAJ",
                    "title": "LAJ in Galaxy",
                    "posturl": quote_plus("history_add_to?%s" % "&".join(f"{key}={value}" for key, value in {'history_id': dataset.history_id, 'ext': 'lav', 'name': 'LAJ Output', 'info': 'Added by LAJ', 'dbkey': dataset.dbkey, 'copy_access_from': dataset.id}.items())),
                    "noseq": "true"
                }
                class_name = "edu.psu.cse.bio.laj.LajApplet.class"
                archive = "/static/laj/laj.jar"
                dataset.peek = create_applet_tag_peek(class_name, archive, params)
            else:
                dataset.peek = "After you add this item to your history, you will be able to launch the LAJ applet."
                dataset.blurb = 'LAJ Multiple Alignment Viewer'
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek(self, dataset):
        try:
            return dataset.peek
        except Exception:
            return "peek unavailable"
