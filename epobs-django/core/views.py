from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import FormView
from schoolauth.views import SchoolPermissionMixin, get_school_pk, get_school
from django.utils.encoding import force_text
from import_export.forms import ImportForm, ConfirmImportForm
from import_export.formats import base_formats
from import_export.tmp_storages import TempFolderStorage


def index_view(request):
    return render(request, 'index.html')


class DeletionFormMixin:

    # The combined edit/delete view expects a form
    # that includes buttons named 'delete' and 'cancel'.
    def post(self, request, **kwargs):
        if 'delete' in request.POST:
            self.object = self.get_object()
            self.object.delete()
            return redirect(self.get_success_url())
        elif 'cancel' in request.POST:
            self.object = self.get_object()
            return redirect(self.get_success_url())
        else:
            return super().post(request, **kwargs)


class SessionRecentsMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.session_recents_key in self.request.session:
            object_list = []
            pk_list = []
            for pk in self.request.session[self.session_recents_key]:
                try:
                    object = self.model.objects.get(pk=pk)
                except ObjectDoesNotExist:
                    continue
                object_list.append(object)
                pk_list.append(pk)
            if len(pk_list) > 0:
                context[self.context_recents_key] = object_list
                self.request.session[self.session_recents_key] = pk_list
            else:
                del self.request.session[self.session_recents_key]
        return context

    def add_object_to_session(self, pk):
        if self.session_recents_key not in self.request.session:
            self.request.session[self.session_recents_key] = []
        self.request.session[self.session_recents_key] = [pk] + self.request.session[self.session_recents_key]

    @property
    def session_recents_key(self):
        return (
            'recent_school%s_%s_list' % (
                str(get_school_pk(self.request.session)),
                self.model.__name__.lower()
            )
        )

    @property
    def context_recents_key(self):
        return 'recent_%s_list' % self.model.__name__.lower()


DEFAULT_FORMATS = (
    base_formats.CSV,
    base_formats.XLS,
    base_formats.XLSX,
    base_formats.TSV,
)


class ImportTool(SchoolPermissionMixin, FormView):
    formats = DEFAULT_FORMATS
    from_encoding = "utf-8"
    template_name = 'import_tool.html'
    form_class = ImportForm
    resource_class = None
    model = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['import_formats'] = self.formats
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.model.__name__
        resource = self.resource_class()
        context['model_import_fields'] = [f.column_name for f in resource.get_user_visible_fields()]
        return context

    def post(self, request, *args, **kwargs):
        if 'confirm-import' in request.POST:
            return self.process_import(request)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request
        return self.import_action(request, form)

    def import_action(self, request, form):
        school = get_school(request.session)
        resource = self.resource_class(school=school, user=request.user)
        import_formats = self.formats
        context = {}
        input_format = import_formats[
            int(form.cleaned_data['input_format'])
        ]()
        import_file = form.cleaned_data['import_file']
        # first always write the uploaded file to disk as it may be a
        # memory file or else based on settings upload handlers
        tmp_storage = self.write_to_tmp_storage(import_file, input_format)
        # then read the file, using the proper format-specific mode
        # warning, big files may exceed memory
        try:
            dataset = self.make_dataset(tmp_storage, input_format)
        except UnicodeDecodeError as e:
            return HttpResponse((u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
        result = resource.import_data(dataset, dry_run=True,
                                      raise_errors=False,
                                      file_name=import_file.name,
                                      user=request.user)
        context['result'] = result
        context['model'] = self.model.__name__
        if not result.has_errors():
            context['confirm_form'] = ConfirmImportForm(initial={
                'import_file_name': tmp_storage.name,
                'original_file_name': import_file.name,
                'input_format': form.cleaned_data['input_format'],
            })
        return TemplateResponse(request, 'confirm_import.html', context)

    def write_to_tmp_storage(self, import_file, input_format):
        tmp_storage = TempFolderStorage()
        data = bytes()
        for chunk in import_file.chunks():
            data += chunk
        tmp_storage.save(data, input_format.get_read_mode())
        return tmp_storage

    def make_dataset(self, tmp_storage, input_format):
        data = tmp_storage.read(input_format.get_read_mode())
        if not input_format.is_binary() and self.from_encoding:
            data = force_text(data, self.from_encoding)
        dataset = input_format.create_dataset(data)
        return dataset

    def process_import(self, request):
        confirm_form = ConfirmImportForm(request.POST)
        if confirm_form.is_valid():
            import_formats = self.formats
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            tmp_storage = TempFolderStorage(name=confirm_form.cleaned_data['import_file_name'])
            dataset = self.make_dataset(tmp_storage, input_format)
            self.process_dataset(dataset, confirm_form.cleaned_data['original_file_name'], request)
            tmp_storage.remove()
            return redirect(self.success_url)
        else:
            pass  # TODO: handle errors

    def process_dataset(self, dataset, file_name, request):
        school = get_school(request.session)
        resource = self.resource_class(school=school, user=request.user)
        return resource.import_data(dataset,
                                    dry_run=False,
                                    raise_errors=True,
                                    file_name=file_name,
                                    user=request.user)
