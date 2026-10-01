# Dates relative to today, so the tests never go stale.
import datetime
_MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sept","Oct","Nov","Dec"]   # the app's en-GB short months
def ahead(n):
    d=datetime.date.today()+datetime.timedelta(days=n)
    return {'long':f"{d:%A} {d.day} {d:%B}",'dm':f"{d.day} {d:%B}",'short':f"{d.day} {_MON[d.month-1]}",'iso':d.isoformat(),'wd':f"{d:%A}",'date':d}
A4,A5,A6,A10=ahead(4),ahead(5),ahead(6),ahead(10)
