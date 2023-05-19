"""Module containing all views for the MyPlanner app."""
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import MyPlanner.forms as forms
import MyPlanner.models as models
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import translation
from django.core.management import call_command
from django.contrib.auth.models import Group, User


domain = "https://ps-1-project.vercel.app/"


def getGuideEmails():
    """Returns a list of all guide emails."""
    # Make email list, derived from all guides that have a login
    # This list is used to send emails to all guides
    guide_emails = []
    # Get all guide objects, that have a login associated
    guide_logins = models.Guide.objects.filter(login__isnull=False)
    print("guide logins", guide_logins)
    for guide in guide_logins:
        email = guide.login.email
        print("Guide email", email)
        guide_emails.append(email)
    return guide_emails


def index(request):
    """View function for home page of site."""
    return render(request, "MyPlanner/index.html")


def form(request):
    """View function for the form page of site."""
    form = forms.GroupVisitForm()

    current_user = request.user

    if request.method == "POST":
        form = forms.GroupVisitForm(request.POST)
        if form.is_valid():
            form.save()
            new_object = form.instance
            # Send email with id of the new group
            print("Sending email!")

            assign_guide_link = domain + "/gids-toewijzen/" + str(new_object.id)

            # Send group info to the guides
            msg_html = render_to_string(
                "MyPlanner/mail/new_visit.html",
                {
                    "new_object": new_object,
                    "assign_guide_link": assign_guide_link,
                    "domain": domain,
                },
            )

            msg_plain = render_to_string(
                "MyPlanner/mail/new_visit.txt",
                {
                    "new_object": new_object,
                    "assign_guide_link": assign_guide_link,
                    "domain": domain,
                },
            )

            send_mail(
                "Nieuwe aanvraag museumbezoek op "
                + str(new_object.datum.strftime("%d/%m/%Y"))
                + " – Pas-sage",
                msg_plain,
                "janpeter.dhalle@gmail.com",
                getGuideEmails(),
                fail_silently=True,
                html_message=msg_html,
            )

            # send confirmation email to the group
            mail_subject = "Bevestiging bezoek aan bezoekerscentrum OPZ"
            msg_html = render_to_string(
                "MyPlanner/mail/confirmation.html", {"new_object": new_object}
            )

            msg_plain = render_to_string(
                "MyPlanner/mail/confirmation.txt", {"new_object": new_object}
            )

            send_mail(
                "Re: " + mail_subject,
                msg_plain,
                "janpeter.dhalle@gmail.com",
                [new_object.emailContactpersoon],
                fail_silently=True,
                html_message=msg_html,
            )

            return render(request, "MyPlanner/form_success.html")

        # else:
        #     form = forms.GroupVisitForm()

    return render(
        request,
        "MyPlanner/form.html",
        {"form": form, "domain": domain, "current_user": current_user},
    )


@login_required
def visits(request, id):
    """View function for the visits page of site."""

    current_user = request.user

    chosen_visit = models.GroupVisit.objects.get(id=id)
    print(chosen_visit)

    # Get the guide that has foreign key to the current user
    currently_logged_in_guide = models.Guide.objects.get(id=1)  # fallback
    for guide in models.Guide.objects.all():
        fk = guide.login
        if fk == current_user:
            currently_logged_in_guide = guide

    if request.method == "POST":
        form = forms.ChangeGuideForm(request.POST, instance=chosen_visit)
        if form.is_valid():
            print("form is valid!")
            form.save()

            # update chosen_visit variable after saving
            chosen_visit = models.GroupVisit.objects.get(id=id)

            # Send email to the guides
            mail_subject = (
                "Wijziging gids museumbezoek "
                + str(chosen_visit.datum.strftime("%d/%m/%Y"))
                + " – Pas-sage"
            )
            msg_html = render_to_string(
                "MyPlanner/mail/change_guide.html",
                {"chosen_visit": chosen_visit, "domain": domain},
            )
            msg_plain = render_to_string(
                "MyPlanner/mail/change_guide.txt",
                {"chosen_visit": chosen_visit, "domain": domain},
            )

            send_mail(
                "Re: " + mail_subject,
                msg_plain,
                "janpeter.dhalle@gmail.com",
                getGuideEmails(),
                fail_silently=True,
                html_message=msg_html,
            )

            # send email to the group
            mail_subject = (
                "Wijziging gids museumbezoek "
                + str(chosen_visit.datum.strftime("%d/%m/%Y"))
                + " – Pas-sage"
            )
            msg_html = render_to_string(
                "MyPlanner/mail/change_guide_group.html",
                {"chosen_visit": chosen_visit, "domain": domain},
            )
            msg_plain = render_to_string(
                "MyPlanner/mail/change_guide_group.txt",
                {"chosen_visit": chosen_visit, "domain": domain},
            )

            send_mail(
                "Re: " + mail_subject,
                msg_plain,
                "janpeter.dhalle@gmail.com",
                [chosen_visit.emailContactpersoon],
                fail_silently=True,
                html_message=msg_html,
            )

        else:
            print("form is not valid!")
            print(form.errors)
    else:
        form = forms.ChangeGuideForm(instance=chosen_visit)

    return render(
        request,
        "MyPlanner/visits.html",
        {
            "chosen_visit": chosen_visit,
            "domain": domain,
            "id": id,
            "form": form,
            "current_user": current_user,
        },
    )


