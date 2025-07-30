from yams.buildobjs import EntityType, String, Datetime
from cubicweb import _

try:
    from yams.buildobjs import RichString
except ImportError:
    from cubicweb.schema import RichString


class Event(EntityType):
    """a calendar event"""
    title = String(required=True, fulltextindexed=True, maxsize=128)
    diem = Datetime(required=True)
    end_date = Datetime(required=False)
    type = String(internationalizable=True,
                  vocabulary=(_('appointment'), _('convention'), _('meeting'),
                              _('social event'), _('work'), _('training')),
                  default='appointment')
    location = String(fulltextindexed=True, maxsize=256)
    description = RichString(fulltextindexed=True)
