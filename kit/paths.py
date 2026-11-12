"""Where things live. Every path can be overridden from the environment.

  IMMOLLIMMA_LIBS   folder with the sample libraries (default: <repo>/libs, filled by tools/setup.sh)
  VSCO_DIR          VSCO-2 CE samples (branch master)               default: $LIBS/VSCO-2-CE
  VSCO_SFZ_DIR      VSCO's SFZ files with links to the sample dirs   default: $LIBS/vsco-sfz
  SSO_DIR           clone of github.com/peastman/sso                 default: $LIBS/sso
  SFIZZ_LIB         libsfizz.so                                      default: <repo>/bin/libsfizz.so
"""
import os

KIT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(KIT)
DATA = os.path.join(KIT, "data")
STYLES = os.path.join(KIT, "styles")

LIBS = os.environ.get("IMMOLLIMMA_LIBS", os.path.join(REPO, "libs"))
VSCO = os.environ.get("VSCO_DIR", os.path.join(LIBS, "VSCO-2-CE"))
VSCO_SFZ = os.environ.get("VSCO_SFZ_DIR", os.path.join(LIBS, "vsco-sfz"))
SSO_ROOT = os.environ.get("SSO_DIR", os.path.join(LIBS, "sso"))
SSO = os.path.join(SSO_ROOT, "Sonatina Symphonic Orchestra")
SFIZZ_LIB = os.environ.get("SFIZZ_LIB", os.path.join(REPO, "bin", "libsfizz.so"))


def expand(p):
    """sample paths in events are stored with placeholders, so an events.json works on any machine"""
    return p.replace("{VSCO}", VSCO).replace("{SSO}", SSO)


def status():
    """what is installed: {name: bool}"""
    return {
        "VSCO-2-CE samples": os.path.isdir(os.path.join(VSCO, "Strings")),
        "VSCO SFZ files": os.path.isfile(os.path.join(VSCO_SFZ, "Harp.sfz")),
        "Sonatina (SSO)": os.path.isdir(os.path.join(SSO, "Samples")),
        "libsfizz": os.path.isfile(SFIZZ_LIB),
    }
