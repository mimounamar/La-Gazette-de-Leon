from django.contrib.auth.models import User
from django.db import models
from multiselectfield import MultiSelectField


class LostPasswordToken(models.Model):
    username = models.CharField(max_length=180, null=False)
    token = models.CharField(max_length=180, null=False)

    def __str__(self):
        return self.username


EDITION_STATUS = (('published', 'Published'),
                  ('wip', 'Work in progress'))


class Edition(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=180, null=False)
    status = MultiSelectField(choices=EDITION_STATUS, default="wip", max_choices=1, max_length=9)

    def publish(self):
        self.status = "published"

    def __str__(self):
        return self.title

    @property
    def done(self):
        articles = Article.objects.filter(edition=self.id, status=["done"])
        return articles.count()

    @property
    def correction(self):
        articles = Article.objects.filter(edition=self.id, status=["correction"])
        return articles.count()

    @property
    def redaction(self):
        articles = Article.objects.filter(edition=self.id, status=["redaction"])
        return articles.count()


ARTICLE_STATUS = (('done', 'Done'),
                  ('correction', 'Correction'),
                  ('redaction', 'Redaction'))
ARTICLE_LABEL = (('actu', 'Actualité'),
                 ('sport', 'Sport'),
                 ('astro', 'Astrologie'),
                 ('art', 'Art'),
                 ('litt', 'Littérature'),
                 ('philo', 'Philosophie'),
                 ('mode', 'Mode'),
                 ('cine', 'Cinéma'),
                 ('itv', 'Interview'),
                 ('musique', 'Musique'),
                 ('micro', 'Micro-trottoir'),
                 ('eco', 'Économie'),
                 ('pop', 'Pop culture'),
                 ('actu-leon', 'Actu Léon'))


class Article(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=180, null=False)
    status = MultiSelectField(choices=ARTICLE_STATUS, null=False, max_choices=1, max_length=10, default="redaction")
    label = MultiSelectField(choices=ARTICLE_LABEL, null=False, max_choices=1, max_length=9)
    redactor_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="redactor_1")
    redactor_2 = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="redactor_2")
    corrector = models.ForeignKey(User, on_delete=models.CASCADE, related_name="corrector")
    content = models.TextField(max_length=50000000, default='{"ops":[{"insert":"Bienvenue."}]}')
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="edition")

    def get_content(self):
        return self.content

    def get_title(self):
        return self.title

    def get_status(self):
        return self.status

    @property
    def full_names(self):
        result = [self.redactor_1.first_name + ' ' + self.redactor_1.last_name]
        if self.redactor_2:
            result.append(self.redactor_2.first_name + ' ' + self.redactor_2.last_name)
        return result

    def __str__(self):
        return self.title




