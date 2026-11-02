// Glavni JavaScript za interakcije uporabniškega vmesnika
document.addEventListener('DOMContentLoaded', function () {
    // Samodejno zapri obvestila (messages/alerts) po 6 sekundah
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // Potrditev za brisanje (če se uporabi na gumbu s class="btn-confirm-delete")
    const deleteButtons = document.querySelectorAll('.btn-confirm-delete');
    deleteButtons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const msg = btn.getAttribute('data-confirm-message') || 'Ali ste prepričani, da želite izbrisati ta element? Dejanja ni mogoče razveljaviti.';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });
});

