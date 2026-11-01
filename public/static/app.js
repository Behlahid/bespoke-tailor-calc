/**
 * Bombay Master Tailors - Bespoke Measurement & Fabric Yardage Application Logic
 * Integrates interactive SVG mannequin, Python calculation API, Three.js 3D Drape fall,
 * and MySQL client ledger.
 */

(function () {
  "use strict";

  // Application Global State
  const state = {
    customerId: 1,
    customers: [],
    activePoint: "chest",
    unit: "in",
    easePreset: "barabar",
    angle: "front",
    garmentStyle: "bandhgala",
    fabricWidth: 58.0,
    patternType: "plain",
    fabricMill: "Raymond Super 120s Charcoal",
    measurements: {
      neck: 16.5,
      shoulder: 18.2,
      chest: 41.5,
      bicep: 14.0,
      wrist: 7.5,
      waist: 34.0,
      hip: 40.0,
      inseam: 32.5,
      outseam: 41.0,
      thigh: 24.5,
      calf: 15.5,
      jacket_length: 30.0,
      shirt_length: 29.5,
      sleeve_length: 25.0,
    },
    calculation: null,
    currentOrder: null,
  };

  // Node names mapping
  const POINT_LABELS = {
    neck: "GALA (NECK)",
    shoulder: "KANDHA (SHOULDER)",
    chest: "CHHATI (CHEST)",
    bicep: "AASTEEN (BICEP)",
    wrist: "MORI (WRIST)",
    waist: "KAMAR (WAIST)",
    hip: "SEAT (HIP BASIN)",
    inseam: "LAMBAI (INSEAM)",
    outseam: "PANT LAMBAI (OUTSEAM)",
    thigh: "JHAANG (THIGH)",
    calf: "PINDLI (CALF)",
    jacket_length: "KOTI LAMBAI (JACKET LENGTH)",
    shirt_length: "KURTA / SHIRT LAMBAI",
    sleeve_length: "AASTEEN LAMBAI (SLEEVE)",
  };

  // ----------------- DOM ELEMENTS -----------------
  const activeCustomerSelect = document.getElementById("activeCustomerSelect");
  const navTabs = document.querySelectorAll(".nav-tab");
  const viewPanels = document.querySelectorAll(".view-panel");
  const toast = document.getElementById("toast");
  const toastMsg = document.getElementById("toastMsg");

  // Naap DOM
  const naapCustomerName = document.getElementById("naapCustomerName");
  const naapCustomerCity = document.getElementById("naapCustomerCity");
  const activeCaliperTitle = document.getElementById("activeCaliperTitle");
  const activeNumericInput = document.getElementById("activeNumericInput");
  const activeUnitSuffix = document.getElementById("activeUnitSuffix");
  const postureNoteInput = document.getElementById("postureNoteInput");
  const bastingContourPath = document.getElementById("bastingContourPath");
  const cadUnitLabel = document.getElementById("cadUnitLabel");
  const btnUnitInch = document.getElementById("btnUnitInch");
  const btnUnitCm = document.getElementById("btnUnitCm");
  const nodeButtons = document.querySelectorAll(".node-btn");
  const angleButtons = document.querySelectorAll(".angle-btn");
  const stepButtons = document.querySelectorAll(".step-btn");
  const easeButtons = document.querySelectorAll(".ease-btn");
  const btnSaveNaap = document.getElementById("btnSaveNaap");
  const btnSendToYardage = document.getElementById("btnSendToYardage");

  // Kapda DOM
  const calcTotalMeters = document.getElementById("calcTotalMeters");
  const calcTotalGaj = document.getElementById("calcTotalGaj");
  const calcTotalYards = document.getElementById("calcTotalYards");
  const calcEfficiency = document.getElementById("calcEfficiency");
  const calcScrappageText = document.getElementById("calcScrappageText");
  const gaugeRing = document.getElementById("gaugeRing");
  const breakdownJacket = document.getElementById("breakdownJacket");
  const breakdownTrouser = document.getElementById("breakdownTrouser");
  const breakdownBuffer = document.getElementById("breakdownBuffer");
  const breakdownLining = document.getElementById("breakdownLining");
  const garmentTypeButtons = document.querySelectorAll(".garment-pill");
  const boltButtons = document.querySelectorAll(".bolt-btn");
  const boltSelectedDesc = document.getElementById("boltSelectedDesc");
  const patternSelect = document.getElementById("patternSelect");
  const fabricMillSelect = document.getElementById("fabricMillSelect");
  const cuttingAdviceText = document.getElementById("cuttingAdviceText");
  const btnCreateOrderParchi = document.getElementById("btnCreateOrderParchi");
  const handfeelButtons = document.querySelectorAll(".handfeel-btn");
  const clothPhysicsLabel = document.getElementById("clothPhysicsLabel");

  // Khata DOM
  const kpiActiveOrders = document.getElementById("kpiActiveOrders");
  const kpiFabricMeters = document.getElementById("kpiFabricMeters");
  const kpiFabricValue = document.getElementById("kpiFabricValue");
  const kpiUrgentFittings = document.getElementById("kpiUrgentFittings");
  const ledgerSearchInput = document.getElementById("ledgerSearchInput");
  const ledgerFilterChips = document.querySelectorAll(".filter-chip");
  const ledgerFeedContainer = document.getElementById("ledgerFeedContainer");

  // Parchi DOM
  const parchiOrderNoBadge = document.getElementById("parchiOrderNoBadge");
  const parchiClientName = document.getElementById("parchiClientName");
  const parchiClientPhone = document.getElementById("parchiClientPhone");
  const parchiTrialDate = document.getElementById("parchiTrialDate");
  const parchiDeliveryDate = document.getElementById("parchiDeliveryDate");
  const parchiFabricName = document.getElementById("parchiFabricName");
  const parchiFabricMeters = document.getElementById("parchiFabricMeters");
  const parchiJacketCloth = document.getElementById("parchiJacketCloth");
  const parchiTrouserCloth = document.getElementById("parchiTrouserCloth");
  const parchiLiningCloth = document.getElementById("parchiLiningCloth");
  const parchiCanvasCloth = document.getElementById("parchiCanvasCloth");
  const parchiClothCost = document.getElementById("parchiClothCost");
  const parchiStitchingCost = document.getElementById("parchiStitchingCost");
  const parchiTotalBill = document.getElementById("parchiTotalBill");
  const parchiAdvancePaid = document.getElementById("parchiAdvancePaid");
  const parchiBalanceDue = document.getElementById("parchiBalanceDue");
  const parchiMeasurementsMatrix = document.getElementById("parchiMeasurementsMatrix");
  const btnPrintDocket = document.getElementById("btnPrintDocket");
  const btnShareDocket = document.getElementById("btnShareDocket");

  // Modal DOM
  const newCustomerModal = document.getElementById("newCustomerModal");
  const btnOpenNewCustomerModal = document.getElementById("btnOpenNewCustomerModal");
  const btnCloseCustomerModal = document.getElementById("btnCloseCustomerModal");
  const btnCancelCustomerModal = document.getElementById("btnCancelCustomerModal");
  const formNewCustomer = document.getElementById("formNewCustomer");

  // ----------------- TOAST HELPER -----------------
  function showToast(msg) {
    if (!toast) return;
    toastMsg.textContent = msg;
    toast.classList.remove("translate-y-[-100px]", "opacity-0");
    toast.classList.add("translate-y-0", "opacity-100");
    setTimeout(() => {
      toast.classList.remove("translate-y-0", "opacity-100");
      toast.classList.add("translate-y-[-100px]", "opacity-0");
    }, 2400);
  }

  // ----------------- TAB NAVIGATION -----------------
  function switchTab(targetId) {
    viewPanels.forEach((p) => p.classList.add("hidden"));
    const activePanel = document.getElementById(targetId);
    if (activePanel) activePanel.classList.remove("hidden");

    navTabs.forEach((tab) => {
      const match = tab.getAttribute("data-target") === targetId;
      if (match) {
        tab.className = "nav-tab active flex flex-col items-center justify-center min-w-[64px] min-h-[44px] text-secondary font-bold transition-colors";
      } else {
        tab.className = "nav-tab flex flex-col items-center justify-center min-w-[64px] min-h-[44px] text-on-surface-variant hover:text-primary transition-colors";
      }
    });

    window.scrollTo({ top: 0, behavior: "smooth" });

    // Refresh specific tab data
    if (targetId === "view-kapda") {
      runCalculation();
      if (drapeContainer && renderer && camera) {
        setTimeout(() => {
          const w = drapeContainer.clientWidth;
          const h = drapeContainer.clientHeight;
          if (w && h) {
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
          }
        }, 60);
      }
    } else if (targetId === "view-khata") {
      loadLedgerOrders();
      loadStats();
    }
  }

  navTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-target");
      switchTab(target);
    });
  });

  // ----------------- THREE.JS 3D DRAPE SIMULATION -----------------
  let scene, camera, renderer, clothMesh, clothGeometry;
  let drapeContainer = document.getElementById("threeDrapeViewport");
  let isDragging = false;
  let previousMousePosition = { x: 0, y: 0 };
  let currentStiffness = 6.2;
  let clothColorHex = 0x1e293b;

  function initThreeDrape() {
    if (!drapeContainer || typeof THREE === "undefined") return;

    const width = drapeContainer.clientWidth || 340;
    const height = drapeContainer.clientHeight || 220;

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b0f17);

    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, 4.2);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    drapeContainer.appendChild(renderer.domElement);

    // Ambient & Directional Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffeaad, 1.2);
    dirLight1.position.set(2, 4, 3);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x75859d, 0.8);
    dirLight2.position.set(-3, -2, 2);
    scene.add(dirLight2);

    // Build Mannequin Torso Base
    const mannequinGroup = new THREE.Group();

    // Torso (Ellipsoidal Cylinder)
    const torsoGeo = new THREE.CylinderGeometry(0.55, 0.45, 1.6, 24);
    const torsoMat = new THREE.MeshStandardMaterial({
      color: 0x181c26,
      roughness: 0.8,
      metalness: 0.1,
    });
    const torsoMesh = new THREE.Mesh(torsoGeo, torsoMat);
    torsoMesh.position.y = -0.1;
    mannequinGroup.add(torsoMesh);

    // Neck
    const neckGeo = new THREE.CylinderGeometry(0.25, 0.28, 0.5, 18);
    const neckMesh = new THREE.Mesh(neckGeo, torsoMat);
    neckMesh.position.y = 0.85;
    mannequinGroup.add(neckMesh);

    // Stand Pedestal (Aged Brass)
    const poleGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.8, 12);
    const brassMat = new THREE.MeshStandardMaterial({
      color: 0xc89b3c,
      roughness: 0.35,
      metalness: 0.8,
    });
    const poleMesh = new THREE.Mesh(poleGeo, brassMat);
    poleMesh.position.y = -1.2;
    mannequinGroup.add(poleMesh);

    scene.add(mannequinGroup);

    // Draped Cloth Mesh
    const segmentsX = 36;
    const segmentsY = 36;
    clothGeometry = new THREE.PlaneGeometry(2.2, 2.4, segmentsX, segmentsY);

    const clothMaterial = new THREE.MeshStandardMaterial({
      color: clothColorHex,
      roughness: 0.7,
      metalness: 0.15,
      side: THREE.DoubleSide,
      wireframe: false,
    });

    clothMesh = new THREE.Mesh(clothGeometry, clothMaterial);
    clothMesh.position.set(0, 0.2, 0.38);
    clothMesh.rotation.x = -0.15;
    scene.add(clothMesh);

    // Drag Interaction
    const dom = renderer.domElement;
    dom.addEventListener("mousedown", (e) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener("mouseup", () => { isDragging = false; });

    dom.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      const deltaX = e.clientX - previousMousePosition.x;
      const deltaY = e.clientY - previousMousePosition.y;

      clothMesh.rotation.y += deltaX * 0.01;
      mannequinGroup.rotation.y += deltaX * 0.01;
      clothMesh.rotation.x += deltaY * 0.005;

      previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    // Touch support (mobile-first with passive listeners)
    dom.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1) {
        isDragging = true;
        previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      }
    }, { passive: true });

    window.addEventListener("touchend", () => { isDragging = false; }, { passive: true });

    dom.addEventListener("touchmove", (e) => {
      if (!isDragging || e.touches.length !== 1) return;
      const deltaX = e.touches[0].clientX - previousMousePosition.x;
      clothMesh.rotation.y += deltaX * 0.012;
      mannequinGroup.rotation.y += deltaX * 0.012;
      previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    }, { passive: true });

    // 60fps Drape Wave Animation
    let clock = new THREE.Clock();
    function animate() {
      requestAnimationFrame(animate);
      const time = clock.getElapsedTime() * 1.8;

      const positionAttr = clothGeometry.attributes.position;
      const waveAmplitude = (10.0 - currentStiffness) * 0.025;

      for (let i = 0; i < positionAttr.count; i++) {
        const x = positionAttr.getX(i);
        const y = positionAttr.getY(i);
        // Realistic drape physics displacement
        const zDisplacement =
          Math.sin(x * 3.5 + time) * waveAmplitude +
          Math.cos(y * 4.0 + time * 0.8) * (waveAmplitude * 0.7);
        positionAttr.setZ(i, zDisplacement);
      }
      positionAttr.needsUpdate = true;
      clothGeometry.computeVertexNormals();

      renderer.render(scene, camera);
    }
    animate();

    // Resize handler
    window.addEventListener("resize", () => {
      if (!drapeContainer || !renderer) return;
      const w = drapeContainer.clientWidth;
      const h = drapeContainer.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });
  }

  // ----------------- CUSTOMER INITIALIZATION -----------------
  async function loadCustomers() {
    try {
      const res = await fetch("/api/customers");
      const list = await res.json();
      state.customers = list;

      activeCustomerSelect.innerHTML = "";
      list.forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = `${c.name} (${c.city || "Mumbai"})`;
        activeCustomerSelect.appendChild(opt);
      });

      if (list.length > 0) {
        state.customerId = list[0].id;
        selectCustomer(list[0]);
      }
    } catch (err) {
      console.error("Failed to load customers:", err);
    }
  }

  function selectCustomer(cust) {
    state.customerId = cust.id;
    activeCustomerSelect.value = cust.id;
    naapCustomerName.textContent = cust.name;
    naapCustomerCity.textContent = cust.city ? `· ${cust.city}` : "";

    if (cust.latest_measurement) {
      const m = cust.latest_measurement;
      state.unit = m.unit || "in";
      state.easePreset = m.ease_preset || "barabar";
      for (const k in state.measurements) {
        if (m[k] !== undefined && m[k] !== null) {
          state.measurements[k] = parseFloat(m[k]);
        }
      }
      if (m.posture_notes) postureNoteInput.value = m.posture_notes;
    }

    updateMannequinNodeLabels();
    updateCaliperDrawer();
    updateEasePillUI();
  }

  activeCustomerSelect.addEventListener("change", (e) => {
    const custId = parseInt(e.target.value);
    const found = state.customers.find((c) => c.id === custId);
    if (found) selectCustomer(found);
  });

  // ----------------- NAAP / MANNEQUIN LOGIC -----------------
  function updateMannequinNodeLabels() {
    nodeButtons.forEach((btn) => {
      const pt = btn.getAttribute("data-point");
      const pill = btn.querySelector(".val-pill");
      if (pill && state.measurements[pt] !== undefined) {
        pill.textContent = state.measurements[pt].toFixed(1);
      }
    });
  }

  function updateCaliperDrawer() {
    const label = POINT_LABELS[state.activePoint] || state.activePoint.toUpperCase();
    activeCaliperTitle.textContent = label;
    const currentVal = state.measurements[state.activePoint] || 0;
    activeNumericInput.value = currentVal.toFixed(2);
    activeUnitSuffix.textContent = state.unit;
    cadUnitLabel.textContent = state.unit === "in" ? "INCHES" : "CENTIMETERS";
  }

  // Node Click Selection
  nodeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      nodeButtons.forEach((b) => {
        b.classList.remove("active", "z-10");
        const ring = b.querySelector(".node-ring");
        if (ring) ring.classList.add("hidden");
        const dot = b.querySelector(".node-dot");
        if (dot) {
          dot.className = "node-dot h-3 w-3 rounded-full bg-surface-container-highest shadow border border-white/60";
          dot.innerHTML = "";
        }
      });

      btn.classList.add("active", "z-10");
      const activeRing = btn.querySelector(".node-ring");
      if (activeRing) activeRing.classList.remove("hidden");
      const activeDot = btn.querySelector(".node-dot");
      if (activeDot) {
        activeDot.className = "node-dot h-4 w-4 rounded-full bg-secondary-container shadow border-2 border-secondary flex items-center justify-center";
        activeDot.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-on-secondary-container"></span>';
      }

      state.activePoint = btn.getAttribute("data-point");
      const arcD = btn.getAttribute("data-arc");
      if (arcD && bastingContourPath) {
        bastingContourPath.setAttribute("d", arcD);
      }

      updateCaliperDrawer();
    });
  });

  // Workshop Stepper Buttons
  stepButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const delta = parseFloat(btn.getAttribute("data-delta"));
      let val = (state.measurements[state.activePoint] || 0) + delta;
      val = Math.max(5, Math.min(80, val));
      state.measurements[state.activePoint] = parseFloat(val.toFixed(2));
      updateCaliperDrawer();
      updateMannequinNodeLabels();
    });
  });

  // Direct Numeric Input
  activeNumericInput.addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val)) {
      state.measurements[state.activePoint] = val;
      updateMannequinNodeLabels();
    }
  });

  // Unit Toggle (Inches <-> CM)
  btnUnitInch.addEventListener("click", () => {
    if (state.unit === "in") return;
    state.unit = "in";
    btnUnitInch.className = "px-2.5 py-1 rounded bg-surface text-primary text-xs font-bold shadow-sm";
    btnUnitCm.className = "px-2.5 py-1 rounded text-on-surface-variant hover:text-primary text-xs";
    // Convert cm to in
    for (const k in state.measurements) {
      state.measurements[k] = parseFloat((state.measurements[k] / 2.54).toFixed(2));
    }
    updateCaliperDrawer();
    updateMannequinNodeLabels();
  });

  btnUnitCm.addEventListener("click", () => {
    if (state.unit === "cm") return;
    state.unit = "cm";
    btnUnitCm.className = "px-2.5 py-1 rounded bg-surface text-primary text-xs font-bold shadow-sm";
    btnUnitInch.className = "px-2.5 py-1 rounded text-on-surface-variant hover:text-primary text-xs";
    // Convert in to cm
    for (const k in state.measurements) {
      state.measurements[k] = parseFloat((state.measurements[k] * 2.54).toFixed(2));
    }
    updateCaliperDrawer();
    updateMannequinNodeLabels();
  });

  // Angle Switcher
  angleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      angleButtons.forEach((b) => {
        b.className = "angle-btn py-2 px-2 rounded text-xs font-bold uppercase tracking-wider text-on-surface-variant hover:text-primary flex items-center justify-center gap-1.5 transition-all";
      });
      btn.className = "angle-btn py-2 px-2 rounded text-xs font-bold uppercase tracking-wider bg-surface text-primary shadow-sm flex items-center justify-center gap-1.5 transition-all";
      state.angle = btn.getAttribute("data-angle");
    });
  });

  // Ease Preset Buttons
  function updateEasePillUI() {
    easeButtons.forEach((btn) => {
      const e = btn.getAttribute("data-ease");
      if (e === state.easePreset) {
        btn.className = "ease-btn py-2 px-2 rounded-lg bg-secondary-container text-on-secondary-container border border-secondary shadow-sm flex flex-col items-center justify-center transition-all font-bold";
      } else {
        btn.className = "ease-btn py-2 px-2 rounded-lg bg-surface-container-low hover:bg-surface-container text-on-surface border border-outline-variant/30 flex flex-col items-center justify-center transition-all";
      }
    });
  }

  easeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      state.easePreset = btn.getAttribute("data-ease");
      updateEasePillUI();
    });
  });

  // Save Measurements to MySQL DB
  btnSaveNaap.addEventListener("click", async () => {
    try {
      const payload = {
        customer_id: state.customerId,
        unit: state.unit,
        ...state.measurements,
        ease_preset: state.easePreset,
        posture_notes: postureNoteInput.value,
      };

      const res = await fetch(`/api/customers/${state.customerId}/measurements`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        showToast("Naap docket saved in MySQL database!");
      }
    } catch (err) {
      console.error(err);
      showToast("Error saving measurement");
    }
  });

  // Transfer Measurements to Yardage Tab
  btnSendToYardage.addEventListener("click", () => {
    switchTab("view-kapda");
    showToast("Measurements pushed to Kapda Calculator!");
  });

  // ----------------- KAPDA / YARDAGE ENGINE -----------------
  async function runCalculation() {
    try {
      // Convert to inches for calculation engine if currently cm
      const measInInches = {};
      for (const k in state.measurements) {
        measInInches[k] = state.unit === "cm" ? state.measurements[k] / 2.54 : state.measurements[k];
      }

      const payload = {
        garment_style: state.garmentStyle,
        measurements: measInInches,
        fabric_width_inches: state.fabricWidth,
        pattern_type: state.patternType,
        fit_preset: state.easePreset,
        extra_options: {
          pleats: true,
          cuffs: false,
          double_breasted: false,
        },
      };

      const res = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      state.calculation = data;

      // Update UI with calculated figures
      calcTotalMeters.textContent = data.total_meters.toFixed(2);
      calcTotalGaj.textContent = `${data.total_gaj.toFixed(2)} Gaj`;
      calcTotalYards.textContent = `${data.total_yards.toFixed(2)} Yards`;

      calcEfficiency.textContent = `${data.efficiency_percent}%`;
      calcScrappageText.textContent = `Scrappage: ~${data.scrappage_meters.toFixed(2)}m (${100 - data.efficiency_percent}%)`;

      // Gauge offset animation
      const offset = 125.6 - 125.6 * (data.efficiency_percent / 100);
      gaugeRing.style.strokeDashoffset = offset.toString();

      // Breakdown
      breakdownJacket.textContent = `${data.breakdown.jacket_meters.toFixed(2)} m`;
      breakdownTrouser.textContent = `${data.breakdown.trouser_meters.toFixed(2)} m`;
      breakdownBuffer.textContent = `+${data.breakdown.buffer_meters.toFixed(2)} m`;
      breakdownLining.textContent = `${data.breakdown.lining_meters.toFixed(2)} m`;

      cuttingAdviceText.textContent = data.cutting_advice;
    } catch (err) {
      console.error("Yardage calculation failed:", err);
    }
  }

  // Garment Pill Switcher
  garmentTypeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      garmentTypeButtons.forEach((b) => {
        b.className = "garment-pill flex items-center gap-1.5 px-3 py-2 rounded bg-surface-container text-on-surface text-xs font-semibold whitespace-nowrap flex-shrink-0";
        const icon = b.querySelector(".material-symbols-outlined");
        if (icon && icon.textContent === "check_circle") icon.textContent = "dry_cleaning";
      });

      btn.className = "garment-pill active flex items-center gap-1.5 px-3 py-2 rounded bg-primary text-secondary-fixed text-xs font-bold whitespace-nowrap shadow flex-shrink-0";
      const icon = btn.querySelector(".material-symbols-outlined");
      if (icon) icon.textContent = "check_circle";

      state.garmentStyle = btn.getAttribute("data-garment");
      runCalculation();
    });
  });

  // Bolt Width Buttons
  boltButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      boltButtons.forEach((b) => {
        b.className = "bolt-btn py-2 px-1 text-center rounded bg-surface-container-low text-on-surface border border-outline-variant/30 text-xs";
      });
      btn.className = "bolt-btn active py-2 px-1 text-center rounded bg-primary text-secondary-fixed font-bold border border-primary shadow text-xs";

      const w = parseFloat(btn.getAttribute("data-width"));
      state.fabricWidth = w;
      if (w === 36) boltSelectedDesc.textContent = '36" Chhota Pana (Single Width Silk/Astar)';
      else if (w === 44) boltSelectedDesc.textContent = '44" Standard Pana (Shirting & Cotton)';
      else boltSelectedDesc.textContent = '58" - 60" Bada Pana (Suiting Standard)';

      runCalculation();
    });
  });

  // Pattern Select
  patternSelect.addEventListener("change", (e) => {
    state.patternType = e.target.value;
    runCalculation();
  });

  // Fabric Mill Select
  fabricMillSelect.addEventListener("change", (e) => {
    state.fabricMill = e.target.value;
  });

  // Hand Feel (3D Drape update)
  handfeelButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      handfeelButtons.forEach((b) => {
        b.className = "handfeel-btn py-1.5 px-2 rounded bg-surface-container-low hover:bg-surface-container text-xs font-semibold text-center border border-outline-variant/30";
      });
      btn.className = "handfeel-btn active py-1.5 px-2 rounded bg-primary text-secondary-fixed text-xs font-bold text-center border border-primary shadow-sm";

      currentStiffness = parseFloat(btn.getAttribute("data-stiffness") || "6.2");
      const hex = btn.getAttribute("data-color");
      const weight = btn.getAttribute("data-weight");
      clothPhysicsLabel.textContent = `${btn.textContent.split("\n")[0].trim()} ${weight}g/m`;

      if (clothMesh && hex) {
        clothMesh.material.color.set(hex);
      }
    });
  });

  // Action: Create Order & Open Parchi
  btnCreateOrderParchi.addEventListener("click", async () => {
    if (!state.calculation) await runCalculation();
    const calc = state.calculation;

    const fabricCost = calc.total_meters * 2450.0;
    const stitchingCost = 6500.0;
    const totalBill = fabricCost + stitchingCost + 1200.0; // lining + canvas
    const advancePaid = 10000.0;

    const payload = {
      customer_id: state.customerId,
      garment_style: state.garmentStyle,
      fabric_name: state.fabricMill,
      fabric_mill: "Raymond Savile Collection India",
      fabric_width_in: state.fabricWidth,
      fabric_pattern: state.patternType,
      total_meters: calc.total_meters,
      total_yards: calc.total_yards,
      total_gaj: calc.total_gaj,
      jacket_meters: calc.breakdown.jacket_meters,
      trouser_meters: calc.breakdown.trouser_meters,
      lining_meters: calc.breakdown.lining_meters,
      canvas_meters: calc.breakdown.canvas_meters,
      fabric_cost: fabricCost,
      stitching_cost: stitchingCost,
      total_bill: totalBill,
      advance_paid: advancePaid,
      balance_amount: totalBill - advancePaid,
      status: "Trial Scheduled",
      trial_stage: "Trial #1",
      trial_date: "12 Nov 2024",
      delivery_date: "18 Nov 2024",
      senior_cutter: "Master V. Sharma",
      workshop_section: "Marine Lines Workshop",
      notes: postureNoteInput.value,
    };

    try {
      const res = await fetch("/api/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const orderData = await res.json();
      state.currentOrder = orderData;
      populateParchiDocket(orderData);
      switchTab("view-parchi");
      showToast(`Katai Parchi generated: ${orderData.order_no}`);
    } catch (err) {
      console.error(err);
      showToast("Error creating order");
    }
  });

  // ----------------- KHATA / LEDGER LOGIC -----------------
  async function loadStats() {
    try {
      const res = await fetch("/api/stats");
      const d = await res.json();
      kpiActiveOrders.textContent = d.active_orders;
      kpiFabricMeters.innerHTML = `${d.fabric_in_atelier_meters}<span class="text-xs font-normal">m</span>`;
      kpiFabricValue.textContent = `₹${d.fabric_value_inr.toLocaleString("en-IN")} Thaan`;
      kpiUrgentFittings.textContent = d.urgent_fittings_week;

      const dialectBadge = document.getElementById("dbDialectBadge");
      if (dialectBadge) {
        dialectBadge.textContent = `${d.database_engine} Active`;
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function loadLedgerOrders(filter = "all", search = "") {
    try {
      let url = `/api/orders?status=${filter}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;

      const res = await fetch(url);
      const orders = await res.json();

      ledgerFeedContainer.innerHTML = "";
      if (orders.length === 0) {
        ledgerFeedContainer.innerHTML = `<div class="p-6 text-center text-xs text-on-surface-variant bg-surface-container-low rounded-xl">Koi order nahi mila. Naya order banayein.</div>`;
        return;
      }

      orders.forEach((o) => {
        const card = document.createElement("article");
        card.className = "bg-surface-container-lowest border border-outline-variant/50 rounded-xl overflow-hidden shadow-sm flex flex-col transition-all hover:shadow-md";

        card.innerHTML = `
          <div class="p-4 pb-3 flex items-start justify-between bg-surface-container-low border-b border-surface-container-high">
            <div class="flex flex-col min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-xs text-secondary font-bold font-mono uppercase">${o.order_no}</span>
                <span class="text-[9px] px-2 py-0.5 bg-secondary-fixed text-on-secondary-fixed font-bold uppercase rounded">${o.status}</span>
              </div>
              <h2 class="font-serif font-bold text-lg text-primary truncate mt-0.5">${o.customer_name}</h2>
              <span class="text-xs text-on-surface-variant">${o.garment_style}</span>
            </div>
            <div class="flex flex-col items-end flex-shrink-0">
              <span class="text-[10px] bg-secondary-container text-on-secondary-container px-2 py-0.5 rounded font-bold uppercase">${o.trial_stage}</span>
              <span class="text-[10px] text-secondary font-bold mt-1 flex items-center gap-1">
                <span class="material-symbols-outlined text-[13px]">schedule</span> ${o.trial_date || "Kal Subah"}
              </span>
            </div>
          </div>
          <div class="p-4 flex flex-col gap-3">
            <div class="flex items-center justify-between text-xs">
              <div class="flex flex-col">
                <span class="text-[10px] uppercase text-on-surface-variant">Fabric & Cut</span>
                <strong class="text-primary">${o.fabric_name}</strong>
              </div>
              <div class="text-right">
                <span class="text-[10px] uppercase text-on-surface-variant">Kul Kapda</span>
                <strong class="font-mono text-secondary block font-bold">${o.total_meters}m (${o.total_gaj} Gaj)</strong>
              </div>
            </div>
            <div class="p-2.5 bg-surface-container-low rounded-lg grid grid-cols-3 gap-2 text-xs text-center">
              <div>
                <span class="text-[9px] text-on-surface-variant uppercase block">Total Bill</span>
                <strong class="text-primary font-bold">₹${o.total_bill.toLocaleString("en-IN")}</strong>
              </div>
              <div>
                <span class="text-[9px] text-on-surface-variant uppercase block">Advance</span>
                <strong class="text-secondary font-bold">₹${o.advance_paid.toLocaleString("en-IN")}</strong>
              </div>
              <div>
                <span class="text-[9px] text-on-surface-variant uppercase block">Balance Baaki</span>
                <strong class="${o.balance_amount > 0 ? "text-red-700" : "text-green-700"} font-bold">₹${o.balance_amount.toLocaleString("en-IN")}</strong>
              </div>
            </div>
            <button class="btn-view-docket w-full py-2 rounded bg-surface-container-high hover:bg-primary hover:text-secondary-fixed text-primary text-xs font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-1.5" data-order-id="${o.id}">
              <span class="material-symbols-outlined text-[16px]">receipt_long</span>
              <span>Katai Parchi Dekho</span>
            </button>
          </div>
        `;

        card.querySelector(".btn-view-docket").addEventListener("click", () => {
          populateParchiDocket(o);
          switchTab("view-parchi");
        });

        ledgerFeedContainer.appendChild(card);
      });
    } catch (err) {
      console.error(err);
    }
  }

  // Filter Chips in Khata
  ledgerFilterChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      ledgerFilterChips.forEach((c) => {
        c.className = "filter-chip flex-shrink-0 px-3 py-1.5 bg-surface-container-high text-on-surface-variant text-xs font-semibold uppercase tracking-wider rounded border border-outline-variant/30";
      });
      chip.className = "filter-chip active flex-shrink-0 px-3 py-1.5 bg-primary text-secondary-fixed text-xs font-bold uppercase tracking-wider rounded";

      const f = chip.getAttribute("data-filter");
      loadLedgerOrders(f, ledgerSearchInput.value);
    });
  });

  // Search in Khata
  ledgerSearchInput.addEventListener("input", (e) => {
    const activeChip = document.querySelector(".filter-chip.active");
    const f = activeChip ? activeChip.getAttribute("data-filter") : "all";
    loadLedgerOrders(f, e.target.value);
  });

  // ----------------- PARCHI / DOCKET LOGIC -----------------
  function populateParchiDocket(o) {
    state.currentOrder = o;
    parchiOrderNoBadge.textContent = `ORDER #${o.order_no}`;
    parchiClientName.textContent = o.customer_name;
    parchiClientPhone.textContent = o.customer_phone || "+91 98201 44892";
    parchiTrialDate.textContent = o.trial_date || "12 Nov 2024";
    parchiDeliveryDate.textContent = o.delivery_date || "18 Nov 2024";
    parchiFabricName.textContent = `${o.fabric_name} (${o.fabric_width_in}" Pana)`;
    parchiFabricMeters.textContent = `${o.total_meters} Meters (${o.total_gaj} Gaj)`;

    parchiJacketCloth.textContent = `${o.jacket_meters}m`;
    parchiTrouserCloth.textContent = `${o.trouser_meters}m`;
    parchiLiningCloth.textContent = `${o.lining_meters}m`;
    parchiCanvasCloth.textContent = `${o.canvas_meters}m`;

    parchiClothCost.textContent = `₹${o.fabric_cost.toLocaleString("en-IN")}`;
    parchiStitchingCost.textContent = `₹${o.stitching_cost.toLocaleString("en-IN")}`;
    parchiTotalBill.textContent = `₹${o.total_bill.toLocaleString("en-IN")}`;
    parchiAdvancePaid.textContent = `₹${o.advance_paid.toLocaleString("en-IN")}`;
    parchiBalanceDue.textContent = `₹${o.balance_amount.toLocaleString("en-IN")}`;

    // Fill measurements matrix
    parchiMeasurementsMatrix.innerHTML = "";
    for (const k in state.measurements) {
      const cell = document.createElement("div");
      cell.className = "bg-surface-container-low p-2 rounded flex flex-col";
      cell.innerHTML = `
        <span class="text-[9px] uppercase tracking-wider text-on-surface-variant truncate">${k.replace("_", " ")}</span>
        <strong class="text-primary font-serif font-bold text-sm mt-0.5">${state.measurements[k]}"</strong>
      `;
      parchiMeasurementsMatrix.appendChild(cell);
    }
  }

  // Print Action
  btnPrintDocket.addEventListener("click", () => {
    window.print();
  });

  // WhatsApp Share Action
  btnShareDocket.addEventListener("click", () => {
    const o = state.currentOrder || {
      order_no: "BY-2024-89",
      customer_name: "Vikram Singhania",
      total_meters: 3.45,
      total_bill: 16935,
    };
    const phone = (o.customer_phone || "").replace(/[^0-9]/g, "");
    const msg = `Namaskar ${o.customer_name} ji! Bombay Master Tailors se aapka Katai Parchi #${o.order_no} taiyar hai. Kul kapda: ${o.total_meters}m. Total bill: ₹${o.total_bill}. Shukriya!`;
    const url = `https://wa.me/${phone ? phone : ""}?text=${encodeURIComponent(msg)}`;
    window.open(url, "_blank");
  });

  // ----------------- MODAL: CREATE CUSTOMER -----------------
  btnOpenNewCustomerModal.addEventListener("click", () => {
    newCustomerModal.classList.remove("hidden");
  });

  function closeCustModal() {
    newCustomerModal.classList.add("hidden");
  }
  btnCloseCustomerModal.addEventListener("click", closeCustModal);
  btnCancelCustomerModal.addEventListener("click", closeCustModal);

  formNewCustomer.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("newCustName").value.trim();
    const phone = document.getElementById("newCustPhone").value.trim();
    const city = document.getElementById("newCustCity").value.trim();
    const notes = document.getElementById("newCustNotes").value.trim();

    try {
      const res = await fetch("/api/customers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, city, notes }),
      });

      const newCust = await res.json();
      state.customers.push(newCust);

      const opt = document.createElement("option");
      opt.value = newCust.id;
      opt.textContent = `${newCust.name} (${newCust.city || "Mumbai"})`;
      activeCustomerSelect.appendChild(opt);

      selectCustomer(newCust);
      closeCustModal();
      showToast(`Grahak ${newCust.name} successfully registered!`);
      switchTab("view-naap");
    } catch (err) {
      console.error(err);
      showToast("Error adding customer");
    }
  });

  // ----------------- APP INITIALIZATION -----------------
  window.addEventListener("DOMContentLoaded", async () => {
    initThreeDrape();
    await loadCustomers();
    await loadStats();
    await runCalculation();
  });
})();

