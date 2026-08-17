from django.urls import path

from .views import (
    CustomersReportView,
    ProfitReportView,
    PurchasesReportView,
    SalesReportView,
    StockReportView,
)

urlpatterns = [
    path("sales/", SalesReportView.as_view(), name="report-sales"),
    path("purchases/", PurchasesReportView.as_view(), name="report-purchases"),
    path("profit/", ProfitReportView.as_view(), name="report-profit"),
    path("stock/", StockReportView.as_view(), name="report-stock"),
    path("customers/", CustomersReportView.as_view(), name="report-customers"),
]