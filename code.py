import streamlit as st
from decimal import Decimal, ROUND_HALF_UP

# ---------- Helpers ----------
def rupiah(n: float | int) -> str:
    s = f"{int(n):,}".replace(",", ".")
    return f"Rp {s}"

def round_rule(amount: float, rule: str) -> int:
    if rule == "none":
        return int(Decimal(amount).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    step = 100 if rule == "100" else 1000
    return int(step * round(amount / step))

# ---------- Page & Sidebar ----------
st.set_page_config(page_title="Split Bill", page_icon="🍽️", layout="centered")

st.sidebar.header("Settings")
tax_pct = st.sidebar.number_input("VAT (PPN) %", min_value=0.0, value=0.0, step=0.5, key="tax_pct")
service_pct = st.sidebar.number_input("Service charge %", min_value=0.0, value=0.0, step=0.5, key="service_pct")
discount = st.sidebar.number_input("Discount amount (IDR)", min_value=0, value=0, step=1000, key="discount")
payment_fee_pct = st.sidebar.number_input("Payment fee % (QRIS/e-wallet/bank) — optional", min_value=0.0, value=0.0, step=0.1, key="payment_fee_pct")
rounding = st.sidebar.selectbox(
    "Rounding",
    options=["none", "100", "1000"],
    index=0,
    format_func=lambda x: {"none":"No rounding","100":"Nearest Rp100","1000":"Nearest Rp1.000"}[x]
)

tax_base = st.sidebar.radio(
    "Tax base (how PPN is calculated)",
    options=["subtotal", "subtotal + service"],
    index=0,
    key="tax_base",
    help="Some places tax only the subtotal; others tax (subtotal + service)."
)

st.title("🍽️ Split Bill (Indonesia)")
st.caption("Split per person with item quantities, VAT/service, discounts, payment fees, and Rupiah rounding.")

# ---------- Inputs ----------
colA, colB = st.columns(2)
with colA:
    n_people = st.number_input("Number of people", min_value=1, value=3, step=1)
with colB:
    n_items = st.number_input("Number of items (lines on receipt)", min_value=1, value=5, step=1)

people = [st.text_input(f"Person #{i+1} name", value=f"Person {i+1}") for i in range(n_people)]

st.subheader("Items")
st.caption("Enter **unit price** and **quantity**. The app multiplies them for totals.")
items = []
for i in range(n_items):
    c1, c2, c_qty, c3 = st.columns([3, 2, 1.2, 3])
    with c1:
        name = st.text_input(f"Item #{i+1} name", value=f"Item {i+1}", key=f"item_name_{i}")
    with c2:
        unit_price = st.number_input("Unit price (IDR)", min_value=0, value=0, step=1000, key=f"item_price_{i}")
    with c_qty:
        qty = st.number_input("Qty", min_value=1, value=1, step=1, key=f"item_qty_{i}")
    with c3:
        assigned = st.multiselect("Charged to", options=people, default=people, key=f"item_people_{i}")

    line_total = unit_price * qty
    items.append({"name": name, "unit_price": unit_price, "qty": qty, "line_total": line_total, "assigned": assigned})

# Quick per-item preview
with st.expander("Preview item totals"):
    for x in items:
        st.write(f"- {x['name']} — {x['qty']} × {rupiah(x['unit_price'])} = **{rupiah(x['line_total'])}**")

st.divider()
st.subheader("Split mode")
mode = st.radio("Choose how to split", ["Per item (default)", "Equal split across all items"])

# ---------- Compute ----------
subtotal = sum(x["line_total"] for x in items)

# Service first
service = subtotal * (service_pct / 100)

# Tax base per your setting
if tax_base == "subtotal":
    tax = subtotal * (tax_pct / 100)
else:
    tax = (subtotal + service) * (tax_pct / 100)

after_discount = max(subtotal + service + tax - discount, 0)
payment_fee = after_discount * (payment_fee_pct / 100)
grand_total = after_discount + payment_fee

m1, m2, m3, m4 = st.columns(4)
m1.metric("Subtotal", rupiah(subtotal))
m2.metric("Service", rupiah(int(service)))
m3.metric("VAT (PPN)", rupiah(int(tax)))
m4.metric("Grand total", rupiah(int(grand_total)))
if discount > 0:
    st.caption(f"Discount applied: - {rupiah(discount)}")
if payment_fee_pct > 0:
    st.caption(f"Payment fee (est.): {rupiah(int(payment_fee))}")

st.divider()
st.subheader("Per-person result")

# Start with zero
per_person = {p: 0.0 for p in people}

if mode == "Equal split across all items":
    share = subtotal / max(n_people, 1)
    for p in people:
        per_person[p] += share
else:
    # Per item: split the *line_total* equally among selected people
    for x in items:
        if not x["assigned"]:
            continue
        split = x["line_total"] / len(x["assigned"])
        for p in x["assigned"]:
            per_person[p] += split

# Allocate service, tax, discount, and payment fee proportionally to pre-allocation
pre_alloc_total = sum(per_person.values()) or 1
for p in people:
    w = per_person[p] / pre_alloc_total
    per_person[p] += w * service
    per_person[p] += w * tax
    per_person[p] -= w * discount
    per_person[p] += w * payment_fee

# Apply rounding rule
per_person_rounded = {p: round_rule(v, rounding) for p, v in per_person.items()}
sum_rounded = sum(per_person_rounded.values())

st.write("**Breakdown per person**")
for p in people:
    st.write(f"- {p}: {rupiah(per_person_rounded[p])}")

# Rounding difference notice
diff = int(round(grand_total)) - sum_rounded
if diff != 0:
    st.info(
        f"Rounding difference: {rupiah(diff)}. "
        f"You can assign it to one person or change the rounding rule."
    )

with st.expander("Notes"):
    st.markdown(
        """
- **Unit price × Qty** builds each line total; splitting is based on the resulting line totals.
- **Tax base** controls whether PPN is on subtotal only, or on (subtotal + service).
- **Payment fees** can be spread proportionally if you enter a %.
- Extend idea: add “already paid” inputs per person to compute change/debts automatically.
        """
    )
