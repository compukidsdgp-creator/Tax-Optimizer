import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="DNA Tax Optimizer", layout="wide")

# 🔑 SET YOUR GEMINI API KEY
genai.configure(api_key="AIzaSyA5a698ZqSTdG2_G3SGqJq4_nz2ZDpP8F0")

model = genai.GenerativeModel("gemini-2.5-flash")

# -----------------------------
# HEADER
# -----------------------------
col1, col2 = st.columns([2, 5])

with col1:
    st.image(r"C:\Users\User\Desktop\app\logo.png", width=250, use_container_width=True)

with col2:
    st.title("DNA Tax Optimizer")
    st.caption("DNA AI-Powered Tax Planning & Advisory Dashboard")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.image(r"C:\Users\User\Desktop\app\logo.png", width=250)

#client_name = st.sidebar.text_input("Client Name")
financial_year = st.sidebar.selectbox("Financial Year", ["2024-25", "2025-26"])

chart_type = st.sidebar.selectbox(
    "Select Chart",
    ["None", "Income Breakdown", "Deductions Breakdown", "Tax Breakdown"]
)

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
non_refundable_offset = lito_offset
refundable_offset = franking_credit

net_tax = max(0, gross_tax - non_refundable_offset)

# Refund comes from refundable credits


# -----------------------------
# PAYG
# -----------------------------
payg = st.slider("PAYG Withheld", 0, 50000, 10000)
instalments = st.slider("Instalments", 0, 50000, 2000)

final_position = payg + instalments + refundable_offset - net_tax

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
if net_tax == 0:
    st.success("Tax Liability: $0")

if final_position > 0:
    st.success(f"Refund: ${round(final_position,2)}")
else:
    st.error(f"Tax Payable: ${round(abs(final_position),2)}")

# -----------------------------
# CHARTS
# -----------------------------
st.header("📈 DNA Dashboard")

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
# STRATEGY OPTIMIZER
# -----------------------------
st.header("DNA Strategy Optimizer")

def tax_after_adjustment(new_income):
    return calculate_tax(new_income) + new_income*0.02 - total_offset

def optimize(max_amt, step):
    best = (0,0)
    for amt in range(step, max_amt+step, step):
        saving = net_tax - tax_after_adjustment(taxable_income - amt)
        if saving > best[1]:
            best = (amt, saving)
    return best

strategies = []

super_amt, super_save = optimize(5000,1000)
strategies.append(("Super",super_save))
st.write(f"Super: Add ${super_amt} → Save ${round(super_save,2)}")

don_amt, don_save = optimize(5000,500)
strategies.append(("Donation",don_save))
st.write(f"Donation: ${don_amt} → Save ${round(don_save,2)}")

# -----------------------------
# AI TAX ADVISOR
# -----------------------------
st.header("DNA driven AI Tax Advisor")

if st.button("Generate AI Advice"):

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Step 1
    status_text.text("🔍 Analyzing income structure...")
    progress_bar.progress(20)

    # Step 2
    status_text.text("📊 Evaluating tax position...")
    progress_bar.progress(40)

    # Step 3
    status_text.text("🏠 Reviewing rental & deductions...")
    progress_bar.progress(60)

    # Step 4
    status_text.text("🧠 Generating AI insights...")
    progress_bar.progress(80)

    # FINAL AI CALL
    prompt = f"""
    Client Income: {total_income}
    Taxable Income: {taxable_income}
    Net Tax: {net_tax}
    Rental: {net_rental}

    Suggest tax saving strategies in brief pointwise in simple understandable manner, so that clients can understand properly. Advise how can the current tax liability can be reduced by giving examples.
    Also at the end suggest to feel free to talk to DNA team and to get consultation ideas mentining our website DNAca.com.au and phone number 02-90644400.
    
    key note: put thi oone ...Please feel free to reach out to us for a personalised consultation to discuss your specific situation and get tailored advice.

Visit our website: DNAca.com.au Or call us on: 02-90644400 first and followed by the advice
    """

    with st.spinner("💡 Finalizing expert recommendations..."):
        response = model.generate_content(prompt)
        advice = response.text

    progress_bar.progress(100)
    status_text.text("✅ Analysis Complete")

    st.success("AI Advice Ready:")
    st.write(advice)

