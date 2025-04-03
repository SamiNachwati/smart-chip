import matplotlib.pyplot as plt
import re
import streamlit as st


def run_cpu_analysis():
    # Set page title and description
    st.title("CPU Benchmark Comparison Tool")
    st.write("Compare performance and value of AMD vs Intel CPUs")

    # File upload option
    uploaded_file = st.file_uploader(
        "Upload CPU data file (or use sample data)", type="txt")

    # Price limit slider
    MAX_D = st.slider("Maximum Price ($)", min_value=500, max_value=5000,
                      value=3000, step=100)

    # Placeholder for data
    d = []

    # Process the data
    if uploaded_file:
        # Read from uploaded file
        content = uploaded_file.getvalue().decode("utf-8")
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
    else:
        # Use sample data if no file uploaded
        st.info("No file uploaded. Using sample data.")
        # Sample data - you can replace with your actual sample data
        sample_data = """
        AMD Ryzen 9 7950X (98%) 46,084 $573
        AMD Ryzen 9 7900X (92%) 41,130 $389
        Intel Core i9-13900K (97%) 54,433 $569
        Intel Core i7-13700K (93%) 40,202 $409
        Intel Core i5-13600K (88%) 34,324 $319
        AMD Ryzen 7 7700X (87%) 32,627 $349
        """
        for ln in sample_data.split('\n'):
            if ln.strip():
                ln = ln.replace("*", "").strip()
                m = re.match(r"(.+?)\s+\((\d+)%\)\s+([\d,]+)\s+\$?([\d,.]+)?",
                             ln)
                if m:
                    mo, r, b, p = m[1], int(m[2]), int(m[3].replace(",", "")), \
                                  float(m[4].replace(",", ""))
                    d.append({"mo": mo, "r": r, "b": b, "p": p})

    # If data is loaded, create visualization
    if d:
        # Sort functions
        cpu_sort = lambda pre: sorted(
            [[i["p"], i["b"], i["mo"], int(i["b"] / i["p"])]
             for i in d if i["mo"].startswith(pre)], key=lambda x: x[1],
            reverse=True)

        # Obtain Intel and AMD's Data with their Pricing, Mark, Model, and cpuMark / $
        amd_bks_price, in_bks_price = cpu_sort("AMD"), cpu_sort("In")

        # Find the best pricing for AMD and Intel
        # Using try/except in case there are no matches under the price limit
        try:
            b_in = next(i for i in in_bks_price if i[0] < MAX_D)
        except StopIteration:
            b_in = None
            st.warning("No Intel CPUs found under the price limit")

        try:
            b_amd = next(i for i in amd_bks_price if i[0] < MAX_D)
        except StopIteration:
            b_amd = None
            st.warning("No AMD CPUs found under the price limit")

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

        # Extract benchmarks & costs
        a_mark, a_mark_cost = set_bk_and_bk_per_cost("AMD")
        i_mark, in_bk_per_cost = set_bk_and_bk_per_cost("In")
        a_cost, i_cost = [i["p"] for i in d if i["mo"].startswith("AMD")], \
                         [i["p"] for i in d if i["mo"].startswith("In")]

        # Create two columns for the charts
        col1, col2 = st.columns(2)

        # Create the figures
        fig1, ax1 = plt.subplots(figsize=(7, 5))

        # First scatter plot
        ax1.scatter(list(a_mark_cost), list(a_mark), marker="o", c="red",
                    label="AMD")
        ax1.scatter(list(in_bk_per_cost), list(i_mark), marker="s", c="blue",
                    label="Intel")

        # Add annotations if best values were found
        if b_amd:
            ax1.annotate(f"{b_amd[2]} ${int(b_amd[0])}",
                         xy=(b_amd[3], b_amd[1]),
                         xytext=(b_amd[3] + 5, b_amd[1] + 5000),
                         arrowprops={"arrowstyle": "->", "color": "grey",
                                     "linestyle": "dashed"})

        if b_in:
            ax1.annotate(f"{b_in[2]} ${int(b_in[0])}",
                         xy=(b_in[3], b_in[1]),
                         xytext=(b_in[3] + 5, b_in[1] + 5000),
                         arrowprops={"arrowstyle": "->", "color": "grey",
                                     "linestyle": "dashed"})

        ax1.set_xlabel("cpuMark / $", fontsize=10)
        ax1.set_ylabel("cpuMark", fontsize=10)
        ax1.set_title("Performance vs. Performance / $", fontsize=12)
        ax1.grid(axis="y", color="grey")
        ax1.legend(loc="upper right")

        # Second figure
        fig2, ax2 = plt.subplots(figsize=(7, 5))

        # Second scatter plot
        ax2.scatter(list(a_cost), list(a_mark), marker="o", c="red",
                    label="AMD")
        ax2.scatter(list(i_cost), list(i_mark), marker="s", c="blue",
                    label="Intel")

        # Add annotations if best values were found
        if b_amd:
            ax2.annotate(f"{b_amd[2]} ${int(b_amd[0])}",
                         xy=(b_amd[0], b_amd[1]),
                         xytext=(b_amd[0] + 200, b_amd[1] + 5000),
                         arrowprops={"arrowstyle": "->", "color": "grey",
                                     "linestyle": "dashed"})

        if b_in:
            ax2.annotate(f"{b_in[2]} ${int(b_in[0])}",
                         xy=(b_in[0], b_in[1]),
                         xytext=(b_in[0] + 200, b_in[1] - 5000),
                         arrowprops={"arrowstyle": "->", "color": "grey",
                                     "linestyle": "dashed"})

        ax2.set_xlabel("Price in USD", fontsize=10)
        ax2.set_ylabel("cpuMark", fontsize=10)
        ax2.set_title("Performance vs. Cost", fontsize=12)
        ax2.set_xscale("log")
        ax2.grid(axis="y", color="grey")
        ax2.legend(loc="upper right")

        # Display plots
        with col1:
            st.pyplot(fig1)

        with col2:
            st.pyplot(fig2)

        # Show summary of best CPUs under price limit
        st.header("Best CPUs Under $" + str(MAX_D))
        if b_amd:
            st.write(
                f"Best AMD: **{b_amd[2]}** - ${int(b_amd[0])} - {b_amd[1]} cpuMarks - {b_amd[3]} cpuMarks/$")
        if b_in:
            st.write(
                f"Best Intel: **{b_in[2]}** - ${int(b_in[0])} - {b_in[1]} cpuMarks - {b_in[3]} cpuMarks/$")
    else:
        st.error("No data to visualize. Please upload a valid CPU data file.")

    # Add a link to your GitHub or source code
    st.markdown("---")
    st.markdown(
        "View the [source code](https://github.com/SamiNachwati/smart-chip) for this application")


if __name__ == "__main__":
    run_cpu_analysis()
