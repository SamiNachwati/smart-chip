import matplotlib.pyplot as plt
import re
import streamlit as st


def run_cpu_analysis():
    st.title("CPU Benchmark Comparison Tool")
    st.write("Compare performance and value of AMD vs Intel CPUs")

    # Price limit slider
    MAX_D = st.slider("Maximum Price ($)", min_value=500, max_value=5000,
                      value=3000, step=100)

    # File upload option with default file fallback
    uploaded_file = st.file_uploader(
        "Upload CPU data file (or use default data)", type="txt")

    # Data array
    d = []

    # Process file data
    if uploaded_file:
        content = uploaded_file.getvalue().decode("utf-8")
        file_source = "uploaded file"
    else:
        # Use default file if no upload
        try:
            with open("multi_core_cpu_data.txt") as text:
                content = text.read()
                file_source = "default file"
        except FileNotFoundError:
            st.error("Default data file not found. Please upload a file.")
            return

    st.info(f"Using data from {file_source}")

    # Process data with original logic
    for ln in content.split('\n'):
        if ln.startswith("#") or not ln.strip() or ln.endswith("NA"):
            continue
        ln = ln.replace("*", "").strip()
        # regex pattern used to get Model, Ranking, Benchmark, and pricing
        m = re.match(r"(.+?)\s+\((\d+)%\)\s+([\d,]+)\s+\$?([\d,.]+)?", ln)
        if m:
            mo, r, b, p = m[1], int(m[2]), int(m[3].replace(",", "")), \
                          float(m[4].replace(",", ""))
            d.append({"mo": mo, "r": r, "b": b, "p": p})

    # Original function: sort each CPU data item by Benchmark in descending order
    cpu_sort = lambda pre: sorted(
        [[i["p"], i["b"], i["mo"], int(i["b"] / i["p"])]
         for i in d if i["mo"].startswith(pre)], key=lambda x: x[1],
        reverse=True)

    # Original function: obtain Intel and AMD's Data
    amd_bks_price, in_bks_price = cpu_sort("AMD"), cpu_sort("In")

    # Find the best pricing for AMD and Intel with error handling
    try:
        b_in = next(i for i in in_bks_price if i[0] < MAX_D)
    except (StopIteration, IndexError):
        st.warning("No Intel CPUs found under the price limit")
        b_in = None

    try:
        b_amd = next(i for i in amd_bks_price if i[0] < MAX_D)
    except (StopIteration, IndexError):
        st.warning("No AMD CPUs found under the price limit")
        b_amd = None

    # Original functions preserved
    def get_lb(a, flag=False):
        """
        Create label for arrow annotation
        a: data array representing sorted CPU array by benchmark
        flag: used to determine if price or mark/price should be used for x-coord
        """
        return [f"{a[2]} ${int(a[0])}", (a[3] if flag else a[0], a[1])]

    def set_bk_and_bk_per_cost(cpu_type):
        """
        method that sets the mark and benchmark per cost
        :param cpu_type: the type of the cpu, In (Intel) or AMD
        :return: cost and mark per cost
        """
        return zip(*[(i["b"], int(i["b"] / i["p"])) for i in d if
                     i["mo"].startswith(cpu_type)])

    # Extract benchmarks & costs (original logic)
    a_mark, a_mark_cost = set_bk_and_bk_per_cost("AMD")
    i_mark, in_bk_per_cost = set_bk_and_bk_per_cost("In")
    a_cost, i_cost = [i["p"] for i in d if i["mo"].startswith("AMD")], \
                     [i["p"] for i in d if i["mo"].startswith("In")]

    # Convert to lists for matplotlib compatibility
    a_mark, a_mark_cost = list(a_mark), list(a_mark_cost)
    i_mark, in_bk_per_cost = list(i_mark), list(in_bk_per_cost)

    # Create two columns for the two plots
    col1, col2 = st.columns(2)

    # First plot - Performance vs. Performance/$
    with col1:
        fig1, ax1 = plt.subplots(figsize=(6, 5))

        # First scatter plot (original logic)
        ax1.scatter(a_mark_cost, a_mark, marker="$A$", c="red", zorder=3)
        ax1.scatter(in_bk_per_cost, i_mark, marker="$in$", c="blue", zorder=2)

        # Add annotations if best values were found
        if b_amd:
            ax1.annotate(*get_lb(b_amd, True), xytext=(40, 95000),
                         arrowprops={"arrowstyle": "->", "color": "grey",
                                     "linestyle": "dashed", "zorder": 3})
        if b_in:
            ax1.annotate(*get_lb(b_in, True), xytext=(75, 83000),
                         arrowprops={"arrowstyle": "->", "color": "grey",
                                     "linestyle": "dashed", "zorder": 2})

        # Apply original plot settings
        ax1.set_xlabel("cpuMark / $", fontsize=10)
        ax1.set_ylabel("cpuMark", fontsize=10)
        ax1.set_title("Performance vs. Performance / $", fontsize=12)
        ax1.set_xlim(1, 200)
        ax1.set_ylim(1, 100000)
        ax1.legend(["AMD", "Intel"], loc="upper right")
        ax1.grid(axis="y", color="grey", zorder=1)
        st.pyplot(fig1)

    # Second plot - Performance vs. Cost
    with col2:
        fig2, ax2 = plt.subplots(figsize=(6, 5))

        # Second scatter plot (original logic)
        ax2.scatter(a_cost, a_mark, marker="$A$", c="red", zorder=3)
        ax2.scatter(i_cost, i_mark, marker="$in$", c="blue", zorder=2)

        # Add annotations if best values were found
        if b_amd:
            ax2.annotate(*get_lb(b_amd), xytext=(52, 95000),
                         arrowprops={"arrowstyle": "->", "color": "grey",
                                     "linestyle": "dashed", "zorder": 3})
        if b_in:
            ax2.annotate(*get_lb(b_in), xytext=(55, 75000),
                         arrowprops={"arrowstyle": "->", "color": "grey",
                                     "linestyle": "dashed", "zorder": 2})

        # Apply original plot settings
        ax2.set_xlabel("Price in USD", fontsize=10)
        ax2.set_ylabel("cpuMark", fontsize=10)
        ax2.set_title("Performance vs. Cost", fontsize=12)
        ax2.set_xlim(40, 10000)
        ax2.set_ylim(1, 100000)
        ax2.set_xscale("log")
        ax2.grid(axis="y", color="grey", zorder=1)
        ax2.set_xticks([50, 100, 250, 500, 1000, 2500, 5000])
        ax2.set_xticklabels([50, 100, 250, 500, 1000, 2500, 5000])
        st.pyplot(fig2)

    # Show overall title
    st.subheader(f"Best CPU under ${MAX_D}")

    # Show the best CPU details
    if b_amd:
        st.write(
            f"**Best AMD:** {b_amd[2]} (${int(b_amd[0])}) - Performance: {b_amd[1]} cpuMark - Value: {b_amd[3]} cpuMark/$")
    if b_in:
        st.write(
            f"**Best Intel:** {b_in[2]} (${int(b_in[0])}) - Performance: {b_in[1]} cpuMark - Value: {b_in[3]} cpuMark/$")

    # Show data table
    if st.checkbox("Show CPU data table"):
        st.dataframe(
            [{"Model": i["mo"], "Ranking": f"{i['r']}%", "Benchmark": i["b"],
              "Price ($)": i["p"]} for i in d],
            use_container_width=True,
            column_config={
                "Model": st.column_config.TextColumn("Model"),
                "Ranking": st.column_config.TextColumn("Ranking"),
                "Benchmark": st.column_config.NumberColumn("Benchmark",
                                                           format="%d"),
                "Price ($)": st.column_config.NumberColumn("Price ($)",
                                                           format="%.2f")
            }
        )


if __name__ == "__main__":
    run_cpu_analysis()