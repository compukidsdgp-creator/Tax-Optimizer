import streamlit as st
import pandas as pd
import plotly.express as px

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="DNA Tax Optimizer", layout="wide")

# -----------------------------
# HEADER
# -----------------------------
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=250, use_container_width=True)
with col2:
    st.title("DNA Tax Optimizer")
    st.caption("AI-Powered Tax Planning & Optimization Dashboard")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.image("logo.png", width=250)
#client_name = st.sidebar.text_input("Client Name")
financial_year = st.sidebar.selectbox("Financial Year", ["2024-25", "2025-26"])

chart_type = st.sidebar.selectbox(
    "Select Chart",
    ["None", "Income Breakdown", "Deductions Breakdown", "Tax Breakdown"]
)

#extra_super = st.sidebar.slider("Extra Super (Simulation)", 0, 20000, 0)
#extra_donation = st.sidebar.slider("Extra Donation (Simulation)", 0, 5000, 0)

# -----------------------------
# INCOME
# -----------------------------
st.header("📥 Income")

salary = st.slider("Salary", 0, 200000, 50000)
allowance = st.slider("Allowances", 0, 50000, 5000)
interest = st.slider("Interest", 0, 20000, 1000)
dividend = st.slider("Dividend (Unfranked)", 0, 20000, 2000)
franked_dividend = st.slider("Dividend (Franked)", 0, 20000, 2000)
capital_gain = st.slider("Capital Gain", 0, 50000, 5000)
other_income = st.slider("Other Income", 0, 50000, 2000)

# -----------------------------
# RENTAL
# -----------------------------
st.header("🏠 Rental Property")

rental_income = st.slider("Rental Income", 0, 50000, 10000)
rental_interest = st.slider("Loan Interest", 0, 40000, 5000)
rental_repairs = st.slider("Repairs", 0, 20000, 2000)
rental_agent = st.slider("Agent Fees", 0, 10000, 1000)
rental_depreciation = st.slider("Depreciation", 0, 20000, 2000)
rental_other = st.slider("Other Rental Expenses", 0, 10000, 1000)

total_rental_expense = sum([rental_interest, rental_repairs,
                            rental_agent, rental_depreciation, rental_other])
net_rental = rental_income - total_rental_expense

st.write(f"Net Rental Position: ${net_rental}")

# -----------------------------
# DEDUCTIONS
# -----------------------------
st.header("📤 Deductions")

car = st.slider("Car", 0, 20000, 2000)
travel = st.slider("Travel", 0, 15000, 1000)
education = st.slider("Education", 0, 15000, 2000)
other_work = st.slider("Work Expenses", 0, 15000, 1000)
donations = st.slider("Donations", 0, 10000, 500)
tax_agent = st.slider("Tax Agent Fees", 0, 5000, 300)
super_contribution = st.slider("Super Contribution", 0, 30000, 2000)
other_deduction = st.slider("Other Deduction", 0, 10000, 500)

total_deductions = sum([car, travel, education, other_work,
                        donations, tax_agent, super_contribution, other_deduction])

# -----------------------------
# TOTAL INCOME
# -----------------------------
total_income = (salary + allowance + interest + dividend +
                franked_dividend + capital_gain + other_income + net_rental)

taxable_income = total_income - total_deductions

# -----------------------------
# TAX FUNCTION
# -----------------------------
def calculate_tax(income):
    if income <= 18200:
        return 0
    elif income <= 45000:
        return (income - 18200) * 0.19
    elif income <= 120000:
        return 5092 + (income - 45000) * 0.325
    elif income <= 180000:
        return 29467 + (income - 120000) * 0.37
    else:
        return 51667 + (income - 180000) * 0.45

tax = calculate_tax(taxable_income)

# -----------------------------
# MEDICARE
# -----------------------------
has_private = st.selectbox("Private Health Cover?", ["Yes", "No"])
medicare = taxable_income * 0.02
surcharge = 0
if has_private == "No" and taxable_income > 90000:
    surcharge = taxable_income * 0.01

total_medicare = medicare + surcharge

# -----------------------------
# OFFSETS
# -----------------------------
def lito(income):
    if income <= 37500:
        return 700
    elif income <= 45000:
        return 700 - (income - 37500) * 0.05
    elif income <= 66667:
        return 325 - (income - 45000) * 0.015
    else:
        return 0

lito_offset = lito(taxable_income)
franking_credit = franked_dividend * 0.3
total_offset = lito_offset + franking_credit

# -----------------------------
# FINAL TAX
# -----------------------------
gross_tax = tax + total_medicare
net_tax = gross_tax - total_offset

