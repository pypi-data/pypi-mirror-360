import re
import ast
import json
from dataclasses import dataclass

from django.core import paginator
from django.db.models import Model
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from accrete.contrib.ui import Filter


class Response:

    def __init__(self, *, template: str, context: dict):
        self.template = template
        self.context = context

    @staticmethod
    def add_trigger(response):
        pass

    def render(self, request) -> str:
        return render_to_string(
            template_name=self.template, context=self.context, request=request
        )

    def response(self, request, extra_content: str = None, replace_body: bool = False) -> HttpResponse:
        extra_content = extra_content or ''
        res = HttpResponse(content=(
            self.render(request)
            + render_to_string('ui/message.html', request=request)
            + extra_content
        ))
        self.add_trigger(res)
        if replace_body:
            res.headers['HX-Retarget'] = 'body'
            res.headers['HX-Reswap'] = 'innerHTML'
            res.headers['HX-Push-Url'] = request.path
        return res


class OobResponse(Response):

    oob_template = 'ui/oob.html'

    def __init__(self, *, template: str, context: dict, swap: str, tag: str = 'div'):
        super().__init__(template=self.oob_template, context=context)
        self.context.update({'oob': {
            'template': template,
            'swap': swap,
            'tag': tag
        }})


class WindowResponse(Response):

    base_template = 'ui/layout.html'

    def __init__(
        self, *,
        title: str,
        context: dict,
        overview_template: str = None,
        header_template: str = None,
        panel_template: str = None,
        is_centered: bool = False
    ):
        super().__init__(template=self.base_template, context=context)
        self.panel_template = panel_template
        if 'has_panel' not in self.context.keys():
            self.context.update(has_panel=self._has_panel())
        self.context.update({
            'title': title,
            'overview_template': overview_template,
            'header_template': header_template,
            'panel_template': panel_template,
            'is_centered': is_centered
        })

    def _has_panel(self):
        return bool(self.panel_template)

    def response(self, request, extra_content: str = None, replace_body: bool = True) -> HttpResponse:
        return super().response(request, extra_content, replace_body)


class ListResponse(WindowResponse):

    def __init__(
        self, *,
        title: str,
        context: dict,
        list_entry_template: str = None,
        page: paginator.Page = None,
        ui_filter: Filter = None,
        endless_scroll: bool = True,
        header_template: str = None,
        panel_template: str = None,
        column_count: int = 1,
        column_height: str = '150px',
        overview_template: str = 'ui/list.html',
        detail_response: 'DetailResponse' = None
    ):
        assert page is not None or ui_filter is not None, _(
            'Argument page or ui_filter must be supplied'
        )
        self.ui_filter = ui_filter
        self.overview_template = overview_template
        self.show_content_right = bool(detail_response)
        super().__init__(
            title=title,
            context=context,
            overview_template=self.overview_template,
            header_template=header_template,
            panel_template=panel_template,
        )
        if ui_filter and not page:
            page = ui_filter.get_page()
        self.context.update({
            'list_entry_template': list_entry_template,
            'page': page,
            'ui_filter': ui_filter,
            'endless_scroll': endless_scroll,
            'column_count': column_count,
            'column_height': column_height,
            'show_content_right': str(self.show_content_right).lower()
        })
        if detail_response:
            self.context.update(detail_response.context)

    def _has_panel(self):
        return bool(self.panel_template or self.ui_filter)

    def response(self, request, extra_content: str = None, replace_body: bool = False) -> HttpResponse:
        return super().response(request, extra_content, replace_body)


class ListEntryResponse(Response):

    base_template = 'ui/list_update.html'

    def __init__(
        self, *,
        instance: Model,
        list_entry_template: str,
        context: dict = None,
        page: paginator.Page = None,
        is_new: bool = False,
        column_count: int = 1,
        column_height: str = '150px',
    ):
        self.page = page
        super().__init__(template=self.base_template, context=context or {})
        self.context.update({
            'instance': instance,
            'list_entry_template': list_entry_template,
            'is_new': is_new,
            'column_count': column_count,
            'column_height': column_height
        })

    def render(self, request) -> str:
        res = super().render(request)
        if self.page:
            pagination_update = OobResponse(
                template='ui/layout.html#pagination',
                swap='innerHTML:#pagination',
                context=dict(page=self.page)
            ).render(request)
            res += pagination_update
        return res


