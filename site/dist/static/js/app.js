const atlasState = {
  map: null,
  layersByFips: new Map(),
  selectedNode: null,
};
const MAP_FIT_PADDING = [8, 8];

(function () {
  const navToggle = document.querySelector(".nav-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (navToggle && navLinks) {
    const closeNav = () => {
      navLinks.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    };

    navToggle.addEventListener("click", () => {
      const isOpen = navLinks.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });
    navLinks.addEventListener("click", (event) => {
      if (event.target.closest("a")) {
        closeNav();
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeNav();
      }
    });
  }

  const mapNode = document.getElementById("atlas-map");
  if (mapNode && window.L) {
    initMap(mapNode);
  }

  const searchInput = document.getElementById("county-search");
  if (searchInput) {
    initSearch(searchInput);
  }
})();

async function initMap(mapNode) {
  const url = mapNode.dataset.mapUrl;
  const map = L.map(mapNode, {
    scrollWheelZoom: false,
    zoomControl: true,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    minZoom: 3,
    maxBounds: [
      [20, -128],
      [53, -62],
    ],
    maxBoundsViscosity: 0.8,
  }).setView([39.8, -98.6], 4);
  atlasState.map = map;
  atlasState.selectedNode = document.getElementById("selected-county");

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 10,
    noWrap: true,
    opacity: 0.22,
  }).addTo(map);

  try {
    const response = await fetch(url);
    const geojson = await response.json();
    const layer = L.geoJSON(geojson, {
      style: (feature) => ({
        color: "#f7f8f6",
        weight: 0.45,
        opacity: 0.9,
        fillColor: colorForScore(feature.properties.support_priority_signal),
        fillOpacity: 0.86,
      }),
      onEachFeature: (feature, countyLayer) => {
        const fips = String(feature.properties.fips).padStart(5, "0");
        atlasState.layersByFips.set(fips, countyLayer);
        countyLayer.bindPopup(popupHtml(feature.properties));
        countyLayer.on("click", () => {
          selectCounty(feature.properties, countyLayer);
        });
        countyLayer.on("mouseover", () => {
          countyLayer.setStyle({ weight: 1.6, color: "#164c50", fillOpacity: 0.94 });
        });
        countyLayer.on("mouseout", () => {
          layer.resetStyle(countyLayer);
        });
      },
    }).addTo(map);
    fitInitialMapView(map, layer);
  } catch (error) {
    mapNode.innerHTML = '<div class="map-error">Map data is unavailable in this build.</div>';
    console.error(error);
  }
}

function fitInitialMapView(map, layer) {
  const bounds = layer.getBounds();
  if (!bounds.isValid()) {
    return;
  }
  map.fitBounds(bounds, { animate: false, padding: MAP_FIT_PADDING });
  const targetZoom = Math.max(map.getZoom(), initialMapMinZoom(map.getContainer().clientWidth));
  map.setView(bounds.getCenter(), targetZoom, { animate: false });
  map.getContainer().dataset.initialZoom = String(map.getZoom());
}

function initialMapMinZoom(width) {
  if (width >= 980) return 4.5;
  if (width >= 760) return 4.25;
  if (width >= 560) return 4.25;
  if (width >= 420) return 3.75;
  return 3.5;
}

function colorForScore(score) {
  const value = Number(score);
  if (!Number.isFinite(value)) return "#d6dfda";
  if (value >= 80) return "#174d52";
  if (value >= 65) return "#2f6f73";
  if (value >= 50) return "#5b978e";
  if (value >= 35) return "#94bfb3";
  if (value >= 20) return "#cde2d9";
  return "#eef5f1";
}

function popupHtml(props) {
  const score = formatNumber(props.support_priority_signal, 1);
  const band = signalBand(props.support_priority_signal);
  const establishments = formatNumber(props.establishments, 0);
  const branches = formatNumber(props.branch_count, 0);
  const branchRate = formatNumber(
    props.branches_per_10k_residents || props.branches_per_1000_establishments,
    1
  );
  const craSignal = formatNumber(
    props.cra_small_business_loans || props.cra_loans_per_1000_establishments,
    1
  );
  const stress = props.poverty_pct
    ? `${formatNumber(props.poverty_pct, 1)}%`
    : formatNumber(props.median_household_income, 0);
  const housing = formatNumber(props.housing_cost_pressure, 1);
  const countyUrl = `counties/${String(props.fips).padStart(5, "0")}.html`;
  return `
    <span class="popup-title">${escapeHtml(props.county_name)}, ${escapeHtml(props.state_abbr)}</span>
    <span class="popup-row"><span>Support signal</span><strong>${score}</strong></span>
    <span class="popup-row"><span>Meaning</span><strong>${escapeHtml(band.label)}</strong></span>
    <span class="popup-row"><span>Establishments</span><strong>${establishments}</strong></span>
    <span class="popup-row"><span>Branches</span><strong>${branches}</strong></span>
    <span class="popup-row"><span>Branch rate</span><strong>${branchRate}</strong></span>
    <span class="popup-row"><span>CRA signal</span><strong>${craSignal}</strong></span>
    <span class="popup-row"><span>Stress context</span><strong>${stress}</strong></span>
    <span class="popup-row"><span>Housing context</span><strong>${housing}</strong></span>
    <span class="popup-row"><span>Data quality</span><strong>${escapeHtml(props.data_quality_grade || "D")}</strong></span>
    <p><a href="${countyUrl}">Open county brief</a></p>
  `;
}

