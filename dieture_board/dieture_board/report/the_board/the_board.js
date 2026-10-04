frappe.query_reports["The Board"] = {
  filters: [],

  formatter(value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname === "effective_status") {
      const status = data.effective_status || "";
      const indicator = {
        GREEN: "green",
        YELLOW: "orange",
        RED: "red",
        "RED (stale)": "red",
      }[status] || "gray";
      return `<span class="indicator-pill ${indicator}">${frappe.utils.escape_html(status)}</span>`;
    }

    if (column.fieldname === "overdue_promises" && Number(data.overdue_promises) > 0) {
      return `<span class="text-danger font-weight-bold">${value}</span>`;
    }

    return value;
  },
};
