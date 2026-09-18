/**
 * booking_member_fetch.js
 * 
 * المسؤول عن: ربط خانة "اختيار العضو" (Select2) بالخانات الأربعة:
 *   - رقم العضوية / الرقم القومي (id_guest_id_no)
 *   - الاسم (id_guest_name)  
 *   - الرتبة (id_guest_rank)
 *   - رقم الهاتف (id_guest_phone)
 *
 * ثلاث طرق لاكتشاف اختيار العضو:
 *   1. زرار "جلب البيانات" - يدوي ومضمون 100%
 *   2. MutationObserver - يراقب تغيير نص Select2
 *   3. Polling - يراقب قيمة الـ select كل 500ms
 */

(function() {
    'use strict';

    var initDone = false;
    function init() {
        if (initDone) return;
        initDone = true;
        setTimeout(initMemberFetch, 1000);
    }

    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        init();
    } else {
        window.addEventListener('DOMContentLoaded', init);
        window.addEventListener('load', init);
    }

    function initMemberFetch() {
        // === 1. Locate the 4 target fields ===
        var idNoEl   = document.getElementById('id_guest_id_no');
        var nameEl   = document.getElementById('id_guest_name');
        var rankEl   = document.getElementById('id_guest_rank');
        var phoneEl  = document.getElementById('id_guest_phone');
        var memberSelect = document.getElementById('id_member');

        if (!memberSelect) return;

        // === 2. Create the "Fetch Data" button ===
        var fetchBtn = document.createElement('button');
        fetchBtn.type = 'button'; // IMPORTANT: prevent form submission
        fetchBtn.innerHTML = '&#x1F504; جلب البيانات';
        fetchBtn.style.cssText = [
            'background: linear-gradient(135deg, #3b82f6, #2563eb)',
            'color: white',
            'border: none',
            'padding: 10px 24px',
            'border-radius: 8px',
            'cursor: pointer',
            'font-size: 15px',
            'font-weight: 700',
            'margin-top: 10px',
            'display: block',
            'transition: all 0.2s ease',
            'box-shadow: 0 2px 8px rgba(59,130,246,0.3)'
        ].join(';');
        
        fetchBtn.onmouseover = function() {
            fetchBtn.style.background = 'linear-gradient(135deg, #2563eb, #1d4ed8)';
            fetchBtn.style.transform = 'translateY(-1px)';
            fetchBtn.style.boxShadow = '0 4px 12px rgba(59,130,246,0.4)';
        };
        fetchBtn.onmouseout = function() {
            fetchBtn.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
            fetchBtn.style.transform = 'translateY(0)';
            fetchBtn.style.boxShadow = '0 2px 8px rgba(59,130,246,0.3)';
        };

        // Place the button after the member field row
        var memberFieldRow = memberSelect.closest('.form-group') || memberSelect.closest('.row') || memberSelect.parentNode;
        if (memberFieldRow) {
            memberFieldRow.style.backgroundColor = '#fdf8e4';
            memberFieldRow.style.border = '2px solid #fdb643';
            memberFieldRow.style.borderRadius = '8px';
            memberFieldRow.style.padding = '15px';
            memberFieldRow.style.marginBottom = '10px';
            memberFieldRow.appendChild(fetchBtn);
        }

        // === 3. The function that fetches member details and populates fields ===
        var isFetching = false;

        function onMemberSelected(memberId) {
            if (!memberId || isFetching) return;
            isFetching = true;

            // Visual feedback on button
            fetchBtn.innerHTML = '⏳ جاري جلب البيانات...';
            fetchBtn.style.opacity = '0.7';
            if (nameEl) nameEl.style.backgroundColor = '#cee0f0';

            fetch('/admin/bookings/booking/get-member-details/?membership_no=' + encodeURIComponent(memberId))
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (nameEl) nameEl.style.backgroundColor = '';

                    if (data.found) {
                        // Fill the 4 fields
                        if (idNoEl) idNoEl.value = data.membership_no || '';
                        if (nameEl) nameEl.value = data.name || '';
                        if (rankEl) rankEl.value = data.rank || '';
                        if (phoneEl) phoneEl.value = data.phone || '';

                        // Make fields readonly with visual indicator
                        [idNoEl, nameEl, rankEl, phoneEl].forEach(function(el) {
                            if (el) {
                                el.readOnly = true;
                                el.style.backgroundColor = '#f1f5f9';
                            }
                        });

                        // Auto-select person_type based on rank
                        var isCivilian = false;
                        if (data.rank) {
                            var r = data.rank.trim();
                            if (r.indexOf('\u0645\u062f\u0646\u064a') !== -1 ||
                                r.indexOf('\u0645\u062f\u0646\u0649') !== -1) {
                                isCivilian = true;
                            }
                        }
                        var targetValue = isCivilian ? 'FAMILY_MEMBER' : 'MILITARY';
                        var targetRadio = document.querySelector('input[name="person_type"][value="' + targetValue + '"]');
                        if (targetRadio) {
                            targetRadio.checked = true;
                            targetRadio.dispatchEvent(new Event('change', {bubbles: true}));
                        }

                        // Success feedback
                        fetchBtn.innerHTML = '&#x2705; تم جلب البيانات بنجاح';
                        fetchBtn.style.background = 'linear-gradient(135deg, #22c55e, #16a34a)';
                        setTimeout(function() {
                            fetchBtn.innerHTML = '&#x1F504; جلب البيانات';
                            fetchBtn.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
                        }, 3000);
                    } else {
                        fetchBtn.innerHTML = '&#x274C; العضو غير موجود';
                        fetchBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                        setTimeout(function() {
                            fetchBtn.innerHTML = '&#x1F504; جلب البيانات';
                            fetchBtn.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
                        }, 3000);
                    }
                })
                .catch(function(err) {
                    console.error('[MemberFetch] API Error:', err);
                    fetchBtn.innerHTML = '&#x274C; خطأ في الاتصال';
                    fetchBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                    setTimeout(function() {
                        fetchBtn.innerHTML = '&#x1F504; جلب البيانات';
                        fetchBtn.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
                    }, 3000);
                    if (nameEl) nameEl.style.backgroundColor = '';
                })
                .finally(function() {
                    isFetching = false;
                    fetchBtn.style.opacity = '1';
                });
        }

        // === 4. Button click handler ===
        fetchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var val = memberSelect.value;
            if (val) {
                lastMemberVal = val;
                onMemberSelected(val);
            } else {
                fetchBtn.innerHTML = '&#x26A0; اختر العضو أولاً';
                fetchBtn.style.background = 'linear-gradient(135deg, #f59e0b, #d97706)';
                setTimeout(function() {
                    fetchBtn.innerHTML = '&#x1F504; جلب البيانات';
                    fetchBtn.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
                }, 2000);
            }
        });

        // === 5. Auto-detect: Polling ===
        var lastMemberVal = memberSelect.value || '';

        // If value already exists on page load (e.g. after save error), fetch immediately
        if (lastMemberVal) {
            onMemberSelected(lastMemberVal);
        }

        setInterval(function() {
            var currentVal = memberSelect.value || '';
            if (currentVal && currentVal !== lastMemberVal) {
                lastMemberVal = currentVal;
                onMemberSelected(currentVal);
            }
        }, 500);

        // === 6. Auto-detect: MutationObserver on Select2 display text ===
        var select2Container = document.getElementById('select2-id_member-container');
        if (select2Container) {
            var observer = new MutationObserver(function(mutations) {
                var currentVal = memberSelect.value || '';
                if (currentVal && currentVal !== lastMemberVal) {
                    lastMemberVal = currentVal;
                    onMemberSelected(currentVal);
                }
            });
            observer.observe(select2Container, { childList: true, characterData: true, subtree: true });
        }

        // === 7. Auto-detect: django.jQuery events ===
        var jq = null;
        if (typeof django !== 'undefined' && django.jQuery) {
            jq = django.jQuery;
        } else if (typeof jQuery !== 'undefined') {
            jq = jQuery;
        }

        if (jq) {
            jq('#id_member').on('select2:select change', function() {
                var currentVal = memberSelect.value || '';
                if (currentVal && currentVal !== lastMemberVal) {
                    lastMemberVal = currentVal;
                    onMemberSelected(currentVal);
                }
            });
        }
    }
})();
