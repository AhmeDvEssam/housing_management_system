(function () {
  const statusLabels = {
    AVAILABLE: "متاح",
    OCCUPIED: "مشغول",
    RESERVED: "محجوز",
    LOTTERY_PENDING: "قرعة – منتظر السداد",
    MAINTENANCE: "تحت الصيانة",
    NOT_BOOKABLE: "غير قابل للحجز",
  };

  const summaryOrder = [
    "AVAILABLE",
    "OCCUPIED",
    "RESERVED",
    "LOTTERY_PENDING",
    "MAINTENANCE",
    "NOT_BOOKABLE",
  ];

  function element(id) {
    return document.getElementById(id);
  }

  function buildParams(filters) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== "") {
        params.append(key, value);
      }
    });
    return params.toString();
  }

  function clearElement(target) {
    while (target.firstChild) {
      target.removeChild(target.firstChild);
    }
  }

  function buildSummary(units) {
    const counts = {
      AVAILABLE: 0,
      OCCUPIED: 0,
      RESERVED: 0,
      LOTTERY_PENDING: 0,
      MAINTENANCE: 0,
      NOT_BOOKABLE: 0,
    };
    units.forEach((unit) => {
      const key = unit.current_status || "AVAILABLE";
      counts[key] = (counts[key] || 0) + 1;
    });

    return summaryOrder.map((status) => ({
      status,
      label: statusLabels[status],
      count: counts[status] || 0,
    }));
  }

  function renderSummary(summaryTarget, items) {
    clearElement(summaryTarget);
    items.forEach((item) => {
      const card = document.createElement("div");
      card.className = "summary-card";

      const label = document.createElement("span");
      label.textContent = item.label;

      const count = document.createElement("strong");
      count.textContent = item.count;

      card.appendChild(label);
      card.appendChild(count);
      summaryTarget.appendChild(card);
    });
  }

  function renderTable(headTarget, bodyTarget, dates, units) {
    clearElement(headTarget);
    clearElement(bodyTarget);

    const headRow = document.createElement("tr");
    const unitHeader = document.createElement("th");
    unitHeader.textContent = "الوحدة";
    headRow.appendChild(unitHeader);
    dates.forEach((date) => {
      const th = document.createElement("th");
      th.textContent = date;
      headRow.appendChild(th);
    });
    headTarget.appendChild(headRow);

    units.forEach((unit) => {
      const row = document.createElement("tr");
      const unitCell = document.createElement("td");

      const meta = document.createElement("div");
      meta.className = "unit-meta";

      const title = document.createElement("div");
      title.className = "unit-title";
      title.textContent = `${unit.unit_no} - ${unit.unit_type_label}`;

      const sub1 = document.createElement("div");
      sub1.className = "unit-sub";
      sub1.textContent = `${unit.building} • ${unit.floor_label}`;

      const sub2 = document.createElement("div");
      sub2.className = "unit-sub";
      const orientation = unit.orientation_label || "اتجاه غير محدد";
      sub2.textContent = `السعة: ${unit.capacity} • ${orientation}`;

      meta.appendChild(title);
      meta.appendChild(sub1);
      meta.appendChild(sub2);
      unitCell.appendChild(meta);
      row.appendChild(unitCell);

      unit.statuses.forEach((day) => {
        const td = document.createElement("td");
        const chip = document.createElement("span");
        chip.className = `chip ${day.status}`;
        chip.textContent = day.label;
        td.appendChild(chip);
        row.appendChild(td);
      });

      bodyTarget.appendChild(row);
    });
  }

  function wallboard() {
    const elements = {
      date: element("filter-date"),
      days: element("filter-days"),
      club: element("filter-club"),
      building: element("filter-building"),
      floor: element("filter-floor"),
      status: element("filter-status"),
      bookingType: element("filter-booking-type"),
      capacity: element("filter-capacity"),
      orientation: element("filter-orientation"),
      applyBtn: element("apply-btn"),
      resetBtn: element("reset-btn"),
      error: element("error"),
      summary: element("summary"),
      tableWrap: element("table-wrap"),
      tableHead: element("table-head"),
      tableBody: element("table-body"),
      emptyState: element("empty-state"),
    };

    function setError(message) {
      if (message) {
        elements.error.textContent = message;
        elements.error.hidden = false;
      } else {
        elements.error.hidden = true;
      }
    }

    function getFilters() {
      return {
        date: elements.date.value.trim(),
        days: elements.days.value,
        club: elements.club.value,
        building: elements.building.value,
        floor: elements.floor.value,
        status: elements.status.value,
        booking_type: elements.bookingType.value,
        capacity: elements.capacity.value,
        orientation: elements.orientation.value,
      };
    }

    function resetFilters() {
      elements.date.value = "";
      elements.days.value = "7";
      elements.club.value = "";
      elements.building.value = "";
      elements.floor.value = "";
      elements.status.value = "";
      elements.bookingType.value = "";
      elements.capacity.value = "";
      elements.orientation.value = "";
      fetchData();
    }

    function renderData(data) {
      const units = data.units || [];
      if (!units.length) {
        elements.tableWrap.hidden = true;
        elements.summary.hidden = true;
        elements.emptyState.hidden = false;
        clearElement(elements.tableHead);
        clearElement(elements.tableBody);
        return;
      }

      elements.emptyState.hidden = true;
      elements.tableWrap.hidden = false;
      elements.summary.hidden = false;

      const summaryItems = buildSummary(units);
      renderSummary(elements.summary, summaryItems);
      renderTable(elements.tableHead, elements.tableBody, data.dates, units);
    }

    function fetchData(showError = true) {
      const params = buildParams(getFilters());
      const url = `/api/dashboard/wallboard${params ? `?${params}` : ""}`;
      fetch(url)
        .then((response) => {
          if (!response.ok) {
            return response.json().then((data) => {
              throw new Error(data.detail || "تعذر تحميل البيانات");
            });
          }
          return response.json();
        })
        .then((data) => {
          setError("");
          renderData(data);
        })
        .catch((err) => {
          if (showError) {
            setError(err.message);
          }
        });
    }

    elements.applyBtn.addEventListener("click", fetchData);
    elements.resetBtn.addEventListener("click", resetFilters);

    fetchData();
    setInterval(() => fetchData(false), 10000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wallboard);
  } else {
    wallboard();
  }
})();
