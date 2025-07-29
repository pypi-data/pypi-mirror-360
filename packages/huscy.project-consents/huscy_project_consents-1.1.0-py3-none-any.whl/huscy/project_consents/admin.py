from django.contrib import admin

from . import models, services


class ProjectConsentAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, project_consent=None):
        if project_consent:
            return self.readonly_fields + ('project', )
        return self.readonly_fields

    def save_model(self, request, project_consent, form, change):
        if change is True:
            services.update_project_consent(
                project_consent,
                text_fragments=project_consent.text_fragments,
            )
        else:
            services.create_project_consent(project=project_consent.project,
                                            text_fragments=project_consent.text_fragments)


class ProjectConsentCategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, project_consent_category, form, change):
        if change is True:
            services.update_project_consent_category(
                project_consent_category,
                name=project_consent_category.name,
                template_text_fragments=project_consent_category.template_text_fragments,
            )
        else:
            services.create_project_consent_category(
                name=project_consent_category.name,
                template_text_fragments=project_consent_category.template_text_fragments,
            )


class ProjectConsentFileAdmin(admin.ModelAdmin):
    list_display = 'id', '_subject', '_project', 'project_consent_version'

    def _project(self, project_consent_file):
        return project_consent_file.project_consent.project.title

    def _subject(self, project_consent_file):
        return project_consent_file.subject.contact.display_name

    def has_change_permission(self, request, project_consent_file=None):
        return False

    def save_model(self, request, project_consent_file, form, change):
        services.create_project_consent_file(
            project_consent=project_consent_file.project_consent,
            subject=project_consent_file.subject,
            filehandle=project_consent_file.filehandle,
        )


class ProjectConsentTokenAdmin(admin.ModelAdmin):
    list_display = 'id', '_project', '_subject', 'created_at', 'created_by'

    def _project(self, project_consent_token):
        return project_consent_token.project.title

    def _subject(self, project_consent_token):
        return project_consent_token.subject.contact.display_name

    def has_change_permission(self, request, project_consent_token=None):
        return False

    def save_model(self, request, project_consent_token, form, change):
        services.create_project_consent_token(
            project=project_consent_token.project,
            subject=project_consent_token.subject,
            creator=request.user,
        )


class ProjectIntermediaryAdmin(admin.ModelAdmin):
    list_display = 'id', '_project', '_username', 'email', 'phone'

    def _project(self, project_intermediary):
        return project_intermediary.project_membership.project.title

    def _username(self, project_intermediary):
        return project_intermediary.project_membership.user.username


admin.site.register(models.ProjectConsent, ProjectConsentAdmin)
admin.site.register(models.ProjectConsentCategory, ProjectConsentCategoryAdmin)
admin.site.register(models.ProjectConsentFile, ProjectConsentFileAdmin)
admin.site.register(models.ProjectConsentToken, ProjectConsentTokenAdmin)
admin.site.register(models.ProjectIntermediary, ProjectIntermediaryAdmin)
