from datetime import date, datetime, timezone
from django.conf import settings
from django.db.models import ForeignKey, Q
from django.urls import reverse
from django.utils.html import escape
from django_datatables_view.base_datatable_view import BaseDatatableView
from re import match, search, sub
from zoneinfo import ZoneInfo

from bemas.models import Codelist, Complaint, Contact, Organization, Originator, Person
from bemas.utils import get_foreign_key_target_model, get_icon_from_settings, is_bemas_admin, \
  is_bemas_user, is_geometry_field
from .functions import generate_foreign_key_link, generate_foreign_key_link_simplified


class GenericTableDataView(BaseDatatableView):
  """
  generic table data composition view
  """

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.columns = self.model._meta.fields
    super().__init__(*args, **kwargs)

  def prepare_results(self, qs):
    """
    loops given queryset, creates cleaned-up JSON representation of the queryset and returns it

    :param qs: queryset
    :return: cleaned-up JSON representation of the queryset
    """
    json_data = []
    if (
        is_bemas_admin(self.request.user)
        or is_bemas_user(self.request.user)
        or self.request.user.is_superuser
    ):
      for item in qs:
        item_data = []
        item_pk = getattr(item, self.model._meta.pk.name)
        address_handled = False
        for column in self.columns:
          # handle non-geometry related fields and non-search content fields only!
          if not is_geometry_field(column.__class__) and not column.name == 'search_content':
            data = None
            value = getattr(item, column.name)
            # foreign key columns (between object classes only):
            # generate appropriate foreign key links
            if (
                not issubclass(self.model, Codelist)
                and issubclass(column.__class__, ForeignKey)
                and not issubclass(get_foreign_key_target_model(column), Codelist)
            ):
              item_data.append(generate_foreign_key_link(column, item))
            # ordinary columns
            elif not column.name.startswith('address_'):
              if value is not None:
                # format Booleans
                if isinstance(value, bool):
                  data = ('ja' if value is True else 'nein')
                # format dates
                elif isinstance(value, date):
                  data = value.strftime('%d.%m.%Y')
                # format timestamps
                elif isinstance(value, datetime):
                  value_tz = value.replace(tzinfo=timezone.utc).astimezone(
                    ZoneInfo(settings.TIME_ZONE))
                  data = value_tz.strftime('%d.%m.%Y, %H:%M Uhr')
                # format lists
                elif type(value) is list:
                  data = '<br>'.join(value)
                else:
                  data = escape(value)
              item_data.append(data)
            # handle addresses
            elif column.name.startswith('address_') and not address_handled:
              # append address string once
              # instead of appending individual strings for all address related values
              data = self.model.objects.get(pk=item_pk).address()
              address_handled = True
              item_data.append(data)
        # object class organization:
        # add column which lists contact(s)
        if issubclass(self.model, Organization):
          data = ''
          contacts = Organization.objects.get(pk=item_pk).contact_set.all()
          if contacts:
            for index, contact in enumerate(contacts):
              data += '<br>' if index > 0 else ''
              data += generate_foreign_key_link_simplified(
                Contact, contact, contact.name_and_function()
              )
          item_data.append(data)
        # object class complaint:
        # add column which lists complainer(s)
        elif issubclass(self.model, Complaint):
          data = ''
          complainers_organizations = Complaint.objects.get(
            pk=item_pk).complainers_organizations.all()
          if complainers_organizations:
            for index, organization in enumerate(complainers_organizations):
              data += '<br>' if index > 0 else ''
              data += generate_foreign_key_link_simplified(Organization, organization)
          complainers_persons = Complaint.objects.get(pk=item_pk).complainers_persons.all()
          if complainers_persons:
            for index, person in enumerate(complainers_persons):
              data += '<br>' if index > 0 or complainers_organizations else ''
              data += generate_foreign_key_link_simplified(Person, person)
          # designate anonymous complaint
          if not data:
            data = '<em><i class="fas fa-' + get_icon_from_settings('anonymous_complaint') + \
                   '"></i> anonyme Beschwerde</em>'
          item_data.append(data)
        # append links for updating and deleting
        if (
            not issubclass(self.model, Codelist)
            or is_bemas_admin(self.request.user)
            or self.request.user.is_superuser
        ):
          view_name_prefix = self.model.__name__.lower()
          title = self.model._meta.verbose_name
          if issubclass(self.model, Codelist):
            view_name_prefix = 'codelists_' + view_name_prefix
            title = 'Codelisteneintrag'
          item_data.append(
            '<a href="' +
            reverse('bemas:' + view_name_prefix + '_update', args=[item_pk]) +
            '"><i class="fas fa-' + get_icon_from_settings('update') +
            '" title="' + title + ' bearbeiten"></i></a>' +
            '<a class="ms-3" href="' +
            reverse('bemas:' + view_name_prefix + '_delete', args=[item_pk]) +
            '"><i class="fas fa-' + get_icon_from_settings('delete') +
            '" title="' + title + ' löschen"></i></a>'
          )
        json_data.append(item_data)
    return json_data

  def filter_queryset(self, qs):
    """
    filters given queryset

    :param qs: queryset
    :return: filtered queryset
    """
    current_search = self.request.GET.get('search[value]', None)
    if current_search:
      qs_params = None
      for search_element in current_search.lower().split():
        qs_params_inner = None
        for column in self.columns:
          search_column = column.name
          # take care of foreign key columns
          if issubclass(column.__class__, ForeignKey):
            # foreign key target model is codelist
            if issubclass(get_foreign_key_target_model(column), Codelist):
              search_column += '__title'
            # foreign key target model is object class
            else:
              search_column += '__search_content'
          case_a = search('^[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}$', search_element)
          case_b = search('^[0-9]{2}\\.[0-9]{4}$', search_element)
          case_c = search('^[0-9]{2}\\.[0-9]{2}$', search_element)
          if case_a or case_b or case_c:
            search_element_splitted = search_element.split('.')
            kwargs = {
                '{0}__{1}'.format(search_column, 'icontains'): (search_element_splitted[
                    2] + '-' if case_a else '') +
                search_element_splitted[1] + '-' +
                search_element_splitted[0]
            }
          elif search_element == 'ja':
            kwargs = {
                '{0}__{1}'.format(search_column, 'icontains'): 'true'
            }
          elif search_element == 'nein' or search_element == 'nei':
            kwargs = {
                '{0}__{1}'.format(search_column, 'icontains'): 'false'
            }
          elif match(r"^[0-9]+,[0-9]+$", search_element):
            kwargs = {
                '{0}__{1}'.format(search_column, 'icontains'): sub(',', '.', search_element)
            }
          else:
            kwargs = {
                '{0}__{1}'.format(search_column, 'icontains'): search_element
            }
          q = Q(**kwargs)
          qs_params_inner = qs_params_inner | q if qs_params_inner else q
        qs_params = qs_params & qs_params_inner if qs_params else qs_params_inner
      qs = qs.filter(qs_params)
    return qs

  def ordering(self, qs):
    """
    sorts given queryset

    :param qs: queryset
    :return: sorted queryset
    """
    # assume initial order since multiple column sorting is prohibited
    if self.request.GET.get('order[1][column]') is not None:
      return qs
    elif self.request.GET.get('order[0][column]') is not None:
      order_column = self.request.GET.get('order[0][column]')
      order_dir = self.request.GET.get('order[0][dir]', None)
      column_names = []
      for column in self.columns:
        column_names.append(column.name)
      column_name = column_names[int(order_column)]
      directory = '-' if order_dir is not None and order_dir == 'desc' else ''
      return qs.order_by(directory + column_name)