async function initSearch(input) {
  const results = document.getElementById("county-search-results");
  atlasState.selectedNode = document.getElementById("selected-county");
  let index = [];
  try {
    const response = await fetch(input.dataset.searchUrl);
    index = await response.json();
  } catch (error) {
    console.error(error);
  }

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    if (!query) {
      results.innerHTML = "";
      return;
    }
    const matches = index
      .filter((item) =>
        `${item.county_name} ${item.state_abbr} ${item.state_name || ""}`
          .toLowerCase()
          .includes(query)
      )
      .slice(0, 8);
    results.innerHTML = matches.length
      ? matches
          .map(
            (item) => `
          <button type="button" data-fips="${escapeHtml(item.fips)}" data-url="${escapeHtml(item.url)}">
            <span>${escapeHtml(item.county_name)}, ${escapeHtml(item.state_abbr)}</span>
            <strong>${escapeHtml(signalBand(item.support_priority_signal).short)} ${formatNumber(item.support_priority_signal, 1)}</strong>
          </button>`
          )
          .join("")
      : '<p class="quiet">No matching county found.</p>';
  });

  results.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-fips]");
    if (!button) {
      return;
    }
    const fips = String(button.dataset.fips || "").padStart(5, "0");
    const item = index.find((candidate) => String(candidate.fips).padStart(5, "0") === fips);
    const layer = atlasState.layersByFips.get(fips);
    if (layer && atlasState.map) {
      selectCounty(layer.feature.properties, layer);
      atlasState.map.fitBounds(layer.getBounds(), { maxZoom: 7, padding: [18, 18] });
      layer.openPopup();
    } else if (item) {
      renderSelectedCounty({
        ...item,
        url: item.url,
      });
    }
  });
}

function selectCounty(props, layer) {
  renderSelectedCounty({
    ...props,
    url: `counties/${String(props.fips).padStart(5, "0")}.html`,
  });
  if (layer && atlasState.map) {
    layer.bringToFront();
  }
}

function renderSelectedCounty(props) {
  const target = atlasState.selectedNode;
  if (!target) {
    return;
  }
  const band = signalBand(props.support_priority_signal);
  const url = props.url || `counties/${String(props.fips).padStart(5, "0")}.html`;
  const branchRate = formatNumber(
    props.branches_per_10k_residents || props.branches_per_1000_establishments,
    1
  );
  const stress = props.poverty_pct
    ? `${formatNumber(props.poverty_pct, 1)}%`
    : formatNumber(props.median_household_income, 0);
  target.innerHTML = `
    <p class="sidebar-title">Selected county</p>
    <h3>${escapeHtml(props.county_name)}, ${escapeHtml(props.state_abbr)}</h3>
    <p class="selected-interpretation"><strong>${escapeHtml(band.label)}</strong> ${escapeHtml(band.text)}</p>
    <dl class="selected-metrics">
      <div><dt>Support signal</dt><dd>${formatNumber(props.support_priority_signal, 1)}</dd></div>
      <div><dt>Data quality</dt><dd>${escapeHtml(props.data_quality_grade || "Unavailable")}</dd></div>
      <div><dt>Business establishments</dt><dd>${formatNumber(props.establishments, 0)}</dd></div>
      <div><dt>Branch signal</dt><dd>${branchRate}</dd></div>
      <div><dt>Stress context</dt><dd>${stress}</dd></div>
    </dl>
    <a class="text-link" href="${escapeHtml(url)}">Open full county brief</a>
  `;
}

function signalBand(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return {
      label: "Score unavailable",
      short: "No score",
      text: "There is not enough public data in this build to interpret the county signal.",
    };
  }
  if (number >= 80) {
    return {
      label: "High follow-up",
      short: "High",
      text: "Several public signals overlap. Treat this as a prompt to review the county brief, check data quality, and prioritize local partner conversations.",
    };
  }
  if (number >= 60) {
    return {
      label: "Elevated",
      short: "Elevated",
      text: "Public data suggests meaningful conditions to review. Compare the drivers before deciding whether follow-up is warranted.",
    };
  }
  if (number >= 40) {
    return {
      label: "Watch",
      short: "Watch",
      text: "Some signals are present, but the story is mixed. Use local knowledge before drawing conclusions.",
    };
  }
  return {
    label: "Lower signal",
    short: "Lower",
    text: "This build shows fewer overlapping public-data signals. Local need may still exist outside the available data.",
  };
}

function formatNumber(value, digits) {
  if (value === null || value === undefined || value === "") return "Unavailable";
  const number = Number(value);
  if (!Number.isFinite(number)) return "Unavailable";
  return number.toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
