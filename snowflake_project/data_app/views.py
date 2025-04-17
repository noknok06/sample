from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import BusinessNegotiation
from .snowflake_utils import SnowflakeConnector
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
import pandas as pd
from datetime import datetime, timedelta

# ホームページビュー
def home(request):
    return render(request, 'data_app/home.html')

def generate_proposal(request):
    if request.method == 'POST':
        try:
            # リクエストからパラメータを取得
            data = json.loads(request.body)
            store_code = data.get('store_code', '')
            days = int(data.get('days', 30))
            
            # POSデータの取得
            snowflake = SnowflakeConnector()
            top_products = snowflake.get_top_selling_products(days=days)
            top_categories = snowflake.get_top_selling_categories(days=days)
            store_performance = snowflake.get_store_performance(days=days)
            maker_performance = snowflake.get_maker_performance(days=days)
            company_performance = snowflake.get_company_performance(days=days)
            
            # 特定の店舗が指定されていれば、その店舗のデータのみをフィルタリング
            if store_code:
                store_data = next((store for store in store_performance if store['STORE_CODE'] == store_code), None)
            else:
                # 指定がなければ売上トップの店舗を選択
                store_data = store_performance[0] if store_performance else None
            
            # 提案内容を生成（より詳細なデータを含む）
            proposal = generate_enhanced_proposal_text(
                top_products, 
                top_categories, 
                store_data, 
                maker_performance[:3] if maker_performance else [],
                company_performance[:2] if company_performance else [],
                days
            )
            
            return JsonResponse({
                'proposal': proposal,
                'top_products': top_products[:5],
                'top_categories': top_categories,
                'store_data': store_data,
                'maker_data': maker_performance[:3] if maker_performance else [],
                'company_data': company_performance[:2] if company_performance else [],
                'all_stores': store_performance
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GETリクエストの場合は提案生成フォームを表示
    # 店舗一覧を取得して表示
    snowflake = SnowflakeConnector()
    store_performance = snowflake.get_store_performance(days=1000)
    
    
    # 店舗名でソートして表示
    store_performance.sort(key=lambda x: x['STORE_NAME'])

    return render(request, 'data_app/generate_proposal.html', {
        'stores': store_performance
    })

def generate_enhanced_proposal_text(top_products, top_categories, store_data, top_makers, top_companies, days):
    """POSデータに基づいてより詳細な提案内容を生成する"""
    
    if not store_data or not top_products or not top_categories:
        return "データが不足しているため、提案を生成できません。"
    
    store_name = store_data['STORE_NAME']
    total_sales = store_data['TOTAL_SALES_AMOUNT']
    product_count = store_data['PRODUCT_COUNT']
    
    # トップカテゴリ
    top_category = top_categories[0]['CATEGORY1_NAME'] if top_categories else '不明'
    top_subcategory = top_categories[0]['CATEGORY2_NAME'] if top_categories else '不明'
    
    # トップ商品
    top_product = top_products[0]['PRODUCT_NAME'] if top_products else '不明'
    top_maker = top_products[0]['MAKER_NAME'] if top_products else '不明'
    
    # トップメーカー
    top_maker_name = top_makers[0]['MAKER_NAME'] if top_makers else '不明'
    
    # トップ会社
    top_company_name = top_companies[0]['COMPANY_NAME'] if top_companies else '不明'
    
    # 提案文を生成
    proposal = f"""
【{store_name}】店舗向け商品提案 - 過去{days}日間の販売実績分析

■ 主要分析結果
・対象期間総売上: {total_sales:,.0f}円（取扱商品数: {product_count}点）
・売上トップカテゴリ: {top_category} > {top_subcategory}
・売上トップ商品: {top_product}（{top_maker}）
・売上トップメーカー: {top_maker_name}
・売上トップ会社: {top_company_name}

■ 提案概要
過去{days}日間の売上データを分析した結果、{top_category}カテゴリの商品が特に好調です。
特に{top_product}が売上に貢献していることから、同シリーズや関連商品の品揃え強化をご提案します。
また、{top_maker_name}の商品ラインナップ全体の拡充も効果が見込まれます。

■ 具体的提案内容
1. {top_maker}の商品ラインナップ拡充
2. {top_subcategory}関連の売場面積拡大（現在の約1.5倍を推奨）
3. 以下のトップセラー商品の在庫レベル向上:
"""

    # トップ5商品を追加
    for i, product in enumerate(top_products[:5], 1):
        proposal += f"   {i}. {product['PRODUCT_NAME']} - 売上: {product['TOTAL_SALES_AMOUNT']:,.0f}円\n"
    
    # トップメーカーと会社の情報を追加
    proposal += f"""
■ トップメーカー分析
"""
    for i, maker in enumerate(top_makers[:3], 1):
        proposal += f"   {i}. {maker['MAKER_NAME']} - 売上: {maker['TOTAL_SALES_AMOUNT']:,.0f}円（取扱商品数: {maker['PRODUCT_COUNT']}点）\n"

    proposal += f"""
■ トップ会社分析
"""
    for i, company in enumerate(top_companies[:2], 1):
        proposal += f"   {i}. {company['COMPANY_NAME']} - 売上: {company['TOTAL_SALES_AMOUNT']:,.0f}円\n"
    
    # 予測売上効果を追加
    expected_increase = total_sales * 0.15  # 単純に15%増と仮定
    proposal += f"""
■ 予測効果
本提案実施により、{top_category}カテゴリ全体で約{expected_increase:,.0f}円（15%増）の
売上向上が期待できます。特に週末の客単価向上に効果があると予測されます。

■ アクションプラン
・商品発注：即日対応可能
・売場変更：1週間以内に実施推奨
・効果測定：実施後3週間で検証
"""

    return proposal

# 商談管理: 商談一覧・検索
class NegotiationListView(ListView):
    model = BusinessNegotiation
    template_name = 'data_app/negotiation_list.html'
    context_object_name = 'negotiations'
    ordering = ['-negotiation_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                customer_name__icontains=search_query
            ) | queryset.filter(
                proposal_content__icontains=search_query
            ) | queryset.filter(
                result_notes__icontains=search_query
            ) | queryset.filter(
                store_name__icontains=search_query
            )
        return queryset

# 商談管理: 商談詳細表示
class NegotiationDetailView(DetailView):
    model = BusinessNegotiation
    template_name = 'data_app/negotiation_detail.html'
    context_object_name = 'negotiation'

# 商談管理: 商談登録
@method_decorator(csrf_exempt, name='dispatch')
class NegotiationCreateView(CreateView):
    model = BusinessNegotiation
    template_name = 'data_app/negotiation_form.html'
    fields = ['negotiation_date', 'customer_name', 'store_code', 'store_name', 
              'proposal_content', 'target_categories', 'target_products', 
              'result_notes', 'person_in_charge', 'expected_sales']
    success_url = reverse_lazy('negotiation-list')
    
    def get_initial(self):
        initial = super().get_initial()
        # URLパラメータから初期値を設定
        proposal = self.request.GET.get('proposal', '')
        store_code = self.request.GET.get('store_code', '')
        store_name = self.request.GET.get('store_name', '')
        categories = self.request.GET.get('categories', '')
        products = self.request.GET.get('products', '')
        expected_sales = self.request.GET.get('expected_sales', '')
        
        if proposal:
            initial['proposal_content'] = proposal
        if store_code:
            initial['store_code'] = store_code
        if store_name:
            initial['store_name'] = store_name
        if categories:
            initial['target_categories'] = categories
        if products:
            initial['target_products'] = products
        if expected_sales:
            initial['expected_sales'] = expected_sales
        
        # 現在の日付を初期値として設定
        initial['negotiation_date'] = datetime.now().date()
        
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, '商談が正常に登録されました。')
        return super().form_valid(form)

# 商談管理: 商談編集
class NegotiationUpdateView(UpdateView):
    model = BusinessNegotiation
    template_name = 'data_app/negotiation_form.html'
    fields = ['negotiation_date', 'customer_name', 'store_code', 'store_name', 
              'proposal_content', 'target_categories', 'target_products', 
              'result_notes', 'person_in_charge', 'expected_sales']
    success_url = reverse_lazy('negotiation-list')
    
    def form_valid(self, form):
        messages.success(self.request, '商談が正常に更新されました。')
        return super().form_valid(form)
        