
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="TQ Recruitment Capacity Model", layout="wide")

st.title("📊 TQ Recruitment Capacity Model")

# --- Inputs ---
st.sidebar.header("Model Inputs")

scenario_hires = {
    "Scenario 1": st.sidebar.number_input("Total Hires – Scenario 1", value=800),
    "Scenario 2": st.sidebar.number_input("Total Hires – Scenario 2", value=1000),
    "Scenario 3": st.sidebar.number_input("Total Hires – Scenario 3", value=1200)
}

fte_hours = st.sidebar.number_input("FTE Hours Per Year", value=1600)
salary = st.sidebar.number_input("Average Salary Per FTE ($)", value=100000)
oncost_pct = st.sidebar.slider("On-Costs %", min_value=0.0, max_value=1.0, value=0.2)

st.header("🧩 Service & Stage Input")

with st.expander("Edit Services and Stage Hours"):
    services = []
    service_volumes = []
    for i in range(6):
        cols = st.columns([3, 1])
        service = cols[0].text_input(f"Service {i+1}", value=f"Service {i+1}")
        volume = cols[1].number_input(f"% Volume (S{i+1})", min_value=0.0, max_value=100.0, value=float(100/6), key=f"v_{i}")
        services.append(service)
        service_volumes.append(volume)

    st.markdown("#### Recruitment Stages")
    stages = [st.text_input(f"Stage {j+1} Name", value=f"Stage {j+1}") for j in range(15)]

    st.markdown("#### Hours per Stage per Service")
    hour_matrix = []
    for i, service in enumerate(services):
        row = []
        st.write(f"**{service}**")
        cols = st.columns(5)
        for j in range(15):
            if j % 5 == 0 and j > 0:
                cols = st.columns(5)
            val = cols[j % 5].number_input(f"{stages[j]} ({service})", min_value=0.0, step=0.1, value=1.0, key=f"h_{i}_{j}")
            row.append(val)
        hour_matrix.append(row)

# --- Calculations ---
st.header("📈 Results by Scenario")

def calculate_outputs(scenario_name, hires):
    results = []
    for i, service in enumerate(services):
        pct = service_volumes[i] / 100
        weighted_hires = hires * pct
        total_stage_hours = sum(hour_matrix[i])
        total_hours = weighted_hires * total_stage_hours
        fte_required = total_hours / fte_hours if fte_hours else 0
        salary_cost = fte_required * salary
        oncosts = salary_cost * oncost_pct
        total_cost = salary_cost + oncosts

        results.append({
            "Scenario": scenario_name,
            "Service": service,
            "% Volume": pct,
            "Weighted Hires": weighted_hires,
            "Total Hours": total_hours,
            "FTE Required": fte_required,
            "Salary Cost": salary_cost,
            "On-Costs": oncosts,
            "Total Cost": total_cost
        })
    return pd.DataFrame(results)

tabs = st.tabs(["Scenario 1", "Scenario 2", "Scenario 3"])
for i, scenario in enumerate(scenario_hires.keys()):
    with tabs[i]:
        df = calculate_outputs(scenario, scenario_hires[scenario])
        st.dataframe(df.style.format({"% Volume": "{:.1%}", "FTE Required": "{:.2f}", "Total Cost": "${:,.0f}"}), use_container_width=True)
        st.bar_chart(df.set_index("Service")["FTE Required"])
        st.caption(f"Total FTE: {df['FTE Required'].sum():.2f} | Total Cost: ${df['Total Cost'].sum():,.0f}")
