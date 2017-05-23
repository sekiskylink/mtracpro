import web
import parsedatetime
from . import csrf_protected, db, require_login, get_session, render
from app.tools.utils import audit_log, default, lit
from app.tools.pagination2 import countquery, doquery, getPaginationString
from settings import PAGE_LIMIT

cal = parsedatetime.Calendar()


class Failed:
    @require_login
    def GET(self):
        params = web.input(page=1)
        try:
            page = int(params.page)
        except:
            page = 1
        limit = PAGE_LIMIT
        start = (page - 1) * limit if page > 0 else 0
        # we start getting requests a month old
        t = cal.parse("2 month ago")[0]
        amonthAgo = '%s-%s-%s' % (t.tm_year, t.tm_mon, t.tm_mday)

        dic = lit(
            relations='requests_view', fields="*",
            criteria="status='failed' AND created > '%s'" % (amonthAgo),
            order="id desc",
            limit=limit, offset=start)
        res = doquery(db, dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page, 0), count, limit, 2, "failed", "?page=")

        l = locals()
        del l['self']
        return render.failed(**l)

    @require_login
    def POST(self):
        params = web.input(page=1, reqid=[])
        try:
            page = int(params.page)
        except:
            page = 1
        limit = PAGE_LIMIT
        start = (page - 1) * limit if page > 0 else 0

        with db.transaction():
            if params.abtn == 'Retry Selected':
                if params.reqid:
                    for val in params.reqid:
                        db.update('requests', where="id = %s" % val, status='ready')
            if params.abtn == 'Delete Selected':
                if params.reqid:
                    for val in params.reqid:
                        db.delete('requests', where="id = %s" % val)
            db.transaction().commit()

        # we start getting requests a month old
        t = cal.parse("2 month ago")[0]
        amonthAgo = '%s-%s-%s' % (t.tm_year, t.tm_mon, t.tm_mday)
        dic = lit(
            relations='requests', fields="*",
            criteria="status='failed' AND created > '%s'" % (amonthAgo),
            order="id desc",
            limit=limit, offset=start)
        res = doquery(db, dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page, 0), count, limit, 2, "failed", "?page=")

        l = locals()
        del l['self']
        return render.failed(**l)
