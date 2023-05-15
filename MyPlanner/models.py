"""Models for MyPlanner app."""
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime, timedelta, time
from django.utils.translation import gettext_lazy as _


class Guide(models.Model):
    """Guide model."""

    voornaam = models.CharField(max_length=100)
    familienaam = models.CharField(max_length=100, blank=True, null=True)
    login = models.ForeignKey(
        User, on_delete=models.CASCADE, default=1, blank=True, null=True
    )

    def __str__(self):
        """Return the guide name as string representation."""

        if self.familienaam is None:
            return self.voornaam
        else:
            return self.voornaam + " " + self.familienaam


class Module(models.Model):
    """Module model."""

    naam = models.CharField(max_length=100)
    beschrijving = models.CharField(max_length=100, blank=True)

    def __str__(self):
        """Return the module name as string representation."""
        return self.naam


class GroupVisit(models.Model):
    """GroupVisit model."""

    groepsnaam = models.CharField(max_length=100)
    voornaamContactpersoon = models.CharField(max_length=100, default="")
    familienaamContactpersoon = models.CharField(max_length=100, default="")
    emailContactpersoon = models.EmailField(default="")
    telContactpersoon = models.CharField(max_length=100, default="")
    # max amount of people is 20
    aantalPersonen = models.IntegerField(
        validators=[MaxValueValidator(20), MinValueValidator(1)]
    )

    heeftBeperkteMobiliteit = models.BooleanField(
        default=False,
        help_text="Vink aan indien u of iemand uit uw groep beperkt mobiel is",
    )
    isSchool = models.BooleanField(default=False)
    studierichting = models.CharField(max_length=100, blank=True, null=True)
    onderwijsniveau = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ("S", "Secundair onderwijs"),
            ("H", "Hoger onderwijs"),
        ],
    )
    studiejaar = models.IntegerField(blank=True, null=True)
    toegewezenGids = models.ForeignKey(
        Guide, on_delete=models.CASCADE, default=1, blank=True, null=True
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        default=1,
        help_text=mark_safe(
            "<a href='https://www.opzgeel.be/nl/bezoekers/bezoekerscentrum'>Meer info over de modules</a>"
        ),
    )
    lunchVooruitzicht = models.BooleanField(
        default=False,
        help_text=mark_safe(
            "<a href='https://www.opzgeel.be/nl/bezoekers/t-vooruitzicht'>Meer info over 't-Vooruitzicht</a>"
        ),
    )
    datum = models.DateField(help_text="Voorkeur voor datum bezoek")
    tijdstip = models.TimeField(help_text="Voorkeur voor tijdstip bezoek")

    # Needed for expiration
    tijdstipAanvraag = models.DateTimeField(auto_now_add=True)

    # Ability to archive visits
    gearchiveerd = models.BooleanField(default=False)
    vragenOfOpmerkingen = models.TextField(blank=True, null=True)

    from datetime import datetime, time

    def prevent_double(self):
        """
        Custom validator to prevent double bookings.
        """

        print(self)
        if hasattr(self, "datum") and hasattr(self, "tijdstip"):
            print("cleaning")
            # Convert time object to datetime object
            dt = datetime.combine(self.datum, self.tijdstip)

            # Check if there is already a group visit at the chosen date and time or within 2 hours
            if (
                GroupVisit.objects.filter(
                    Q(datum=self.datum, tijdstip=self.tijdstip)
                    | Q(  # exact match
                        datum=self.datum,
                        tijdstip__range=[
                            (dt - timedelta(minutes=30)).time(),
                            (dt + timedelta(minutes=30)).time(),
                        ],
                    )
                    | Q(  # within 30 mins
                        datum=self.datum,
                        tijdstip__lt=self.tijdstip,
                        tijdstip__gte=(dt - timedelta(hours=2)).time(),
                    )
                    | Q(  # within 2 hours before
                        datum=self.datum,
                        tijdstip__gt=self.tijdstip,
                        tijdstip__lte=(dt + timedelta(hours=2)).time(),
                    )  # within 2 hours after
                )
                .exclude(pk=self.pk)
                .exists()
            ):
                overlapping_visit = (
                    GroupVisit.objects.filter(
                        Q(datum=self.datum, tijdstip=self.tijdstip)
                        | Q(  # exact match
                            datum=self.datum,
                            tijdstip__range=[
                                (dt - timedelta(minutes=30)).time(),
                                (dt + timedelta(minutes=30)).time(),
                            ],
                        )
                        | Q(  # within 30 mins
                            datum=self.datum,
                            tijdstip__lt=self.tijdstip,
                            tijdstip__gte=(dt - timedelta(hours=2)).time(),
                        )
                        | Q(  # within 2 hours before
                            datum=self.datum,
                            tijdstip__gt=self.tijdstip,
                            tijdstip__lte=(dt + timedelta(hours=2)).time(),
                        )  # within 2 hours after
                    )
                    .exclude(pk=self.pk)
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

    def __str__(self):
        """Return the chosengroup name as string representation."""
        return self.groepsnaam
