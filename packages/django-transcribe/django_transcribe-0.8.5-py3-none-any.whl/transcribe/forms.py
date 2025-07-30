import html
import logging

from django import forms
from django.core.exceptions import ValidationError

from .models import Project, Task, task_file_name

log = logging.getLogger(__name__)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class NoColon(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(NoColon, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True


class ProjectForm(NoColon):
    upload_media_files = MultipleFileField(
        required=False,
        label='Upload media files',
    )

    class Meta:
        model = Project
        fields = (
            'title',
            'description',
            'media_type',
            'guidelines',
            'transcribers_per_task',
            'priority',
            'upload_media_files',
            'allow_global_transcriptions',
            'transcribers',
            'reviewers',
        )
        labels = {
            'priority': (
                'Project Priority (0 = default.'
                ' A higher number = higher priority.)'
            )
        }
        widgets = {
            'description': forms.Textarea(
                attrs={'placeholder': 'Describe the transcription project.'}
            ),
            'guidelines': forms.Textarea(
                attrs={'placeholder': 'Enter project guidelines here.'}
            ),
        }

    def valid_filetype(self, project, file_type):
        """
        Returns True if the file type is valid for the project's media type.
        """
        media_type = self.cleaned_data['media_type']
        if media_type == 'text':
            if file_type.lower() not in ('bmp', 'jpg', 'jpeg', 'png', 'txt'):
                raise ValidationError(
                    'File not a supported `text` project'
                    ' file type. ({})'.format(file_type)
                )
        elif media_type == 'audio':
            if file_type.lower() not in ('mp3', 'wav', 'txt'):
                raise ValidationError(
                    'File not a supported `audio` project'
                    ' file type. ({})'.format(file_type)
                )
        return True

    def process_txt_files(self):
        """
        Process the text files connected to the Project form and load
        them into the correct tasks as transcriptions.
        """
        existing_tasks = Task.objects.filter(project=self.instance)
        txt_files = self.txt_files
        for name, txt in txt_files.items():
            try:
                task = existing_tasks.filter(file__contains=name + '.')[0]
                # save text from txt file to Task object
                content = txt[1].read()
                try:
                    text = content.decode('utf-8')
                except UnicodeDecodeError:
                    text = content.decode('iso-8859-1')
                task.transcription = self.get_processed_text(text)
                task.save()
            except (Task.DoesNotExist, IndexError):
                log.exception('problem processing text file')

    def get_processed_text(self, text):
        """Given unprocessed text, process it and return the result."""
        text = html.escape(text, quote=False)  # HTML encode
        text = text.replace('ÿþ', '').replace('þÿ', '')  # remove UTF-16 BOM
        return text

    def clean(self):
        rtn = super().clean()
        project = self.instance
        self.project = project
        self.tasks = []
        existing_tasks = Task.objects.filter(project=project)
        self.txt_files = {}

        try:
            files = self.files.getlist('upload_media_files', [])
        except AttributeError:
            files = []

        for file in files:
            name, ext = file.name.rsplit('.', maxsplit=1)
            filename = task_file_name(self, file.name)

            if self.valid_filetype(project, ext):
                # if the extension is txt, save if for later processing
                if ext == 'txt':
                    self.txt_files[name] = [filename, file]
                    continue

                task = Task()
                # if the Task file name already exists, use the existing task
                if existing_tasks.filter(file=filename).exists():
                    task = existing_tasks.filter(file=filename).first()

                task.file = file
                self.tasks.append(task)

        return rtn

    def save(self, commit=True):
        """
        Once the form has been cleaned and validated, part of saving it
        should involve saving the tasks attached to the project and the
        media files for the tasks.
        """
        rtn = super(ProjectForm, self).save(commit=True)
        if self.is_valid():
            for task in self.tasks:
                task.project = self.instance
                task.save()
            self.process_txt_files()
        return rtn

    def save_m2m(self):
        """
        Trying to save the form raises an exception of save_m2m is not
        defined.
        """
        pass
