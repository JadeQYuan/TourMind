from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from decimal import Decimal
from app.core.deps import DBDep, require_roles
from app.models.order import CustomerOrder
from app.models.bill import Bill

router = APIRouter(
    prefix="/dashboard",
    tags=["数据看板"],
    dependencies=[Depends(require_roles("admin", "system_admin"))],
)


def _default_start() -> date:
    today = date.today()
    return today - timedelta(days=30)


@router.get("")
async def get_dashboard(
    db: DBDep,
    start_date: date = Query(default_factory=_default_start),
    end_date: date = Query(default_factory=date.today),
):
    """统一返回看板全部聚合数据"""
    from sqlalchemy import case, desc, literal_column
    from app.models.product import Product
    from app.models.supplier import Supplier

    # ── 1. 汇总 KPI ──────────────────────────────────────────────────────
    income_stmt = (
        select(func.coalesce(func.sum(Bill.amount), Decimal("0")))
        .where(Bill.bill_type == "income")
        .where(Bill.bill_date >= start_date)
        .where(Bill.bill_date <= end_date)
    )
    expense_stmt = (
        select(func.coalesce(func.sum(Bill.amount), Decimal("0")))
        .where(Bill.bill_type == "expense")
        .where(Bill.bill_date >= start_date)
        .where(Bill.bill_date <= end_date)
    )
    order_count_stmt = (
        select(func.count(CustomerOrder.id))
        .where(CustomerOrder.created_at >= start_date)
        .where(CustomerOrder.created_at <= end_date)
    )

    total_income = (await db.execute(income_stmt)).scalar_one() or Decimal("0")
    total_expense = (await db.execute(expense_stmt)).scalar_one() or Decimal("0")
    total_orders = (await db.execute(order_count_stmt)).scalar_one()
    total_profit = total_income - total_expense

    summary = {
        "total_orders": total_orders,
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "total_profit": float(total_profit),
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
    }

    # ── 2. 订单状态分布 ─────────────────────────────────────────────────
    status_labels = {
        "pending_deposit": "待下定",
        "pending_payment": "待付款",
        "completed": "已完成",
    }
    dist_stmt = (
        select(CustomerOrder.status, func.count(CustomerOrder.id))
        .group_by(CustomerOrder.status)
    )
    dist_rows = (await db.execute(dist_stmt)).all()
    order_status_distribution = [
        {"status": row[0], "label": status_labels.get(row[0], row[0]), "count": row[1]}
        for row in dist_rows
    ]

    # ── 3. 月度收支趋势（按月分组） ─────────────────────────────────────
    month_func = func.to_char(Bill.bill_date, "YYYY-MM")
    trend_stmt = (
        select(
            month_func.label("month"),
            func.coalesce(
                func.sum(func.nullif(case((Bill.bill_type == "income", Bill.amount), else_=None), None)), Decimal("0")
            ).label("income"),
            func.coalesce(
                func.sum(func.nullif(case((Bill.bill_type == "expense", Bill.amount), else_=None), None)), Decimal("0")
            ).label("expense"),
        )
        .where(Bill.bill_date >= start_date)
        .where(Bill.bill_date <= end_date)
        .group_by(month_func)
        .order_by(month_func)
    )
    trend_rows = (await db.execute(trend_stmt)).all()
    monthly_income_trend = [
        {
            "month": row.month,
            "income": float(row.income or 0),
            "expense": float(row.expense or 0),
            "profit": float((row.income or 0) - (row.expense or 0)),
        }
        for row in trend_rows
    ]

    # ── 4. Top 5 产品（按订单数） ────────────────────────────────────────
    top_products_stmt = (
        select(
            CustomerOrder.product_id,
            CustomerOrder.product_name,
            func.count(CustomerOrder.id).label("order_count"),
            func.coalesce(func.sum(CustomerOrder.price), Decimal("0")).label("total_income"),
        )
        .where(CustomerOrder.created_at >= start_date)
        .where(CustomerOrder.created_at <= end_date)
        .group_by(CustomerOrder.product_id, CustomerOrder.product_name)
        .order_by(desc("order_count"))
        .limit(5)
    )
    top_products_rows = (await db.execute(top_products_stmt)).all()
    top_products = [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "order_count": row.order_count,
            "total_income": float(row.total_income or 0),
        }
        for row in top_products_rows
    ]

    # ── 5. Top 5 供应商（按成本） ────────────────────────────────────────
    top_suppliers_stmt = (
        select(
            CustomerOrder.supplier_id,
            CustomerOrder.supplier_name,
            func.count(CustomerOrder.id).label("order_count"),
            func.coalesce(func.sum(CustomerOrder.cost), Decimal("0")).label("total_cost"),
        )
        .where(CustomerOrder.supplier_id.isnot(None))
        .where(CustomerOrder.created_at >= start_date)
        .where(CustomerOrder.created_at <= end_date)
        .group_by(CustomerOrder.supplier_id, CustomerOrder.supplier_name)
        .order_by(desc("total_cost"))
        .limit(5)
    )
    top_suppliers_rows = (await db.execute(top_suppliers_stmt)).all()
    top_suppliers = [
        {
            "supplier_id": row.supplier_id,
            "supplier_name": row.supplier_name,
            "order_count": row.order_count,
            "total_cost": float(row.total_cost or 0),
        }
        for row in top_suppliers_rows
    ]

    # ── 6. 最近 5 个订单 ─────────────────────────────────────────────────
    recent_stmt = (
        select(CustomerOrder)
        .order_by(CustomerOrder.created_at.desc())
        .limit(5)
    )
    recent_rows = (await db.execute(recent_stmt)).scalars().all()
    recent_orders = [
        {
            "id": o.id,
            "order_no": o.order_no,
            "customer_name": o.customer_name,
            "product_name": o.product_name,
            "travel_date": o.travel_date.isoformat() if o.travel_date else None,
            "price": float(o.price) if o.price is not None else None,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
        }
        for o in recent_rows
    ]

    return {
        "summary": summary,
        "order_status_distribution": order_status_distribution,
        "monthly_income_trend": monthly_income_trend,
        "top_products": top_products,
        "top_suppliers": top_suppliers,
        "recent_orders": recent_orders,
    }
