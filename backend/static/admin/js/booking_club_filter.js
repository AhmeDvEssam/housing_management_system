window.addEventListener('load', function() {
    console.log("[Cascading Dropdowns] Window loaded, waiting for Jazzmin...");
    
    setTimeout(function() {
        console.log("[Cascading Dropdowns] Initializing...");
        
        var clubEl = document.getElementById('id_club');
        var buildingEl = document.getElementById('id_building');
        var unitEl = document.getElementById('id_unit');
        var unitsEl = document.getElementById('id_units');
        var clsEl = document.getElementById('id_classification');
        var typeEl = document.getElementById('id_unit_type');

        if (!clubEl || !buildingEl) {
            console.error("[Cascading Dropdowns] Missing required form fields!");
            return;
        }

        // 1. Fully neutralize Select2 on building and unit
        var jqVariables = [window.jQuery, window.$, window.django ? window.django.jQuery : null];
        jqVariables.forEach(function($jq) {
            if ($jq) {
                try {
                    if (buildingEl && $jq(buildingEl).data('select2')) $jq(buildingEl).select2('destroy');
                    if (unitEl && $jq(unitEl).data('select2')) $jq(unitEl).select2('destroy');
                } catch(e) {}
            }
        });
        
        // Remove any leftover Select2 junk
        var s2containers = document.querySelectorAll('#id_building + .select2-container, #id_unit + .select2-container, #id_units + .select2-container');
        s2containers.forEach(function(c) { c.remove(); });

        // Apply native styling
        var styleNative = function(el) {
            if (!el) return;
            el.classList.add('form-control');
        };
        styleNative(buildingEl);
        if (unitEl) styleNative(unitEl);

        // 2. Fetch API Helpers
        function setSelectOptions(el, defaultText, optionsMap) {
            if (!el) return;
            el.innerHTML = '<option value="">-- ' + defaultText + ' --</option>';
            optionsMap.forEach(function(opt) {
                var o = document.createElement('option');
                o.value = opt.id;
                o.textContent = opt.name;
                el.appendChild(o);
            });
        }

        function loadBuildings(clubId, callback) {
            setSelectOptions(buildingEl, "اختر المبنى", []);
            setSelectOptions(unitEl, "اختر الوحدة", []);
            if(clsEl) clsEl.value = '';
            if(typeEl) typeEl.value = '';

            if (!clubId) {
                if (callback) callback();
                return;
            }

            console.log("[Cascading Dropdowns] Fetching buildings for club:", clubId);
            fetch('/admin/bookings/booking/get-buildings-for-club/?club_id=' + clubId)
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    setSelectOptions(buildingEl, "اختر المبنى", data.buildings || []);
                    if (callback) callback();
                })
                .catch(function(err) { console.error("Error loading buildings:", err); });
        }

        function loadUnits(buildingId, callback) {
            setSelectOptions(unitEl, "اختر الوحدة", []);
            if(clsEl) clsEl.value = '';
            if(typeEl) typeEl.value = '';

            if (!buildingId) {
                if (callback) callback();
                return;
            }

            console.log("[Cascading Dropdowns] Fetching units for building:", buildingId);
            fetch('/admin/bookings/booking/get-units-for-building/?building_id=' + buildingId)
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    setSelectOptions(unitEl, "اختر الوحدة", data.units || []);
                    if (callback) callback();
                })
                .catch(function(err) { console.error("Error loading units:", err); });
        }

        function loadClassification(unitId) {
            if (!unitId) {
                if(clsEl) clsEl.value = '';
                if(typeEl) typeEl.value = '';
                return;
            }

            fetch('/admin/bookings/booking/get-unit-details/?unit_id=' + unitId)
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if(clsEl) clsEl.value = data.classification || '';
                    if(typeEl) typeEl.value = data.unit_type || '';
                })
                .catch(function(err) { console.error("Error loading classification:", err); });
        }

        // 3. Event Listeners
        var clubChanged = function(val) {
            if (clubEl.dataset.prevValue === val) return;
            clubEl.dataset.prevValue = val;
            loadBuildings(val);
        };

        jqVariables.forEach(function($jq) {
            if ($jq) {
                $jq(clubEl).on('change select2:select', function(e) {
                    clubChanged(e.target.value);
                });
            }
        });
        clubEl.addEventListener('change', function(e) {
            clubChanged(e.target.value);
        });

        buildingEl.addEventListener('change', function(e) {
            if (!isBulkMode()) {
                loadUnits(e.target.value);
            }
        });

        if (unitEl) {
            unitEl.addEventListener('change', function(e) {
                loadClassification(e.target.value);
            });
        }

        // ========================================
        // BULK INSERT MODE (Cart System)
        // ========================================
        var selectedUnits = {}; // { id: { name, building, club } }

        function isBulkMode() {
            var toggle = document.getElementById('bulkModeToggle');
            return toggle && toggle.checked;
        }

        // Only build bulk UI if 'units' field exists (adding mode)
        if (unitsEl) {
            // Find the unit row and units row
            var unitRow = unitEl ? unitEl.closest('.form-group') : null;
            var unitsRow = unitsEl.closest('.form-group');

            // Hide the raw units select (we manage it via JS)
            if (unitsRow) unitsRow.style.display = 'none';

            // Create the bulk mode toggle + cart UI
            var bulkContainer = document.createElement('div');
            bulkContainer.id = 'bulkModeContainer';
            bulkContainer.innerHTML = '' +
                '<div style="margin: 8px 0; padding: 12px 16px; background: linear-gradient(135deg, #e8f5e9, #f1f8e9); border-radius: 10px; border: 1px solid #c8e6c9;">' +
                '  <label style="cursor:pointer; font-weight:bold; display:flex; align-items:center; gap:10px; margin:0; font-size:15px; color:#2e7d32;">' +
                '    <input type="checkbox" id="bulkModeToggle" style="width:20px; height:20px; accent-color:#2e7d32;">' +
                '    <span>🔄 تفعيل الحجز الجماعي (Bulk Insert)</span>' +
                '  </label>' +
                '</div>' +
                '<div id="bulkArea" style="display:none; margin: 10px 0;">' +
                '  <div style="border: 2px solid #1976d2; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">' +
                '    <div style="background: linear-gradient(135deg, #1976d2, #1565c0); padding: 12px 16px; color: white; font-weight: bold; font-size: 14px;">' +
                '      📦 اختر الوحدات من المبنى المحدد' +
                '    </div>' +
                '    <div style="padding: 12px 16px;">' +
                '      <div id="bulkUnitsList" style="display:flex; flex-wrap:wrap; gap:6px; min-height:40px; align-items:center;">' +
                '        <span style="color:#999; font-size:13px;">اختر مبنى أولاً...</span>' +
                '      </div>' +
                '      <div style="margin-top:10px; display:flex; gap:8px; align-items:center;">' +
                '        <button type="button" id="addToCartBtn" style="background:#1976d2; color:white; border:none; padding:8px 20px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:13px;">➕ إضافة المحدد</button>' +
                '        <button type="button" id="selectAllUnitsBtn" style="background:#7b1fa2; color:white; border:none; padding:8px 16px; border-radius:8px; cursor:pointer; font-size:13px;">✅ تحديد الكل</button>' +
                '      </div>' +
                '    </div>' +
                '  </div>' +
                '  <div id="cartSection" style="margin-top: 12px; border: 2px solid #388e3c; border-radius: 12px; overflow:hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">' +
                '    <div style="background: linear-gradient(135deg, #388e3c, #2e7d32); padding: 12px 16px; color: white; font-weight: bold; font-size: 14px;">' +
                '      🛒 الوحدات المختارة (<span id="cartCount">0</span>)' +
                '    </div>' +
                '    <div id="cartItems" style="padding: 12px 16px; min-height: 40px; display:flex; flex-wrap:wrap; gap:6px; align-items:center;">' +
                '      <span style="color:#999; font-size:13px;">لم يتم اختيار وحدات بعد...</span>' +
                '    </div>' +
                '    <div id="cartClearRow" style="display:none; padding:8px 16px; border-top: 1px solid #e0e0e0;">' +
                '      <button type="button" id="clearCartBtn" style="background:#c62828; color:white; border:none; padding:6px 16px; border-radius:8px; cursor:pointer; font-size:12px;">🗑️ مسح الكل</button>' +
                '    </div>' +
                '  </div>' +
                '</div>';

            // Insert after the building row
            var buildingRow = buildingEl.closest('.form-group');
            if (buildingRow) {
                buildingRow.parentNode.insertBefore(bulkContainer, buildingRow.nextSibling);
            }

            // Toggle bulk mode
            document.getElementById('bulkModeToggle').addEventListener('change', function() {
                var bulkArea = document.getElementById('bulkArea');
                if (this.checked) {
                    bulkArea.style.display = 'block';
                    if (unitEl) { unitEl.disabled = true; unitEl.style.opacity = '0.5'; }
                    // Load units for current building
                    if (buildingEl.value) loadBulkUnits(buildingEl.value);
                } else {
                    bulkArea.style.display = 'none';
                    if (unitEl) { unitEl.disabled = false; unitEl.style.opacity = '1'; }
                }
            });

            // Load bulk units as checkboxes
            function loadBulkUnits(buildingId) {
                var listEl = document.getElementById('bulkUnitsList');
                listEl.innerHTML = '<span style="color:#999; font-size:13px;">⏳ جاري التحميل...</span>';

                if (!buildingId) {
                    listEl.innerHTML = '<span style="color:#999; font-size:13px;">اختر مبنى أولاً...</span>';
                    return;
                }

                fetch('/admin/bookings/booking/get-units-for-building/?building_id=' + buildingId)
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        listEl.innerHTML = '';
                        var units = data.units || [];
                        if (units.length === 0) {
                            listEl.innerHTML = '<span style="color:#999; font-size:13px;">لا توجد وحدات متاحة في هذا المبنى</span>';
                            return;
                        }
                        units.forEach(function(u) {
                            if (selectedUnits[u.id]) return; // Already in cart
                            var label = document.createElement('label');
                            label.style.cssText = 'display:inline-flex; align-items:center; gap:5px; padding:6px 12px; background:#e3f2fd; border-radius:20px; cursor:pointer; font-size:13px; border:1px solid #90caf9; transition: all 0.2s; user-select:none;';
                            label.innerHTML = '<input type="checkbox" class="bulk-unit-cb" value="' + u.id + '" data-name="' + u.name + '" style="accent-color:#1976d2; width:16px; height:16px;"> ' + u.name;
                            label.addEventListener('mouseenter', function() { this.style.background = '#bbdefb'; });
                            label.addEventListener('mouseleave', function() { this.style.background = '#e3f2fd'; });
                            listEl.appendChild(label);
                        });
                        if (!listEl.children.length) {
                            listEl.innerHTML = '<span style="color:#999; font-size:13px;">كل الوحدات مضافة بالفعل ✓</span>';
                        }
                    })
                    .catch(function(err) {
                        listEl.innerHTML = '<span style="color:red;">خطأ في التحميل</span>';
                    });
            }

            // Add to cart
            document.getElementById('addToCartBtn').addEventListener('click', function() {
                var checkboxes = document.querySelectorAll('#bulkUnitsList .bulk-unit-cb:checked');
                if (checkboxes.length === 0) return;

                var buildingName = buildingEl.options[buildingEl.selectedIndex] ? buildingEl.options[buildingEl.selectedIndex].text : '';
                var clubName = clubEl.options[clubEl.selectedIndex] ? clubEl.options[clubEl.selectedIndex].text : '';

                checkboxes.forEach(function(cb) {
                    selectedUnits[cb.value] = {
                        name: cb.dataset.name,
                        building: buildingName.replace('-- ', '').replace(' --', ''),
                        club: clubName.replace('-- ', '').replace(' --', '')
                    };
                });

                renderCart();
                if (buildingEl.value) loadBulkUnits(buildingEl.value);
            });

            // Select all
            document.getElementById('selectAllUnitsBtn').addEventListener('click', function() {
                var checkboxes = document.querySelectorAll('#bulkUnitsList .bulk-unit-cb');
                checkboxes.forEach(function(cb) { cb.checked = true; });
            });

            // Clear cart
            document.getElementById('clearCartBtn').addEventListener('click', function() {
                selectedUnits = {};
                renderCart();
                if (buildingEl.value) loadBulkUnits(buildingEl.value);
            });

            // Render cart
            function renderCart() {
                var cartEl = document.getElementById('cartItems');
                var countEl = document.getElementById('cartCount');
                var clearRow = document.getElementById('cartClearRow');

                cartEl.innerHTML = '';
                var ids = Object.keys(selectedUnits);
                countEl.textContent = ids.length;
                clearRow.style.display = ids.length > 0 ? 'block' : 'none';

                // Update hidden select
                unitsEl.innerHTML = '';
                ids.forEach(function(id) {
                    var opt = document.createElement('option');
                    opt.value = id;
                    opt.selected = true;
                    opt.textContent = selectedUnits[id].name;
                    unitsEl.appendChild(opt);
                });

                if (ids.length === 0) {
                    cartEl.innerHTML = '<span style="color:#999; font-size:13px;">لم يتم اختيار وحدات بعد...</span>';
                    return;
                }

                ids.forEach(function(id) {
                    var tag = document.createElement('span');
                    tag.style.cssText = 'display:inline-flex; align-items:center; gap:6px; padding:6px 12px; background:#c8e6c9; border-radius:20px; font-size:13px; border:1px solid #81c784; animation: fadeIn 0.3s;';
                    tag.innerHTML = '<strong>' + selectedUnits[id].name + '</strong> <small style="opacity:0.7;">(' + selectedUnits[id].building + ')</small>';

                    var removeBtn = document.createElement('button');
                    removeBtn.type = 'button';
                    removeBtn.dataset.id = id;
                    removeBtn.style.cssText = 'border:none; background:#e53935; color:white; cursor:pointer; font-weight:bold; width:20px; height:20px; border-radius:50%; font-size:12px; line-height:20px; padding:0; text-align:center;';
                    removeBtn.textContent = '×';
                    removeBtn.addEventListener('click', function() {
                        delete selectedUnits[this.dataset.id];
                        renderCart();
                        if (buildingEl.value) loadBulkUnits(buildingEl.value);
                    });
                    tag.appendChild(removeBtn);
                    cartEl.appendChild(tag);
                });
            }

            // Hook building change for bulk mode
            buildingEl.addEventListener('change', function() {
                if (isBulkMode()) {
                    loadBulkUnits(this.value);
                }
            });
        }

        // --- Period auto-fill dates ---
        var periodEl = document.getElementById('id_period');
        if (periodEl) {
            function fillDatesFromPeriod(periodId) {
                console.log("[Period] Fetching dates for period:", periodId);
                if (!periodId) return;
                
                fetch('/admin/bookings/booking/get-period-dates/?period_id=' + periodId)
                    .then(function(res) { return res.json(); })
                    .then(function(data) {
                        console.log("[Period] Got dates:", data);
                        if (data.start_date && data.end_date) {
                            var startEl = document.getElementById('id_start_date') 
                                       || document.querySelector('input[name="start_date"]');
                            var endEl = document.getElementById('id_end_date')
                                     || document.querySelector('input[name="end_date"]');
                            
                            if (startEl) {
                                startEl.value = data.start_date;
                                startEl.dispatchEvent(new Event('change', { bubbles: true }));
                                startEl.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                            if (endEl) {
                                endEl.value = data.end_date;
                                endEl.dispatchEvent(new Event('change', { bubbles: true }));
                                endEl.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        }
                    })
                    .catch(function(err) { console.error("[Period] Error:", err); });
            }

            periodEl.addEventListener('change', function(e) {
                fillDatesFromPeriod(e.target.value);
            });

            jqVariables.forEach(function($jq) {
                if ($jq) {
                    try {
                        $jq(periodEl).on('select2:select', function(e) {
                            fillDatesFromPeriod(periodEl.value);
                        });
                    } catch(ex) {}
                }
            });
        }

        // --- Live Price Calculation ---
        var unitElPrice = document.getElementById('id_unit');
        var startElPrice = document.getElementById('id_start_date') || document.querySelector('input[name="start_date"]');
        var endElPrice = document.getElementById('id_end_date') || document.querySelector('input[name="end_date"]');
        var isPlus50El = document.getElementById('id_is_plus_50');
        var totalPriceEl = document.getElementById('id_total_price');

        // Track last known values to avoid unnecessary API calls
        var lastPriceParams = '';

        function calculatePrice() {
            if (!totalPriceEl) return;
            var unit_id = unitElPrice ? unitElPrice.value : null;
            var start_date = startElPrice ? startElPrice.value : null;
            var end_date = endElPrice ? endElPrice.value : null;
            
            var personTypeChecked = document.querySelector('input[name="person_type"]:checked');
            var person_type = personTypeChecked ? personTypeChecked.value : null;
            var is_plus_50 = isPlus50El ? isPlus50El.checked : false;

            if (!unit_id || !start_date || !end_date || !person_type) {
                console.log("[Price] Skipped - missing:", 
                    !unit_id ? "unit" : "", 
                    !start_date ? "start" : "", 
                    !end_date ? "end" : "", 
                    !person_type ? "person_type" : "");
                return;
            }

            var discount_percentage = document.getElementById('id_discount_percentage') ? document.getElementById('id_discount_percentage').value : '';
            // Avoid duplicate API calls for same params
            var currentParams = unit_id + '|' + start_date + '|' + end_date + '|' + person_type + '|' + is_plus_50 + '|' + discount_percentage;
            if (currentParams === lastPriceParams) return;
            lastPriceParams = currentParams;

            console.log("[Price] Calculating:", {unit_id: unit_id, start: start_date, end: end_date, person: person_type, plus50: is_plus_50});

            var url = '/api/calculate-price/?unit_id=' + unit_id + 
                      '&start_date=' + start_date + 
                      '&end_date=' + end_date + 
                      '&person_type=' + person_type + 
                      '&is_plus_50=' + is_plus_50;

            fetch(url)
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    console.log("[Price] Result:", data);
                    if (data.total_price !== undefined) {
                        var base_price = data.base_price || data.total_price;
                        
                        // Count active companions (not marked for deletion and has a name entered)
                        var companionRows = document.querySelectorAll('.dynamic-companions:not(.deleted)');
                        var numCompanions = 0;
                        companionRows.forEach(function(row) {
                            var deleteInput = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
                            if (!deleteInput || !deleteInput.checked) {
                                // Make sure it's not a template row (has id containing __prefix__)
                                if (row.id && row.id.indexOf('__prefix__') === -1) {
                                    // Check if the companion actually has a name entered
                                    var nameInput = row.querySelector('input[name$="-name"]');
                                    var idInput = row.querySelector('input[name$="-national_id"]');
                                    var hasData = false;
                                    if (nameInput && nameInput.value.trim() !== '') hasData = true;
                                    if (idInput && idInput.value.trim() !== '') hasData = true;
                                    
                                    if (hasData) {
                                        numCompanions++;
                                    }
                                }
                            }
                        });

                        var final_total = base_price;
                        if (numCompanions > 0) {
                            final_total = base_price + (base_price * 0.375 * numCompanions);
                        }
                        
                        var discountEl = document.getElementById('id_discount_percentage');
                        if (discountEl && discountEl.value && !isNaN(discountEl.value)) {
                            var discountVal = parseFloat(discountEl.value);
                            if (discountVal > 0) {
                                final_total = final_total * (1 - (discountVal / 100));
                            }
                        }

                        totalPriceEl.value = final_total;

                        // Inject or update hidden base_price input so backend receives it
                        var basePriceInput = document.getElementById('id_base_price');
                        if (!basePriceInput) {
                            basePriceInput = document.createElement('input');
                            basePriceInput.type = 'hidden';
                            basePriceInput.id = 'id_base_price';
                            basePriceInput.name = 'base_price';
                            totalPriceEl.parentNode.appendChild(basePriceInput);
                        }
                        basePriceInput.value = base_price;

                        // Flash green to show it updated
                        totalPriceEl.style.transition = 'background-color 0.3s';
                        totalPriceEl.style.backgroundColor = '#d4edda';
                        setTimeout(function(){
                            totalPriceEl.style.backgroundColor = '#e9ecef';
                        }, 500);
                    }
                    if (data.error) {
                        console.warn("[Price] API Warning:", data.error);
                    }
                })
                .catch(function(err) { console.error("[Price Calculation Error]", err); });
        }

        // Also recalculate price when companions are added or deleted
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // Added a new companion row
                    lastPriceParams = '';
                    calculatePrice();
                }
            });
        });
        
        var companionsInlineGroup = document.getElementById('companions-group');
        if (companionsInlineGroup) {
            observer.observe(companionsInlineGroup, { childList: true, subtree: true });
        }
        
        // Listen to delete checkbox and input changes in companions
        document.body.addEventListener('change', function(e) {
            if (e.target && (e.target.matches('.dynamic-companions input[type="checkbox"][name$="-DELETE"]') || e.target.matches('.dynamic-companions input'))) {
                lastPriceParams = '';
                calculatePrice();
            }
        });
        document.body.addEventListener('input', function(e) {
            if (e.target && e.target.matches('.dynamic-companions input')) {
                lastPriceParams = '';
                calculatePrice();
            }
        });

        // 1. Standard DOM events
        var isPlus50El = document.getElementById('id_is_plus_50');
        var discountPercentageEl = document.getElementById('id_discount_percentage');
        var priceInputs = [unitElPrice, startElPrice, endElPrice, isPlus50El, discountPercentageEl];
        priceInputs.forEach(function(el) {
            if (el) {
                el.addEventListener('change', calculatePrice);
                el.addEventListener('input', calculatePrice);
                if (el !== isPlus50El) {
                    el.addEventListener('blur', calculatePrice);
                }
                if (el === discountPercentageEl) {
                    el.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' || e.keyCode === 13) {
                            e.preventDefault();
                            return false;
                        }
                    });
                }
            }
        });
        
        // 2. Person type radio buttons (event delegation)
        document.body.addEventListener('change', function(e) {
            if (e.target && e.target.name === 'person_type') {
                lastPriceParams = ''; // Force recalculation
                calculatePrice();
            }
        });

        // 3. jQuery datepicker events (Jazzmin uses Bootstrap/jQuery datepickers)
        jqVariables.forEach(function($jq) {
            if ($jq) {
                try {
                    // Bootstrap datepicker events
                    if (startElPrice) {
                        $jq(startElPrice).on('dp.change changeDate change', function() { 
                            lastPriceParams = ''; calculatePrice(); 
                        });
                    }
                    if (endElPrice) {
                        $jq(endElPrice).on('dp.change changeDate change', function() { 
                            lastPriceParams = ''; calculatePrice(); 
                        });
                    }
                } catch(ex) { console.log("[Price] jQuery datepicker hook error:", ex); }
            }
        });

        // 4. Polling: check every 500ms if date values changed (catches ANY method of input)
        var lastStartVal = startElPrice ? startElPrice.value : '';
        var lastEndVal = endElPrice ? endElPrice.value : '';
        var lastUnitVal = unitElPrice ? unitElPrice.value : '';
        
        setInterval(function() {
            var currStart = startElPrice ? startElPrice.value : '';
            var currEnd = endElPrice ? endElPrice.value : '';
            var currUnit = unitElPrice ? unitElPrice.value : '';
            
            if (currStart !== lastStartVal || currEnd !== lastEndVal || currUnit !== lastUnitVal) {
                lastStartVal = currStart;
                lastEndVal = currEnd;
                lastUnitVal = currUnit;
                lastPriceParams = ''; // Force recalculation
                calculatePrice();
            }
        }, 500);

        // 4. Initial Bootstrap
        var initialClub = clubEl.value;
        var initialBuilding = buildingEl.value;
        var initialUnit = unitEl ? unitEl.value : '';
        clubEl.dataset.prevValue = initialClub;

        if (initialClub && buildingEl.options.length <= 1) {
            loadBuildings(initialClub, function() {
                if (initialBuilding) {
                    buildingEl.value = initialBuilding;
                    loadUnits(initialBuilding, function() {
                        if (initialUnit && unitEl) {
                            unitEl.value = initialUnit;
                            loadClassification(initialUnit);
                            calculatePrice();
                        }
                    });
                }
            });
        } else if (initialUnit) {
            loadClassification(initialUnit);
            calculatePrice();
        }

    }, 800);
});
