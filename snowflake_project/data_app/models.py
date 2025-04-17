from django.db import models

class BusinessNegotiation(models.Model):
    negotiation_date = models.DateField(verbose_name='商談日')
    customer_name = models.CharField(max_length=100, verbose_name='顧客名')
    store_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='店舗コード')
    store_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='店舗名')
    proposal_content = models.TextField(verbose_name='提案内容')
    target_categories = models.CharField(max_length=255, blank=True, null=True, verbose_name='対象カテゴリ')
    target_products = models.TextField(blank=True, null=True, verbose_name='対象商品')
    result_notes = models.TextField(verbose_name='結果メモ', blank=True, null=True)
    person_in_charge = models.CharField(max_length=50, verbose_name='担当者')
    expected_sales = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='予想売上')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def __str__(self):
        return f"{self.customer_name} - {self.negotiation_date}"

    class Meta:
        verbose_name = '商談記録'
        verbose_name_plural = '商談記録'