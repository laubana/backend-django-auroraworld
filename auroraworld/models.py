from django.db import models


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    email = models.CharField(unique=True, max_length=255, db_column='email')
    password = models.CharField(max_length=255, db_column='password')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.id


class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    name = models.CharField(unique=True, max_length=255, db_column='name')

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.id


class Link(models.Model):
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    created_by = models.CharField(max_length=255, db_column='created_by')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        db_column='category_id'
    )
    category_name = models.CharField(max_length=255, db_column='category_name')
    name = models.CharField(max_length=255, db_column='name')
    url = models.CharField(max_length=255, db_column='url')

    class Meta:
        db_table = 'links'

    def __str__(self):
        return self.id


class Share(models.Model):
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    link = models.ForeignKey(
        Link,
        on_delete=models.CASCADE,
        db_column='link_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    user_email = models.CharField(max_length=255, db_column='user_email')
    is_writable = models.BooleanField(default=False, db_column='is_writable')

    class Meta:
        db_table = 'shares'
        unique_together = (('link', 'user'),)

    def __str__(self):
        return self.id