@login_required
def assignGuide(request, id):
    """View function for the assignGuide page of site."""
    current_user = request.user

    chosen_visit = models.GroupVisit.objects.get(id=id)

    # Get the guide that has foreign key to the current user
    linked_guide = models.Guide.objects.get(id=1)  # fallback
    for guide in models.Guide.objects.all():
        fk = guide.login
        if fk == current_user:
            linked_guide = guide

    chosen_visit.toegewezenGids = linked_guide
    chosen_visit.save()

    # Send email to the guides
    mail_subject = (
        "Gids toegewezen aan museumbezoek "
        + str(chosen_visit.datum.strftime("%d/%m/%Y"))
        + " – Pas-sage"
    )

    msg_html = render_to_string(
        "MyPlanner/mail/assigned_guide.html",
        {"chosen_visit": chosen_visit, "domain": domain, "linked_guide": linked_guide},
    )
    msg_plain = render_to_string(
        "MyPlanner/mail/assigned_guide.txt",
        {"chosen_visit": chosen_visit, "domain": domain, "linked_guide": linked_guide},
    )

    send_mail(
        "Re: " + mail_subject,
        msg_plain,
        "janpeter.dhalle@gmail.com",
        getGuideEmails(),
        fail_silently=True,
        html_message=msg_html,
    )

    # send confirmation email to the group
    mail_subject = (
        "Gids toegewezen voor uw museumbezoek op "
        + str(chosen_visit.datum.strftime("%d/%m/%Y"))
        + " – Pas-sage"
    )

    msg_html = render_to_string(
        "MyPlanner/mail/assigned_guide_group.html", {"chosen_visit": chosen_visit}
    )

    msg_plain = render_to_string(
        "MyPlanner/mail/assigned_guide_group.txt", {"chosen_visit": chosen_visit}
    )

    send_mail(
        "Re: " + mail_subject,
        msg_plain,
        "janpeter.dhalle@gmail.com",
        [chosen_visit.emailContactpersoon],
        fail_silently=True,
        html_message=msg_html,
    )

    return render(
        request,
        "MyPlanner/success.html",
        {
            "chosen_visit": chosen_visit,
            "linked_guide": linked_guide,
            "domain": domain,
            "current_user": current_user,
        },
    )


# TODO: Add a Form with a dropdown menu to select guide, and maybe add new guide!


