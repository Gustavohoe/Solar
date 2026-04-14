from django.db import models
from django.contrib.auth.models import User

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    valor = models.FloatField()
    estoque = models.IntegerField()

    def __str__(self):
        return self.nome


class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    qtd = models.IntegerField()
    fat = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.produto} - {self.qtd}"