# -----------------------------
# CHATBOT
# -----------------------------
#st.header("💬 AI Chatbot")

#if "chat" not in st.session_state:
    #st.session_state.chat = []

#for msg in st.session_state.chat:
    #st.chat_message(msg["role"]).write(msg["content"])

#user_input = st.chat_input("Ask tax question...")

#if user_input:
    #st.session_state.chat.append({"role":"user","content":user_input})

    #context = f"Income:{total_income}, Tax:{net_tax}, Rental:{net_rental}"

    #reply = model.generate_content(context + user_input).text

   # st.session_state.chat.append({"role":"assistant","content":reply})

   # st.chat_message("assistant").write(reply)

# -----------------------------
# PDF
# -----------------------------

def generate_pdf():
    file_path = "tax_report.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    # -----------------------------
    # HEADER
    # -----------------------------
    content.append(Image(r"C:\Users\User\Desktop\app\logo.png", width=120, height=60))
    content.append(Paragraph("DNA Tax Advisory Report", styles["Title"]))
    content.append(Spacer(1, 10))

    #content.append(Paragraph(f"Client: {client_name}", styles["Normal"]))
    content.append(Paragraph(f"Financial Year: {financial_year}", styles["Normal"]))
    content.append(Spacer(1, 15))

    # -----------------------------
    # INCOME TABLE
    # -----------------------------
    content.append(Paragraph("Income Summary", styles["Heading2"]))

    income_data = [
        ["Category", "Amount"],
        ["Salary", salary],
        ["Allowance", allowance],
        ["Interest", interest],
        ["Dividend", dividend],
        ["Franked Dividend", franked_dividend],
        ["Capital Gain", capital_gain],
        ["Rental", net_rental],
        ["Other", other_income],
    ]

    table = Table(income_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    # -----------------------------
    # EXPENSE TABLE
    # -----------------------------
    content.append(Paragraph("Deductions Summary", styles["Heading2"]))

    expense_data = [
        ["Category", "Amount"],
        ["Car", car],
        ["Travel", travel],
        ["Education", education],
        ["Work", other_work],
        ["Donations", donations],
        ["Tax Agent", tax_agent],
        ["Super", super_contribution],
        ["Other", other_deduction],
    ]

    table2 = Table(expense_data)
    table2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    content.append(table2)
    content.append(Spacer(1, 20))

    # -----------------------------
    # CHART (INCOME)
    # -----------------------------
    content.append(Paragraph("Income Visualization", styles["Heading2"]))

    drawing = Drawing(400, 200)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 125
    chart.width = 300

    chart.data = [[salary, allowance, interest, dividend, net_rental]]
    chart.categoryAxis.categoryNames = ["Salary","Allow","Interest","Div","Rental"]

    drawing.add(chart)
    content.append(drawing)
    content.append(Spacer(1, 20))

    # -----------------------------
    # TAX SUMMARY
    # -----------------------------
    content.append(Paragraph("Tax Position", styles["Heading2"]))

    content.append(Paragraph(f"Total Income: ${total_income}", styles["Normal"]))
    content.append(Paragraph(f"Total Deductions: ${total_deductions}", styles["Normal"]))
    content.append(Paragraph(f"Taxable Income: ${taxable_income}", styles["Normal"]))
    content.append(Paragraph(f"Tax Payable: ${round(net_tax,2)}", styles["Normal"]))
    content.append(Spacer(1, 20))

    # -----------------------------
    # AI ADVICE
    # -----------------------------
    content.append(Paragraph("Professional Tax Advice", styles["Heading2"]))

    try:
        prompt = f"""
        Client Income: {total_income}
        Taxable Income: {taxable_income}
        Net Tax: {net_tax}
        Rental: {net_rental}

        Provide concise professional tax advice.
        """

        response = model.generate_content(prompt)
        advice_text = response.text

    except:
        advice_text = "AI advice unavailable. Please review manually."

    content.append(Paragraph(advice_text, styles["Normal"]))

    # -----------------------------
    # DISCLAIMER
    # -----------------------------
    content.append(Spacer(1, 20))
    content.append(Paragraph(
        "Disclaimer: This report is generated for advisory purposes only. "
        "Please consult a registered tax agent for final decisions.",
        styles["Italic"]
    ))

    # BUILD PDF
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