@login_required
def archive_and_notify(request, id):
    # Archive
    chosen_visit = models.GroupVisit.objects.get(id=id)
    chosen_visit.gearchiveerd = True
    chosen_visit.save()

    # Send email to the group
    mail_subject = (
        "Geen gids beschikbaar voor een museumbezoek op "
        + str(chosen_visit.datum.strftime("%d/%m/%Y"))
        + " – Pas-sage"
    )
    msg_html = render_to_string(
        "MyPlanner/mail/archived.html", {"chosen_visit": chosen_visit, "domain": domain}
    )
    msg_plain = render_to_string(
        "MyPlanner/mail/archived.txt", {"chosen_visit": chosen_visit, "domain": domain}
    )

    # Notify the group
    send_mail(
        "Re: " + mail_subject,
        msg_plain,
        "janpeter.dhalle@gmail.com",
        [chosen_visit.emailContactpersoon],
        fail_silently=True,
        html_message=msg_html,
    )

    # Also notify the guides
    mail_subject = "Groep " + str(chosen_visit.id) + " is geannuleerd"
    msg_html = render_to_string(
        "MyPlanner/mail/archived_guide.html",
        {"chosen_visit": chosen_visit, "domain": domain},
    )
    msg_plain = render_to_string(
        "MyPlanner/mail/archived_guide.txt",
        {"chosen_visit": chosen_visit, "domain": domain},
    )

    # Notify the guides
    send_mail(
        "Re: " + mail_subject,
        msg_plain,
        "janpeter.dhalle@gmail.com",
        getGuideEmails(),
        fail_silently=True,
        html_message=msg_html,
    )

    return redirect("all_visits")


@login_required
def all_visits(request):
    """View function for the all_visits page of site."""
    all_visits = models.GroupVisit.objects.all().filter(gearchiveerd=False)
    current_user = request.user

    return render(
        request,
        "MyPlanner/all_visits.html",
        {"all_visits": all_visits, "domain": domain, "current_user": current_user},
    )


@login_required
def all_guide_visits(request):
    # Get the guide that has foreign key to the current user
    current_user = request.user
    currently_logged_in_guide = models.Guide.objects.get(id=1)  # fallback
    for guide in models.Guide.objects.all():
        fk = guide.login
        if fk == current_user:
            currently_logged_in_guide = guide

    all_visits = models.GroupVisit.objects.all().filter(
        gearchiveerd=False, toegewezenGids=currently_logged_in_guide
    )

    # tell the template that we are filtering
    filtered = True

    return render(
        request,
        "MyPlanner/all_visits.html",
        {
            "all_visits": all_visits,
            "domain": domain,
            "current_user": current_user,
            "currently_logged_in_guide": currently_logged_in_guide,
            "filtered": filtered,
        },
    )


@login_required
def all_archived_visits(request):
    all_archived_visits = models.GroupVisit.objects.all().filter(gearchiveerd=True)
    current_user = request.user

    return render(
        request,
        "MyPlanner/all_archived.html",
        {
            "all_archived_visits": all_archived_visits,
            "domain": domain,
            "current_user": current_user,
        },
    )


@login_required
def delete_visit(request, id):
    """View function for the delete_visit page of site."""
    chosen_visit = models.GroupVisit.objects.get(id=id)
    chosen_visit.delete()
    messages.info(request, "Bezoek verwijderd!")

    return redirect("all_visits")


@login_required
def edit_visit(request, id):
    current_user = request.user
    translation.activate("nl")
    chosen_visit = models.GroupVisit.objects.get(id=id)
    if request.method == "POST":
        form = forms.GroupVisitForm(request.POST, instance=chosen_visit)
        if form.is_valid():
            form = forms.GroupVisitForm(request.POST, instance=chosen_visit)
            form.save()
            return redirect("all_visits")

        else:
            print(form.errors)
    else:
        form = forms.GroupVisitForm(instance=chosen_visit)

    # Render the edit form with the current values of the object
    return render(
        request,
        "MyPlanner/edit_visit.html",
        {"chosen_visit": chosen_visit, "form": form, "current_user": current_user},
    )


# api endpoint for cronjob
def checkvisits(request):
    call_command("checkvisits")
    print("Checkvisits called")
    return JsonResponse({"message": "Checkvisits called"})


@staff_member_required
def createGuideUser(request):
    current_user = request.user
    if request.method == "POST":
        print("POST")
        form = forms.NewGuideUserForm(request.POST)
        if form.is_valid():
            print("VALID")
            user = form.save()
            print("USER", user)

            # Create a new guide object
            guide = models.Guide(
                voornaam=user.first_name, familienaam=user.last_name, login=user
            )
            guide.save()

            guides_group = Group.objects.get(name="Gidsen")
            guides_group.user_set.add(user)

            return redirect("all_visits")
        else:
            print(form.errors)
    else:
        form = forms.NewGuideUserForm()

    return render(
        request,
        "MyPlanner/new_guide_user.html",
        {"form": form, "current_user": current_user, "domain": domain},
    )