# -----------------------------
# PAYG
# -----------------------------
payg = st.slider("PAYG Withheld", 0, 50000, 10000)
instalments = st.slider("Instalments", 0, 50000, 2000)

final_position = payg + instalments - net_tax

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"${total_income}")
col2.metric("Taxable Income", f"${taxable_income}")
col3.metric("Net Tax", f"${round(net_tax,2)}")

# -----------------------------
# RESULT
# -----------------------------
if final_position > 0:
    st.success(f"Refund: ${round(final_position,2)}")
else:
    st.error(f"Tax Payable: ${round(abs(final_position),2)}")

# -----------------------------
# CHARTS
# -----------------------------
st.header("📈 Dashboard")

if chart_type == "Income Breakdown":
    df = pd.DataFrame({
        "Category": ["Salary","Allowance","Interest","Dividend","Franked","Capital","Rental","Other"],
        "Amount": [salary, allowance, interest, dividend, franked_dividend, capital_gain, net_rental, other_income]
    })
    st.plotly_chart(px.pie(df, names="Category", values="Amount"))

elif chart_type == "Deductions Breakdown":
    df = pd.DataFrame({
        "Category": ["Car","Travel","Education","Work","Donation","TaxAgent","Super","Other"],
        "Amount": [car, travel, education, other_work, donations, tax_agent, super_contribution, other_deduction]
    })
    st.plotly_chart(px.bar(df, x="Category", y="Amount"))

elif chart_type == "Tax Breakdown":
    df = pd.DataFrame({
        "Category": ["Tax","Medicare","Offset"],
        "Amount": [tax, total_medicare, total_offset]
    })
    st.plotly_chart(px.bar(df, x="Category", y="Amount"))

# -----------------------------
# ADVANCED STRATEGY OPTIMIZER
# -----------------------------
st.header("Advanced Strategy Optimizer")

def tax_after_adjustment(new_income):
    new_tax = calculate_tax(new_income)
    new_medicare = new_income * 0.02
    return new_tax + new_medicare - total_offset


def optimize_strategy(max_amount, step):
    best = {"amount": 0, "saving": 0, "efficiency": 0}

    for amt in range(step, max_amount + step, step):
        new_income = taxable_income - amt
        new_tax = tax_after_adjustment(new_income)
        saving = net_tax - new_tax

        efficiency = saving / amt if amt else 0

        if saving > best["saving"]:
            best = {"amount": amt, "saving": saving, "efficiency": efficiency}

    return best


strategies = []

# SUPER
remaining_super = max(0, 27500 - super_contribution)
if remaining_super > 0:
    res = optimize_strategy(min(remaining_super, 20000), 1000)
    strategies.append(("Super", res))
    st.write(f"Super → Add ${res['amount']} → Save ${round(res['saving'],2)}")

# DONATION
res = optimize_strategy(5000, 500)
strategies.append(("Donation", res))
st.write(f"Donation → ${res['amount']} → Save ${round(res['saving'],2)}")

# WORK
res = optimize_strategy(8000, 500)
strategies.append(("Work", res))
st.write(f"Work Expenses → ${res['amount']} → Save ${round(res['saving'],2)}")

# RENTAL
if net_rental >= 0:
    res = optimize_strategy(10000, 1000)
    strategies.append(("Negative Gearing", res))
    st.write(f"Rental Strategy → ${res['amount']} → Save ${round(res['saving'],2)}")

# RANKING
st.subheader("Best Strategies")
for name, data in sorted(strategies, key=lambda x: x[1]["saving"], reverse=True):
    st.write(f"{name} → Save ${round(data['saving'],2)}")

# COMBINED
total_opt = sum([s[1]["amount"] for s in strategies])
combined_income = taxable_income - total_opt
combined_tax = tax_after_adjustment(combined_income)
combined_saving = net_tax - combined_tax

st.success(f"Combined Strategy → Save ${round(combined_saving,2)}")

# -----------------------------
# PDF
# -----------------------------
def generate_pdf():
    file_path = "tax_report.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []
    content.append(Image("logo.png", width=100, height=50))
    content.append(Paragraph("DNA Tax Report", styles["Title"]))
    content.append(Spacer(1,12))

    #content.append(Paragraph(f"Client: {client_name}", styles["Normal"]))
    content.append(Paragraph(f"Taxable Income: ${taxable_income}", styles["Normal"]))
    content.append(Paragraph(f"Net Tax: ${round(net_tax,2)}", styles["Normal"]))

    doc.build(content)
    return file_path

st.header("📄 Export Report")

if st.button("Generate PDF"):
    pdf = generate_pdf()
    with open(pdf, "rb") as f:
        st.download_button("Download PDF", f, file_name="Tax_Report.pdf")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("© 2026 DNA | AI Tax Solutions")
