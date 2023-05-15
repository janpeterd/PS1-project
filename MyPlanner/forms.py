from django import forms
from django.forms import TimeInput, DateInput, TextInput, NumberInput, PasswordInput
from datetime import timedelta, datetime
from django.contrib.auth.models import User
from MyPlanner.models import GroupVisit
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm

import MyPlanner.models as models


class GroupVisitForm(forms.ModelForm):
    class Meta:
        model = models.GroupVisit
        fields = [
            "groepsnaam",
            "voornaamContactpersoon",
            "familienaamContactpersoon",
            "emailContactpersoon",
            "telContactpersoon",
            "aantalPersonen",
            "heeftBeperkteMobiliteit",
            "lunchVooruitzicht",
            "isSchool",
            "onderwijsniveau",
            "studierichting",
            "studiejaar",
            "module",
            "datum",
            "tijdstip",
            "vragenOfOpmerkingen",
        ]

        labels = {
            "groepsnaam": "Naam groep (of school)",
            "voornaamContactpersoon": "Voornaam contactpersoon",
            "familienaamContactpersoon": "Familienaam contactpersoon",
            "emailContactpersoon": "E-mailadres contactpersoon",
            "telContactpersoon": "Telefoonnummer contactpersoon",
            "aantalPersonen": "Aantal personen",
            "heeftBeperkteMobiliteit": "Deelnemers met beperkte mobiliteit?",
            "lunchVooruitzicht": "Eigen lunchpakket in 't Vooruitzicht",
            "isSchool": "School",
            "onderwijsniveau": "Onderwijsniveau",
            "studierichting": "Studierichting",
            "studiejaar": "(Studie)jaar",
            "module": "Module",
            "datum": "Datum",
            "tijdstip": "Tijd",
            "vragenOfOpmerkingen": "Vragen of opmerkingen",
        }

        widgets = {
            # HTML can only handle dates in the format YYYY-MM-DD
            "datum": DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "tijdstip": TimeInput(attrs={"type": "time"}),
            "groepsnaam": TextInput(attrs={"placeholder": "Naam van de groep"}),
            "voornaamContactpersoon": TextInput(attrs={"placeholder": "Uw voornaam"}),
            "familienaamContactpersoon": TextInput(
                attrs={"placeholder": "Uw familienaam"}
            ),
            "emailContactpersoon": TextInput(attrs={"placeholder": "Uw e-mailadres"}),
            "telContactpersoon": TextInput(attrs={"placeholder": "Uw telefoonnummer"}),
            "aantalPersonen": NumberInput(
                attrs={"placeholder": "Aantal personen in uw groep"}
            ),
        }

        # helptext?
        help_texts = {
            "onderwijsniveau": "Dit veld moet enkel worden ingevuld bij aanvraag voor een schoolgroep.",
            "studiejaar": "Dit veld moet enkel worden ingevuld bij aanvraag voor een schoolgroep.",
            "studierichting": "Dit veld moet enkel worden ingevuld bij aanvraag voor een schoolgroep.",
            "tijdstip": "Vul een voorkeur van uur in tussen 9u en 18u (liefst op het uur of op het half uur).\
            Wenst u buiten deze uren een bezoek te brengen dan kunt u dit in het veld Vragen of opmerkingen aangeven.",
        }

    def clean(self):
        cleaned_data = super().clean()
        print("Cleaned data: ", cleaned_data)
        self.check_double_booking()
        return cleaned_data

    def check_double_booking(self):
        """
        Custom validator to prevent double bookings.
        """

        datum = self.cleaned_data["datum"]
        print("DATUM", datum)
        tijdstip = self.cleaned_data["tijdstip"]
        print("TIJDSTIP", tijdstip)

        print("cleaning")
        # Convert time object to datetime object
        dt = datetime.combine(datum, tijdstip)
        group_visit_pk = self.instance.pk if self.instance else None

        # Check if there is already a group visit at the chosen date and time or within 2 hours
        if (
            GroupVisit.objects.filter(
                Q(datum=datum, tijdstip=tijdstip)
                | Q(  # exact match
                    datum=datum,
                    tijdstip__range=[
                        (dt - timedelta(minutes=30)).time(),
                        (dt + timedelta(minutes=30)).time(),
                    ],
                )
                | Q(  # within 30 mins
                    datum=datum,
                    tijdstip__lt=tijdstip,
                    tijdstip__gte=(dt - timedelta(hours=2)).time(),
                )
                | Q(  # within 2 hours before
                    datum=datum,
                    tijdstip__gt=tijdstip,
                    tijdstip__lte=(dt + timedelta(hours=2)).time(),
                )  # within 2 hours after
            )
            .exclude(pk=group_visit_pk)
            .exists()
        ):
            overlapping_visit = (
                GroupVisit.objects.filter(
                    Q(datum=datum, tijdstip=tijdstip)
                    | Q(  # exact match
                        datum=datum,
                        tijdstip__range=[
                            (dt - timedelta(minutes=30)).time(),
                            (dt + timedelta(minutes=30)).time(),
                        ],
                    )
                    | Q(  # within 30 mins
                        datum=datum,
                        tijdstip__lt=tijdstip,
                        tijdstip__gte=(dt - timedelta(hours=2)).time(),
                    )
                    | Q(  # within 2 hours before
                        datum=datum,
                        tijdstip__gt=tijdstip,
                        tijdstip__lte=(dt + timedelta(hours=2)).time(),
                    )  # within 2 hours after
                )
                .exclude(pk=group_visit_pk)
                .first()
            )
            print("Er is al een groepsbezoek gepland op deze datum en tijd.")
            raise ValidationError(
                {
                    "datum": _(
                        "Er is al een groepsbezoek gepland op "
                        + str(overlapping_visit.datum.strftime("%d/%m/%Y"))
                        + " om "
                        + str(overlapping_visit.tijdstip.strftime("%H:%M"))
                        + "."
                        + " Gelieve een ander tijdstip te kiezen."
                    )
                }
            )


class ChangeGuideForm(forms.ModelForm):
    class Meta:
        model = models.GroupVisit
        fields = ["toegewezenGids"]
        labels = {"toegewezenGids": "Verander de gids voor het bezoek"}


# This form is for the guide to fill in
class NewGuideUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        labels = {
            "username": "Gebruikersnaam",
            "first_name": "Voornaam",
            "last_name": "Familienaam",
            "email": "E-mailadres",
        }
