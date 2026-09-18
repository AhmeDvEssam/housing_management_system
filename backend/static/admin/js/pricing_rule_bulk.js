window.addEventListener('load', function() {
    console.log("[Pricing Bulk] Initializing...");

    // Find the elements
    var clubEl = document.getElementById('id_club');
    var buildingsEl = document.getElementById('id_buildings');
    var unitsEl = document.getElementById('id_units');
    var monthsEl = document.getElementById('id_months');

    if (!clubEl) return;

    // Hide original multiselects and their labels/containers
    var hideRow = function(el) {
        if (!el) return;
        var row = el.closest('.form-row');
        if (row) row.style.display = 'none';
    };
    
    hideRow(buildingsEl);
    hideRow(unitsEl);
    hideRow(monthsEl);

    // Create Bulk UI Container
    var bulkContainer = document.createElement('div');
    bulkContainer.id = 'bulkPricingContainer';
    bulkContainer.style.cssText = 'margin: 20px 0; padding: 20px; background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px;';

    bulkContainer.innerHTML = `
        <h3 style="margin-top:0; border-bottom: 1px solid #ccc; padding-bottom: 10px;">التحديد السريع (اختياري)</h3>
        
        <div style="margin-bottom: 20px;">
            <h4 style="color: #1976d2;">1. الأشهر المطبق عليها السعر</h4>
            <div id="monthsGrid" style="display: flex; gap: 10px; flex-wrap: wrap;">
                ${Array.from({length: 12}, (_, i) => i + 1).map(m => `
                    <label style="background: #e3f2fd; padding: 5px 12px; border-radius: 20px; cursor: pointer; border: 1px solid #90caf9;">
                        <input type="checkbox" class="month-cb" value="${m}"> شهر ${m}
                    </label>
                `).join('')}
            </div>
            <small style="color: #666;">* إذا لم تختر أي شهر، سيطبق السعر طوال العام.</small>
        </div>

        <div style="margin-bottom: 20px;">
            <h4 style="color: #388e3c;">2. العمارات المطبق عليها</h4>
            <div id="buildingsGrid" style="display: flex; gap: 10px; flex-wrap: wrap; min-height: 40px; padding: 10px; background: white; border: 1px dashed #ccc; border-radius: 4px;">
                <span style="color: #999;">يرجى اختيار النادي أولاً...</span>
            </div>
            <small style="color: #666;">* إذا لم تختر أي عمارة، سيطبق السعر على كل عمارات النادي.</small>
        </div>

        <div>
            <h4 style="color: #f57c00;">3. الوحدات المطبق عليها</h4>
            <div id="unitsGrid" style="display: flex; gap: 10px; flex-wrap: wrap; min-height: 40px; padding: 10px; background: white; border: 1px dashed #ccc; border-radius: 4px;">
                <span style="color: #999;">يرجى اختيار عمارات أولاً لعرض وحداتها...</span>
            </div>
            <small style="color: #666;">* إذا لم تختر أي وحدة، سيطبق السعر على كل وحدات العمارات المحددة أعلاه.</small>
        </div>
    `;

    // Insert after Club row
    var clubRow = clubEl.closest('.form-row');
    clubRow.parentNode.insertBefore(bulkContainer, clubRow.nextSibling);

    // Initial state loading
    var selectedMonths = monthsEl.value ? monthsEl.value.split(',') : [];
    document.querySelectorAll('.month-cb').forEach(cb => {
        if (selectedMonths.includes(cb.value)) cb.checked = true;
        cb.addEventListener('change', updateHiddenMonths);
    });

    function updateHiddenMonths() {
        var checked = Array.from(document.querySelectorAll('.month-cb:checked')).map(cb => cb.value);
        monthsEl.value = checked.join(',');
    }

    var buildingsGrid = document.getElementById('buildingsGrid');
    var unitsGrid = document.getElementById('unitsGrid');

    function fetchBuildings(clubId) {
        buildingsGrid.innerHTML = '<span style="color: #999;">جاري التحميل...</span>';
        unitsGrid.innerHTML = '<span style="color: #999;">يرجى اختيار عمارات أولاً...</span>';
        
        if (!clubId) {
            buildingsGrid.innerHTML = '<span style="color: #999;">يرجى اختيار النادي أولاً...</span>';
            return;
        }

        fetch('/admin/bookings/booking/get-buildings-for-club/?club_id=' + clubId)
            .then(r => r.json())
            .then(data => {
                buildingsGrid.innerHTML = '';
                if (!data.buildings || data.buildings.length === 0) {
                    buildingsGrid.innerHTML = '<span style="color: #999;">لا توجد عمارات في هذا النادي.</span>';
                    return;
                }
                
                // Get already selected from hidden select
                var selectedB = Array.from(buildingsEl.options).filter(o => o.selected).map(o => o.value);

                data.buildings.forEach(b => {
                    var isChecked = selectedB.includes(b.id.toString());
                    var label = document.createElement('label');
                    label.style.cssText = 'background: #e8f5e9; padding: 5px 12px; border-radius: 20px; cursor: pointer; border: 1px solid #a5d6a7; display: flex; align-items: center; gap: 5px;';
                    label.innerHTML = `<input type="checkbox" class="building-cb" value="${b.id}" ${isChecked ? 'checked' : ''}> ${b.name}`;
                    buildingsGrid.appendChild(label);
                });

                document.querySelectorAll('.building-cb').forEach(cb => {
                    cb.addEventListener('change', function() {
                        updateHiddenBuildings();
                        fetchUnitsForSelectedBuildings();
                    });
                });
                
                if (selectedB.length > 0) fetchUnitsForSelectedBuildings();
            });
    }

    function updateHiddenBuildings() {
        var checkedIds = Array.from(document.querySelectorAll('.building-cb:checked')).map(cb => cb.value);
        Array.from(buildingsEl.options).forEach(opt => {
            opt.selected = checkedIds.includes(opt.value);
        });
    }

    function fetchUnitsForSelectedBuildings() {
        var checkedIds = Array.from(document.querySelectorAll('.building-cb:checked')).map(cb => cb.value);
        if (checkedIds.length === 0) {
            unitsGrid.innerHTML = '<span style="color: #999;">يرجى اختيار عمارات أولاً...</span>';
            updateHiddenUnits();
            return;
        }

        unitsGrid.innerHTML = '<span style="color: #999;">جاري التحميل...</span>';
        
        var promises = checkedIds.map(bId => fetch('/admin/bookings/booking/get-units-for-building/?building_id=' + bId).then(r => r.json()));
        
        Promise.all(promises).then(results => {
            unitsGrid.innerHTML = '';
            var allUnits = [];
            results.forEach(res => {
                if (res.units) allUnits = allUnits.concat(res.units);
            });

            if (allUnits.length === 0) {
                unitsGrid.innerHTML = '<span style="color: #999;">لا توجد وحدات.</span>';
                return;
            }

            // Get already selected
            var selectedU = Array.from(unitsEl.options).filter(o => o.selected).map(o => o.value);

            allUnits.forEach(u => {
                var isChecked = selectedU.includes(u.id.toString());
                var label = document.createElement('label');
                label.style.cssText = 'background: #fff3e0; padding: 5px 12px; border-radius: 20px; cursor: pointer; border: 1px solid #ffcc80; display: flex; align-items: center; gap: 5px;';
                label.innerHTML = `<input type="checkbox" class="unit-cb" value="${u.id}" ${isChecked ? 'checked' : ''}> ${u.name}`;
                unitsGrid.appendChild(label);
            });

            document.querySelectorAll('.unit-cb').forEach(cb => {
                cb.addEventListener('change', updateHiddenUnits);
            });
        });
    }

    function updateHiddenUnits() {
        var checkedIds = Array.from(document.querySelectorAll('.unit-cb:checked')).map(cb => cb.value);
        Array.from(unitsEl.options).forEach(opt => {
            opt.selected = checkedIds.includes(opt.value);
        });
    }

    // Bind club change event (handle select2 if present)
    var jq = window.jQuery || window.$;
    if (jq && jq(clubEl).data('select2')) {
        jq(clubEl).on('change', function() {
            fetchBuildings(this.value);
        });
    } else {
        clubEl.addEventListener('change', function() {
            fetchBuildings(this.value);
        });
    }

    // Initial load
    if (clubEl.value) {
        fetchBuildings(clubEl.value);
    }
});
