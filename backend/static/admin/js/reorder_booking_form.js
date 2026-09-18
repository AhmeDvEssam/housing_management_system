document.addEventListener('DOMContentLoaded', function() {
    // Reorder fieldsets and inlines to: Booking Data, Companions, Notes, Contract
    
    // Find Notes fieldset
    let notesFieldset = null;
    let fieldsets = document.querySelectorAll('fieldset.module, div.card');
    fieldsets.forEach(function(fs) {
        let title = fs.querySelector('.card-header .card-title, h2');
        if (title && title.textContent.includes('ملاحظات')) {
            notesFieldset = fs.closest('.card') || fs;
        }
    });
    
    // Find Companions inline
    let companionsInline = document.getElementById('companion_set-group');
    if (!companionsInline) {
        let inlineForms = document.querySelectorAll('.inline-group');
        inlineForms.forEach(function(ig) {
            if (ig.id && ig.id.includes('companion_set')) {
                companionsInline = ig.closest('.card') || ig;
            }
        });
    }

    // Find Contract inline
    let contractInline = document.getElementById('contract_detail-group');
    if (!contractInline) {
        let inlineForms = document.querySelectorAll('.inline-group');
        inlineForms.forEach(function(ig) {
            if (ig.id && (ig.id.includes('contract_detail') || ig.id.includes('contract'))) {
                contractInline = ig.closest('.card') || ig;
            }
        });
    }

    if (notesFieldset && companionsInline) {
        // Insert Companions inline BEFORE Notes fieldset
        notesFieldset.parentNode.insertBefore(companionsInline, notesFieldset);
    }
    
    // Make sure Contract inline is AFTER Notes fieldset
    if (notesFieldset && contractInline) {
        notesFieldset.parentNode.insertBefore(contractInline, notesFieldset.nextSibling);
    }
});
