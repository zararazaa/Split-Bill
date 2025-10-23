import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Quicksand', sans-serif;
    }

    /* Optional: make headers stand out */
    h1, h2, h3 {
        font-family: 'Quicksand', sans-serif;
        font-weight: 600;
        color: #d81b60;
    }
    </style>
""", unsafe_allow_html=True)

# Formatting
def rupiah(n: float | int) -> str:
    s = f"{int(n):,}".replace(",", ".")
    return f"Rp {s}"

def round_rule(amount: float, rule: str) -> int:
    if rule == "none":
        return int(Decimal(amount).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    step = 100 if rule == "100" else 1000
    return int(step * round(amount / step))

# Page Split
st.set_page_config(page_title="Split Bill", page_icon="🍽️", layout="centered")


# To make it pretty
st.markdown("""
<style>
:root{
  --primary: #E37383;     /* your primary */
  --bg:      #F9F6EE;     /* background */
  --text:    #0D0D0D;     /* text */
}

/* App + sidebar colors */
.stApp { background: var(--bg); color: var(--text); }
section[data-testid="stSidebar"] { background: var(--bg); }

/* Headings */
h1, h2, h3, h4 { color: var(--text); }

/* ---------- Input borders ---------- */
/* Text input */
div[data-testid="stTextInput"] > div > div {
  border: 2px solid var(--primary);
  border-radius: 12px;
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(227,115,131,0.08) inset;
}

/* Number input */
div[data-testid="stNumberInput"] > div {
  border: 2px solid var(--primary);
  border-radius: 12px;
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(227,115,131,0.08) inset;
}

/* Selectbox */
div[data-testid="stSelectbox"] > div {
  border: 2px solid var(--primary);
  border-radius: 12px;
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(227,115,131,0.08) inset;
}

/* Multiselect */
div[data-testid="stMultiSelect"] > div {
  border: 2px solid var(--primary);
  border-radius: 12px;
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(227,115,131,0.08) inset;
}
/* Multiselect pills */
div[data-baseweb="tag"] {
  background: #FDE6EA;           /* soft pink chip */
  color: var(--text);
  border-radius: 999px;
}

/* Radio group */
div[data-testid="stRadio"] {
  border: 2px solid var(--primary);
  border-radius: 12px;
  padding: 12px 14px;
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(227,115,131,0.08) inset;
}

/* Focus/hover effect for inputs */
div[data-testid="stTextInput"] > div > div:focus-within,
div[data-testid="stNumberInput"] > div:focus-within,
div[data-testid="stSelectbox"] > div:focus-within,
div[data-testid="stMultiSelect"] > div:focus-within,
div[data-testid="stRadio"]:focus-within {
  border-color: #cc5f6f;
  box-shadow: 0 0 0 4px rgba(227,115,131,0.18) inset;
}

/* Buttons in your color */
div.stButton > button {
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 10px;
}
div.stButton > button:hover {
  filter: brightness(1.05);
  transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)


st.sidebar.header("Settings")
tax_pct = st.sidebar.number_input("VAT (PPN) %", min_value=0.0, value=0.0, step=0.5, key="tax_pct")
service_pct = st.sidebar.number_input("Service charge %", min_value=0.0, value=0.0, step=0.5, key="service_pct")
discount_pct = st.sidebar.number_input(
    "Discount (%)", 
    min_value=0.0, 
    max_value=100.0, 
    value=0.0, 
    step=0.5, 
    key="discount_pct",
    help="Applied to the subtotal, and TAX is then based on the discounted subtotal.")
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

st.title("Split Bill :D")
st.caption("RIP Line Split Bill, you will be dearly missed")

# Inputs
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

# Item summary
with st.expander("Preview item totals"):
    for x in items:
        st.write(f"- {x['name']} — {x['qty']} × {rupiah(x['unit_price'])} = **{rupiah(x['line_total'])}**")

st.divider()
st.subheader("Split mode")
mode = st.radio("Choose how to split", ["Per item (default)", "Equal split across all items"])

# Calculating
subtotal = sum(x["line_total"] for x in items)

# Discount first (on subtotal)
discount_amount = subtotal * (discount_pct / 100.0)
discounted_subtotal = max(subtotal - discount_amount, 0)

# Service first
service = subtotal * (service_pct / 100.0)

# Tax base per your setting
if tax_base == "subtotal":
    tax = discounted_subtotal * (tax_pct / 100.0)
else:
    tax = (discounted_subtotal + service) * (tax_pct / 100.0)

grand_total = discounted_subtotal + service + tax



# Totals
m1, m2, m3, m4 = st.columns(4)
m1.metric("Subtotal", rupiah(subtotal))
m2.metric("Service", rupiah(int(service)))
m3.metric("VAT (PPN)", rupiah(int(tax)))
m4.metric("Grand total", rupiah(int(round(grand_total))))
if discount_pct > 0:
    st.caption(f"Discount ({discount_pct:.1f}%) applied to subtotal: - {rupiah(int(discount_amount))}")


if discount_pct > 0:
    st.caption(f"Discount ({discount_pct:.1f}%) applied: - {rupiah(int(discount_amount))}")


# Hides the results
has_names = all(p.strip() for p in people)
has_assignments = any(x["line_total"] > 0 and len(x["assigned"]) > 0 for x in items)
ready = (subtotal > 0) and has_names and has_assignments


if ready:
    st.divider()
    st.subheader("Per-person result")

    # Start with zero
    per_person = {p: 0.0 for p in people}

    if mode == "Equal split across all items":
        share = subtotal / max(n_people, 1)
        for p in people:
            per_person[p] += share
    else:
        for x in items:
            if not x["assigned"]:
                continue
            split = x["line_total"] / len(x["assigned"])
            for p in x["assigned"]:
                per_person[p] += split

    # Service + Tax + Discount
    pre_alloc_total = sum(per_person.values()) or 1
    for p in people:
        w = per_person[p] / pre_alloc_total
        per_person[p] += w * service
        per_person[p] += w * tax
        per_person[p] -= w * discount_amount


    # Rounding
    per_person_rounded = {p: round_rule(v, rounding) for p, v in per_person.items()}
    sum_rounded = sum(per_person_rounded.values())

    max_value = max(per_person_rounded.values())
    leaders = [p for p, v in per_person_rounded.items() if v == max_value]
    single_winner = (len(leaders) == 1)
    
    st.write("**Breakdown per person**")
    for p in people:
        if single_winner and p == leaders[0]:
            st.markdown(f"- **{p}: {rupiah(per_person_rounded[p])} 5 big booms for the biggest spender <3**")
        else:
            st.write(f"- {p}: {rupiah(per_person_rounded[p])}")


    diff = int(round(grand_total)) - sum_rounded
    if diff != 0:
        st.info(
            f"Rounding difference: {rupiah(diff)}. "
            f"You can assign it to one person or change the rounding rule."
        )


with st.expander("Notes"):
    st.markdown(
        """  
- **Tax**: figure out the ratio and split urself :).  
        """
    )
















