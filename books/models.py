from django.db import models

from base.models import State, GenericBaseModel, salutations, BaseModel
from members.models import Members


# Create your models here.

class Author(GenericBaseModel):
    # FRESHMAN = "FR"
    # SOPHOMORE = "SO"
    # JUNIOR = "JR"
    # SENIOR = "SR"
    # GRADUATE = "GR"
    # YEAR_IN_SCHOOL_CHOICES = [
    #     (FRESHMAN, "Freshman"),
    #     (SOPHOMORE, "Sophomore"),
    #     (JUNIOR, "Junior"),
    #     (SENIOR, "Senior"),
    #     (GRADUATE, "Graduate"),
    # ]
    salutation = models.CharField(choices=salutations(), max_length=5)
    state = models.ForeignKey(State, default=State.default_state, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.salutation} {self.name}"
class Category(GenericBaseModel):
    state = models.ForeignKey(State,default=State.default_state, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta(object):
        ordering = ('name',)
class Books(BaseModel):
    title = models.CharField(max_length=100)
    published_date = models.DateField()
    edition = models.CharField(max_length=10)
    book_image = models.ImageField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.ForeignKey(State, default=State.default_state, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.author}"


class BookIssued(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    member = models.ForeignKey(Members, on_delete=models.CASCADE)
    issued_date = models.DateTimeField(auto_now_add=True)
    borrow_duration = models.IntegerField(default=0)
    return_date = models.DateTimeField()
    return_fee = models.DecimalField(default=0.0, decimal_places=2, max_digits=16)
    fee_paid = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book} - {self.member} - {self.return_date}"


