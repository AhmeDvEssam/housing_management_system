window.addEventListener('load', function() {
    // 1. Locate fields
    var idNoEl = document.getElementById('id_guest_id_no');
    var nameEl = document.getElementById('id_guest_name');
    var rankEl = document.getElementById('id_guest_rank');
    var phoneEl = document.getElementById('id_guest_phone');
    var memberSelect = document.getElementById('id_member');
    
    if (!memberSelect) return;

    // Optional visual highlight for the member field row
    var memberFieldRow = memberSelect.closest('.form-group') || memberSelect.closest('.row') || memberSelect.parentNode;
    if (memberFieldRow) {
        memberFieldRow.style.backgroundColor = '#fdf8e4';
        memberFieldRow.style.border = '2px solid #fdb643';
        memberFieldRow.style.borderRadius = '8px';
        memberFieldRow.style.padding = '15px';
        memberFieldRow.style.marginBottom = '20px';
    }

    function onMemberSelected(memberId) {
        if (!memberId) return;

        if (nameEl) nameEl.style.backgroundColor = '#cee0f0';
        
        fetch('/admin/bookings/booking/get-member-details/?membership_no=' + encodeURIComponent(memberId))
            .then(function(res) {
                return res.json(); 
            })
            .then(function(data) {
                if (nameEl) nameEl.style.backgroundColor = '';
                if (data.found) {
                    if (idNoEl) idNoEl.value = data.membership_no || '';
                    if (nameEl) nameEl.value = data.name || '';
                    if (rankEl) rankEl.value = data.rank || '';
                    if (phoneEl) phoneEl.value = data.phone || '';
                    
                    [idNoEl, nameEl, rankEl, phoneEl].forEach(function(el) {
                        if (el) {
                            el.readOnly = true;
                            el.style.backgroundColor = '#f1f5f9';
                        }
                    });
                    
                    var isCivilian = false;
                    if (data.rank) {
                        var r = data.rank.trim();
                        // Checking for civilian ranks in Arabic
                        if (r.indexOf('\u0645\u062F\u0646\u064A') !== -1) { // 'مدني'
                            isCivilian = true;
                        }
                    }

                    var targetPersonTypeValue = isCivilian ? 'FAMILY_MEMBER' : 'MILITARY';
                    var targetRadio = document.querySelector('input[name="person_type"][value="' + targetPersonTypeValue + '"]');
                    if (targetRadio) {
                        targetRadio.checked = true;
                    }
                }
            })
            .catch(function(err) {
                console.error("Fetch API ERROR: ", err);
            });
    }

    // 2. Bind to django.jQuery for Select2 events
    var jq = null;
    if (typeof django !== 'undefined' && django.jQuery) {
        jq = django.jQuery;
    } else if (typeof jQuery !== 'undefined') {
        jq = jQuery;
    } else if (typeof $ !== 'undefined') {
        jq = $;
    }

    var lastMemberVal = memberSelect.value || '';
    
    if (jq) {
        jq(document).on('select2:select', '#id_member', function(e) {
            var currentVal = memberSelect.value || (e.params && e.params.data ? e.params.data.id : '');
            if (currentVal && currentVal !== lastMemberVal) {
                lastMemberVal = currentVal;
                onMemberSelected(currentVal);
            }
        });
        jq(document).on('change', '#id_member', function(e) {
            var currentVal = memberSelect.value || '';
            if (currentVal && currentVal !== lastMemberVal) {
                lastMemberVal = currentVal;
                onMemberSelected(currentVal);
            }
        });
    } else {
        // Fallback polling if no jQuery found
        setInterval(function() {
            var currentVal = memberSelect.value || '';
            if (currentVal !== lastMemberVal) {
                lastMemberVal = currentVal;
                onMemberSelected(currentVal);
            }
        }, 500);
    }
});