class TableResponse(WindowResponse):

    def __init__(
        self, *,
        title: str,
        context: dict,
        instance_label: str,
        fields: list[str],
        footer: dict = None,
        page: paginator.Page = None,
        ui_filter: Filter = None,
        endless_scroll: bool = True,
        header_template: str = None,
        panel_template: str = None,
        overview_template: str = 'ui/table.html',
        detail_response: 'DetailResponse' = None
    ):
        assert page is not None or ui_filter is not None, _(
            'Argument page or ui_filter must be supplied'
        )
        self.ui_filter = ui_filter
        self.overview_template = overview_template
        super().__init__(
            title=title,
            context=context,
            overview_template=self.overview_template,
            header_template=header_template,
            panel_template=panel_template
        )
        if ui_filter and not page:
            page = ui_filter.get_page()
        self.context.update({
            'page': page,
            'ui_filter': ui_filter,
            'endless_scroll': endless_scroll,
            'fields': fields,
            'instance_label': instance_label,
            'footer': footer
        })
        if detail_response:
            self.context.update(detail_response.context)

    def _has_panel(self):
        return bool(self.panel_template or self.ui_filter)

    def response(self, request, extra_content: str = None, replace_body: bool = False) -> HttpResponse:
        return super().response(request, extra_content, replace_body)


class TableRowResponse(Response):

    base_template = 'ui/table_row_update.html'

    def __init__(
        self, *,
        instance: Model,
        fields: list[str],
        footer: dict = None,
        page: paginator.Page = None,
    ):
        self.page = page
        context = {
            'instance': instance,
            'fields': fields,
            'footer': footer,
            'page': page
        }
        super().__init__(template=self.base_template, context=context)

    def render(self, request) -> str:
        res = super().render(request)
        if self.page:
            pagination_update = OobResponse(
                template='ui/layout.html#pagination',
                swap='innerHTML:#pagination',
                context=dict(page=self.page)
            ).render(request)
            res += pagination_update
        return res


class DetailResponse(Response):

    base_template = 'ui/detail.html'

    def __init__(
        self, *,
        context: dict,
        header_template: str = None,
        data_template: str = None
    ):
        super().__init__(template=self.base_template, context=context)
        self.header_template = header_template
        self.data_template = data_template
        self.context.update({
            'detail_header_template': header_template,
            'detail_data_template': data_template
        })

    @staticmethod
    def add_trigger(response):
        add_trigger(response, 'activate-detail')


class ModalResponse(Response):

    def __init__(
        self, *,
        modal_id: str,
        template: str,
        context: dict,
        title: str = None,
        is_update: bool = False,
        is_blocking: bool = False,
        modal_width: str = None

    ):
        super().__init__(template=template, context=context)
        self.context.update({
            'title': title,
            'modal_id': re.sub(r'[^A-Za-z-]+', '', modal_id).strip('-'),
            'is_update': is_update,
            'is_blocking': is_blocking,
            'modal_width': modal_width
        })


@dataclass
class ClientTrigger:

    trigger: dict | str
    header: str = 'HX-Trigger'


class TriggerResponse:

    def __init__(self, trigger: list[ClientTrigger]):
        self.trigger = trigger

    def response(self):
        res = HttpResponse()
        res.headers['HX-Reswap'] = 'none'
        for trigger in self.trigger:
            add_trigger(res, trigger.trigger, trigger.header)
        return res


def search_select_response(queryset) -> HttpResponse:
    return HttpResponse(render_to_string(
        'ui/widgets/model_search_select_options.html',
        {'options': queryset}
    ))


def message_response(request, persistent: bool = False):
    return HttpResponse(content=(render_to_string(
        'ui/message.html', context={'persistent': persistent}, request=request
    )))


def add_trigger(
    response: HttpResponse,
    trigger: dict | str,
    header: str = 'HX-Trigger'
) -> HttpResponse:
    if isinstance(trigger, str):
        trigger = {trigger: ''}
    res_trigger = response.headers.get(header)
    if not res_trigger:
        response.headers[header] = json.dumps(trigger)
        return response
    try:
        res_trigger = ast.literal_eval(response.headers.get(header, '{}'))
    except SyntaxError:
        res_trigger = {response.headers[header]: ''}
    res_trigger.update(trigger)
    response.headers[header] = json.dumps(res_trigger)
    return response


def update(request, ui_responses: list[Response]) -> HttpResponse:
    response = HttpResponse()
    content = ''
    print(ui_responses)
    for res in ui_responses:
        print(res.context)
        content += res.render(request)
        res.add_trigger(response)
    content += render_to_string('ui/message.html', request=request)
    response.content = content
    return response
