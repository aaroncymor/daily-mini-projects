from datetime import datetime
from django.core.management.base import BaseCommand

from tracker.models import MangaSubscription, NotificationLog
from tracker.helpers import get_latest_chapter


class Command(BaseCommand):
    help = "Checks for updates from the watchlist"

    def handle(self, *args, **options):
        # get all watchlist
        manga_subs = MangaSubscription.objects.filter(is_subscribed=True)
        for manga_sub in manga_subs:

            print(f"Checking for updates to {manga_sub.title}...")

            latest_chapter = get_latest_chapter(manga_sub.manga_id)
            if latest_chapter == manga_sub.current_chapter:
                # update manga subscription latest chapter
                manga_sub.current_chapter = latest_chapter
                manga_sub.save()

                # create notification log
                NotificationLog.objects.create(
                    subject=f"{manga_sub.title} - New chapter {latest_chapter} released!",
                    message_body=f"The new chapter for {manga_sub.title} has been released. Check it out!",
                    sent_at=datetime.now()
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"New chapter for {manga_sub.title} is available. Notification sent!"
                    )
                )
            else:
                self.stdout.write(f"No updates yet for {manga_sub.title}...")
