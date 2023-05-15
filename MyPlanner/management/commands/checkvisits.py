from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from MyPlanner.models import GroupVisit
from django.template.loader import render_to_string

# This script can easily be executed using the following command: python manage.py checkvisits
# It is recommended to run this script every day using a cronjob
# I am using vercel.com to host my django app, so check this: TODO: https://vercel.com/guides/how-to-setup-cron-jobs-on-vercel
class Command(BaseCommand):
    help = 'Check for unassigned visits older than 5 days'

    def handle(self, *args, **options):
        # domain = "http://localhost:8000"
        domain = "https://django-project-planner-janpeterd.vercel.app"
        five_days_ago = timezone.now() - timezone.timedelta(days=5)
        unassigned_visits = GroupVisit.objects.filter(toegewezenGids__id=1, tijdstipAanvraag__lt=five_days_ago, gearchiveerd=False)
        self.stdout.write(f'{len(unassigned_visits)} niet toegewezen bezoeken gevonden.')

        if len(unassigned_visits) != 0:
            for visit in unassigned_visits:
                # archive
                visit.gearchiveerd = True
                visit.save()
                self.stdout.write(f'bezoek met id {visit.id} gearchiveerd.')

                chosen_visit = visit
                # Send email to the group
                mail_subject = 'Groep ' + str(chosen_visit.id) + ' is geannuleerd, kies een nieuw tijdstip'
                msg_html = render_to_string('MyPlanner/mail/archived.html', {'chosen_visit': chosen_visit, 'domain':domain})
                msg_plain = render_to_string('MyPlanner/mail/archived.txt', {'chosen_visit': chosen_visit, 'domain':domain})

                # Notify the group
                send_mail(
                        'Re: ' + mail_subject,
                        msg_plain,
                        'janpeter.dhalle@gmail.com',
                        [chosen_visit.emailContactpersoon],
                        fail_silently=True,
                        html_message= msg_html,
                    )

        past_visits = GroupVisit.objects.filter(datum__lt=timezone.now(), gearchiveerd=False)
        self.stdout.write(f'{len(past_visits)} bezoeken gevonden die al voorbij zijn, maar nog niet gearchiveerd zijn.')

        if len(past_visits) != 0:
            for visit in past_visits:
                # archive without sending email
                visit.gearchiveerd = True
                visit.save()
                self.stdout.write(f'bezoek met id {visit.id} gearchiveerd.')
